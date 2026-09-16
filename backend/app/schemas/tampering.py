from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class TamperingStatus(str, Enum):
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"

class SuspiciousRegion(BaseModel):
    type: str = Field(..., description="Type of anomaly (e.g., 'ela_anomaly', 'copy_move_clone')")
    bbox: List[int] = Field(..., description="[x1, y1, x2, y2] bounding box")
    confidence: float = Field(..., description="Confidence score [0, 1]")

class ForensicSignal(BaseModel):
    status: TamperingStatus
    score: float = Field(..., ge=0.0, le=1.0, description="Normalized evidence score [0, 1]")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Reliability/confidence of this signal")
    explanation: str = Field(..., description="Explainable reason for the score")

class TamperingResponse(BaseModel):
    document_id: str
    overall_status: TamperingStatus
    tampering_score: float = Field(..., ge=0.0, le=1.0, description="Overall evidence score of tampering [0, 1]. NOT a probability.")
    severity: str = Field(..., description="Severity level: LOW, MODERATE, HIGH")
    signals: Dict[str, ForensicSignal] = Field(..., description="Independent forensic signals")
    suspicious_regions: List[SuspiciousRegion] = []
    processing_time_ms: int
