import time
from datetime import datetime, timezone
from app.schemas.report import (
    ScreeningReportRequest,
    ScreeningReportResponse,
    ScreeningStatus,
    HumanReadableFinding,
    DocumentInfo
)
from app.schemas.risk import RiskLevel
from app.schemas.validation import ValidationStatus
from app.schemas.tampering import TamperingStatus
from app.schemas.face import FaceVerificationStatus

def generate_screening_report(document_id: str, request: ScreeningReportRequest, document_type: str = "PASSPORT") -> ScreeningReportResponse:
    start_time = time.time()
    
    # Map Risk Level to Screening Status
    if request.risk_result.risk_level == RiskLevel.LOW:
        overall_status = ScreeningStatus.CLEAR
    elif request.risk_result.risk_level in (RiskLevel.MEDIUM, RiskLevel.HIGH):
        overall_status = ScreeningStatus.REVIEW
    else:  # CRITICAL
        overall_status = ScreeningStatus.HIGH_RISK

    findings = []
    
    # 1. Validation Findings
    if request.validation_result.status == ValidationStatus.PASSED:
        findings.append(HumanReadableFinding(
            category="Validation",
            status="Passed",
            summary="All validation checks passed.",
            details=[]
        ))
    else:
        status_str = "Warning" if request.validation_result.status == ValidationStatus.WARNING else "Failed"
        details = [f"{c.check}: {c.message}" for c in request.validation_result.checks if c.status != ValidationStatus.PASSED]
        findings.append(HumanReadableFinding(
            category="Validation",
            status=status_str,
            summary=f"Document validation returned {status_str.lower()} with {len(details)} issues.",
            details=details
        ))

    # 2. Tampering Findings
    t_status = request.tampering_result.overall_status.value.capitalize()
    t_sev = request.tampering_result.severity
    findings.append(HumanReadableFinding(
        category="Tampering",
        status=t_status,
        summary=f"Tampering detection is {t_status.lower()} ({t_sev} severity).",
        details=[f"{k}: {v.explanation}" for k, v in request.tampering_result.signals.items()]
    ))

    # 3. Face Verification Findings
    if request.face_result is None:
        findings.append(HumanReadableFinding(
            category="Face Verification",
            status="Unavailable",
            summary="Face verification was unavailable or not included in the provided results.",
            details=[]
        ))
    else:
        f_status = request.face_result.status.value.capitalize()
        f_summary = request.face_result.message
        findings.append(HumanReadableFinding(
            category="Face Verification",
            status=f_status,
            summary=f_summary,
            details=[]
        ))

    # 4. Risk Findings
    r_details = [f"{f.category} ({f.signal}): {f.message}" for f in request.risk_result.factors]
    findings.append(HumanReadableFinding(
        category="Risk",
        status=request.risk_result.risk_level.value,
        summary=f"Risk Engine assessed this document at {request.risk_result.risk_level.value} risk.",
        details=r_details
    ))

    # Document Information Selection
    fields = request.ocr_result.extracted_fields
    mrz = request.validation_result.mrz_data
    
    doc_info = DocumentInfo(
        document_type=document_type,
        name=fields.name
    )
    
    if document_type == "PAN":
        doc_info.document_number = fields.pan_number
        doc_info.date_of_birth = fields.date_of_birth
        doc_info.fathers_name = fields.fathers_name
    elif document_type == "AADHAAR":
        # Mask the first 8 digits in the report
        if fields.aadhaar_number and len(fields.aadhaar_number) == 12:
            doc_info.document_number = f"XXXX XXXX {fields.aadhaar_number[8:]}"
        else:
            doc_info.document_number = fields.aadhaar_number
        doc_info.date_of_birth = fields.date_of_birth or fields.year_of_birth
        doc_info.gender = fields.gender
    else:
        # Default PASSPORT/VISA
        doc_info.name = fields.name or (mrz.name if mrz else None)
        doc_info.document_number = fields.passport_number or (mrz.passport_number if mrz else None)
        doc_info.nationality = fields.nationality or (mrz.nationality if mrz else None)
        doc_info.date_of_birth = fields.date_of_birth or (mrz.date_of_birth if mrz else None)
        doc_info.gender = fields.gender or (mrz.sex if mrz else None)
        doc_info.issue_date = fields.issue_date
        doc_info.expiry_date = fields.expiry_date or (mrz.expiry_date if mrz else None)

    process_time_ms = int((time.time() - start_time) * 1000)
    ts = datetime.now(timezone.utc).isoformat()
    
    return ScreeningReportResponse(
        document_id=request.ocr_result.document_id,
        overall_status=overall_status,
        risk_score=request.risk_result.risk_score,
        risk_level=request.risk_result.risk_level,
        document_information=doc_info,
        findings=findings,
        processing_time_ms=process_time_ms,
        timestamp=ts
    )
