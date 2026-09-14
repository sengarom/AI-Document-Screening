from typing import List
from app.schemas.ocr import OCRResponse, OCRExtractedFields, OCRDetection
from app.schemas.validation import ValidationResponse, ValidationCheck, ValidationStatus, MRZParsedData

from app.services.validation.field_validators import (
    validate_required_fields,
    validate_dates,
    validate_passport_number,
    validate_gender
)
from app.services.validation.mrz.mrz_parser import extract_mrz_lines, parse_mrz
from app.services.validation.mrz.mrz_validator import validate_mrz_checksums
from app.services.validation.consistency_validator import validate_consistency

def validate_document(document_id: str, ocr_data: OCRResponse) -> ValidationResponse:
    checks: List[ValidationCheck] = []
    
    # 1. Field Validations
    checks.extend(validate_required_fields(ocr_data.extracted_fields))
    checks.extend(validate_dates(ocr_data.extracted_fields))
    checks.extend(validate_passport_number(ocr_data.extracted_fields.passport_number))
    checks.extend(validate_gender(ocr_data.extracted_fields.gender))
    
    # 2. MRZ parsing and validation
    mrz_lines = extract_mrz_lines(ocr_data.detections)
    mrz_parsed = None
    if mrz_lines and len(mrz_lines) == 2:
        mrz_parsed = parse_mrz(mrz_lines)
        checks.extend(validate_mrz_checksums(mrz_lines))
    else:
        checks.append(ValidationCheck(
            check="mrz_detected", 
            status=ValidationStatus.WARNING, 
            message="No MRZ detected or incomplete MRZ."
        ))
        
    # 3. Consistency checks
    checks.extend(validate_consistency(ocr_data.extracted_fields, mrz_parsed))
    
    # Calculate overall status
    is_valid = True
    overall_status = ValidationStatus.PASSED
    
    for c in checks:
        if c.status == ValidationStatus.FAILED:
            is_valid = False
            overall_status = ValidationStatus.FAILED
            break
            
    if is_valid:
        # Check for warnings
        for c in checks:
            if c.status == ValidationStatus.WARNING:
                overall_status = ValidationStatus.WARNING
                break
                
    return ValidationResponse(
        document_id=document_id,
        valid=is_valid,
        status=overall_status,
        checks=checks
    )
