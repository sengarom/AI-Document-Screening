import re

# 1. Update risk.py
with open('backend/app/schemas/risk.py', 'r', encoding='utf-8') as f:
    risk_content = f.read()

if 'from app.schemas.identity import IdentityLinkResponse' not in risk_content:
    risk_content = risk_content.replace('from app.schemas.face import FaceVerificationResponse', 'from app.schemas.face import FaceVerificationResponse\nfrom app.schemas.identity import IdentityLinkResponse')

if 'identity_link_result: Optional[IdentityLinkResponse] = None' not in risk_content:
    risk_content = risk_content.replace('face_result: Optional[FaceVerificationResponse] = None', 'face_result: Optional[FaceVerificationResponse] = None\n    identity_link_result: Optional[IdentityLinkResponse] = None')

with open('backend/app/schemas/risk.py', 'w', encoding='utf-8') as f:
    f.write(risk_content)

# 2. Update report.py
with open('backend/app/schemas/report.py', 'r', encoding='utf-8') as f:
    report_content = f.read()

if 'from app.schemas.identity import IdentityLinkResponse' not in report_content:
    report_content = report_content.replace('from app.schemas.face import FaceVerificationResponse', 'from app.schemas.face import FaceVerificationResponse\nfrom app.schemas.identity import IdentityLinkResponse')

if 'identity_link_result: Optional[IdentityLinkResponse] = None' not in report_content:
    report_content = report_content.replace('face_result: Optional[FaceVerificationResponse] = None', 'face_result: Optional[FaceVerificationResponse] = None\n    identity_link_result: Optional[IdentityLinkResponse] = None')

with open('backend/app/schemas/report.py', 'w', encoding='utf-8') as f:
    f.write(report_content)

print("Updated schemas to support identity links.")
