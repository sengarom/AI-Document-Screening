"""Synthetic-image tests for the document upload and preprocessing module."""

from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image, features

from app.api import documents
from app.main import app


def make_image_bytes(image_format: str, size: tuple[int, int] = (120, 80)) -> bytes:
    """Create an in-memory synthetic image; no real documents are used."""
    image = Image.new("RGB", size, color=(40, 100, 180))
    output = BytesIO()
    image.save(output, format=image_format)
    return output.getvalue()


@pytest.fixture()
def client_with_test_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(documents, "ORIGINAL_UPLOADS_DIR", tmp_path / "originals")
    monkeypatch.setattr(documents, "PROCESSED_UPLOADS_DIR", tmp_path / "processed")
    return TestClient(app)


def upload(client: TestClient, name: str, image_bytes: bytes, content_type: str):
    return client.post("/api/documents/upload", files={"file": (name, image_bytes, content_type)})


def test_health_endpoint_still_works(client_with_test_storage: TestClient) -> None:
    response = client_with_test_storage.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "AI Document Screening System"}


def test_valid_jpg_upload_and_preprocessing(client_with_test_storage: TestClient) -> None:
    response = upload(client_with_test_storage, "synthetic.jpg", make_image_bytes("JPEG"), "image/jpeg")
    body = response.json()
    assert response.status_code == 201
    assert body["success"] is True
    assert "document_id" in body
    assert body["original_filename"] == "synthetic.jpg"
    assert body["filename"].endswith(".jpg")
    assert body["original_width"] == 120
    assert body["original_height"] == 80
    assert body["processed_width"] == 120
    assert body["processed_height"] == 80
    assert body["preprocessing_status"] == "completed"


def test_valid_png_upload(client_with_test_storage: TestClient) -> None:
    response = upload(client_with_test_storage, "synthetic.png", make_image_bytes("PNG"), "image/png")
    assert response.status_code == 201
    assert response.json()["content_type"] == "image/png"


@pytest.mark.skipif(not features.check("webp"), reason="Pillow was built without WEBP support")
def test_valid_webp_upload_when_supported(client_with_test_storage: TestClient) -> None:
    response = upload(client_with_test_storage, "synthetic.webp", make_image_bytes("WEBP"), "image/webp")
    assert response.status_code == 201
    assert response.json()["content_type"] == "image/webp"


def test_unsupported_file_type_is_rejected(client_with_test_storage: TestClient) -> None:
    response = upload(client_with_test_storage, "notes.txt", b"not an image", "text/plain")
    assert response.status_code == 415


def test_empty_file_is_rejected(client_with_test_storage: TestClient) -> None:
    response = upload(client_with_test_storage, "empty.png", b"", "image/png")
    assert response.status_code == 422
    assert "empty" in response.json()["detail"].lower()


def test_corrupt_image_is_rejected(client_with_test_storage: TestClient) -> None:
    response = upload(client_with_test_storage, "broken.png", b"not really a png", "image/png")
    assert response.status_code == 422
    assert "valid image" in response.json()["detail"].lower()


def test_mismatched_mime_type_is_rejected(client_with_test_storage: TestClient) -> None:
    response = upload(client_with_test_storage, "synthetic.png", make_image_bytes("PNG"), "image/jpeg")
    assert response.status_code == 415


def test_file_larger_than_limit_is_rejected(client_with_test_storage: TestClient) -> None:
    response = upload(client_with_test_storage, "large.png", b"x" * (10 * 1024 * 1024 + 1), "image/png")
    assert response.status_code == 413


def test_large_image_keeps_aspect_ratio_and_original_is_untouched(
    client_with_test_storage: TestClient, tmp_path: Path
) -> None:
    original_bytes = make_image_bytes("PNG", size=(4000, 2000))
    response = upload(client_with_test_storage, "wide.png", original_bytes, "image/png")
    body = response.json()
    stored_original = tmp_path / "originals" / body["filename"]
    stored_processed = tmp_path / "processed" / f"{Path(body['filename']).stem}_processed.png"
    assert response.status_code == 201
    assert body["original_width"] == 4000
    assert body["original_height"] == 2000
    assert body["processed_width"] == 2000
    assert body["processed_height"] == 1000
    assert stored_original.read_bytes() == original_bytes
    assert stored_processed.exists()
