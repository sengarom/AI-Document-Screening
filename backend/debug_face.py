import cv2
import numpy as np
from pathlib import Path
import time
from app.services.face.engine import get_face_engines
from app.schemas.face import FaceVerificationStatus, FaceVerificationResponse

SFACE_COSINE_THRESHOLD = 0.363

def debug_face_verification(doc_path, ref_path):
    print(f"DOCUMENT IMAGE: {doc_path}")
    print(f"SELFIE IMAGE: {ref_path}")
    
    doc_img = cv2.imread(doc_path)
    ref_img = cv2.imread(ref_path)
    
    if doc_img is None: print("Failed to load doc")
    if ref_img is None: print("Failed to load ref")
        
    detector, recognizer = get_face_engines()
    
    def debug_detect(image, source_name):
        h, w = image.shape[:2]
        print(f"-> {source_name} dimensions: {w}x{h}")
        detector.setInputSize((w, h))
        _, faces = detector.detect(image)
        
        if faces is None:
            print(f"-> {source_name} face detection: 0 faces found")
            return None
        
        print(f"-> {source_name} face detection: {len(faces)} faces found")
        for i, face in enumerate(faces):
            box_x, box_y, box_w, box_h = face[:4]
            conf = face[-1]
            print(f"   Face {i+1}: box=({box_x}, {box_y}, {box_w}, {box_h}), conf={conf:.4f}")
        
        return faces[0] if len(faces) > 0 else None
        
    print("-> face detection")
    doc_face = debug_detect(doc_img, "document")
    ref_face = debug_detect(ref_img, "selfie")
    
    if doc_face is not None and ref_face is not None:
        print("-> selected document face crop")
        print("-> selected selfie face crop")
        
        aligned_doc_face = recognizer.alignCrop(doc_img, doc_face)
        aligned_ref_face = recognizer.alignCrop(ref_img, ref_face)
        print(f"   Aligned doc crop shape: {aligned_doc_face.shape}")
        print(f"   Aligned ref crop shape: {aligned_ref_face.shape}")
        
        print("-> SFace embeddings")
        doc_embedding = recognizer.feature(aligned_doc_face)
        ref_embedding = recognizer.feature(aligned_ref_face)
        
        print(f"   Embedding shape: {doc_embedding.shape}")
        print("-> raw similarity")
        cosine_score = recognizer.match(doc_embedding, ref_embedding, cv2.FaceRecognizerSF_FR_COSINE)
        l2_score = recognizer.match(doc_embedding, ref_embedding, cv2.FaceRecognizerSF_FR_NORM_L2)
        print(f"   Raw SFace cosine similarity: {cosine_score}")
        print(f"   Raw SFace L2 distance: {l2_score}")
        print(f"   Configured similarity threshold: {SFACE_COSINE_THRESHOLD}")
        
        is_match = bool(cosine_score >= SFACE_COSINE_THRESHOLD)
        print(f"-> normalized similarity: {cosine_score}")
        
        print("-> API response")
        response = FaceVerificationResponse(
            document_id="test",
            status=FaceVerificationStatus.MATCH if is_match else FaceVerificationStatus.NO_MATCH,
            verified=is_match,
            similarity_score=float(cosine_score),
            message="Match" if is_match else "No match",
            processing_time_ms=100
        )
        print(response.model_dump_json(indent=2))
        
        print("-> frontend displayed percentage")
        print(f"   (If frontend expects match_score): {0}%")
        print(f"   (If frontend uses similarity_score): {round(cosine_score * 100)}%")

if __name__ == '__main__':
    debug_face_verification(
        'tests/fixtures/synthetic_face_a.jpg',
        'tests/fixtures/synthetic_face_b.jpg'
    )
