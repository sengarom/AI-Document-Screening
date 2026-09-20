import pytest
import numpy as np
from unittest.mock import MagicMock
from app.services.ocr import ocr_service

def test_extract_text_handles_numpy_arrays(monkeypatch):
    # Mock the paddle engine
    mock_engine = MagicMock()
    
    # Create numpy arrays to simulate PaddleOCR 3.7.0 output
    # 'rec_texts': list of strings or numpy arrays
    # 'rec_scores': numpy array of floats
    # 'dt_polys': numpy array of shape (N, 4, 2)
    
    mock_result = {
        'rec_texts': ["NAME: JOHN DOE", np.str_("DOC NO: U12345678")],
        'rec_scores': np.array([0.95, 0.98], dtype=np.float32),
        'dt_polys': np.array([
            [[10.0, 10.0], [100.0, 10.0], [100.0, 30.0], [10.0, 30.0]],
            [[10.0, 40.0], [200.0, 40.0], [200.0, 60.0], [10.0, 60.0]]
        ], dtype=np.float32)
    }
    
    # Predict returns an iterable
    mock_engine.predict.return_value = iter([mock_result])
    
    # Patch get_ocr_engine
    monkeypatch.setattr(ocr_service, "get_ocr_engine", lambda: mock_engine)
    
    # Execute the service directly
    response = ocr_service.extract_text("dummy_path.png", "doc_123")
    
    assert response.success is True
    assert len(response.detections) == 2
    
    # Verify exact types are native Python, NOT numpy
    d1 = response.detections[0]
    assert type(d1.text) is str
    assert type(d1.confidence) is float
    assert type(d1.bbox[0]) is int
    assert d1.bbox == [10, 10, 100, 30]
    
    d2 = response.detections[1]
    assert type(d2.text) is str
    assert type(d2.confidence) is float
    assert type(d2.bbox[0]) is int
    assert d2.bbox == [10, 40, 200, 60]
    
    # Verify field extraction
    assert response.extracted_fields.name == "JOHN DOE"
    assert response.extracted_fields.passport_number == "U12345678"

def test_extract_passport_fields_spatial_layout():
    from app.schemas.ocr import OCRDetection
    from app.services.ocr.ocr_service import _extract_passport_fields
    
    detections = [
        # Same line: Passport No
        OCRDetection(text="Passport No: X98765432", confidence=0.99, bbox=[10, 10, 200, 20]),
        
        # Type: P vs Passport
        OCRDetection(text="Type: P", confidence=0.99, bbox=[10, 25, 80, 35]),
        
        # Surname and Given Names (Vertical/Horizontal mix)
        OCRDetection(text="Surname:", confidence=0.99, bbox=[10, 40, 80, 50]),
        OCRDetection(text="SMITH", confidence=0.99, bbox=[150, 40, 200, 50]),
        OCRDetection(text="Given Names:", confidence=0.99, bbox=[10, 60, 100, 70]),
        OCRDetection(text="JANE", confidence=0.99, bbox=[150, 60, 200, 70]),
        
        # Two column layout: Nationality left, DOB right
        OCRDetection(text="Nationality:", confidence=0.99, bbox=[10, 80, 90, 90]),
        OCRDetection(text="UTOPIAN", confidence=0.99, bbox=[150, 80, 220, 90]),
        OCRDetection(text="Date of Birth:", confidence=0.99, bbox=[250, 80, 350, 90]),
        OCRDetection(text="15/05/1990", confidence=0.99, bbox=[250, 100, 350, 110]), # Below
        
        # Sex
        OCRDetection(text="Sex / Genre:", confidence=0.99, bbox=[10, 120, 90, 130]),
        OCRDetection(text="F", confidence=0.99, bbox=[150, 120, 160, 130]),
        
        # Issue Date (Below)
        OCRDetection(text="Date of Issue:", confidence=0.99, bbox=[10, 140, 100, 150]),
        OCRDetection(text="10 JAN / JAN 2020", confidence=0.99, bbox=[10, 160, 150, 170]),
        
        # Expiry Date (Below)
        OCRDetection(text="Date of Expiry:", confidence=0.99, bbox=[10, 180, 100, 190]),
        OCRDetection(text="09 JAN / JAN 2030", confidence=0.99, bbox=[10, 200, 150, 210]),
        
        # Fallback Country Code (Should not be used because Nationality is present)
        OCRDetection(text="Country Code: UTO", confidence=0.99, bbox=[10, 220, 150, 230]),
    ]
    
    fields = _extract_passport_fields(detections)
    assert fields.name == "JANE SMITH"
    assert fields.nationality == "UTOPIAN"
    assert fields.date_of_birth == "15/05/1990"
    assert fields.gender == "F"
    assert fields.issue_date == "10 JAN / JAN 2020"
    assert fields.expiry_date == "09 JAN / JAN 2030"
    assert fields.passport_number == "X98765432"

def test_extract_passport_fields_fallback_name():
    from app.schemas.ocr import OCRDetection
    from app.services.ocr.ocr_service import _extract_passport_fields
    
    detections = [
        OCRDetection(text="Name:", confidence=0.99, bbox=[10, 10, 60, 20]),
        OCRDetection(text="ALICE", confidence=0.99, bbox=[10, 30, 60, 40]), # Below
        OCRDetection(text="Country Code: XYZ", confidence=0.99, bbox=[10, 50, 150, 60]), # Same line
    ]
    
    fields = _extract_passport_fields(detections)
    assert fields.name == "ALICE"
    assert fields.nationality == "XYZ"

def _extract_passport_fields(detections):
    print("extract_passport_fields running")


def test_extract_passport_fields_fathers_name_regression():
    from app.schemas.ocr import OCRDetection
    from app.services.ocr.ocr_service import _extract_passport_fields
    
    # User's reported failure case layout
    detections = [
        OCRDetection(text="FULL NAME:", confidence=0.99, bbox=[10, 10, 100, 20]),
        OCRDetection(text="ARJUN MEHRA", confidence=0.99, bbox=[110, 10, 250, 20]),
        
        OCRDetection(text="FATHER'S NAME:", confidence=0.99, bbox=[10, 40, 150, 50]),
        OCRDetection(text="JAMES MEHRA", confidence=0.99, bbox=[160, 40, 300, 50]),
        
        OCRDetection(text="DATE OF BIRTH: 14/08/1998", confidence=0.99, bbox=[10, 70, 300, 80]),
        OCRDetection(text="GENDER: MALE", confidence=0.99, bbox=[10, 100, 200, 110]),
    ]
    
    fields = _extract_passport_fields(detections)
    assert fields.name == "ARJUN MEHRA"
    assert fields.fathers_name == "JAMES MEHRA"
    assert fields.date_of_birth == "14/08/1998"
    assert fields.gender == "M"

def test_extract_passport_fields_fathers_name_ordering_regression():
    from app.schemas.ocr import OCRDetection
    from app.services.ocr.ocr_service import _extract_passport_fields
    
    # Father's name appearing before Name in OCR detection order
    detections = [
        OCRDetection(text="FATHER'S NAME: JAMES MEHRA", confidence=0.99, bbox=[10, 10, 300, 20]),
        OCRDetection(text="NAME: ARJUN MEHRA", confidence=0.99, bbox=[10, 40, 250, 50]),
    ]
    
    fields = _extract_passport_fields(detections)
    assert fields.name == "ARJUN MEHRA"
    assert fields.fathers_name == "JAMES MEHRA"

def test_extract_passport_fields_fathers_name_robustness():
    from app.schemas.ocr import OCRDetection
    from app.services.ocr.ocr_service import _extract_passport_fields

    # A. FULL NAME before FATHER'S NAME
    detections_a = [
        OCRDetection(text="FULL NAME:", confidence=0.99, bbox=[10, 10, 100, 20]),
        OCRDetection(text="ARJUN MEHRA", confidence=0.99, bbox=[110, 10, 250, 20]),
        OCRDetection(text="FATHER'S NAME:", confidence=0.99, bbox=[10, 40, 150, 50]),
        OCRDetection(text="JAMES MEHRA", confidence=0.99, bbox=[160, 40, 300, 50]),
    ]
    fields_a = _extract_passport_fields(detections_a)
    assert fields_a.name == "ARJUN MEHRA"
    assert fields_a.fathers_name == "JAMES MEHRA"

    # B. FATHER'S NAME before FULL NAME
    detections_b = [
        OCRDetection(text="FATHER'S NAME:", confidence=0.99, bbox=[10, 10, 150, 20]),
        OCRDetection(text="JAMES MEHRA", confidence=0.99, bbox=[160, 10, 300, 20]),
        OCRDetection(text="FULL NAME:", confidence=0.99, bbox=[10, 40, 100, 50]),
        OCRDetection(text="ARJUN MEHRA", confidence=0.99, bbox=[110, 40, 250, 50]),
    ]
    fields_b = _extract_passport_fields(detections_b)
    assert fields_b.name == "ARJUN MEHRA"
    assert fields_b.fathers_name == "JAMES MEHRA"

    # C. Both labels in the same OCR detection (e.g., FATHER'S NAME: JAMES MEHRA)
    detections_c = [
        OCRDetection(text="FATHER'S NAME: JAMES MEHRA", confidence=0.99, bbox=[10, 10, 300, 20]),
        OCRDetection(text="FULL NAME: ARJUN MEHRA", confidence=0.99, bbox=[10, 40, 250, 50]),
    ]
    fields_c = _extract_passport_fields(detections_c)
    assert fields_c.name == "ARJUN MEHRA"
    assert fields_c.fathers_name == "JAMES MEHRA"

    # E. Horizontally adjacent (done above in A and B)
    # F. Vertically adjacent
    detections_f = [
        OCRDetection(text="FULL NAME", confidence=0.99, bbox=[10, 10, 100, 20]),
        OCRDetection(text="ARJUN MEHRA", confidence=0.99, bbox=[10, 30, 200, 40]),
        OCRDetection(text="FATHER S NAME", confidence=0.99, bbox=[10, 60, 150, 70]), # Test OCR error "S"
        OCRDetection(text="JAMES MEHRA", confidence=0.99, bbox=[10, 80, 200, 90]),
    ]
    fields_f = _extract_passport_fields(detections_f)
    assert fields_f.name == "ARJUN MEHRA"
    assert fields_f.fathers_name == "JAMES MEHRA"

    # G. Arbitrary list order (visual position still correct)
    detections_g = [
        OCRDetection(text="JAMES MEHRA", confidence=0.99, bbox=[160, 40, 300, 50]),
        OCRDetection(text="FULL NAME:", confidence=0.99, bbox=[10, 10, 100, 20]),
        OCRDetection(text="FATHER'S NAME:", confidence=0.99, bbox=[10, 40, 150, 50]),
        OCRDetection(text="ARJUN MEHRA", confidence=0.99, bbox=[110, 10, 250, 20]),
    ]
    fields_g = _extract_passport_fields(detections_g)
    assert fields_g.name == "ARJUN MEHRA"
    assert fields_g.fathers_name == "JAMES MEHRA"

def test_extract_passport_fields_negative_cases():
    from app.schemas.ocr import OCRDetection
    from app.services.ocr.ocr_service import _extract_passport_fields

    # Legitimate name field
    detections_1 = [
        OCRDetection(text="NAME: ARJUN MEHRA", confidence=0.99, bbox=[10, 10, 200, 20]),
    ]
    assert _extract_passport_fields(detections_1).name == "ARJUN MEHRA"
    assert _extract_passport_fields(detections_1).fathers_name is None

    # Legitimate full name field
    detections_2 = [
        OCRDetection(text="FULL NAME: ARJUN MEHRA", confidence=0.99, bbox=[10, 10, 250, 20]),
    ]
    assert _extract_passport_fields(detections_2).name == "ARJUN MEHRA"
    assert _extract_passport_fields(detections_2).fathers_name is None

    # Only Father's Name exists
    detections_3 = [
        OCRDetection(text="FATHER'S NAME: JAMES MEHRA", confidence=0.99, bbox=[10, 10, 300, 20]),
        # Add some unrelated text to ensure NAME isn't triggered
        OCRDetection(text="DATE OF BIRTH: 01/01/2000", confidence=0.99, bbox=[10, 40, 200, 50]),
    ]
    fields_3 = _extract_passport_fields(detections_3)
    assert fields_3.fathers_name == "JAMES MEHRA"
    assert fields_3.name is None
