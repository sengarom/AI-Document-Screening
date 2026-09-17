from typing import List, Tuple
from app.schemas.risk import RiskFactor
from app.schemas.validation import ValidationResponse, ValidationStatus
from app.schemas.tampering import TamperingResponse, TamperingStatus
from app.schemas.face import FaceVerificationResponse, FaceVerificationStatus

def get_risk_level(score: int) -> str:
    if score < 25: return 'LOW'
    if score < 50: return 'MEDIUM'
    if score < 75: return 'HIGH'
    return 'CRITICAL'

def score_validation(validation_result: ValidationResponse, max_points: int) -> Tuple[int, List[RiskFactor]]:
    factors = []
    total_contribution = 0
    
    if validation_result.status == ValidationStatus.PASSED:
        factors.append(RiskFactor(
            category='Validation',
            signal='PASSED',
            contribution=0,
            message='Document validation passed with no issues.'
        ))
        return 0, factors

    penalties = {
        'required_field_missing': 10,
        'date_of_birth_logic': 10,
        'issue_date_logic': 10,
        'issue_expiry_logic': 10,
        'dob_issue_logic': 10,
        'expiry_date_logic': 5,
        'mrz_passport_number_checksum': 15,
        'mrz_date_of_birth_checksum': 15,
        'mrz_expiry_checksum': 15,
        'mrz_composite_checksum': 15,
        'visual_mrz_passport_number_match': 15,
        'visual_mrz_gender_match': 15,
        'visual_mrz_dob_match': 15,
        'visual_mrz_expiry_match': 15,
        'unknown_failure': 5
    }

    for check in validation_result.checks:
        if check.status in [ValidationStatus.FAILED, ValidationStatus.WARNING]:
            base_penalty = 0
            base_msg = 'Validation check produced an anomaly.'
            
            if check.check.startswith('required_field_'):
                base_penalty = 10
                base_msg = 'A mandatory field is missing from the document.'
            elif check.check in penalties:
                base_penalty = penalties[check.check]
                if 'checksum' in check.check:
                    base_msg = 'Machine Readable Zone (MRZ) checksum validation failed.'
                elif 'match' in check.check:
                    base_msg = 'Visual data does not match the Machine Readable Zone (MRZ).'
                elif 'expiry_date_logic' == check.check:
                    base_msg = 'The document has expired.'
                elif 'logic' in check.check:
                    base_msg = 'Logical inconsistency in document dates.'
            else:
                base_penalty = penalties['unknown_failure']
                base_msg = 'A general validation check failed.'
                
            penalty = base_penalty
            if check.status == ValidationStatus.WARNING:
                penalty = int(base_penalty / 2)
                
            if penalty > 0:
                total_contribution += penalty
                factors.append(RiskFactor(
                    category='Validation',
                    signal=check.status.value.upper(),
                    contribution=penalty,
                    message=base_msg
                ))

    # If status is FAILED but absolutely NO recognizable checks were provided
    if validation_result.status == ValidationStatus.FAILED and len(validation_result.checks) == 0:
        total_contribution = max_points
        factors.append(RiskFactor(
            category='Validation',
            signal='FAILED',
            contribution=max_points,
            message='Document failed general validation.'
        ))

    # Cap at active maximum
    if total_contribution > max_points:
        total_contribution = max_points
        
    current_sum = sum(f.contribution for f in factors)
    if current_sum > max_points and len(factors) > 0:
        scale = max_points / current_sum
        adjusted_sum = 0
        for i, f in enumerate(factors):
            if i == len(factors) - 1:
                f.contribution = max_points - adjusted_sum
            else:
                f.contribution = int(f.contribution * scale)
                adjusted_sum += f.contribution

    return total_contribution, factors

def score_tampering(tampering_result: TamperingResponse, max_points: int) -> Tuple[int, List[RiskFactor]]:
    contribution = int(tampering_result.tampering_score * max_points)
    
    factors = []
    if contribution > 0:
        factors.append(RiskFactor(
            category='Tampering',
            signal=f'Score {tampering_result.tampering_score:.2f}',
            contribution=contribution,
            message=f'Forensic analysis produced elevated tampering evidence ({tampering_result.severity} severity).'
        ))
    else:
        factors.append(RiskFactor(
            category='Tampering',
            signal='PASSED',
            contribution=0,
            message='No significant forensic signals detected.'
        ))
        
    return contribution, factors

def score_face(face_result: FaceVerificationResponse, max_points: int) -> Tuple[int, List[RiskFactor]]:
    penalty = 0
    signal = face_result.status.value.upper()
    message = 'Face verification status.'
    
    if face_result.status == FaceVerificationStatus.NO_MATCH:
        penalty = max_points
        message = 'The reference selfie does not match the document face.'
    elif face_result.status == FaceVerificationStatus.NO_FACE_DOCUMENT:
        penalty = max_points
        message = 'No face was found on the provided document.'
    elif face_result.status == FaceVerificationStatus.QUALITY_FAILURE:
        penalty = int(max_points / 2)
        message = 'Poor image quality prevented reliable face verification.'
    elif face_result.status == FaceVerificationStatus.MULTIPLE_FACES_DOCUMENT:
        penalty = int(max_points / 2)
        message = 'Multiple faces were found on the document.'
    elif face_result.status == FaceVerificationStatus.MATCH:
        penalty = 0
        message = 'The reference selfie matches the document face.'

    factors = [RiskFactor(
        category='Face Verification',
        signal=signal,
        contribution=penalty,
        message=message
    )]
    
    return penalty, factors