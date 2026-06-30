import io
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.document import DocumentService

client = TestClient(app)

@pytest.fixture
def mock_document_service():
    with patch("app.api.v1.endpoints.documents.get_document_service") as mock_get_service:
        mock_service = AsyncMock(spec=DocumentService)
        # We need to configure the dependency override properly
        app.dependency_overrides[app.api.v1.endpoints.documents.get_document_service] = lambda: mock_service
        yield mock_service
        app.dependency_overrides.clear()


def test_upload_document_success(mock_document_service):
    # Setup mock
    import uuid
    from datetime import datetime
    doc_id = uuid.uuid4()
    mock_document_service.upload_document.return_value = {
        "id": doc_id,
        "original_filename": "test.pdf",
        "stored_filename": "test-stored.pdf",
        "bucket_name": "documents",
        "storage_path": "test-stored.pdf",
        "mime_type": "application/pdf",
        "file_size": 1024,
        "upload_status": "ready",
        "description": "test desc",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    
    file_content = b"test content"
    files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {"title": "test.pdf", "description": "test desc"}

    response = client.post("/api/v1/documents/upload", files=files, data=data)
    
    assert response.status_code == 201
    assert response.json()["original_filename"] == "test.pdf"
    assert response.json()["upload_status"] == "ready"


def test_list_documents(mock_document_service):
    mock_document_service.list_documents.return_value = {
        "items": [],
        "total": 0,
        "skip": 0,
        "limit": 100
    }

    response = client.get("/api/v1/documents")
    
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_get_document(mock_document_service):
    import uuid
    from datetime import datetime
    doc_id = uuid.uuid4()
    
    mock_document_service.get_document.return_value = {
        "id": doc_id,
        "original_filename": "test.pdf",
        "stored_filename": "test-stored.pdf",
        "bucket_name": "documents",
        "storage_path": "test-stored.pdf",
        "mime_type": "application/pdf",
        "file_size": 1024,
        "upload_status": "ready",
        "description": "test desc",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    response = client.get(f"/api/v1/documents/{doc_id}")
    
    assert response.status_code == 200
    assert response.json()["original_filename"] == "test.pdf"


def test_get_download_url(mock_document_service):
    import uuid
    doc_id = uuid.uuid4()
    
    mock_document_service.get_download_url.return_value = "https://example.com/download"

    response = client.get(f"/api/v1/documents/{doc_id}/download")
    
    assert response.status_code == 200
    assert response.json()["download_url"] == "https://example.com/download"


def test_delete_document(mock_document_service):
    import uuid
    doc_id = uuid.uuid4()
    
    mock_document_service.delete_document.return_value = True

    response = client.delete(f"/api/v1/documents/{doc_id}")
    
    assert response.status_code == 204
