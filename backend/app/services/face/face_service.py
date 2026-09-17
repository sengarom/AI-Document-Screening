import time
import cv2
import numpy as np
from pathlib import Path

from app.schemas.face import FaceVerificationResponse, FaceVerificationStatus
from app.services.face.engine import get_face_engines

SFACE_COSINE_THRESHOLD = 0.363

def verify_faces(document_id: str, document_image_path: str, reference_image_bytes: bytes) -> FaceVerificationResponse:
    """
    Compare the face in the document against the reference selfie.
    Embeddings are kept only in process memory for the duration of verification 
    and are not intentionally persisted, logged, or stored.
    """
    start_time = time.time()
    
    # 1. Decode reference image in memory (does not touch persistent disk)
    reference_array = np.frombuffer(reference_image_bytes, np.uint8)
    ref_img = cv2.imdecode(reference_array, cv2.IMREAD_COLOR)
    if ref_img is None:
        raise ValueError("Could not decode reference image.")
        
    # 2. Read document image from disk
    doc_img = cv2.imread(document_image_path)
    if doc_img is None:
        raise ValueError(f"Could not read document image: {document_image_path}")

    # Initialize engines
    detector, recognizer = get_face_engines()
    
    # Helper to get the single valid face from an image
    def get_single_face(image: np.ndarray, source_name: str) -> tuple[np.ndarray, FaceVerificationStatus, str]:
        h, w = image.shape[:2]
        detector.setInputSize((w, h))
        
        # detect returns (status, faces)
        _, faces = detector.detect(image)
        
        if faces is None or len(faces) == 0:
            status = FaceVerificationStatus.NO_FACE_DOCUMENT if source_name == "document" else FaceVerificationStatus.NO_FACE_REFERENCE
            return None, status, f"No face detected in {source_name}."
            
        if len(faces) > 1:
            status = FaceVerificationStatus.MULTIPLE_FACES_DOCUMENT if source_name == "document" else FaceVerificationStatus.MULTIPLE_FACES_REFERENCE
            return None, status, f"Multiple faces detected in {source_name}. Exactly one face is required."
            
        face = faces[0]
        # Basic quality check: face box must be at least 40x40
        box_w, box_h = face[2], face[3]
        if box_w < 40 or box_h < 40:
            return None, FaceVerificationStatus.QUALITY_FAILURE, f"Detected face in {source_name} is too small ({int(box_w)}x{int(box_h)})."
            
        # Basic blur check via variance of Laplacian
        x, y = max(0, int(face[0])), max(0, int(face[1]))
        w_box, h_box = int(box_w), int(box_h)
        face_roi = image[y:min(h, y+h_box), x:min(w, x+w_box)]
        if face_roi.size > 0:
            gray_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            variance = cv2.Laplacian(gray_roi, cv2.CV_64F).var()
            if variance < 10.0:
                return None, FaceVerificationStatus.QUALITY_FAILURE, f"Detected face in {source_name} is too blurry."
                
        return face, None, ""

    # 3. Detect exactly one face in both images
    doc_face, doc_err_status, doc_err_msg = get_single_face(doc_img, "document")
    if doc_err_status:
        return FaceVerificationResponse(
            document_id=document_id,
            status=doc_err_status,
            verified=False,
            similarity_score=0.0,
            message=doc_err_msg,
            processing_time_ms=int((time.time() - start_time) * 1000)
        )
        
    ref_face, ref_err_status, ref_err_msg = get_single_face(ref_img, "reference")
    if ref_err_status:
        return FaceVerificationResponse(
            document_id=document_id,
            status=ref_err_status,
            verified=False,
            similarity_score=0.0,
            message=ref_err_msg,
            processing_time_ms=int((time.time() - start_time) * 1000)
        )
        
    # 4. Extract embeddings
    # Align faces first using the 5 landmarks provided by YuNet
    aligned_doc_face = recognizer.alignCrop(doc_img, doc_face)
    aligned_ref_face = recognizer.alignCrop(ref_img, ref_face)
    
    doc_embedding = recognizer.feature(aligned_doc_face)
    ref_embedding = recognizer.feature(aligned_ref_face)
    
    # 5. Calculate Similarity
    # match function returns either cosine or L2 distance.
    # CV_64F isn't strictly necessary, we use standard cosine metric constant: cv2.FaceRecognizerSF_FR_COSINE = 0
    cosine_score = recognizer.match(doc_embedding, ref_embedding, cv2.FaceRecognizerSF_FR_COSINE)
    
    # In OpenCV SFace, the returned match score for COSINE is actually the cosine similarity (higher is better).
    # The recommended threshold for positive match is >= 0.363
    is_match = bool(cosine_score >= SFACE_COSINE_THRESHOLD)
    
    status = FaceVerificationStatus.MATCH if is_match else FaceVerificationStatus.NO_MATCH
    msg = "Faces match." if is_match else "Faces do not match."
    
    response = FaceVerificationResponse(
        document_id=document_id,
        status=status,
        verified=is_match,
        similarity_score=float(cosine_score),
        message=msg,
        processing_time_ms=int((time.time() - start_time) * 1000)
    )
    
    # Explicitly clear variables holding biometrics
    del doc_embedding
    del ref_embedding
    del aligned_doc_face
    del aligned_ref_face
    del ref_img
    
    return response
