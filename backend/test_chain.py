from app.services.risk.risk_service import calculate_risk
from app.services.report.report_service import generate_screening_report
from app.schemas.risk import RiskScoreRequest
from app.schemas.report import ScreeningReportRequest
from app.schemas.validation import ValidationResponse, ValidationStatus
from app.schemas.tampering import TamperingResponse, TamperingStatus
from app.schemas.face import FaceVerificationResponse, FaceVerificationStatus
from app.schemas.ocr import OCRResponse, DocumentFields

val = ValidationResponse(document_id="1", status=ValidationStatus.PASSED, checks=[])
tamp = TamperingResponse(document_id="1", tampering_score=0.0, severity="LOW", overall_status=TamperingStatus.PASSED, signals={})
face = FaceVerificationResponse(document_id="1", status=FaceVerificationStatus.NO_MATCH, verified=False, similarity_score=0.1, message="NO")
ocr = OCRResponse(document_id="1", raw_text="", extracted_fields=DocumentFields())

risk_req = RiskScoreRequest(
    validation_result=val,
    tampering_result=tamp,
    face_result=face
)

risk_res = calculate_risk(risk_req)
print("RISK RESULT:")
print(risk_res.model_dump())

report_req = ScreeningReportRequest(
    ocr_result=ocr,
    validation_result=val,
    tampering_result=tamp,
    face_result=face,
    risk_result=risk_res
)

report_res = generate_screening_report("1", report_req)
print("REPORT RESULT:")
print(report_res.model_dump())
