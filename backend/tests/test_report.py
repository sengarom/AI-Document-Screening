import pytest
from app.schemas.report import ScreeningReportRequest, ScreeningStatus
from app.schemas.ocr import OCRResponse, OCRExtractedFields
from app.schemas.validation import ValidationResponse, ValidationStatus, ValidationCheck
from app.schemas.tampering import TamperingResponse, TamperingStatus, ForensicSignal
from app.schemas.face import FaceVerificationResponse, FaceVerificationStatus
from app.schemas.risk import RiskScoreResponse, RiskLevel, RiskFactor
from app.services.report.report_service import generate_screening_report

def create_base_request(doc_id="doc123"):
    return ScreeningReportRequest(
        ocr_result=OCRResponse(
            success=True,
            document_id=doc_id,
            engine="test",
            device="cpu",
            detections=[],
            extracted_fields=OCRExtractedFields(
                name="JOHN DOE",
                passport_number="A1234567"
            )
        ),
        validation_result=ValidationResponse(
            document_id=doc_id,
            valid=True,
            status=ValidationStatus.PASSED,
            checks=[
                ValidationCheck(check="dummy_check", status=ValidationStatus.PASSED, message="All good")
            ]
        ),
        tampering_result=TamperingResponse(
            document_id=doc_id,
            overall_status=TamperingStatus.PASSED,
            tampering_score=0.0,
            severity="LOW",
            signals={},
            processing_time_ms=10
        ),
        face_result=FaceVerificationResponse(
            document_id=doc_id,
            status=FaceVerificationStatus.MATCH,
            verified=True,
            similarity_score=0.9,
            message="Face matched",
            processing_time_ms=10
        ),
        risk_result=RiskScoreResponse(
            document_id=doc_id,
            risk_score=10,
            risk_level=RiskLevel.LOW,
            factors=[]
        )
    )

def test_report_clean():
    req = create_base_request()
    resp = generate_screening_report("doc1", req)
    
    assert resp.document_id == "doc123"
    assert resp.overall_status == ScreeningStatus.CLEAR
    assert resp.risk_score == 10
    assert resp.risk_level == RiskLevel.LOW
    
    # Document info
    assert resp.document_information.name == "JOHN DOE"
    assert resp.document_information.document_number == "A1234567"
    assert resp.document_information.date_of_birth is None
    
    # Findings
    val_finding = next(f for f in resp.findings if f.category == "Validation")
    assert val_finding.status == "Passed"
    assert "All validation checks passed" in val_finding.summary
    
    face_finding = next(f for f in resp.findings if f.category == "Face Verification")
    assert face_finding.status == "Match"
    assert "Face matched" in face_finding.summary
    
    assert resp.processing_time_ms >= 0
    assert "T" in resp.timestamp # Valid ISO

def test_report_review_medium():
    req = create_base_request()
    req.risk_result.risk_level = RiskLevel.MEDIUM
    req.risk_result.risk_score = 40
    req.validation_result.status = ValidationStatus.WARNING
    req.validation_result.checks = [
        ValidationCheck(check="expiry_date", status=ValidationStatus.WARNING, message="Expires soon")
    ]
    
    resp = generate_screening_report("doc1", req)
    assert resp.overall_status == ScreeningStatus.REVIEW
    
    val_finding = next(f for f in resp.findings if f.category == "Validation")
    assert val_finding.status == "Warning"
    assert "returned warning with 1 issues" in val_finding.summary.lower()
    assert "expiry_date: Expires soon" in val_finding.details

def test_report_review_high():
    req = create_base_request()
    req.risk_result.risk_level = RiskLevel.HIGH
    req.risk_result.risk_score = 60
    resp = generate_screening_report("doc1", req)
    assert resp.overall_status == ScreeningStatus.REVIEW

def test_report_high_risk_critical():
    req = create_base_request()
    req.risk_result.risk_level = RiskLevel.CRITICAL
    req.risk_result.risk_score = 90
    
    req.face_result.status = FaceVerificationStatus.NO_MATCH
    req.face_result.verified = False
    req.face_result.similarity_score = -0.1
    req.face_result.message = "Did not match"
    
    resp = generate_screening_report("doc1", req)
    assert resp.overall_status == ScreeningStatus.HIGH_RISK
    
    face_finding = next(f for f in resp.findings if f.category == "Face Verification")
    assert face_finding.status == "No_match"
    assert "did not match" in face_finding.summary.lower()

def test_report_validation_failure():
    req = create_base_request()
    req.validation_result.status = ValidationStatus.FAILED
    req.validation_result.checks = [
        ValidationCheck(check="mrz_checksum", status=ValidationStatus.FAILED, message="Checksum failed")
    ]
    resp = generate_screening_report("doc1", req)
    val_finding = next(f for f in resp.findings if f.category == "Validation")
    assert val_finding.status == "Failed"
    assert "mrz_checksum: Checksum failed" in val_finding.details

def test_report_elevated_tampering():
    req = create_base_request()
    req.tampering_result.overall_status = TamperingStatus.FAILED
    req.tampering_result.severity = "HIGH"
    req.tampering_result.signals = {
        "ela": ForensicSignal(status=TamperingStatus.FAILED, score=0.9, confidence=0.8, explanation="High ELA variance")
    }
    
    resp = generate_screening_report("doc1", req)
    tamp_finding = next(f for f in resp.findings if f.category == "Tampering")
    assert tamp_finding.status == "Failed"
    assert "(HIGH severity)" in tamp_finding.summary
    assert "ela: High ELA variance" in tamp_finding.details

def test_report_face_unavailable():
    req = create_base_request()
    req.face_result = None
    
    resp = generate_screening_report("doc1", req)
    face_finding = next(f for f in resp.findings if f.category == "Face Verification")
    assert face_finding.status == "Unavailable"
    assert "was unavailable" in face_finding.summary.lower()

def test_report_multiple_findings():
    req = create_base_request()
    req.validation_result.status = ValidationStatus.FAILED
    req.validation_result.checks = [ValidationCheck(check="A", status=ValidationStatus.FAILED, message="B")]
    req.tampering_result.overall_status = TamperingStatus.WARNING
    req.tampering_result.severity = "MODERATE"
    req.face_result.status = FaceVerificationStatus.QUALITY_FAILURE
    req.risk_result.risk_level = RiskLevel.HIGH
    req.risk_result.factors = [
        RiskFactor(category="Tampering", signal="WARNING", contribution=20, message="Suspicious pixels")
    ]
    
    resp = generate_screening_report("doc1", req)
    assert len(resp.findings) == 4
    
    risk_finding = next(f for f in resp.findings if f.category == "Risk")
    assert "Tampering (WARNING): Suspicious pixels" in risk_finding.details

def test_deterministic_generation():
    req = create_base_request()
    resp1 = generate_screening_report("doc1", req)
    resp2 = generate_screening_report("doc1", req)
    
    assert resp1.overall_status == resp2.overall_status
    assert resp1.risk_score == resp2.risk_score
    assert len(resp1.findings) == len(resp2.findings)


def test_report_uses_mrz_fallback():
    # Construct a report request with missing visual fields but valid MRZ data
    from app.schemas.report import ScreeningReportRequest
    from app.schemas.risk import RiskScoreResponse, RiskLevel
    from app.schemas.tampering import TamperingResponse, TamperingStatus
    from app.schemas.validation import MRZParsedData

    from tests.test_validation_service import create_mock_ocr_response, validate_document
    ocr_resp = create_mock_ocr_response({
        "name": None,
        "passport_number": None,
        "nationality": None,
        "date_of_birth": None,
        "gender": None,
        "issue_date": None,
        "expiry_date": None
    })

    val_resp = validate_document("test", ocr_resp)
    # Manually inject MRZ data to simulate a success
    val_resp.mrz_data = MRZParsedData(
        document_type="P",
        issuing_country="UTO",
        passport_number="L898902C3",
        nationality="UTO",
        date_of_birth="12/08/1974",
        sex="F",
        expiry_date="15/04/2012",
        name="ANNA MARIA ERIKSSON"
    )

    tamp_resp = TamperingResponse(
        document_id="test",
        overall_status=TamperingStatus.PASSED,
        tampering_score=0.1,
        severity="Low",
        suspicious_regions=[],
        signals={},
        processing_time_ms=100
    )

    risk_resp = RiskScoreResponse(
        document_id="test",
        risk_score=10,
        risk_level=RiskLevel.LOW,
        factors=[]
    )

    req = ScreeningReportRequest(
        ocr_result=ocr_resp,
        validation_result=val_resp,
        tampering_result=tamp_resp,
        risk_result=risk_resp,
        face_result=None,
        document_type="PASSPORT"
    )

    from app.services.report.report_service import generate_screening_report
    report = generate_screening_report("test", req, "PASSPORT")

    # DocumentInfo should be populated via MRZ fallback
    assert report.document_information.name == "ANNA MARIA ERIKSSON"
    assert report.document_information.document_number == "L898902C3"
    assert report.document_information.nationality == "UTO"
    assert report.document_information.date_of_birth == "12/08/1974"
    assert report.document_information.gender == "F"
    assert report.document_information.expiry_date == "15/04/2012"
