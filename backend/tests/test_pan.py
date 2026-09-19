import pytest
from app.schemas.ocr import OCRDetection
from app.services.ocr.ocr_service import _extract_pan_fields

def test_extract_pan_fields_spatial():
    # Synthetic PAN Layout
    # INCOME TAX DEPARTMENT (y=10)
    # Name: (y=40)
    # JOHN DOE (y=60)
    # Father's Name: (y=90)
    # JAMES DOE (y=110)
    # Date of Birth (y=140)
    # 22/10/1985 (y=160)
    # Signature ...
    # ABCDE1234F (y=200)
    
    detections = [
        OCRDetection(text="INCOME TAX DEPARTMENT", confidence=0.95, bbox=[50, 10, 250, 30]),
        OCRDetection(text="Name", confidence=0.9, bbox=[20, 40, 80, 55]),
        OCRDetection(text="JOHN DOE", confidence=0.98, bbox=[20, 60, 150, 80]),
        OCRDetection(text="Father's Name", confidence=0.88, bbox=[20, 90, 150, 105]),
        OCRDetection(text="JAMES DOE", confidence=0.96, bbox=[20, 110, 150, 130]),
        OCRDetection(text="Date of Birth", confidence=0.92, bbox=[20, 140, 120, 155]),
        OCRDetection(text="22/10/1985", confidence=0.99, bbox=[20, 160, 120, 180]),
        OCRDetection(text="GOVT OF INDIA", confidence=0.8, bbox=[300, 40, 400, 55]),
        OCRDetection(text="ABCDE1234F", confidence=0.99, bbox=[150, 200, 280, 220])
    ]
    
    fields = _extract_pan_fields(detections)
    
    assert fields.name == "JOHN DOE"
    assert fields.fathers_name == "JAMES DOE"
    assert fields.date_of_birth == "22/10/1985"
    assert fields.pan_number == "ABCDE1234F"

def test_extract_pan_fields_missing():
    # Only PAN and Name
    detections = [
        OCRDetection(text="Name", confidence=0.9, bbox=[20, 40, 80, 55]),
        OCRDetection(text="JANE SMITH", confidence=0.98, bbox=[20, 60, 150, 80]),
        OCRDetection(text="XXXXX9999X", confidence=0.99, bbox=[150, 200, 280, 220])
    ]
    
    fields = _extract_pan_fields(detections)
    assert fields.name == "JANE SMITH"
    assert fields.fathers_name is None
    assert fields.date_of_birth is None
    assert fields.pan_number == "XXXXX9999X"

def test_extract_pan_noisy_pan_number():
    # OCR mistake in PAN Number (e.g. O instead of 0, I instead of 1)
    # The regex \b[A-Z]{5}[0-9]{4}[A-Z]{1}\b might fail if noisy, but let's test if it handles spaces or similar things if implemented.
    # We will just verify it extracts a strictly valid one, and ignores a slightly malformed one if we haven't implemented fuzzy matching.
    detections = [
        OCRDetection(text="ABCDE 1234 F", confidence=0.99, bbox=[150, 200, 280, 220]), # Spaces inside PAN
        OCRDetection(text="Name", confidence=0.9, bbox=[20, 40, 80, 55]),
        OCRDetection(text="NOISY NAME", confidence=0.98, bbox=[20, 60, 150, 80]),
    ]
    
    fields = _extract_pan_fields(detections)
    assert fields.name == "NOISY NAME"
    assert fields.pan_number == "ABCDE1234F" # It should strip spaces
