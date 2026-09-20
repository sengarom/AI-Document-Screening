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
