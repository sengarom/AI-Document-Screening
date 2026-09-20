import pytest
from app.schemas.ocr import OCRResponse, OCRExtractedFields, OCRDetection
from app.schemas.validation import ValidationStatus
from app.services.validation.validation_service import validate_document

def create_mock_ocr_response(
    extracted_fields: dict,
    mrz_lines: list[str] = None
) -> OCRResponse:
    detections = []
    if mrz_lines:
        for idx, line in enumerate(mrz_lines):
            # Give a fake bounding box that ensures correct ordering
            detections.append(OCRDetection(text=line, confidence=0.99, bbox=[0, idx*10, 500, idx*10+10]))
            
    fields = OCRExtractedFields(**extracted_fields)
    return OCRResponse(
        success=True,
        document_id="test_id",
        engine="mock",
        device="cpu",
        detections=detections,
        extracted_fields=fields
    )

def test_valid_document_with_mrz():
    # John Doe, Utopia, valid MRZ
    fields = {
        "name": "JOHN DOE",
        "passport_number": "A12345678",
        "nationality": "UTO",
        "date_of_birth": "15 JAN 1990",
        "gender": "M",
        "issue_date": "10 JAN 2020",
        "expiry_date": "09 JAN 2030"
    }
    # Checksum: A12345678 -> 1+2+3+4+5+6+7+8 = ? wait, A is 10. weights: 7, 3, 1
    # Actually let's use a known valid MRZ for testing.
    # From wiki:
    # P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<
    # L898902C36UTO7408122F1204159ZE184226B<<<<<1
    
    # We'll use the synthetic valid MRZ for JANE SMITH provided by user
    mrz_lines = [
        "P<UTOSMITH<<JANE<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
        "X987654327UTO9005156F3001097<<<<<<<<<<<<<<00"
    ]
    
    fields = {
        "name": "JANE SMITH",
        "passport_number": "X98765432",
        "nationality": "UTO",
        "date_of_birth": "15 MAY 1990",
        "gender": "F",
        "issue_date": "10 JAN 2020",
        "expiry_date": "09 JAN 2030" 
    }
    
    response = validate_document("test", create_mock_ocr_response(fields, mrz_lines))
    
    assert response.valid is True
    # Because expiry is 2030, it's not expired, so we expect PASSED
    assert response.status == ValidationStatus.PASSED
    
    check_dict = {c.check: c.status for c in response.checks}
    assert check_dict["required_field_name"] == ValidationStatus.PASSED
    assert check_dict["mrz_passport_number_checksum"] == ValidationStatus.PASSED
    assert check_dict["mrz_date_of_birth_checksum"] == ValidationStatus.PASSED
    assert check_dict["mrz_expiry_checksum"] == ValidationStatus.PASSED
    assert check_dict["mrz_composite_checksum"] == ValidationStatus.PASSED
    assert check_dict["visual_mrz_passport_number_match"] == ValidationStatus.PASSED
    assert check_dict["visual_mrz_dob_match"] == ValidationStatus.PASSED
    assert check_dict["visual_mrz_gender_match"] == ValidationStatus.PASSED
    assert check_dict["visual_mrz_expiry_match"] == ValidationStatus.PASSED

def test_malformed_incomplete_mrz():
    # Only 38 characters instead of 44, missing checksums
    mrz_lines = [
        "P<UTOSMITH<<JANE<<<<<<<<<<<<<<<<<<<<<<",
        "X987654323UTO9005156F3001090<<<<<<<<<<"
    ]
    fields = {
        "name": "JANE SMITH",
        "passport_number": "X98765432",
        "nationality": "UTO",
        "date_of_birth": "15 MAY 1990",
        "gender": "F",
        "issue_date": "10 JAN 2020",
        "expiry_date": "09 JAN 2030"
    }
    response = validate_document("test", create_mock_ocr_response(fields, mrz_lines))
    # Because there are FAILED checks (checksums), valid is False.
    assert response.valid is False
    assert response.status == ValidationStatus.FAILED
    
    check_dict = {c.check: c.status for c in response.checks}
    # It detected the MRZ, padded it, but checksums failed
    assert check_dict.get("mrz_composite_checksum") == ValidationStatus.FAILED

def test_mrz_reconstruction_with_noise():
    # Simulated fragmented and noisy detections for the 2x44 MRZ
    from app.schemas.ocr import OCRDetection
    
    # We'll pass raw detections directly to simulate spatial layout reconstruction
    # Line 1: 'P<UT0SMITH<<JANE<<<<<<<<<<<<<<<<<<<<<<<<<' (length 41, UT0 instead of UTO)
    # Line 2: 'X987654327UT09005156F3001097<<<<<<<<<<<00' (length 41, UT0 instead of UTO)
    detections = [
        OCRDetection(text='P<UT0SMITH<<', confidence=0.98, bbox=[27, 791, 500, 834]),
        OCRDetection(text='JANE<<<<<<<<<<<<<<<<<<<<<<<<<', confidence=0.98, bbox=[510, 791, 1179, 834]),
        OCRDetection(text='X987654327UT09005156F', confidence=0.99, bbox=[29, 850, 600, 893]),
        OCRDetection(text='3001097<<<<<<<<<<<00', confidence=0.99, bbox=[610, 850, 1178, 893])
    ]
    
    fields = {
        "name": "JANE SMITH",
        "passport_number": "X98765432",
        "nationality": "UTO",
        "date_of_birth": "15 MAY 1990",
        "gender": "F",
        "issue_date": "10 JAN 2020",
        "expiry_date": "09 JAN 2030"
    }
    
    response = create_mock_ocr_response(fields, [])
    response.detections = detections # Override with spatial ones
    
    validation_response = validate_document("test", response)
    
    assert validation_response.valid is True
    assert validation_response.status == ValidationStatus.PASSED
    
    check_dict = {c.check: c.status for c in validation_response.checks}
    # These should pass because the 41-char noisy fragmented detections were merged, padded to 44, and '0' fixed to 'O'
    assert check_dict["mrz_composite_checksum"] == ValidationStatus.PASSED
    assert check_dict["mrz_detected"] == ValidationStatus.PASSED

def test_missing_required_fields():
    fields = {
        "name": None,
        "passport_number": "A12345678",
        "date_of_birth": None,
        "expiry_date": "09 JAN 2030"
    }
    response = validate_document("test", create_mock_ocr_response(fields, []))
    assert response.valid is False
    assert response.status == ValidationStatus.FAILED
    
    check_dict = {c.check: c.status for c in response.checks}
    assert check_dict["required_field_name"] == ValidationStatus.FAILED
    assert check_dict["required_field_date_of_birth"] == ValidationStatus.FAILED

def test_invalid_dates():
    fields = {
        "name": "JOHN DOE",
        "passport_number": "A12345678",
        "date_of_birth": "15 JAN 2050", # future DOB
        "issue_date": "10 JAN 2020",
        "expiry_date": "09 JAN 2019" # before issue
    }
    response = validate_document("test", create_mock_ocr_response(fields, []))
    assert response.valid is False
    
    check_dict = {c.check: c.status for c in response.checks}
    assert check_dict["date_of_birth_logic"] == ValidationStatus.FAILED
    assert check_dict["issue_expiry_logic"] == ValidationStatus.FAILED

def test_future_issue_date():
    fields = {
        "name": "JOHN DOE",
        "passport_number": "A12345678",
        "date_of_birth": "15 JAN 1990",
        "issue_date": "10 JAN 2050", # future issue
        "expiry_date": "09 JAN 2060" 
    }
    response = validate_document("test", create_mock_ocr_response(fields, []))
    assert response.valid is False
    check_dict = {c.check: c.status for c in response.checks}
    assert check_dict["issue_date_logic"] == ValidationStatus.FAILED

def test_malformed_passport_number():
    fields = {
        "name": "JOHN DOE",
        "passport_number": "A!@#", # Invalid characters, too short
        "date_of_birth": "15 JAN 1990",
        "expiry_date": "09 JAN 2030" 
    }
    response = validate_document("test", create_mock_ocr_response(fields, []))
    assert response.valid is False
    check_dict = {c.check: c.status for c in response.checks}
    assert check_dict["passport_number_format"] == ValidationStatus.FAILED

def test_invalid_gender():
    fields = {
        "name": "JOHN DOE",
        "passport_number": "A12345678",
        "date_of_birth": "15 JAN 1990",
        "expiry_date": "09 JAN 2030",
        "gender": "Q"
    }
    response = validate_document("test", create_mock_ocr_response(fields, []))
    assert response.valid is False
    check_dict = {c.check: c.status for c in response.checks}
    assert check_dict["gender_format"] == ValidationStatus.FAILED

def test_visual_mrz_mismatch():
    mrz_lines = [
        "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<",
        "L898902C36UTO7408122F1204159ZE184226B<<<<<10"
    ]
    # Visual extraction says John Doe, but MRZ says ANNA MARIA.
    # Passport visually extracted as X99999, MRZ is L898902C3
    fields = {
        "name": "JOHN DOE",
        "passport_number": "X9999999",
        "nationality": "UTO",
        "date_of_birth": "12 AUG 1974",
        "gender": "M", # Visual says M, MRZ says F
        "issue_date": "01 JAN 2002",
        "expiry_date": "15 APR 2012"
    }
    response = validate_document("test", create_mock_ocr_response(fields, mrz_lines))
    assert response.valid is False
    
    check_dict = {c.check: c.status for c in response.checks}
    assert check_dict["visual_mrz_passport_number_match"] == ValidationStatus.FAILED
    assert check_dict["visual_mrz_gender_match"] == ValidationStatus.FAILED
def test_required_fields_visual_missing_mrz_valid():
    # Visual fields missing, but MRZ present and valid
    fields = {
        "name": None,
        "passport_number": None,
        "date_of_birth": None,
        "expiry_date": None
    }
    mrz_lines = [
        "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<",
        "L898902C36UTO7408122F1204159ZE184226B<<<<<10"
    ]
    resp = create_mock_ocr_response(fields, mrz_lines)
    val = validate_document("test", resp)
    
    # Validation should pass because MRZ supplies the required fields
    assert val.valid is True
    assert val.status == ValidationStatus.PASSED
    
    # Check that required fields are PASSED
    req_checks = [c for c in val.checks if c.check.startswith("required_field_")]
    assert len(req_checks) == 4
    for rc in req_checks:
        assert rc.status == ValidationStatus.PASSED
        assert "satisfied via MRZ" in rc.message

def test_required_fields_both_missing():
    # Both visual and MRZ missing
    fields = {
        "name": None,
        "passport_number": None,
        "date_of_birth": None,
        "expiry_date": None
    }
    resp = create_mock_ocr_response(fields, [])
    val = validate_document("test", resp)
    
    # Should fail
    assert val.valid is False
    req_checks = [c for c in val.checks if c.check.startswith("required_field_")]
    assert len(req_checks) == 4
    for rc in req_checks:
        assert rc.status == ValidationStatus.FAILED
        assert "is missing" in rc.message

def test_visual_mrz_contradiction():
    # Visual present but contradicts MRZ
    fields = {
        "name": "ANNA MARIA",
        "passport_number": "DIFFERENT", # Contradicts L898902C3
        "date_of_birth": "12/08/1974", # Matches MRZ
        "expiry_date": "15/04/2012", # Matches MRZ
        "gender": "F"
    }
    mrz_lines = [
        "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<",
        "L898902C36UTO7408122F1204159ZE184226B<<<<<10"
    ]
    resp = create_mock_ocr_response(fields, mrz_lines)
    val = validate_document("test", resp)
    
    assert val.valid is False
    ppt_match = next((c for c in val.checks if c.check == "visual_mrz_passport_number_match"), None)
    assert ppt_match is not None
    assert ppt_match.status == ValidationStatus.FAILED

def test_visual_mrz_matching():
    # Visual present and matches MRZ
    fields = {
        "name": "ANNA MARIA",
        "passport_number": "L898902C3", 
        "date_of_birth": "12/08/1974", 
        "expiry_date": "15/04/2012", 
        "gender": "F"
    }
    mrz_lines = [
        "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<",
        "L898902C36UTO7408122F1204159ZE184226B<<<<<10"
    ]
    resp = create_mock_ocr_response(fields, mrz_lines)
    val = validate_document("test", resp)
    
    assert val.valid is True
    ppt_match = next((c for c in val.checks if c.check == "visual_mrz_passport_number_match"), None)
    assert ppt_match is not None
    assert ppt_match.status == ValidationStatus.PASSED

def test_mrz_data_survives_validation_response():
    fields = {
        "name": None,
        "passport_number": None,
        "date_of_birth": None,
        "expiry_date": None
    }
    mrz_lines = [
        "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<",
        "L898902C36UTO7408122F1204159ZE184226B<<<<<10"
    ]
    resp = create_mock_ocr_response(fields, mrz_lines)
    val = validate_document("test", resp)
    
    assert val.mrz_data is not None
    assert val.mrz_data.passport_number == "L898902C3"
    assert val.mrz_data.name == "ANNA MARIA ERIKSSON"
