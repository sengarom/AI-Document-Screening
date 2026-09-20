from app.services.validation.mrz.mrz_parser import extract_mrz_lines
from app.schemas.ocr import OCRDetection
import pytest

def test_extract_mrz_lines_positive():
    detections = [
        OCRDetection(text="P<INDTHAPLIYAL<<GARIMA<<<<<<<<<<<<<<<<<<<<<<", confidence=0.9, bbox=[1, 100, 315, 110]),
        OCRDetection(text="SP003369<21ND9407015F34090281065269546124<78", confidence=0.9, bbox=[1, 120, 315, 130])
    ]
    lines = extract_mrz_lines(detections)
    assert len(lines) == 2
    assert lines[0].startswith("P<IND")

def test_extract_mrz_lines_negative_ordinary_text():
    # Long text with one <
    detections = [
        OCRDetection(text="THISISVERYLONGTEXTTHATISNOTANMRZBUTHAON<ECHAR", confidence=0.9, bbox=[1, 100, 315, 110])
    ]
    lines = extract_mrz_lines(detections)
    # Depending on logic, it might currently be accepted.
    assert len(lines) == 0

def test_extract_mrz_lines_negative_malformed():
    # Text with lots of spaces, special chars, and a <
    detections = [
        OCRDetection(text="ADDRESS: 123 STREET, APARTMENT < 45, CITY, STATE 123456", confidence=0.9, bbox=[1, 100, 315, 110])
    ]
    lines = extract_mrz_lines(detections)
    assert len(lines) == 0

if __name__ == "__main__":
    pytest.main(["-v", "test_mrz_parser.py"])


from app.services.validation.mrz.mrz_parser import parse_mrz

def test_parse_mrz_dates():
    lines = [
        "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<",
        "L898902C36UTO7408122F1204159ZE184226B<<<<<10"
    ]
    parsed = parse_mrz(lines)
    assert parsed.date_of_birth == "12/08/1974"  # DOB: century 1900 because 74 > current_yy
    assert parsed.expiry_date == "15/04/2012"  # Expiry: century 2000

def test_parse_mrz_century_boundary():
    # If yy is like 20, DOB is 2020. Expiry is 2020.
    lines = [
        "P<UTOSMITH<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
        "L898902C36UTO2001012M2001019ZE184226B<<<<<10"
    ]
    parsed = parse_mrz(lines)
    assert parsed.date_of_birth == "01/01/2020"
    assert parsed.expiry_date == "01/01/2020"
