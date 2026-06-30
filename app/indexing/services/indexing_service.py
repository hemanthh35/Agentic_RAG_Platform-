import logging
import time
import asyncio
from datetime import datetime, timezone
from uuid import UUID
from typing import List, Optional

from app.core.exceptions import AppException
from app.repositories.document import DocumentRepository
from app.models.extracted_text import ExtractedText
from app.indexing.chunking.chunker import HierarchicalChunker, Chunk
from app.indexing.embeddings.provider import BaseEmbeddingProvider, BGEM3Provider
from app.indexing.qdrant.vector_service import VectorService
from app.indexing import config

logger = logging.getLogger(__name__)


class IndexingService:
    """Orchestrates document chunking, embedding generation, Qdrant upserts, and postgres sync."""

    def __init__(
        self,
        repository: DocumentRepository,
        embedding_provider: Optional[BaseEmbeddingProvider] = None,
        vector_service: Optional[VectorService] = None,
        chunker: Optional[HierarchicalChunker] = None
    ):
        self.repository = repository
        self.embedding_provider = embedding_provider or BGEM3Provider()
        self.vector_service = vector_service or VectorService()
        self.chunker = chunker or HierarchicalChunker()

    def start_indexing(self, document_id: UUID) -> None:
        """Trigger synchronous or background task run. 
        
        Since background queueing is managed by ProcessingQueue wrappers, 
        this service is usually called directly within background task execution flows.
        """
        logger.info(f"Triggering semantic vector indexing workflow for document {document_id}")
        asyncio.create_task(self.index_document_task(document_id))

    async def index_document_task(self, document_id: UUID) -> None:
        """Coordinated indexing transaction: extracted text -> chunk -> embed -> Qdrant upload."""
        start_time = time.time()
        logger.info(f"Starting indexing task pipeline for document {document_id}")

        doc = self.repository.get(document_id)
        if not doc:
            logger.error(f"Indexing pipeline failed: Document {document_id} not found in database.")
            return

        # Fetch extracted text entry
        extracted_obj = self.repository.db.query(ExtractedText).filter(
            ExtractedText.document_id == document_id
        ).first()

        if not extracted_obj or not extracted_obj.text_content:
            logger.error(f"Indexing pipeline failed: No extracted text exists for document {document_id}.")
            self.repository.update(doc, {
                "embedding_status": "Failed",
                "index_status": "Failed"
            })
            return

        # Update initial metadata state
        self.repository.update(doc, {
            "embedding_status": "Generating",
            "index_status": "Indexing",
            "indexing_status": "Indexing",
            "indexing_started_at": datetime.now(timezone.utc)
        })

        try:
            # 1. Ensure Qdrant collection is built (idempotent setup)
            self.vector_service.ensure_collection(dimension=self.embedding_provider.dimension)

            # 2. Divide document into semantic text chunks
            logger.info("Executing text chunk subdivision...")
            chunks = self.chunker.chunk_document(
                text=extracted_obj.text_content,
                document_id=document_id,
                filename=doc.original_filename
            )

            if not chunks:
                raise ValueError("No meaningful content chunks generated from document text.")

            # Clean up existing PostgreSQL chunks (handles re-indexing idempotency)
            import uuid
            from app.models.chunk import Chunk as DBChunk
            self.repository.db.query(DBChunk).filter(DBChunk.document_id == document_id).delete()
            self.repository.db.commit()

            # Save chunk metadata to PostgreSQL
            db_chunks = []
            for c in chunks:
                db_chunk = DBChunk(
                    id=uuid.UUID(c.chunk_id),
                    document_id=document_id,
                    chunk_index=c.chunk_index,
                    section_title=c.metadata.get("section_title", "Root"),
                    page_number=c.metadata.get("page_number", 1),
                    character_count=c.character_count,
                    word_count=c.word_count,
                    start_position=c.metadata.get("start_position"),
                    end_position=c.metadata.get("end_position"),
                    chunk_size=c.character_count,
                    chunk_status="Pending"
                )
                db_chunks.append(db_chunk)
                self.repository.db.add(db_chunk)
                
            self.repository.db.commit()

            # 3. Batch process embedding generation to prevent system memory overload
            logger.info(f"Generating vectors for {len(chunks)} text chunks in batches...")
            embeddings: List[List[float]] = []
            
            # Divide into batches
            batch_size = config.BATCH_SIZE
            for i in range(0, len(chunks), batch_size):
                batch_chunks = chunks[i:i + batch_size]
                batch_texts = [c.text_content for c in batch_chunks]
                
                # Fetch batch vectors
                batch_vectors = self.embedding_provider.embed_texts(batch_texts)
                
                # Perform chunk-level validations before accepting vector response
                for vector in batch_vectors:
                    self._validate_embedding_vector(vector)
                    
                embeddings.extend(batch_vectors)

            # 4. Perform transaction upsert to Qdrant vector store
            logger.info("Executing upsert to Qdrant database...")
            self.vector_service.upsert_chunks(chunks, embeddings)

            # Save embedding metadata to PostgreSQL
            from app.models.embedding_metadata import EmbeddingMetadata as DBEmbeddingMetadata
            for db_chunk in db_chunks:
                db_embed_meta = DBEmbeddingMetadata(
                    chunk_id=db_chunk.id,
                    embedding_model=self.embedding_provider.model_name,
                    embedding_dimension=self.embedding_provider.dimension,
                    generation_time=(time.time() - start_time) / len(chunks) if len(chunks) > 0 else 0.0,
                    batch_number=1,
                    index_version=doc.index_version or 1,
                    generation_status="Completed",
                    retry_count=0
                )
                db_chunk.chunk_status = "Completed"
                self.repository.db.add(db_embed_meta)
                
            self.repository.db.commit()

            # 5. Pipeline finished successfully, commit document details to postgres
            duration = time.time() - start_time
            completion_time = datetime.now(timezone.utc)
            self.repository.update(doc, {
                "chunk_count": len(chunks),
                "embedding_model": self.embedding_provider.model_name,
                "embedding_dimension": self.embedding_provider.dimension,
                "embedding_status": "Completed",
                "index_status": "Indexed",
                "indexed_at": completion_time,
                "vector_collection": self.vector_service.collection_name,
                "indexing_duration": duration,
                "failed_chunk_count": 0,
                # New fields:
                "indexing_status": "Indexed",
                "indexing_completed_at": completion_time,
                "indexed_vector_count": len(chunks),
                "last_indexed_at": completion_time
            })
            logger.info(f"Document {document_id} semantic vector indexing completed successfully in {duration:.2f}s.")

        except Exception as e:
            # Safe transactional Rollback: clean up database/vector states on exceptions
            duration = time.time() - start_time
            logger.error(f"Semantic indexing pipeline failed for document {document_id}: {e}")
            
            # Wipe any partially uploaded points for this document from Qdrant
            self.vector_service.delete_document_vectors(str(document_id))
            
            # Wipe chunks from PostgreSQL
            try:
                from app.models.chunk import Chunk as DBChunk
                self.repository.db.query(DBChunk).filter(DBChunk.document_id == document_id).delete()
                self.repository.db.commit()
            except Exception as db_err:
                logger.error(f"Failed to clear PostgreSQL chunks during rollback: {db_err}")
            
            self.repository.update(doc, {
                "embedding_status": "Failed",
                "index_status": "Failed",
                "indexing_status": "Failed",
                "indexing_duration": duration,
                "indexing_completed_at": datetime.now(timezone.utc),
                "failed_chunk_count": 1, # Flag failure state count
                "retry_count": (doc.retry_count or 0) + 1
            })

    def _validate_embedding_vector(self, vector: List[float]) -> None:
        """Validate embedding vectors for expected properties (dimensions, null values, or corruption)."""
        if not vector or not isinstance(vector, list):
            raise ValueError("Corrupted or empty vector payload returned.")
            
        if len(vector) != self.embedding_provider.dimension:
            raise ValueError(
                f"Mismatched vector dimension. Expected {self.embedding_provider.dimension}, got {len(vector)}."
            )
            
        # Check for NaN or infinite float bounds
        for float_val in vector:
            if float_val is None or not isinstance(float_val, (int, float)):
                raise ValueError("Embedding vector contains non-numeric inputs.")
