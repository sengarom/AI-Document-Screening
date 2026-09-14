from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api import documents
from tests.mocks.mock_ocr import mock_extract_text

@pytest.fixture()
def client_with_mocked_ocr(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(documents, "ORIGINAL_UPLOADS_DIR", tmp_path / "originals")
    monkeypatch.setattr(documents, "PROCESSED_UPLOADS_DIR", tmp_path / "processed")
    # Patch the extract_text function imported in documents.py
    monkeypatch.setattr(documents, "extract_text", mock_extract_text)
    
    (tmp_path / "processed").mkdir(parents=True, exist_ok=True)
    return TestClient(app, raise_server_exceptions=False)

def test_run_ocr_success(client_with_mocked_ocr: TestClient, tmp_path: Path) -> None:
    # Setup dummy processed image
    doc_id = "test_doc.png"
    processed_file = tmp_path / "processed" / "test_doc_processed.png"
    processed_file.touch()
    
    response = client_with_mocked_ocr.post(f"/api/documents/{doc_id}/ocr")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["document_id"] == doc_id
    assert body["extracted_fields"]["name"] == "JOHN DOE"
    assert len(body["detections"]) == 4

def test_run_ocr_document_not_found(client_with_mocked_ocr: TestClient) -> None:
    response = client_with_mocked_ocr.post("/api/documents/non_existent.jpg/ocr")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_run_ocr_malformed(client_with_mocked_ocr: TestClient, tmp_path: Path) -> None:
    # Setup dummy processed image
    doc_id = "malformed_doc.png"
    processed_file = tmp_path / "processed" / "malformed_doc_processed.png"
    processed_file.touch()
    
    response = client_with_mocked_ocr.post(f"/api/documents/{doc_id}/ocr")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["extracted_fields"]["name"] is None
    assert len(body["detections"]) == 0

def test_run_ocr_server_error(client_with_mocked_ocr: TestClient, tmp_path: Path) -> None:
    doc_id = "fail_doc.png"
    processed_file = tmp_path / "processed" / "fail_doc_processed.png"
    processed_file.touch()
    
    # Fastapi will catch the exception and return 500
    response = client_with_mocked_ocr.post(f"/api/documents/{doc_id}/ocr")
    assert response.status_code == 500
