import pytest
from app.schemas.ocr import OCRDetection
from app.services.ocr.ocr_service import _extract_aadhaar_fields

def test_extract_aadhaar_fields_spatial():
    # Synthetic Aadhaar Layout
    # GOVERNMENT OF INDIA (y=10)
    # 
    # MOCK NAME (y=60)
    # DOB: 15/08/1992 (y=90)
    # MALE (y=120)
    # 
    # 1111 2222 3333 (y=180)
    
    detections = [
        OCRDetection(text="GOVERNMENT OF INDIA", confidence=0.95, bbox=[50, 10, 250, 30]),
        OCRDetection(text="MOCK NAME", confidence=0.98, bbox=[20, 60, 150, 80]),
        OCRDetection(text="DOB: 15/08/1992", confidence=0.96, bbox=[20, 90, 150, 110]),
        OCRDetection(text="MALE", confidence=0.99, bbox=[20, 120, 100, 140]),
        OCRDetection(text="1111 2222 3333", confidence=0.99, bbox=[50, 180, 250, 200])
    ]
    
    fields = _extract_aadhaar_fields(detections)
    
    assert fields.name == "MOCK NAME"
    assert fields.date_of_birth == "15/08/1992"
    assert fields.gender == "M"
    assert fields.aadhaar_number == "111122223333"

def test_extract_aadhaar_yob():
    # Test Year of Birth (YOB) fallback and female gender
    detections = [
        OCRDetection(text="OTHER NAME", confidence=0.98, bbox=[20, 60, 150, 80]),
        OCRDetection(text="Year of Birth: 1980", confidence=0.96, bbox=[20, 90, 150, 110]),
        OCRDetection(text="Female", confidence=0.99, bbox=[20, 120, 100, 140]),
        OCRDetection(text="9999 8888 7777", confidence=0.99, bbox=[50, 180, 250, 200])
    ]
    
    fields = _extract_aadhaar_fields(detections)
    
    assert fields.name == "OTHER NAME"
    assert fields.date_of_birth is None
    assert fields.year_of_birth == "1980"
    assert fields.gender == "F"
    assert fields.aadhaar_number == "999988887777"

def test_extract_aadhaar_missing_optional():
    # Only Name and Aadhaar number
    detections = [
        OCRDetection(text="JUST A NAME", confidence=0.98, bbox=[20, 60, 150, 80]),
        OCRDetection(text="5555 6666 7777", confidence=0.99, bbox=[50, 180, 250, 200])
    ]
    
    fields = _extract_aadhaar_fields(detections)
    
    assert fields.name == "JUST A NAME"
    assert fields.date_of_birth is None
    assert fields.gender is None
    assert fields.aadhaar_number == "555566667777"
