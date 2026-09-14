from typing import List
from app.schemas.validation import ValidationCheck, ValidationStatus

def _mrz_char_value(c: str) -> int:
    if c == '<': return 0
    if '0' <= c <= '9': return int(c)
    if 'A' <= c <= 'Z': return ord(c) - 55
    return 0 # Fallback for OCR garbage

def _calculate_checksum(data: str) -> str:
    weights = [7, 3, 1]
    total = sum(_mrz_char_value(c) * weights[i % 3] for i, c in enumerate(data))
    return str(total % 10)

def validate_mrz_checksums(lines: List[str]) -> List[ValidationCheck]:
    """Validates ICAO checksums for TD3 MRZ."""
    checks = []
    
    if len(lines) != 2:
        return [ValidationCheck(check="mrz_detected", status=ValidationStatus.FAILED, message="MRZ could not be fully detected or is not 2 lines.")]
        
    checks.append(ValidationCheck(check="mrz_detected", status=ValidationStatus.PASSED, message="2-line MRZ detected."))
    
    line2 = lines[1].ljust(44, '<')[:44]
    
    # Checksum 1: Passport Number
    passport_num = line2[0:9]
    passport_check = line2[9]
    if _calculate_checksum(passport_num) == passport_check:
        checks.append(ValidationCheck(check="mrz_passport_number_checksum", status=ValidationStatus.PASSED, message="MRZ passport number checksum is valid."))
    else:
        checks.append(ValidationCheck(check="mrz_passport_number_checksum", status=ValidationStatus.FAILED, message=f"MRZ passport number checksum failed (expected {_calculate_checksum(passport_num)}, got {passport_check})."))

    # Checksum 2: Date of Birth
    dob = line2[13:19]
    dob_check = line2[19]
    if _calculate_checksum(dob) == dob_check:
        checks.append(ValidationCheck(check="mrz_date_of_birth_checksum", status=ValidationStatus.PASSED, message="MRZ DOB checksum is valid."))
    else:
        checks.append(ValidationCheck(check="mrz_date_of_birth_checksum", status=ValidationStatus.FAILED, message=f"MRZ DOB checksum failed."))
        
    # Checksum 3: Expiry
    exp = line2[21:27]
    exp_check = line2[27]
    if _calculate_checksum(exp) == exp_check:
        checks.append(ValidationCheck(check="mrz_expiry_checksum", status=ValidationStatus.PASSED, message="MRZ expiry checksum is valid."))
    else:
        checks.append(ValidationCheck(check="mrz_expiry_checksum", status=ValidationStatus.FAILED, message=f"MRZ expiry checksum failed."))
        
    # Checksum 4: Composite
    composite_data = line2[0:10] + line2[13:20] + line2[21:43]
    composite_check = line2[43]
    if _calculate_checksum(composite_data) == composite_check:
        checks.append(ValidationCheck(check="mrz_composite_checksum", status=ValidationStatus.PASSED, message="MRZ composite checksum is valid."))
    else:
        checks.append(ValidationCheck(check="mrz_composite_checksum", status=ValidationStatus.FAILED, message=f"MRZ composite checksum failed."))
        
    return checks
