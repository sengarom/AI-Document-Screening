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

def generate_screening_report(request: ScreeningReportRequest) -> ScreeningReportResponse:
    start_time = time.time()
    
    document_id = request.risk_result.document_id
    
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
    t_details = [f"{sig_name}: {sig_data.explanation}" for sig_name, sig_data in request.tampering_result.signals.items() if sig_data.score > 0]
    findings.append(HumanReadableFinding(
        category="Tampering",
        status=t_status,
        summary=f"Forensic analysis returned {t_status.lower()} ({t_sev} severity).",
        details=t_details
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
        f_status = request.face_result.status
        if f_status == FaceVerificationStatus.MATCH:
            f_summary = "Face matched reference successfully."
        elif f_status == FaceVerificationStatus.NO_MATCH:
            f_summary = "Face did not match the reference image."
        else:
            f_summary = f"Face verification returned {f_status.value}."
            
        findings.append(HumanReadableFinding(
            category="Face Verification",
            status=f_status.value.capitalize(),
            summary=f_summary,
            details=[request.face_result.message]
        ))
        
    # 4. Risk Findings
    r_details = [f"{f.category} ({f.signal}): {f.message}" for f in request.risk_result.factors]
    findings.append(HumanReadableFinding(
        category="Risk",
        status=request.risk_result.risk_level.value,
        summary=f"Risk Engine assessed this document at {request.risk_result.risk_level.value} risk.",
        details=r_details
    ))
    
    # Document Info Mapping
    # Need to extract from request.ocr_result.extracted_fields
    # For document_type, let's see if we have it. The plan says populate from OCRResponse if available.
    # OCR extracted fields: name, passport_number, nationality, date_of_birth, gender, issue_date, expiry_date
    ocr_fields = request.ocr_result.extracted_fields
    doc_info = DocumentInfo(
        document_type=None,
        name=ocr_fields.name,
        document_number=ocr_fields.passport_number,
        nationality=ocr_fields.nationality,
        date_of_birth=ocr_fields.date_of_birth,
        gender=ocr_fields.gender,
        issue_date=ocr_fields.issue_date,
        expiry_date=ocr_fields.expiry_date
    )

    processing_time_ms = int((time.time() - start_time) * 1000)
    timestamp_str = datetime.now(timezone.utc).isoformat()
    
    return ScreeningReportResponse(
        document_id=document_id,
        overall_status=overall_status,
        risk_score=request.risk_result.risk_score,
        risk_level=request.risk_result.risk_level,
        document_information=doc_info,
        findings=findings,
        processing_time_ms=processing_time_ms,
        timestamp=timestamp_str
    )
