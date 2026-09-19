from typing import List
from app.schemas.ocr import OCRResponse, OCRDetection, OCRExtractedFields

def mock_extract_text(file_path: str, document_id: str, document_type: str = "PASSPORT") -> OCRResponse:
    """A mock OCR extraction service for testing without GPU/PaddleOCR."""
    
    if "fail" in document_id:
        raise Exception("Mock OCR Failure")
        
    if "malformed" in document_id:
        return OCRResponse(
            success=False,
            document_id=document_id,
            device="cpu",
            detections=[],
            extracted_fields=OCRExtractedFields(),
            raw_output={"error": "Malformed OCR"}
        )
        
    detections = [
        OCRDetection(text="REPUBLIC OF UTOPIA", confidence=0.99, bbox=[30, 30, 200, 50]),
        OCRDetection(text="NAME: JOHN DOE", confidence=0.95, bbox=[30, 60, 200, 80]),
        OCRDetection(text="SEX: M", confidence=0.98, bbox=[30, 90, 100, 110]),
        OCRDetection(text="PASSPORT NO: U12345678", confidence=0.97, bbox=[30, 120, 250, 140])
    ]
    
    fields = OCRExtractedFields(
        name="JOHN DOE",
        gender="M",
        passport_number="U12345678"
    )
    
    return OCRResponse(
        success=True,
        document_id=document_id,
        device="cpu",
        detections=detections,
        extracted_fields=fields,
        raw_output=None
    )

