from app.schemas.risk import RiskScoreRequest, RiskScoreResponse, RiskLevel, RiskFactor
from app.schemas.face import FaceVerificationStatus
from app.services.risk.scoring_rules import get_risk_level, score_validation, score_tampering, score_face

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
        
    total_score = max(0, min(100, total_score))
    
    return RiskScoreResponse(
        document_id=request.validation_result.document_id,
        risk_score=total_score,
        risk_level=RiskLevel(get_risk_level(total_score)),
        factors=all_factors
    )