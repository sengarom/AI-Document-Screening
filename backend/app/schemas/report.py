from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from app.schemas.ocr import OCRResponse
from app.schemas.validation import ValidationResponse
from app.schemas.tampering import TamperingResponse
from app.schemas.face import FaceVerificationResponse
from app.schemas.risk import RiskScoreResponse, RiskLevel

class ScreeningStatus(str, Enum):
    CLEAR = "clear"
    REVIEW = "review"
    HIGH_RISK = "high_risk"

class HumanReadableFinding(BaseModel):
    category: str = Field(..., description="E.g., Validation, Tampering, Face Verification, Risk")
    status: str = Field(..., description="Passed, Warning, Failed, Match, etc.")
    summary: str = Field(..., description="A concise, human-readable summary sentence.")
    details: List[str] = Field(default=[], description="Specific issue strings or explanations.")

class DocumentInfo(BaseModel):
    document_type: Optional[str] = None
    name: Optional[str] = None
    document_number: Optional[str] = None
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

class ScreeningReportRequest(BaseModel):
    ocr_result: OCRResponse
    validation_result: ValidationResponse
    tampering_result: TamperingResponse
    face_result: Optional[FaceVerificationResponse] = None
    risk_result: RiskScoreResponse

class ScreeningReportResponse(BaseModel):
    document_id: str
    overall_status: ScreeningStatus
    risk_score: int
    risk_level: RiskLevel
    document_information: DocumentInfo
    findings: List[HumanReadableFinding]
    processing_time_ms: int = Field(..., description="Time spent generating this specific report.")
    timestamp: str = Field(..., description="Server-side ISO 8601 timezone-aware timestamp.")
    disclaimer: str = "This report is an assistive screening tool. It does not establish legal document authenticity, identity, or government verification."

