from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class ValidationStatus(str, Enum):
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"

class ValidationCheck(BaseModel):
    check: str
    status: ValidationStatus
    message: str

class ValidationResponse(BaseModel):
    document_id: str
    valid: bool
    status: ValidationStatus
    checks: List[ValidationCheck]
    authenticity_warning: str = "Document validation checks internal consistency and formatting. It does not establish document authenticity."

class MRZParsedData(BaseModel):
    document_type: Optional[str] = None
    issuing_country: Optional[str] = None
    passport_number: Optional[str] = None
    nationality: Optional[str] = None
    date_of_birth: Optional[str] = None
    sex: Optional[str] = None
    expiry_date: Optional[str] = None
    name: Optional[str] = None
