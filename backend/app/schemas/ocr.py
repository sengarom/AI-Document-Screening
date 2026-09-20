from typing import List, Optional, Any
from pydantic import BaseModel, Field

class OCRDetection(BaseModel):
    text: str
    confidence: float
    bbox: List[int] # [x1, y1, x2, y2]

class OCRExtractedFields(BaseModel):
    name: Optional[str] = None
    passport_number: Optional[str] = None
    nationality: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    fathers_name: Optional[str] = None
    pan_number: Optional[str] = None
    aadhaar_number: Optional[str] = None
    year_of_birth: Optional[str] = None
    address: Optional[str] = None
    provenance: Optional[dict] = None

class OCRResponse(BaseModel):
    success: bool
    document_id: str
    engine: str = "paddleocr-3.7.0"
    device: str
    detections: List[OCRDetection]
    extracted_fields: OCRExtractedFields
    raw_output: Any = Field(default=None, description="Raw PaddleOCR output for debugging (optional)")
    authenticity_warning: str = "OCR extraction does not establish document authenticity."

