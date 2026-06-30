import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4

from app.document_processing.services.parsers import ParserFactory, TXTParser, MarkdownParser
from app.models.extracted_text import ExtractedText
from app.document_processing.services.cleaners import TextCleaner
from app.document_processing.services.processing_service import DocumentProcessingService
from app.repositories.document import DocumentRepository
from app.services.storage import StorageService


def test_parser_factory_selection():
    pdf_parser = ParserFactory.get_parser("sample.pdf")
    docx_parser = ParserFactory.get_parser("report.docx")
    txt_parser = ParserFactory.get_parser("notes.txt")
    md_parser = ParserFactory.get_parser("readme.md")

    assert pdf_parser.__class__.__name__ == "PDFParser"
    assert docx_parser.__class__.__name__ == "DOCXParser"
    assert txt_parser.__class__.__name__ == "TXTParser"
    assert md_parser.__class__.__name__ == "MarkdownParser"

    with pytest.raises(ValueError):
        ParserFactory.get_parser("image.png")


def test_txt_parser_extraction():
    parser = TXTParser()
    test_content = b"Hello, this is standard text."
    extracted = parser.parse(test_content, "test.txt")
    
    assert extracted.raw_text == "Hello, this is standard text."
    assert extracted.parser_used == "native_txt"
    assert extracted.character_count == len(test_content)
    assert extracted.word_count == 5


def test_markdown_parser_cleaning():
    parser = MarkdownParser()
    md_content = b"# Heading 1\nThis is a **bold** paragraph with [link](https://google.com) and `code`."
    extracted = parser.parse(md_content, "readme.md")
    
    # Assert markdown syntax was cleaned
    assert "Heading 1" in extracted.raw_text
    assert "# Heading 1" not in extracted.raw_text
    assert "**bold**" not in extracted.raw_text
    assert "bold" in extracted.raw_text
    assert "[link]" not in extracted.raw_text
    assert "link" in extracted.raw_text


def test_text_cleaner_pipeline():
    dirty_text = "Line 1 \r\n\n\n  Line 2  \n\n\n\nLine 3 \x00"
    cleaned = TextCleaner.clean(dirty_text)
    
    # Lines are trimmed, line endings normalized, multiple blank lines collapsed
    assert cleaned == "Line 1\n\nLine 2\n\nLine 3"


@pytest.mark.asyncio
async def test_processing_service_successful_pipeline():
    # Setup mocks
    doc_id = uuid4()
    mock_doc = MagicMock()
    mock_doc.id = doc_id
    mock_doc.original_filename = "document.txt"
    mock_doc.storage_path = "document_key"
    mock_doc.extracted_text_version = 1
    
    mock_repo = MagicMock(spec=DocumentRepository)
    mock_repo.get.return_value = mock_doc
    # Database session mock for ExtractedText query
    mock_repo.db = MagicMock()
    mock_repo.db.query().filter().first.return_value = None
    
    mock_storage = MagicMock(spec=StorageService)
    # Storage download mock returning file bytes
    mock_storage.client = MagicMock()
    mock_storage.client.storage.from_().download = MagicMock(return_value=b"Hello plain text file.")
    mock_storage.bucket_name = "documents"
    mock_storage.upload_file = AsyncMock(return_value="extracted/doc.txt")
    
    mock_queue = MagicMock()
    
    service = DocumentProcessingService(mock_repo, mock_storage, mock_queue)
    
    # Process task
    await service.process_document_task(doc_id)
    
    # Asserts
    mock_repo.get.assert_called_with(doc_id)
    mock_storage.upload_file.assert_called_once()
    
    # Verify status updates inside repo
    update_calls = mock_repo.update.call_args_list
    # First status transition to processing
    assert update_calls[0][0][1]["processing_status"] == "Processing"
    # Final status transition to completed
    assert update_calls[1][0][1]["processing_status"] == "Completed"
    assert update_calls[1][0][1]["word_count"] == 4
    assert update_calls[1][0][1]["parser_used"] == "native_txt"


@pytest.mark.asyncio
async def test_processing_service_failure_retry():
    doc_id = uuid4()
    mock_doc = MagicMock()
    mock_doc.id = doc_id
    mock_doc.original_filename = "document.txt"
    mock_doc.storage_path = "document_key"
    mock_doc.extracted_text_version = 1
    
    mock_repo = MagicMock(spec=DocumentRepository)
    mock_repo.get.return_value = mock_doc
    mock_repo.db = MagicMock()
    mock_repo.db.query().filter().first.return_value = None
    
    mock_storage = MagicMock(spec=StorageService)
    mock_storage.client = MagicMock()
    # Trigger a mock storage download failure
    mock_storage.client.storage.from_().download = MagicMock(side_effect=Exception("Connection Timeout"))
    mock_storage.bucket_name = "documents"
    
    mock_queue = MagicMock()
    
    service = DocumentProcessingService(mock_repo, mock_storage, mock_queue)
    
    # Process task
    await service.process_document_task(doc_id, retry_count=0)
    
    # Asserts
    update_calls = mock_repo.update.call_args_list
    assert update_calls[0][0][1]["processing_status"] == "Processing"
    # Should update status to failed due to storage exception
    assert update_calls[1][0][1]["processing_status"] == "Failed"
    assert "Connection Timeout" in update_calls[1][0][1]["processing_error"]
    
    # Should schedule a retry since retry_count < MAX_RETRIES
    mock_queue.enqueue.assert_called_once()
    assert mock_queue.enqueue.call_args[0][0].__name__ == "_delayed_retry"
