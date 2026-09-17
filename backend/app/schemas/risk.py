from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from app.schemas.validation import ValidationResponse
from app.schemas.tampering import TamperingResponse
from app.schemas.face import FaceVerificationResponse

class RiskLevel(str, Enum):
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    CRITICAL = 'CRITICAL'

class RiskFactor(BaseModel):
    category: str = Field(..., description='E.g., Validation, Tampering, Face Verification')
    signal: str = Field(..., description='Brief signal type (e.g., WARNING, Score 0.62, NO_MATCH)')
    contribution: int = Field(..., description='Points contributed to the total risk score (0-100)')
    message: str = Field(..., description='Safe, generic, human-readable explanation devoid of PII')

class RiskScoreRequest(BaseModel):
    validation_result: ValidationResponse
    tampering_result: TamperingResponse
    face_result: Optional[FaceVerificationResponse] = None

class RiskScoreResponse(BaseModel):
    document_id: str
    risk_score: int = Field(..., ge=0, le=100, description='Total screening risk score from 0 (lowest observed risk) to 100 (highest observed risk). Not a probability of fraud or authenticity.')
    risk_level: RiskLevel
    factors: List[RiskFactor] = Field(..., description='Detailed explanation of score contributions')
    disclaimer: str = 'This score represents screening risk based on available signals, not a statistical probability of fraud.'