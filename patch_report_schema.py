import re

with open('backend/app/schemas/report.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_enum = '''class ScreeningStatus(str, Enum):
    CLEAR = "clear"
    REVIEW = "review"
    HIGH_RISK = "high_risk"'''

new_enum = '''class ScreeningStatus(str, Enum):
    CLEAR = "clear"
    REQUIRE_REVIEW = "require_review"
    REJECTED = "rejected"
    # Legacy support
    REVIEW = "review"
    HIGH_RISK = "high_risk"'''

content = content.replace(old_enum, new_enum)

old_resp = '''class ScreeningReportResponse(BaseModel):
    document_id: str
    overall_status: ScreeningStatus
    risk_score: int
    risk_level: RiskLevel
    document_information: DocumentInfo
    findings: List[HumanReadableFinding]
    processing_time_ms: int = Field(..., description="Time spent generating this specific report.")
    timestamp: str = Field(..., description="Server-side ISO 8601 timezone-aware timestamp.")
    disclaimer: str = "This report is an assistive screening tool. It does not establish legal document authenticity, identity, or government verification."'''

new_resp = '''class ScreeningReportResponse(BaseModel):
    document_id: str
    overall_status: ScreeningStatus
    decision: ScreeningStatus = Field(default=ScreeningStatus.REQUIRE_REVIEW, description="Final deterministic decision")
    decision_reason: str = Field(default="", description="Human readable reason for the decision")
    risk_score: int
    risk_level: RiskLevel
    document_information: DocumentInfo
    findings: List[HumanReadableFinding]
    processing_time_ms: int = Field(..., description="Time spent generating this specific report.")
    timestamp: str = Field(..., description="Server-side ISO 8601 timezone-aware timestamp.")
    disclaimer: str = "This report is an assistive screening tool. It does not establish legal document authenticity, identity, or government verification."'''

content = content.replace(old_resp, new_resp)

with open('backend/app/schemas/report.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched schemas/report.py")
