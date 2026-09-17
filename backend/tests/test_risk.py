import pytest
from app.schemas.risk import RiskScoreRequest, RiskLevel, RiskScoreResponse
from app.schemas.validation import ValidationResponse, ValidationStatus, ValidationCheck
from app.schemas.tampering import TamperingResponse, TamperingStatus
from app.schemas.face import FaceVerificationResponse, FaceVerificationStatus

def make_validation(status: ValidationStatus, checks: list = None) -> ValidationResponse:
    if checks is None:
        checks = []
    return ValidationResponse(
        document_id='doc1',
        valid=(status == ValidationStatus.PASSED),
        status=status,
        checks=checks
    )

def make_tampering(score: float, status: TamperingStatus = TamperingStatus.PASSED) -> TamperingResponse:
    return TamperingResponse(
        document_id='doc1',
        overall_status=status,
        tampering_score=score,
        severity='LOW' if score < 0.3 else 'HIGH',
        signals={},
        processing_time_ms=100
    )

def make_face(status: FaceVerificationStatus) -> FaceVerificationResponse:
    return FaceVerificationResponse(
        document_id='doc1',
        status=status,
        verified=(status == FaceVerificationStatus.MATCH),
        similarity_score=0.9 if status == FaceVerificationStatus.MATCH else 0.1,
        message='Test',
        processing_time_ms=100
    )

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_risk_everything_passes():
    req = RiskScoreRequest(
        validation_result=make_validation(ValidationStatus.PASSED),
        tampering_result=make_tampering(0.0),
        face_result=make_face(FaceVerificationStatus.MATCH)
    )
    resp = client.post('/api/documents/doc1/risk-score', json=req.model_dump())
    assert resp.status_code == 200
    data = resp.json()
    assert data['risk_score'] == 0
    assert data['risk_level'] == 'LOW'

def test_risk_validation_warning():
    req = RiskScoreRequest(
        validation_result=make_validation(ValidationStatus.WARNING, [
            ValidationCheck(check='expiry_date_logic', status=ValidationStatus.WARNING, message='Expired.')
        ]),
        tampering_result=make_tampering(0.0),
        face_result=make_face(FaceVerificationStatus.MATCH)
    )
    resp = client.post('/api/documents/doc1/risk-score', json=req.model_dump())
    assert resp.status_code == 200
    data = resp.json()
    assert data['risk_score'] == 2

def test_risk_validation_missing_required_field():
    req = RiskScoreRequest(
        validation_result=make_validation(ValidationStatus.FAILED, [
            ValidationCheck(check='required_field_name', status=ValidationStatus.FAILED, message='Missing.')
        ]),
        tampering_result=make_tampering(0.0),
        face_result=make_face(FaceVerificationStatus.MATCH)
    )
    resp = client.post('/api/documents/doc1/risk-score', json=req.model_dump())
    assert resp.status_code == 200
    data = resp.json()
    assert data['risk_score'] == 10

def test_risk_validation_mrz_checksum_failure():
    req = RiskScoreRequest(
        validation_result=make_validation(ValidationStatus.FAILED, [
            ValidationCheck(check='mrz_composite_checksum', status=ValidationStatus.FAILED, message='Failed.')
        ]),
        tampering_result=make_tampering(0.0),
        face_result=make_face(FaceVerificationStatus.MATCH)
    )
    resp = client.post('/api/documents/doc1/risk-score', json=req.model_dump())
    assert resp.status_code == 200
    assert resp.json()['risk_score'] == 15

def test_risk_validation_visual_mrz_mismatch():
    req = RiskScoreRequest(
        validation_result=make_validation(ValidationStatus.FAILED, [
            ValidationCheck(check='visual_mrz_dob_match', status=ValidationStatus.FAILED, message='Failed.')
        ]),
        tampering_result=make_tampering(0.0),
        face_result=make_face(FaceVerificationStatus.MATCH)
    )
    resp = client.post('/api/documents/doc1/risk-score', json=req.model_dump())
    assert resp.status_code == 200
    assert resp.json()['risk_score'] == 15
    
def test_risk_face_not_supplied():
    req = RiskScoreRequest(
        validation_result=make_validation(ValidationStatus.FAILED, [
            ValidationCheck(check='unknown_failure', status=ValidationStatus.FAILED, message='Generic.')
        ]),
        tampering_result=make_tampering(0.0)
    )
    resp = client.post('/api/documents/doc1/risk-score', json=req.model_dump())
    assert resp.status_code == 200
    assert resp.json()['risk_score'] == 5
    
    req = RiskScoreRequest(
        validation_result=make_validation(ValidationStatus.FAILED, [
            ValidationCheck(check='mrz_composite_checksum', status=ValidationStatus.FAILED, message=''),
            ValidationCheck(check='visual_mrz_dob_match', status=ValidationStatus.FAILED, message=''),
            ValidationCheck(check='visual_mrz_gender_match', status=ValidationStatus.FAILED, message=''),
            ValidationCheck(check='visual_mrz_expiry_match', status=ValidationStatus.FAILED, message='')
        ]),
        tampering_result=make_tampering(0.0)
    )
    resp = client.post('/api/documents/doc1/risk-score', json=req.model_dump())
    assert resp.status_code == 200
    assert resp.json()['risk_score'] == 50
    
def test_risk_face_error_or_no_reference():
    req = RiskScoreRequest(
        validation_result=make_validation(ValidationStatus.PASSED),
        tampering_result=make_tampering(1.0, TamperingStatus.FAILED),
        face_result=make_face(FaceVerificationStatus.ERROR)
    )
    resp = client.post('/api/documents/doc1/risk-score', json=req.model_dump())
    data = resp.json()
    assert data['risk_score'] == 50
    
    face_factor = next(f for f in data['factors'] if f['category'] == 'Face Verification')
    assert face_factor['contribution'] == 0
    assert 'error' in face_factor['message'].lower()

def test_risk_face_mismatch():
    req = RiskScoreRequest(
        validation_result=make_validation(ValidationStatus.PASSED),
        tampering_result=make_tampering(0.0),
        face_result=make_face(FaceVerificationStatus.NO_MATCH)
    )
    resp = client.post('/api/documents/doc1/risk-score', json=req.model_dump())
    assert resp.json()['risk_score'] == 20
    
def test_risk_multiple_simultaneous():
    req = RiskScoreRequest(
        validation_result=make_validation(ValidationStatus.FAILED, [
            ValidationCheck(check='mrz_composite_checksum', status=ValidationStatus.FAILED, message=''),
            ValidationCheck(check='required_field_name', status=ValidationStatus.FAILED, message='')
        ]),
        tampering_result=make_tampering(0.5),
        face_result=make_face(FaceVerificationStatus.NO_MATCH)
    )
    resp = client.post('/api/documents/doc1/risk-score', json=req.model_dump())
    assert resp.json()['risk_score'] == 65

def test_risk_score_bounds():
    req = RiskScoreRequest(
        validation_result=make_validation(ValidationStatus.FAILED, [
            ValidationCheck(check='mrz_composite_checksum', status=ValidationStatus.FAILED, message=''),
            ValidationCheck(check='visual_mrz_dob_match', status=ValidationStatus.FAILED, message=''),
            ValidationCheck(check='visual_mrz_gender_match', status=ValidationStatus.FAILED, message=''),
            ValidationCheck(check='visual_mrz_expiry_match', status=ValidationStatus.FAILED, message='')
        ]),
        tampering_result=make_tampering(1.0, TamperingStatus.FAILED),
        face_result=make_face(FaceVerificationStatus.NO_MATCH)
    )
    resp = client.post('/api/documents/doc1/risk-score', json=req.model_dump())
    assert resp.json()['risk_score'] == 100
def test_risk_validation_warning_half_penalty():
    req = RiskScoreRequest(
        validation_result=make_validation(ValidationStatus.WARNING, [
            ValidationCheck(check="required_field_name", status=ValidationStatus.WARNING, message="Missing.")
        ]),
        tampering_result=make_tampering(0.0),
        face_result=make_face(FaceVerificationStatus.MATCH)
    )
    resp = client.post("/api/documents/doc1/risk-score", json=req.model_dump())
    assert resp.status_code == 200
    # FAILED penalty is 10. WARNING should be 5.
    assert resp.json()["risk_score"] == 5

def test_risk_validation_recognized_failed():
    req = RiskScoreRequest(
        validation_result=make_validation(ValidationStatus.FAILED, [
            ValidationCheck(check="required_field_name", status=ValidationStatus.FAILED, message="Missing.")
        ]),
        tampering_result=make_tampering(0.0),
        face_result=make_face(FaceVerificationStatus.MATCH)
    )
    resp = client.post("/api/documents/doc1/risk-score", json=req.model_dump())
    assert resp.status_code == 200
    assert resp.json()["risk_score"] == 10

def test_risk_validation_recognized_warning():
    req = RiskScoreRequest(
        validation_result=make_validation(ValidationStatus.WARNING, [
            ValidationCheck(check="mrz_composite_checksum", status=ValidationStatus.WARNING, message="Warning.")
        ]),
        tampering_result=make_tampering(0.0),
        face_result=make_face(FaceVerificationStatus.MATCH)
    )
    resp = client.post("/api/documents/doc1/risk-score", json=req.model_dump())
    assert resp.status_code == 200
    # MRZ checksum FAILED is 15. WARNING should be 7.
    assert resp.json()["risk_score"] == 7

def test_risk_validation_unknown_failed():
    req = RiskScoreRequest(
        validation_result=make_validation(ValidationStatus.FAILED, [
            ValidationCheck(check="something_random", status=ValidationStatus.FAILED, message="Unknown.")
        ]),
        tampering_result=make_tampering(0.0),
        face_result=make_face(FaceVerificationStatus.MATCH)
    )
    resp = client.post("/api/documents/doc1/risk-score", json=req.model_dump())
    assert resp.status_code == 200
    assert resp.json()["risk_score"] == 5  # default is 5

def test_risk_validation_failed_no_checks():
    req = RiskScoreRequest(
        validation_result=make_validation(ValidationStatus.FAILED, []),
        tampering_result=make_tampering(0.0),
        face_result=make_face(FaceVerificationStatus.MATCH)
    )
    resp = client.post("/api/documents/doc1/risk-score", json=req.model_dump())
    assert resp.status_code == 200
    # No checks means full fallback of active max (40 because face is active)
    assert resp.json()["risk_score"] == 40

def test_risk_safe_500_error():
    # Force an error by passing a bad document_id to trigger a different kind of exception?
    # No, mismatched document ID raises 400.
    # We can mock calculate_risk to throw an exception to test the 500 error.
    from unittest import mock
    with mock.patch("app.api.documents.calculate_risk", side_effect=Exception("Secret internal database error 12345")):
        req = RiskScoreRequest(
            validation_result=make_validation(ValidationStatus.PASSED),
            tampering_result=make_tampering(0.0),
            face_result=make_face(FaceVerificationStatus.MATCH)
        )
        resp = client.post("/api/documents/doc1/risk-score", json=req.model_dump())
        assert resp.status_code == 500
        data = resp.json()
        assert "Secret internal database error" not in data["detail"]
        assert data["detail"] == "Risk scoring failed due to an internal server error."

