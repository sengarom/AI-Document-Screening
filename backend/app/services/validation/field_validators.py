import re
from datetime import datetime, date
from typing import List, Optional, Tuple
from app.schemas.validation import ValidationCheck, ValidationStatus, MRZParsedData
from app.schemas.ocr import OCRExtractedFields

def parse_date(date_str: str) -> Optional[date]:
    if not date_str:
        return None
    
    # Normalize OCR mistakes in dates: I -> 1, O -> 0, etc.
    # We will just rely on datetime parsing for now, stripping weird characters
    clean_str = re.sub(r'[^a-zA-Z0-9]', ' ', date_str.upper())
    parts = clean_str.split()
    
    # Handle "10 JAN JAN 2020" or "10 JAN 2020"
    if len(parts) >= 3:
        day = parts[0]
        year = parts[-1]
        # Find the month
        months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        month_idx = -1
        for p in parts[1:-1]:
            try:
                month_idx = months.index(p) + 1
                break
            except ValueError:
                continue
        
        # If we couldn't find a text month, maybe it's DD MM YYYY
        if month_idx == -1 and len(parts) == 3:
            try:
                month_idx = int(parts[1])
            except ValueError:
                pass
                
        if month_idx != -1:
            try:
                return date(int(year), month_idx, int(day))
            except ValueError:
                return None
                
    # Try basic DD/MM/YYYY or similar if it wasn't split by spaces
    clean_slash = re.sub(r'[^0-9]', '/', date_str)
    parts = [p for p in clean_slash.split('/') if p]
    if len(parts) == 3:
        try:
            return date(int(parts[2]), int(parts[1]), int(parts[0]))
        except ValueError:
            return None
            
    return None

def validate_required_fields(fields: OCRExtractedFields, mrz: Optional[MRZParsedData] = None) -> List[ValidationCheck]:
    checks = []
    required = ["name", "passport_number", "date_of_birth", "expiry_date"]
    for req in required:
        val = getattr(fields, req, None)
        mrz_val = getattr(mrz, req, None) if mrz else None
        
        if val:
            checks.append(ValidationCheck(
                check=f"required_field_{req}",
                status=ValidationStatus.PASSED,
                message=f"Mandatory field '{req}' is present."
            ))
        elif mrz_val:
            checks.append(ValidationCheck(
                check=f"required_field_{req}",
                status=ValidationStatus.PASSED,
                message=f"Mandatory field '{req}' satisfied via MRZ."
            ))
        else:
            checks.append(ValidationCheck(
                check=f"required_field_{req}",
                status=ValidationStatus.FAILED,
                message=f"Mandatory field '{req}' is missing."
            ))
    return checks

def validate_dates(fields: OCRExtractedFields) -> List[ValidationCheck]:
    checks = []
    today = date.today()
    
    dob = parse_date(fields.date_of_birth) if fields.date_of_birth else None
    issue = parse_date(fields.issue_date) if fields.issue_date else None
    expiry = parse_date(fields.expiry_date) if fields.expiry_date else None
    
    if fields.date_of_birth and not dob:
        checks.append(ValidationCheck(check="date_of_birth_format", status=ValidationStatus.FAILED, message="Date of Birth is malformed."))
    
    if dob:
        if dob > today:
            checks.append(ValidationCheck(check="date_of_birth_logic", status=ValidationStatus.FAILED, message="Date of Birth is in the future."))
        else:
            checks.append(ValidationCheck(check="date_of_birth_logic", status=ValidationStatus.PASSED, message="Date of Birth logic is valid."))
            
    if fields.issue_date and not issue:
        checks.append(ValidationCheck(check="issue_date_format", status=ValidationStatus.FAILED, message="Issue Date is malformed."))
        
    if issue:
        if issue > today:
            checks.append(ValidationCheck(check="issue_date_logic", status=ValidationStatus.FAILED, message="Issue Date is in the future."))
        else:
            checks.append(ValidationCheck(check="issue_date_logic", status=ValidationStatus.PASSED, message="Issue Date logic is valid."))
            
    if fields.expiry_date and not expiry:
        checks.append(ValidationCheck(check="expiry_date_format", status=ValidationStatus.FAILED, message="Expiry Date is malformed."))
        
    if expiry:
        if expiry < today:
            checks.append(ValidationCheck(check="expiry_date_logic", status=ValidationStatus.WARNING, message="Document has expired."))
        else:
            checks.append(ValidationCheck(check="expiry_date_logic", status=ValidationStatus.PASSED, message="Document is not expired."))
            
    if issue and expiry:
        if expiry <= issue:
            checks.append(ValidationCheck(check="issue_expiry_logic", status=ValidationStatus.FAILED, message="Expiry date is before or equal to issue date."))
        else:
            checks.append(ValidationCheck(check="issue_expiry_logic", status=ValidationStatus.PASSED, message="Expiry is after issue date."))
            
    if dob and issue:
        if issue <= dob:
            checks.append(ValidationCheck(check="dob_issue_logic", status=ValidationStatus.FAILED, message="Issue date is before or equal to Date of Birth."))
            
    return checks

def validate_passport_number(passport_num: Optional[str]) -> List[ValidationCheck]:
    if not passport_num:
        return []
    
    clean = passport_num.replace(" ", "").upper()
    if not re.match(r'^[A-Z0-9]{6,12}$', clean):
        return [ValidationCheck(check="passport_number_format", status=ValidationStatus.FAILED, message="Passport number format is malformed.")]
    return [ValidationCheck(check="passport_number_format", status=ValidationStatus.PASSED, message="Passport number format is plausible.")]

def validate_gender(gender: Optional[str]) -> List[ValidationCheck]:
    if not gender:
        return []
    if gender.upper() not in ["M", "F", "X", "MALE", "FEMALE"]:
        return [ValidationCheck(check="gender_format", status=ValidationStatus.FAILED, message="Gender format is invalid.")]
    return [ValidationCheck(check="gender_format", status=ValidationStatus.PASSED, message="Gender format is valid.")]
