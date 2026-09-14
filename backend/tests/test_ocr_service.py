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

def test_extract_fields_spatial_layout():
    from app.schemas.ocr import OCRDetection
    from app.services.ocr.ocr_service import _extract_fields
    
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
    
    fields = _extract_fields(detections)
    assert fields.name == "JANE SMITH"
    assert fields.nationality == "UTOPIAN"
    assert fields.date_of_birth == "15/05/1990"
    assert fields.gender == "F"
    assert fields.issue_date == "10 JAN / JAN 2020"
    assert fields.expiry_date == "09 JAN / JAN 2030"
    assert fields.passport_number == "X98765432"

def test_extract_fields_fallback_name():
    from app.schemas.ocr import OCRDetection
    from app.services.ocr.ocr_service import _extract_fields
    
    detections = [
        OCRDetection(text="Name:", confidence=0.99, bbox=[10, 10, 60, 20]),
        OCRDetection(text="ALICE", confidence=0.99, bbox=[10, 30, 60, 40]), # Below
        OCRDetection(text="Country Code: XYZ", confidence=0.99, bbox=[10, 50, 150, 60]), # Same line
    ]
    
    fields = _extract_fields(detections)
    assert fields.name == "ALICE"
    assert fields.nationality == "XYZ"
