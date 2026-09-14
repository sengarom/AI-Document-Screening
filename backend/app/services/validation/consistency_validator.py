import re
from typing import List, Optional
from datetime import date
from app.schemas.validation import ValidationCheck, ValidationStatus, MRZParsedData
from app.schemas.ocr import OCRExtractedFields
from app.services.validation.field_validators import parse_date

def _clean_str(s: Optional[str]) -> str:
    if not s:
        return ""
    return re.sub(r'[^A-Z0-9]', '', s.upper())

def validate_consistency(visual: OCRExtractedFields, mrz: Optional[MRZParsedData]) -> List[ValidationCheck]:
    checks = []
    if not mrz:
        checks.append(ValidationCheck(
            check="visual_mrz_consistency",
            status=ValidationStatus.WARNING,
            message="MRZ data unavailable. Skipping consistency checks."
        ))
        return checks

    # Passport Number
    vis_ppt = _clean_str(visual.passport_number)
    mrz_ppt = _clean_str(mrz.passport_number)
    if vis_ppt and mrz_ppt:
        # Sometimes visual passport has extra characters, but they should contain each other
        if vis_ppt == mrz_ppt or mrz_ppt in vis_ppt or vis_ppt in mrz_ppt:
            checks.append(ValidationCheck(check="visual_mrz_passport_number_match", status=ValidationStatus.PASSED, message="Passport number matches MRZ."))
        else:
            checks.append(ValidationCheck(check="visual_mrz_passport_number_match", status=ValidationStatus.FAILED, message=f"Passport number mismatch (Visual: {visual.passport_number}, MRZ: {mrz.passport_number})."))
            
    # Gender
    if visual.gender and mrz.sex:
        v_gender = visual.gender.upper().strip()
        m_gender = mrz.sex.upper().strip()
        v_canonical = "M" if v_gender in ["M", "MALE"] else ("F" if v_gender in ["F", "FEMALE"] else v_gender)
        m_canonical = "M" if m_gender in ["M", "MALE"] else ("F" if m_gender in ["F", "FEMALE"] else m_gender)
        if v_canonical == m_canonical:
            checks.append(ValidationCheck(check="visual_mrz_gender_match", status=ValidationStatus.PASSED, message="Gender matches MRZ."))
        else:
            checks.append(ValidationCheck(check="visual_mrz_gender_match", status=ValidationStatus.FAILED, message="Gender does not match MRZ."))

    # DOB
    v_dob_obj = parse_date(visual.date_of_birth)
    if v_dob_obj and mrz.date_of_birth and len(mrz.date_of_birth) == 6:
        try:
            m_year = int(mrz.date_of_birth[0:2])
            m_month = int(mrz.date_of_birth[2:4])
            m_day = int(mrz.date_of_birth[4:6])
            
            # YY to YYYY conversion standard (heuristic: < 50 is 2000s, >= 50 is 1900s)
            full_year = 2000 + m_year if m_year < 50 else 1900 + m_year
            
            if v_dob_obj.year == full_year and v_dob_obj.month == m_month and v_dob_obj.day == m_day:
                checks.append(ValidationCheck(check="visual_mrz_dob_match", status=ValidationStatus.PASSED, message="Date of Birth matches MRZ."))
            else:
                checks.append(ValidationCheck(check="visual_mrz_dob_match", status=ValidationStatus.FAILED, message="Date of Birth does not match MRZ."))
        except ValueError:
            pass

    # Expiry
    v_exp_obj = parse_date(visual.expiry_date)
    if v_exp_obj and mrz.expiry_date and len(mrz.expiry_date) == 6:
        try:
            m_year = int(mrz.expiry_date[0:2])
            m_month = int(mrz.expiry_date[2:4])
            m_day = int(mrz.expiry_date[4:6])
            
            full_year = 2000 + m_year if m_year < 80 else 1900 + m_year # expiry usually in 2000s
            
            if v_exp_obj.year == full_year and v_exp_obj.month == m_month and v_exp_obj.day == m_day:
                checks.append(ValidationCheck(check="visual_mrz_expiry_match", status=ValidationStatus.PASSED, message="Expiry Date matches MRZ."))
            else:
                checks.append(ValidationCheck(check="visual_mrz_expiry_match", status=ValidationStatus.FAILED, message="Expiry Date does not match MRZ."))
        except ValueError:
            pass

    return checks
