import pytest
import cv2
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from app.main import app
from app.schemas.face import FaceVerificationStatus
from app.services.face.face_service import verify_faces

client = TestClient(app)

# Helper to create a dummy image (e.g. noise or simple shapes) in memory
def create_dummy_image(w=200, h=200, color=(255, 255, 255)):
    img = np.random.randint(0, 256, (h, w, 3), dtype=np.uint8)
    img[:] = color
    img = cv2.randn(img, 128, 50) # Add noise
    _, buf = cv2.imencode('.jpg', img)
    return buf.tobytes()

@patch('app.services.face.face_service.get_face_engines')
def test_no_face_document(mock_get, tmp_path):
    mock_detector = MagicMock()
    # detect returns (status, faces) where faces is None or []
    mock_detector.detect.return_value = (1, None)
    mock_get.return_value = (mock_detector, MagicMock())
    
    doc_path = tmp_path / "doc.jpg"
    cv2.imwrite(str(doc_path), np.zeros((100, 100, 3), dtype=np.uint8))
    
    ref_bytes = create_dummy_image()
    
    resp = verify_faces("123", str(doc_path), ref_bytes)
    assert resp.status == FaceVerificationStatus.NO_FACE_DOCUMENT
    assert not resp.verified
    assert resp.similarity_score == 0.0

@patch('app.services.face.face_service.get_face_engines')
def test_multiple_faces_document(mock_get, tmp_path):
    mock_detector = MagicMock()
    # Mock multiple faces: format is [x, y, w, h, ...]
    mock_detector.detect.return_value = (1, np.array([[10, 10, 50, 50], [60, 60, 50, 50]]))
    mock_get.return_value = (mock_detector, MagicMock())
    
    doc_path = tmp_path / "doc.jpg"
    cv2.imwrite(str(doc_path), np.zeros((200, 200, 3), dtype=np.uint8))
    
    resp = verify_faces("123", str(doc_path), create_dummy_image())
    assert resp.status == FaceVerificationStatus.MULTIPLE_FACES_DOCUMENT

@patch('app.services.face.face_service.get_face_engines')
def test_no_face_reference(mock_get, tmp_path):
    mock_detector = MagicMock()
    # First call (document): 1 face
    # Second call (reference): 0 faces
    mock_detector.detect.side_effect = [
        (1, np.array([[10, 10, 50, 50]])),
        (1, None)
    ]
    mock_get.return_value = (mock_detector, MagicMock())
    
    doc_path = tmp_path / "doc.jpg"
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    img = cv2.randn(img, 128, 50)
    cv2.imwrite(str(doc_path), img)
    
    resp = verify_faces("123", str(doc_path), create_dummy_image())
    assert resp.status == FaceVerificationStatus.NO_FACE_REFERENCE

@patch('app.services.face.face_service.get_face_engines')
def test_poor_quality_face(mock_get, tmp_path):
    mock_detector = MagicMock()
    # Face bounding box is 20x20 (too small, <40 threshold)
    mock_detector.detect.return_value = (1, np.array([[10, 10, 20, 20]]))
    mock_get.return_value = (mock_detector, MagicMock())
    
    doc_path = tmp_path / "doc.jpg"
    cv2.imwrite(str(doc_path), np.zeros((100, 100, 3), dtype=np.uint8))
    
    resp = verify_faces("123", str(doc_path), create_dummy_image())
    assert resp.status == FaceVerificationStatus.QUALITY_FAILURE

def test_api_invalid_document_id():
    resp = client.post(
        "/api/documents/invalid_doc/face-verification",
        files={"reference_image": ("ref.jpg", b"fake_bytes", "image/jpeg")}
    )
    assert resp.status_code == 404

def test_api_corrupted_reference(tmp_path):
    doc_path = tmp_path / "valid_processed.png"
    cv2.imwrite(str(doc_path), np.zeros((100, 100, 3), dtype=np.uint8))
    
    with patch('app.api.documents.PROCESSED_UPLOADS_DIR', tmp_path):
        resp = client.post(
            "/api/documents/valid/face-verification",
            files={"reference_image": ("ref.jpg", b"corrupted", "image/jpeg")}
        )
        assert resp.status_code == 500


# ==========================================
# E2E REAL MODEL TESTS (Synthetic Images)
# ==========================================

def test_real_model_e2e_same_face():
    """
    Test real OpenCV SFace loading, embedding, and similarity.
    Uses a legally safe, AI-generated synthetic face (A vs A).
    """
    fixture_a = Path(__file__).parent / "fixtures" / "synthetic_face_a.jpg"
    
    with open(fixture_a, "rb") as f:
        ref_bytes = f.read()
        
    resp = verify_faces("123", str(fixture_a), ref_bytes)
    
    assert resp.status == FaceVerificationStatus.MATCH
    assert resp.verified is True
    # Similarity should be ~1.0
    assert resp.similarity_score > 0.9

def test_real_model_e2e_different_face():
    """
    Test real OpenCV SFace loading, embedding, and similarity.
    Uses two different legally safe, AI-generated synthetic faces (A vs B).
    """
    fixture_a = Path(__file__).parent / "fixtures" / "synthetic_face_a.jpg"
    fixture_b = Path(__file__).parent / "fixtures" / "synthetic_face_b.jpg"
    
    with open(fixture_b, "rb") as f:
        ref_bytes = f.read()
        
    resp = verify_faces("123", str(fixture_a), ref_bytes)
    
    assert resp.status == FaceVerificationStatus.NO_MATCH
    assert resp.verified is False
    assert resp.similarity_score < 0.363



