import time
import asyncio
import logging
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from app.core.exceptions import AppException
from app.repositories.document import DocumentRepository
from app.services.storage import StorageService
from app.document_processing.services.queue import ProcessingQueue
from app.document_processing.services.parsers import ParserFactory
from app.document_processing.services.cleaners import TextCleaner
from app.models.extracted_text import ExtractedText

logger = logging.getLogger(__name__)

# Configurable constants for retry logic and limits
MAX_RETRIES = 3
BASE_DELAY_SECONDS = 2
PROCESSING_TIMEOUT_SECONDS = 30.0


class DocumentProcessingService:
    """Orchestrator service for the document processing pipeline."""

    def __init__(
        self,
        repository: DocumentRepository,
        storage: StorageService,
        queue: Optional[ProcessingQueue] = None
    ):
        self.repository = repository
        self.storage = storage
        self.queue = queue

    def start_processing(self, document_id: UUID) -> None:
        """Trigger background processing job for a document."""
        if not self.queue:
            logger.error("ProcessingQueue is not initialized. Cannot run background processing.")
            raise AppException(status_code=500, detail="Background worker system is not configured.")

        # Update status to QUEUED
        try:
            doc = self.repository.get(document_id)
            if not doc:
                raise AppException(status_code=404, detail="Document not found.")

            self.repository.update(doc, {
                "processing_status": "Queued"
            })
            
            logger.info(f"Document {document_id} marked as Queued. Dispatching to background queue.")
            self.queue.enqueue(self.process_document_task, document_id, 0)
        except Exception as e:
            logger.error(f"Failed to enqueue processing job for document {document_id}: {e}")
            raise AppException(status_code=500, detail="Failed to initialize processing job.")

    async def process_document_task(self, document_id: UUID, retry_count: int = 0) -> None:
        """Background task running the extraction, cleaning, and storage pipeline."""
        start_time = time.time()
        logger.info(f"Starting processing task for document {document_id} (Attempt {retry_count + 1})")

        doc = self.repository.get(document_id)
        if not doc:
            logger.error(f"Processing failed: Document {document_id} not found in database.")
            return

        # Update status to Processing
        self.repository.update(doc, {
            "processing_status": "Processing",
            "processing_started_at": datetime.now(timezone.utc),
            "retry_count": retry_count
        })

        try:
            # 1. Load File from Supabase Storage
            if not self.storage.client:
                raise RuntimeError("Supabase client is not configured in StorageService.")

            # Download with timeout
            loop = asyncio.get_event_loop()
            logger.info(f"Downloading file from storage: {doc.storage_path}")
            
            file_bytes = await loop.run_in_executor(
                None,
                lambda: self.storage.client.storage.from_(self.storage.bucket_name).download(doc.storage_path)
            )

            if not file_bytes:
                raise ValueError("Downloaded file is empty or missing.")

            # 2. Select parser & Extract raw text (with processing timeout)
            parser = ParserFactory.get_parser(doc.original_filename)
            
            logger.info(f"Parser selected: {parser.__class__.__name__} for {doc.original_filename}")
            
            # Execute parsing with timeout
            extracted = await asyncio.wait_for(
                loop.run_in_executor(None, parser.parse, file_bytes, doc.original_filename),
                timeout=PROCESSING_TIMEOUT_SECONDS
            )

            # 3. Clean and normalize extracted text
            cleaned_text = TextCleaner.clean(extracted.raw_text)

            # Calculate stats
            duration = time.time() - start_time
            line_count = len(cleaned_text.splitlines())
            word_count = len(cleaned_text.split())
            char_count = len(cleaned_text)

            # 4. Save to PostgreSQL extracted_texts table
            extracted_obj = self.repository.db.query(ExtractedText).filter(
                ExtractedText.document_id == document_id
            ).first()

            extracted_data = {
                "document_id": document_id,
                "text_content": cleaned_text,
                "parser_used": extracted.parser_used,
                "version_number": doc.extracted_text_version,
                "character_count": char_count,
                "word_count": word_count,
                "page_count": extracted.page_count,
                "line_count": line_count,
                "extraction_status": "Completed",
                "processing_duration": duration
            }

            if extracted_obj:
                for key, val in extracted_data.items():
                    setattr(extracted_obj, key, val)
                self.repository.db.add(extracted_obj)
            else:
                new_extracted = ExtractedText(**extracted_data)
                self.repository.db.add(new_extracted)

            self.repository.db.commit()

            # 5. Store extracted text backup in Supabase Storage
            extracted_path = f"extracted/{document_id}.txt"
            cleaned_bytes = cleaned_text.encode("utf-8")
            
            await self.storage.upload_file(
                file_path=extracted_path,
                file_bytes=cleaned_bytes,
                content_type="text/plain"
            )

            # 6. Complete processing & update metadata in PostgreSQL
            self.repository.update(doc, {
                "processing_status": "Completed",
                "processing_completed_at": datetime.now(timezone.utc),
                "parser_used": extracted.parser_used,
                "page_count": extracted.page_count,
                "word_count": word_count,
                "character_count": char_count,
                "line_count": line_count,
                "processing_duration": duration,
                "extraction_completed": True,
                "processing_error": None
            })
            
            logger.info(f"Document {document_id} successfully processed and marked Completed in {duration:.2f}s.")

        except asyncio.TimeoutError:
            # Cancel task safely
            duration = time.time() - start_time
            logger.error(f"Processing timeout for document {document_id} after {PROCESSING_TIMEOUT_SECONDS}s.")
            await self._handle_processing_failure(
                doc,
                error_msg=f"Processing timed out after {PROCESSING_TIMEOUT_SECONDS} seconds.",
                retry_count=retry_count,
                duration=duration,
                is_retryable=True
            )

        except (ValueError, TypeError) as non_retryable_err:
            # Fatal validation or parsing errors (corrupted formats, empty files, etc.) - do not retry
            duration = time.time() - start_time
            logger.error(f"Non-retryable processing error for document {document_id}: {non_retryable_err}")
            await self._handle_processing_failure(
                doc,
                error_msg=str(non_retryable_err),
                retry_count=retry_count,
                duration=duration,
                is_retryable=False
            )

        except Exception as retryable_err:
            # Database timeouts, network errors, storage failures - retryable
            duration = time.time() - start_time
            logger.error(f"Unexpected processing error for document {document_id}: {retryable_err}")
            await self._handle_processing_failure(
                doc,
                error_msg=str(retryable_err),
                retry_count=retry_count,
                duration=duration,
                is_retryable=True
            )

    async def _handle_processing_failure(
        self,
        doc,
        error_msg: str,
        retry_count: int,
        duration: float,
        is_retryable: bool
    ) -> None:
        """Handle failure states and queue retries with exponential backoff if applicable."""
        # 1. Update document DB state with error details
        self.repository.update(doc, {
            "processing_status": "Failed",
            "processing_completed_at": datetime.now(timezone.utc),
            "processing_duration": duration,
            "processing_error": error_msg,
            "extraction_completed": False
        })

        # 2. Queue retry if appropriate
        if is_retryable and retry_count < MAX_RETRIES:
            next_retry = retry_count + 1
            backoff_delay = BASE_DELAY_SECONDS * (2 ** retry_count)
            
            logger.warning(
                f"Scheduling retry {next_retry}/{MAX_RETRIES} for document {doc.id} in {backoff_delay} seconds."
            )
            
            # Enqueue backoff task
            if self.queue:
                self.repository.update(doc, {"processing_status": "Retrying"})
                self.queue.enqueue(self._delayed_retry, doc.id, next_retry, backoff_delay)
        else:
            logger.error(f"Document {doc.id} processing permanently Failed. No more retries.")

    async def _delayed_retry(self, document_id: UUID, next_retry: int, delay: int) -> None:
        """Sleep wrapper for scheduling retry with backoff."""
        await asyncio.sleep(delay)
        await self.process_document_task(document_id, next_retry)
