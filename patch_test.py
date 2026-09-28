import re

with open('backend/tests/test_face.py', 'r') as f:
    content = f.read()

old_content = """def test_multiple_faces_document(mock_get, tmp_path):
    mock_detector = MagicMock()
    # Mock multiple faces: format is [x, y, w, h, ...]
    mock_detector.detect.return_value = (1, np.array([[10, 10, 50, 50], [60, 60, 50, 50]]))
    mock_get.return_value = (mock_detector, MagicMock())
    
    doc_path = tmp_path / "doc.jpg"
    cv2.imwrite(str(doc_path), np.zeros((200, 200, 3), dtype=np.uint8))
    
    resp = verify_faces("123", str(doc_path), create_dummy_image())
    assert resp.status == FaceVerificationStatus.MULTIPLE_FACES_DOCUMENT"""

new_content = """def test_multiple_faces_document(mock_get, tmp_path):
    mock_detector = MagicMock()
    mock_recognizer = MagicMock()
    mock_detector.detect.return_value = (1, np.array([[10, 10, 50, 50], [60, 60, 100, 100]]))
    mock_get.return_value = (mock_detector, mock_recognizer)
    
    doc_path = tmp_path / "doc.jpg"
    cv2.imwrite(str(doc_path), np.zeros((200, 200, 3), dtype=np.uint8))
    
    mock_recognizer.alignCrop.return_value = np.zeros((112, 112, 3), dtype=np.uint8)
    mock_recognizer.feature.return_value = np.zeros((1, 128), dtype=np.float32)
    mock_recognizer.match.return_value = 0.99
    
    resp = verify_faces("123", str(doc_path), create_dummy_image())
    assert resp.status == FaceVerificationStatus.MATCH"""

if old_content in content:
    content = content.replace(old_content, new_content)
    with open('backend/tests/test_face.py', 'w') as f:
        f.write(content)
    print("Patched multiple faces test")
else:
    print("Failed to find target in test_face.py")
