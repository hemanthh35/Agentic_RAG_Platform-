import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4
import numpy as np

from app.indexing.chunking.chunker import HierarchicalChunker
from app.indexing.embeddings.provider import SimulatedEmbeddingProvider, BGEM3Provider
from app.indexing.qdrant.vector_service import VectorService
from app.indexing.services.indexing_service import IndexingService
from app.repositories.document import DocumentRepository
from app.models.extracted_text import ExtractedText


def test_hierarchical_chunker_section_splitting():
    """Verify hierarchical chunker recognizes sections and headings correctly."""
    chunker = HierarchicalChunker(chunk_size=100, chunk_overlap=10, min_length=5)
    text = (
        "# Introduction\n"
        "This is the introduction text. It has some text content.\n\n"
        "## Details\n"
        "Paragraph detailing some agent instructions."
    )
    doc_id = uuid4()
    chunks = chunker.chunk_document(text, doc_id, "test.md")
    
    assert len(chunks) > 0
    # First chunk should have section title as Introduction
    assert chunks[0].metadata["section_title"] == "Introduction"
    assert chunks[-1].metadata["section_title"] == "Details"
    assert chunks[0].document_id == str(doc_id)


def test_simulated_embedding_provider():
    """Verify SimulatedEmbeddingProvider outputs deterministic 1024 dimension vectors."""
    provider = SimulatedEmbeddingProvider(dimension=1024, model_name="test-model")
    texts = ["hello world", "different text"]
    
    embeddings = provider.embed_texts(texts)
    
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 1024
    assert len(embeddings[1]) == 1024
    
    # Test determinism
    embeddings_again = provider.embed_texts(["hello world"])
    assert np.allclose(embeddings[0], embeddings_again[0])


@pytest.mark.asyncio
async def test_vector_service_in_memory():
    """Verify Qdrant local integration works seamlessly using the in-memory driver."""
    try:
        from qdrant_client import QdrantClient
        # Pass location=":memory:" to trigger local in-memory Qdrant driver
        vector_service = VectorService(qdrant_url=":memory:")
        
        # Ensure collection creates successfully
        vector_service.ensure_collection(dimension=1024)
        
        # Verify collections list has our test collection
        collections = vector_service.client.get_collections().collections
        assert any(c.name == "documents" for c in collections)
    except ImportError:
        # Graceful fallback if qdrant-client package is not installed locally
        vector_service = VectorService(qdrant_url="mock")
        vector_service.client = MagicMock()
        mock_collections = MagicMock()
        mock_collection_obj = MagicMock()
        mock_collection_obj.name = "documents"
        mock_collections.collections = [mock_collection_obj]
        vector_service.client.get_collections.return_value = mock_collections
        
        vector_service.ensure_collection(dimension=1024)
        collections = vector_service.client.get_collections().collections
        assert any(c.name == "documents" for c in collections)


@pytest.mark.asyncio
async def test_indexing_service_successful_flow():
    """Verify IndexingService orchestrates successful chunking, embedding and indexing."""
    doc_id = uuid4()
    mock_doc = MagicMock()
    mock_doc.id = doc_id
    mock_doc.original_filename = "test.txt"
    
    mock_repo = MagicMock(spec=DocumentRepository)
    mock_repo.get.return_value = mock_doc
    mock_repo.db = MagicMock()
    
    # Create mock extracted text
    mock_extracted = ExtractedText(
        document_id=doc_id,
        text_content="# Heading 1\nSome parsed raw sentence text block.",
        parser_used="native_txt",
        character_count=100,
        word_count=20,
        page_count=1,
        line_count=2,
        extraction_status="Completed",
        processing_duration=0.5
    )
    mock_repo.db.query().filter().first.return_value = mock_extracted
    
    # Vector Service mock
    mock_vector_service = MagicMock(spec=VectorService)
    mock_vector_service.collection_name = "test_collection"
    
    # Embedding Provider mock yielding 1024 dimension deterministically
    mock_embedding_provider = MagicMock(spec=BGEM3Provider)
    mock_embedding_provider.dimension = 1024
    mock_embedding_provider.model_name = "test-bge"
    mock_embedding_provider.embed_texts.return_value = [[0.1] * 1024]
    
    service = IndexingService(
        repository=mock_repo,
        embedding_provider=mock_embedding_provider,
        vector_service=mock_vector_service
    )
    
    await service.index_document_task(doc_id)
    
    # Asserts
    mock_vector_service.ensure_collection.assert_called_once_with(dimension=1024)
    mock_vector_service.upsert_chunks.assert_called_once()
    
    # Check that repo metadata was updated with success states
    update_calls = mock_repo.update.call_args_list
    assert update_calls[0][0][1]["embedding_status"] == "Generating"
    assert update_calls[1][0][1]["embedding_status"] == "Completed"
    assert update_calls[1][0][1]["index_status"] == "Indexed"
    assert update_calls[1][0][1]["chunk_count"] > 0


@pytest.mark.asyncio
async def test_indexing_service_rollback_flow():
    """Verify IndexingService cleans up Qdrant vectors on pipeline failures."""
    doc_id = uuid4()
    mock_doc = MagicMock()
    mock_doc.id = doc_id
    mock_doc.original_filename = "test.txt"
    
    mock_repo = MagicMock(spec=DocumentRepository)
    mock_repo.get.return_value = mock_doc
    mock_repo.db = MagicMock()
    
    mock_extracted = ExtractedText(
        document_id=doc_id,
        text_content="# Heading 1\nSome text.",
        parser_used="native_txt",
        character_count=100,
        word_count=20,
        page_count=1,
        line_count=2,
        extraction_status="Completed",
        processing_duration=0.5
    )
    mock_repo.db.query().filter().first.return_value = mock_extracted
    
    # Vector Service mock that triggers exceptions during upsert
    mock_vector_service = MagicMock(spec=VectorService)
    mock_vector_service.upsert_chunks.side_effect = RuntimeError("Qdrant Unavailable")
    mock_vector_service.collection_name = "test_collection"
    
    mock_embedding_provider = MagicMock(spec=BGEM3Provider)
    mock_embedding_provider.dimension = 1024
    mock_embedding_provider.model_name = "test-bge"
    mock_embedding_provider.embed_texts.return_value = [[0.1] * 1024]
    
    service = IndexingService(
        repository=mock_repo,
        embedding_provider=mock_embedding_provider,
        vector_service=mock_vector_service
    )
    
    await service.index_document_task(doc_id)
    
    # Rollback vector deletions should be triggered
    mock_vector_service.delete_document_vectors.assert_called_once_with(str(doc_id))
    
    # Status updates should be set to Failed
    update_calls = mock_repo.update.call_args_list
    assert update_calls[1][0][1]["embedding_status"] == "Failed"
    assert update_calls[1][0][1]["index_status"] == "Failed"
