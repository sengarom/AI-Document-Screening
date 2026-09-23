import json
import time
import numpy as np
import cv2
from pathlib import Path
from typing import List, Tuple, Dict, Any

from app.core.config import PROCESSED_UPLOADS_DIR
from app.schemas.identity import IdentityLinkResponse, IdentityLinkStatus, IdentityMatch
from app.services.face.engine import get_face_engines
from app.services.face.face_service import SFACE_COSINE_THRESHOLD
from app.services.document.metadata_service import get_document_metadata

IDENTITY_STORE_PATH = PROCESSED_UPLOADS_DIR / "identities.json"

def _load_identities() -> List[Dict[str, Any]]:
    if not IDENTITY_STORE_PATH.exists():
        return []
    try:
        with open(IDENTITY_STORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save_identities(identities: List[Dict[str, Any]]):
    with open(IDENTITY_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(identities, f)

def get_face_embedding(document_image_path: str) -> Tuple[np.ndarray, IdentityLinkStatus, str]:
    doc_img = cv2.imread(document_image_path)
    if doc_img is None:
        return None, IdentityLinkStatus.ERROR, "Could not read document image."
        
    detector, recognizer = get_face_engines()
    
    h, w = doc_img.shape[:2]
    detector.setInputSize((w, h))
    
    _, faces = detector.detect(doc_img)
    
    if faces is None or len(faces) == 0:
        return None, IdentityLinkStatus.NO_FACE, "No face detected in document."
        
    if len(faces) > 1:
        return None, IdentityLinkStatus.ERROR, "Multiple faces detected in document."
        
    face = faces[0]
    box_w, box_h = face[2], face[3]
    if box_w < 40 or box_h < 40:
        return None, IdentityLinkStatus.NO_FACE, "Detected face is too small."
        
    x, y = max(0, int(face[0])), max(0, int(face[1]))
    w_box, h_box = int(box_w), int(box_h)
    face_roi = doc_img[y:min(h, y+h_box), x:min(w, x+w_box)]
    if face_roi.size > 0:
        gray_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(gray_roi, cv2.CV_64F).var()
        if variance < 10.0:
            return None, IdentityLinkStatus.NO_FACE, "Detected face is too blurry."
            
    aligned_doc_face = recognizer.alignCrop(doc_img, face)
    doc_embedding = recognizer.feature(aligned_doc_face)
    
    return doc_embedding, None, ""

def analyze_identity_links(document_id: str, current_user: dict) -> IdentityLinkResponse:
    stem = Path(document_id).stem
    processed_file = PROCESSED_UPLOADS_DIR / f"{stem}_processed.png"
    
    if not processed_file.exists():
        return IdentityLinkResponse(
            document_id=document_id,
            status=IdentityLinkStatus.ERROR,
            message="Processed document not found."
        )

    try:
        embedding, err_status, err_msg = get_face_embedding(str(processed_file))
    except Exception as e:
        return IdentityLinkResponse(
            document_id=document_id,
            status=IdentityLinkStatus.ERROR,
            message=f"Failed to process face: {str(e)}"
        )
        
    if err_status:
        return IdentityLinkResponse(
            document_id=document_id,
            status=err_status,
            message=err_msg
        )
        
    identities = _load_identities()
    
    authorized_identities = []
    for identity in identities:
        if identity["document_id"] == document_id:
            continue
            
        if current_user.get("role") == "ADMIN" or identity.get("owner_id") == current_user.get("id"):
            authorized_identities.append(identity)

    is_stored = any(ident["document_id"] == document_id for ident in identities)
    if not is_stored:
        doc_meta = get_document_metadata(document_id)
        doc_type = doc_meta.get("document_type", "PASSPORT")
        
        identities.append({
            "document_id": document_id,
            "owner_id": current_user.get("id"),
            "document_type": doc_type,
            "timestamp": int(time.time()),
            "embedding": embedding.flatten().tolist()
        })
        _save_identities(identities)

    if not authorized_identities:
        return IdentityLinkResponse(
            document_id=document_id,
            status=IdentityLinkStatus.NO_PREVIOUS_IDENTITIES,
            message="No previous identities available."
        )
        
    _, recognizer = get_face_engines()
    matches = []
    
    for identity in authorized_identities:
        ref_emb = np.array(identity["embedding"], dtype=np.float32).reshape(1, -1)
        cosine_score = recognizer.match(embedding, ref_emb, cv2.FaceRecognizerSF_FR_COSINE)
        
        if cosine_score >= SFACE_COSINE_THRESHOLD:
            matches.append(IdentityMatch(
                document_id=identity["document_id"],
                document_type=identity["document_type"],
                similarity=float(cosine_score),
                requires_review=True
            ))
            
    matches.sort(key=lambda x: x.similarity, reverse=True)
    
    if not matches:
        return IdentityLinkResponse(
            document_id=document_id,
            status=IdentityLinkStatus.NO_MATCH,
            message="No potential identity links found."
        )
        
    if len(matches) == 1:
        return IdentityLinkResponse(
            document_id=document_id,
            status=IdentityLinkStatus.POTENTIAL_MATCH,
            matches=matches,
            message="Potential identity link detected — review recommended. Face similarity exceeded the configured review threshold against a previous authorized verification case. This signal does not establish that the identities are the same person or that fraud occurred."
        )
    else:
        return IdentityLinkResponse(
            document_id=document_id,
            status=IdentityLinkStatus.MULTIPLE_POTENTIAL_MATCHES,
            matches=matches,
            message="Multiple potential identity links detected. Face similarity exceeded the configured review threshold against previous authorized verification cases. This signal does not establish that the identities are the same person or that fraud occurred."
        )
