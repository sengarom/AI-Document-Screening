import pytest
import os
import json
import numpy as np
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.services.identity.identity_service import IDENTITY_STORE_PATH
from app.core.config import PROCESSED_UPLOADS_DIR, ORIGINAL_UPLOADS_DIR

@pytest.fixture
def clean_identity_store():
    if IDENTITY_STORE_PATH.exists():
        IDENTITY_STORE_PATH.unlink()
    yield
    if IDENTITY_STORE_PATH.exists():
        IDENTITY_STORE_PATH.unlink()

@pytest.fixture
def mock_face_embedding():
    return np.random.rand(1, 128).astype(np.float32)

@pytest.fixture
def mock_get_face_embedding():
    with patch("app.services.identity.identity_service.get_face_embedding") as mock_get:
        yield mock_get

@pytest.fixture
def mock_get_engines():
    with patch("app.services.identity.identity_service.get_face_engines") as mock_engines:
        mock_recognizer = MagicMock()
        mock_engines.return_value = (None, mock_recognizer)
        yield mock_recognizer

@pytest.fixture
def mock_processed_file():
    doc_id = "test_doc"
    path = PROCESSED_UPLOADS_DIR / f"{doc_id}_processed.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    yield doc_id
    path.unlink()

@pytest.fixture
def mock_metadata():
    with patch("app.services.identity.identity_service.get_document_metadata") as mock_meta:
        mock_meta.return_value = {"document_type": "PASSPORT", "owner_id": "test_user"}
        yield mock_meta

@pytest.fixture
def auth_client():
    client = TestClient(app)
    # Mocking require_document_ownership
    # We will just patch require_document_ownership in the dependency overrides
    return client

def test_empty_identity_index(auth_client, clean_identity_store, mock_get_face_embedding, mock_processed_file, mock_metadata):
    mock_get_face_embedding.return_value = (np.random.rand(1, 128), None, "")
    
    
    # Wait, getting the dependency right is tricky. Let's just override it by name:
    from app.api.documents import require_document_ownership
    app.dependency_overrides[require_document_ownership] = lambda: {"id": "test_user", "role": "USER"}
    
    response = auth_client.get(f"/api/documents/{mock_processed_file}/identity-links")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "no_previous_identities"

def test_no_face(auth_client, mock_get_face_embedding, mock_processed_file):
    from app.api.documents import require_document_ownership
    app.dependency_overrides[require_document_ownership] = lambda: {"id": "test_user", "role": "USER"}
    
    mock_get_face_embedding.return_value = (None, "no_face", "No face detected in document.")
    response = auth_client.get(f"/api/documents/{mock_processed_file}/identity-links")
    assert response.status_code == 200
    assert response.json()["status"] == "no_face"

def test_different_face(auth_client, clean_identity_store, mock_get_face_embedding, mock_processed_file, mock_metadata, mock_get_engines):
    from app.api.documents import require_document_ownership
    app.dependency_overrides[require_document_ownership] = lambda: {"id": "test_user", "role": "USER"}
    
    # Pre-populate store
    IDENTITY_STORE_PATH.write_text(json.dumps([{
        "document_id": "other_doc",
        "owner_id": "test_user",
        "document_type": "PASSPORT",
        "timestamp": 12345,
        "embedding": np.random.rand(128).tolist()
    }]))
    
    mock_get_face_embedding.return_value = (np.random.rand(1, 128), None, "")
    mock_get_engines.match.return_value = 0.1 # Below threshold
    
    response = auth_client.get(f"/api/documents/{mock_processed_file}/identity-links")
    assert response.status_code == 200
    assert response.json()["status"] == "no_match"

def test_matching_face(auth_client, clean_identity_store, mock_get_face_embedding, mock_processed_file, mock_metadata, mock_get_engines):
    from app.api.documents import require_document_ownership
    app.dependency_overrides[require_document_ownership] = lambda: {"id": "test_user", "role": "USER"}
    
    IDENTITY_STORE_PATH.write_text(json.dumps([{
        "document_id": "other_doc",
        "owner_id": "test_user",
        "document_type": "PASSPORT",
        "timestamp": 12345,
        "embedding": np.random.rand(128).tolist()
    }]))
    
    mock_get_face_embedding.return_value = (np.random.rand(1, 128), None, "")
    mock_get_engines.match.return_value = 0.8 # Above threshold
    
    response = auth_client.get(f"/api/documents/{mock_processed_file}/identity-links")
    assert response.status_code == 200
    assert response.json()["status"] == "potential_match"
    assert len(response.json()["matches"]) == 1

def test_multiple_potential_matches(auth_client, clean_identity_store, mock_get_face_embedding, mock_processed_file, mock_metadata, mock_get_engines):
    from app.api.documents import require_document_ownership
    app.dependency_overrides[require_document_ownership] = lambda: {"id": "test_user", "role": "USER"}
    
    IDENTITY_STORE_PATH.write_text(json.dumps([
        {
            "document_id": "other_doc1",
            "owner_id": "test_user",
            "document_type": "PASSPORT",
            "timestamp": 12345,
            "embedding": np.random.rand(128).tolist()
        },
        {
            "document_id": "other_doc2",
            "owner_id": "test_user",
            "document_type": "PASSPORT",
            "timestamp": 12346,
            "embedding": np.random.rand(128).tolist()
        }
    ]))
    
    mock_get_face_embedding.return_value = (np.random.rand(1, 128), None, "")
    mock_get_engines.match.return_value = 0.8 # Above threshold
    
    response = auth_client.get(f"/api/documents/{mock_processed_file}/identity-links")
    assert response.status_code == 200
    assert response.json()["status"] == "multiple_potential_matches"
    assert len(response.json()["matches"]) == 2

def test_current_case_self_exclusion(auth_client, clean_identity_store, mock_get_face_embedding, mock_processed_file, mock_metadata, mock_get_engines):
    from app.api.documents import require_document_ownership
    app.dependency_overrides[require_document_ownership] = lambda: {"id": "test_user", "role": "USER"}
    
    IDENTITY_STORE_PATH.write_text(json.dumps([{
        "document_id": mock_processed_file,
        "owner_id": "test_user",
        "document_type": "PASSPORT",
        "timestamp": 12345,
        "embedding": np.random.rand(128).tolist()
    }]))
    
    mock_get_face_embedding.return_value = (np.random.rand(1, 128), None, "")
    mock_get_engines.match.return_value = 0.8
    
    response = auth_client.get(f"/api/documents/{mock_processed_file}/identity-links")
    assert response.status_code == 200
    assert response.json()["status"] == "no_previous_identities"

def test_invalid_document_id(auth_client):
    from app.api.documents import require_document_ownership
    app.dependency_overrides[require_document_ownership] = lambda: {"id": "test_user", "role": "USER"}
    
    response = auth_client.get("/api/documents/invalid_doc_id/identity-links")
    assert response.status_code == 200
    assert response.json()["status"] == "error"

def test_unauthorized_user(auth_client, clean_identity_store, mock_get_face_embedding, mock_processed_file, mock_metadata, mock_get_engines):
    app.dependency_overrides = {}
    # Rely on actual auth, no cookie provided -> 401
    response = auth_client.get(f"/api/documents/{mock_processed_file}/identity-links")
    assert response.status_code == 401

def test_admin_access(auth_client, clean_identity_store, mock_get_face_embedding, mock_processed_file, mock_metadata, mock_get_engines):
    from app.api.documents import require_document_ownership
    app.dependency_overrides[require_document_ownership] = lambda: {"id": "admin_user", "role": "ADMIN"}
    
    IDENTITY_STORE_PATH.write_text(json.dumps([{
        "document_id": "other_doc",
        "owner_id": "other_user",
        "document_type": "PASSPORT",
        "timestamp": 12345,
        "embedding": np.random.rand(128).tolist()
    }]))
    
    mock_get_face_embedding.return_value = (np.random.rand(1, 128), None, "")
    mock_get_engines.match.return_value = 0.8
    
    response = auth_client.get(f"/api/documents/{mock_processed_file}/identity-links")
    assert response.status_code == 200
    assert response.json()["status"] == "potential_match"

def test_malformed_identity_storage(auth_client, clean_identity_store, mock_get_face_embedding, mock_processed_file, mock_metadata):
    from app.api.documents import require_document_ownership
    app.dependency_overrides[require_document_ownership] = lambda: {"id": "test_user", "role": "USER"}
    
    IDENTITY_STORE_PATH.write_text("invalid json")
    
    mock_get_face_embedding.return_value = (np.random.rand(1, 128), None, "")
    
    response = auth_client.get(f"/api/documents/{mock_processed_file}/identity-links")
    assert response.status_code == 200
    assert response.json()["status"] == "no_previous_identities"

def test_duplicate_embeddings_cases(auth_client, clean_identity_store, mock_get_face_embedding, mock_processed_file, mock_metadata, mock_get_engines):
    from app.api.documents import require_document_ownership
    app.dependency_overrides[require_document_ownership] = lambda: {"id": "test_user", "role": "USER"}
    
    IDENTITY_STORE_PATH.write_text(json.dumps([
        {
            "document_id": "other_doc",
            "owner_id": "test_user",
            "document_type": "PASSPORT",
            "timestamp": 12345,
            "embedding": np.random.rand(128).tolist()
        },
        {
            "document_id": "other_doc",
            "owner_id": "test_user",
            "document_type": "PASSPORT",
            "timestamp": 12346,
            "embedding": np.random.rand(128).tolist()
        }
    ]))
    
    mock_get_face_embedding.return_value = (np.random.rand(1, 128), None, "")
    mock_get_engines.match.return_value = 0.8
    
    response = auth_client.get(f"/api/documents/{mock_processed_file}/identity-links")
    assert response.status_code == 200
    # The duplicate should be caught or just evaluated normally (2 matches)
    assert response.json()["status"] == "multiple_potential_matches"


def test_existing_face_verification_regression(auth_client, mock_processed_file, mock_metadata):
    from app.api.documents import require_document_ownership
    auth_client.app.dependency_overrides[require_document_ownership] = lambda: {"id": "test_user", "role": "USER"}
    
    from unittest.mock import patch
    with patch("app.api.documents.verify_faces") as mock_verify:
        from app.schemas.face import FaceVerificationResponse, FaceVerificationStatus
        mock_verify.return_value = FaceVerificationResponse(
            document_id=mock_processed_file,
            status=FaceVerificationStatus.MATCH,
            verified=True,
            similarity_score=0.9,
            message="Faces match.",
            processing_time_ms=100
        )
        
        response = auth_client.post(
            f"/api/documents/{mock_processed_file}/face-verification",
            files={"reference_image": ("dummy.jpg", b"dummy_content", "image/jpeg")}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "match"
