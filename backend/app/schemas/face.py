from pydantic import BaseModel, Field
from enum import Enum

class FaceVerificationStatus(str, Enum):
    MATCH = "match"
    NO_MATCH = "no_match"
    NO_FACE_DOCUMENT = "no_face_document"
    MULTIPLE_FACES_DOCUMENT = "multiple_faces_document"
    NO_FACE_REFERENCE = "no_face_reference"
    MULTIPLE_FACES_REFERENCE = "multiple_faces_reference"
    QUALITY_FAILURE = "quality_failure"
    ERROR = "error"

class FaceVerificationResponse(BaseModel):
    document_id: str
    status: FaceVerificationStatus
    verified: bool = Field(..., description="True only if status is MATCH")
    similarity_score: float = Field(..., description="Cosine similarity score [-1.0, 1.0]. NOT a probability. 0.0 if not compared.")
    message: str = Field(..., description="Human-readable explanation of the result.")
    processing_time_ms: int
