from typing import List, Tuple, Optional
import re
from datetime import datetime
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

def validate_document(document_id: str, ocr_data: OCRResponse, document_type: str = "PASSPORT") -> ValidationResponse:
    mrz_data = None
    if document_type == "PAN":
        checks = _validate_pan(ocr_data.extracted_fields, ocr_data.detections)
    elif document_type == "AADHAAR":
        checks = _validate_aadhaar(ocr_data.extracted_fields, ocr_data.detections)
    else:
        checks, mrz_data = _validate_passport(ocr_data)
        
    is_valid = True
    overall_status = ValidationStatus.PASSED
    
    for c in checks:
        if c.status == ValidationStatus.FAILED:
            is_valid = False
            overall_status = ValidationStatus.FAILED
            break
            
    if is_valid:
        for c in checks:
            if c.status == ValidationStatus.WARNING:
                overall_status = ValidationStatus.WARNING
                break
                
    return ValidationResponse(
        document_id=document_id,
        valid=is_valid,
        status=overall_status,
        checks=checks,
        mrz_data=mrz_data
    )

def _validate_passport(ocr_data: OCRResponse) -> Tuple[List[ValidationCheck], Optional[MRZParsedData]]:
    checks: List[ValidationCheck] = []
    
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
        
    # 1. Field Validations
    checks.extend(validate_required_fields(ocr_data.extracted_fields, mrz_parsed))
    checks.extend(validate_dates(ocr_data.extracted_fields))
    checks.extend(validate_passport_number(ocr_data.extracted_fields.passport_number))
    checks.extend(validate_gender(ocr_data.extracted_fields.gender))
    
    # 3. Consistency checks
    checks.extend(validate_consistency(ocr_data.extracted_fields, mrz_parsed))
    return checks, mrz_parsed

def _validate_pan(fields: OCRExtractedFields, detections: List[OCRDetection]) -> List[ValidationCheck]:
    checks: List[ValidationCheck] = []
    
    # PAN number presence and format
    if not fields.pan_number:
        checks.append(ValidationCheck(check="pan_number", status=ValidationStatus.FAILED, message="PAN number could not be extracted."))
    elif not re.fullmatch(r'[A-Z]{5}[0-9]{4}[A-Z]', fields.pan_number):
        checks.append(ValidationCheck(check="pan_number_format", status=ValidationStatus.FAILED, message="PAN number does not match expected format (e.g. ABCDE1234F)."))
    else:
        checks.append(ValidationCheck(check="pan_number_format", status=ValidationStatus.PASSED, message="PAN format is valid."))

    # Name presence
    if not fields.name:
        checks.append(ValidationCheck(check="name", status=ValidationStatus.WARNING, message="Name could not be confidently extracted."))
    else:
        checks.append(ValidationCheck(check="name", status=ValidationStatus.PASSED, message="Name is present."))

    # DOB validation
    if not fields.date_of_birth:
        checks.append(ValidationCheck(check="date_of_birth", status=ValidationStatus.WARNING, message="Date of birth could not be extracted."))
    else:
        try:
            # typical format DD/MM/YYYY or DD-MM-YYYY
            clean_dob = re.sub(r'[/.\-]', '-', fields.date_of_birth)
            dob_obj = datetime.strptime(clean_dob, "%d-%m-%Y")
            if dob_obj > datetime.now():
                checks.append(ValidationCheck(check="date_of_birth", status=ValidationStatus.FAILED, message="Date of birth cannot be in the future."))
            else:
                checks.append(ValidationCheck(check="date_of_birth", status=ValidationStatus.PASSED, message="Date of birth is valid."))
        except ValueError:
            checks.append(ValidationCheck(check="date_of_birth", status=ValidationStatus.FAILED, message="Date of birth format is invalid."))

    # Check for overall low confidence
    avg_conf = sum(d.confidence for d in detections) / max(len(detections), 1)
    if avg_conf < 0.6:
        checks.append(ValidationCheck(check="ocr_confidence", status=ValidationStatus.WARNING, message="Low overall text extraction confidence."))
        
    return checks

def _validate_aadhaar(fields: OCRExtractedFields, detections: List[OCRDetection]) -> List[ValidationCheck]:
    checks: List[ValidationCheck] = []
    
    if not fields.aadhaar_number:
        checks.append(ValidationCheck(check="aadhaar_number", status=ValidationStatus.FAILED, message="Aadhaar number could not be extracted."))
    elif not re.fullmatch(r'\d{12}', fields.aadhaar_number):
        checks.append(ValidationCheck(check="aadhaar_number_format", status=ValidationStatus.FAILED, message="Aadhaar number must be exactly 12 digits."))
    else:
        checks.append(ValidationCheck(check="aadhaar_number_format", status=ValidationStatus.PASSED, message="Aadhaar format is valid."))

    if not fields.name:
        checks.append(ValidationCheck(check="name", status=ValidationStatus.WARNING, message="Name could not be confidently extracted."))
    else:
        checks.append(ValidationCheck(check="name", status=ValidationStatus.PASSED, message="Name is present."))

    if fields.date_of_birth:
        try:
            clean_dob = re.sub(r'[/.\-]', '-', fields.date_of_birth)
            dob_obj = datetime.strptime(clean_dob, "%d-%m-%Y")
            if dob_obj > datetime.now():
                checks.append(ValidationCheck(check="date_of_birth", status=ValidationStatus.FAILED, message="Date of birth cannot be in the future."))
            else:
                checks.append(ValidationCheck(check="date_of_birth", status=ValidationStatus.PASSED, message="Date of birth is valid."))
        except ValueError:
            checks.append(ValidationCheck(check="date_of_birth", status=ValidationStatus.FAILED, message="Date of birth format is invalid."))
    elif fields.year_of_birth:
        try:
            if int(fields.year_of_birth) > datetime.now().year:
                checks.append(ValidationCheck(check="year_of_birth", status=ValidationStatus.FAILED, message="Year of birth cannot be in the future."))
            else:
                checks.append(ValidationCheck(check="year_of_birth", status=ValidationStatus.PASSED, message="Year of birth is valid."))
        except ValueError:
            checks.append(ValidationCheck(check="year_of_birth", status=ValidationStatus.FAILED, message="Year of birth format is invalid."))
    else:
        checks.append(ValidationCheck(check="dob_or_yob", status=ValidationStatus.WARNING, message="Neither Date of Birth nor Year of Birth could be extracted."))

    if fields.gender:
        if fields.gender not in ["M", "F", "O"]:
            checks.append(ValidationCheck(check="gender", status=ValidationStatus.FAILED, message="Extracted gender is invalid."))
        else:
            checks.append(ValidationCheck(check="gender", status=ValidationStatus.PASSED, message="Gender is valid."))

    avg_conf = sum(d.confidence for d in detections) / max(len(detections), 1)
    if avg_conf < 0.6:
        checks.append(ValidationCheck(check="ocr_confidence", status=ValidationStatus.WARNING, message="Low overall text extraction confidence."))
        
    return checks
