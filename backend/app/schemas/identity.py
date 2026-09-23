from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class IdentityLinkStatus(str, Enum):
    NOT_ASSESSED = "not_assessed"
    NO_FACE = "no_face"
    NO_PREVIOUS_IDENTITIES = "no_previous_identities"
    NO_MATCH = "no_match"
    POTENTIAL_MATCH = "potential_match"
    MULTIPLE_POTENTIAL_MATCHES = "multiple_potential_matches"
    ERROR = "error"

class IdentityMatch(BaseModel):
    document_id: str
    document_type: str
    similarity: float
    requires_review: bool

class IdentityLinkResponse(BaseModel):
    document_id: str
    status: IdentityLinkStatus
    matches: List[IdentityMatch] = []
    message: str
