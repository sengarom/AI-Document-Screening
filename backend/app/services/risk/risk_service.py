from app.schemas.risk import RiskScoreRequest, RiskScoreResponse, RiskLevel, RiskFactor
from app.schemas.face import FaceVerificationStatus
from app.schemas.validation import ValidationStatus
from app.schemas.identity import IdentityLinkStatus
from app.services.risk.scoring_rules import get_risk_level, score_validation, score_tampering, score_face, score_identity_link

def calculate_risk(request: RiskScoreRequest) -> RiskScoreResponse:
    use_face = False
    if request.face_result:
        unusable_statuses = [
            FaceVerificationStatus.NO_FACE_REFERENCE,
            FaceVerificationStatus.MULTIPLE_FACES_REFERENCE,
            FaceVerificationStatus.ERROR
        ]
        if request.face_result.status not in unusable_statuses:
            use_face = True
            
    val_max = 40 if use_face else 50
    tamp_max = 40 if use_face else 50
    face_max = 20 if use_face else 0
    link_max = 20
    
    total_score = 0
    all_factors = []
    
    val_score, val_factors = score_validation(request.validation_result, val_max)
    total_score += val_score
    all_factors.extend(val_factors)
    
    tamp_score, tamp_factors = score_tampering(request.tampering_result, tamp_max)
    total_score += tamp_score
    all_factors.extend(tamp_factors)
    
    if use_face and request.face_result:
        face_score, face_factors = score_face(request.face_result, face_max)
        total_score += face_score
        all_factors.extend(face_factors)
    elif request.face_result:
        msg = 'Reference image provided was invalid (e.g., no face or multiple faces).'
        if request.face_result.status == FaceVerificationStatus.ERROR:
            msg = 'Technical error during face verification.'
        all_factors.append(RiskFactor(
            category='Face Verification',
            signal=request.face_result.status.value.upper(),
            contribution=0,
            message=msg
        ))
        
    if request.identity_link_result:
        link_score, link_factors = score_identity_link(request.identity_link_result, link_max)
        total_score += link_score
        all_factors.extend(link_factors)
        
    # --- ENFORCE SEVERITY FLOORS ---
    floor = 0
    
    # Validation Floors
    if request.validation_result.status == ValidationStatus.FAILED:
        floor = max(floor, 50)
        
    # Tampering Floors
    if request.tampering_result.overall_status.value.upper() == 'REJECTED' or request.tampering_result.tampering_score > 0.8:
        floor = max(floor, 75)
    elif request.tampering_result.tampering_score > 0.4:
        floor = max(floor, 70)
        
    # Face Floors
    if request.face_result:
        if request.face_result.status == FaceVerificationStatus.NO_MATCH:
            floor = max(floor, 60)
        elif request.face_result.status in [FaceVerificationStatus.NO_FACE_DOCUMENT, FaceVerificationStatus.NO_FACE_REFERENCE, FaceVerificationStatus.MULTIPLE_FACES_DOCUMENT, FaceVerificationStatus.MULTIPLE_FACES_REFERENCE, FaceVerificationStatus.QUALITY_FAILURE]:
            floor = max(floor, 40)
            
    # Identity Link Floors
    if request.identity_link_result:
        if request.identity_link_result.status == IdentityLinkStatus.MULTIPLE_POTENTIAL_MATCHES:
            floor = max(floor, 75)
        elif request.identity_link_result.status == IdentityLinkStatus.POTENTIAL_MATCH:
            floor = max(floor, 40)
            
    total_score = max(total_score, floor)
    total_score = max(0, min(100, total_score))
    
    return RiskScoreResponse(
        document_id=request.validation_result.document_id,
        risk_score=total_score,
        risk_level=RiskLevel(get_risk_level(total_score)),
        factors=all_factors
    )