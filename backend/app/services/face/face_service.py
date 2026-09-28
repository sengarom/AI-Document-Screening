import time
import cv2
import numpy as np
from pathlib import Path

from app.schemas.face import FaceVerificationResponse, FaceVerificationStatus
from app.services.face.engine import get_face_engines

SFACE_COSINE_THRESHOLD = 0.363

def verify_faces(document_id: str, document_image_path: str, reference_image_bytes: bytes) -> FaceVerificationResponse:
    start_time = time.time()
    
    reference_array = np.frombuffer(reference_image_bytes, np.uint8)
    ref_img = cv2.imdecode(reference_array, cv2.IMREAD_COLOR)
    if ref_img is None:
        raise ValueError("Could not decode reference image.")
        
    doc_img = cv2.imread(document_image_path)
    if doc_img is None:
        raise ValueError(f"Could not read document image: {document_image_path}")

    detector, recognizer = get_face_engines()
    
    def get_single_face(image: np.ndarray, source_name: str) -> tuple[np.ndarray, np.ndarray, FaceVerificationStatus, str]:
        h, w = image.shape[:2]
        
        # Scale large images down so YuNet can reliably detect faces
        max_dim = 800
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            proc_img = cv2.resize(image, (int(w * scale), int(h * scale)))
            h, w = proc_img.shape[:2]
        else:
            proc_img = image.copy()
            
        detector.setInputSize((w, h))
        _, faces = detector.detect(proc_img)
        
        if faces is None or len(faces) == 0:
            status = FaceVerificationStatus.NO_FACE_DOCUMENT if source_name == "document" else FaceVerificationStatus.NO_FACE_REFERENCE
            return proc_img, None, status, f"No face detected in {source_name}."
            
        if len(faces) > 1:
            # Sort faces by area descending
            sorted_faces = sorted(list(faces), key=lambda f: f[2] * f[3], reverse=True)
            # Find the first face that passes quality check
            valid_face = None
            for f in sorted_faces:
                # Must be reasonably sized relative to image (not a tiny noise box)
                box_w, box_h = f[2], f[3]
                if box_w < 30 or box_h < 30:
                    continue
                # Could add location heuristics here if needed (e.g. left side of Aadhar)
                valid_face = f
                break
                
            if valid_face is None:
                # Fallback to largest if all failed heuristics
                valid_face = sorted_faces[0]
                
            faces = [valid_face]
            
        face = faces[0]
        box_w, box_h = face[2], face[3]
        if box_w < 30 or box_h < 30:
            return proc_img, None, FaceVerificationStatus.QUALITY_FAILURE, f"Detected face in {source_name} is too small ({int(box_w)}x{int(box_h)})."
            
        x, y = max(0, int(face[0])), max(0, int(face[1]))
        w_box, h_box = int(box_w), int(box_h)
        face_roi = proc_img[y:min(h, y+h_box), x:min(w, x+w_box)]
        if face_roi.size > 0:
            gray_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            variance = cv2.Laplacian(gray_roi, cv2.CV_64F).var()
            if variance < 5.0:  # Relaxed blur threshold slightly for resized images
                return proc_img, None, FaceVerificationStatus.QUALITY_FAILURE, f"Detected face in {source_name} is too blurry."
                
        return proc_img, face, None, ""

    proc_doc, doc_face, doc_err_status, doc_err_msg = get_single_face(doc_img, "document")
    if doc_err_status:
        return FaceVerificationResponse(
            document_id=document_id,
            status=doc_err_status,
            verified=False,
            similarity_score=0.0,
            message=doc_err_msg,
            processing_time_ms=int((time.time() - start_time) * 1000)
        )
        
    proc_ref, ref_face, ref_err_status, ref_err_msg = get_single_face(ref_img, "reference")
    if ref_err_status:
        return FaceVerificationResponse(
            document_id=document_id,
            status=ref_err_status,
            verified=False,
            similarity_score=0.0,
            message=ref_err_msg,
            processing_time_ms=int((time.time() - start_time) * 1000)
        )
        
    aligned_doc_face = recognizer.alignCrop(proc_doc, doc_face)
    aligned_ref_face = recognizer.alignCrop(proc_ref, ref_face)
    
    doc_embedding = recognizer.feature(aligned_doc_face)
    ref_embedding = recognizer.feature(aligned_ref_face)
    
    cosine_score = recognizer.match(doc_embedding, ref_embedding, cv2.FaceRecognizerSF_FR_COSINE)
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
    
    return response
