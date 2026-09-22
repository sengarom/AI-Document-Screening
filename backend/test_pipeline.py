import sys
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

login_data = {"username": "user@example.com", "password": "User@123"}
r = client.post("/api/auth/login", data=login_data)
if r.status_code != 200:
    print("Login failed:", r.text)
    sys.exit(1)

with open("tests/test_images/passport_clean.jpg", "rb") as f:
    files = {"file": ("passport_clean.jpg", f, "image/jpeg")}
    data = {"document_type": "PASSPORT"}
    r = client.post("/api/documents/upload", files=files, data=data)
    if r.status_code != 201:
        print("Upload failed:", r.text)
        sys.exit(1)
    doc_id = r.json()["document_id"]

r_ocr = client.post(f"/api/documents/{doc_id}/ocr")
r_val = client.post(f"/api/documents/{doc_id}/validate")
r_tam = client.post(f"/api/documents/{doc_id}/tampering")

risk_payload = {
    "validation_result": r_val.json(),
    "tampering_result": r_tam.json(),
    "face_result": None
}
print(f"Sending to risk_payload...")
r_risk = client.post(f"/api/documents/{doc_id}/risk-score", json=risk_payload)
print("Risk status:", r_risk.status_code)
if r_risk.status_code != 200:
    print("Risk error:", r_risk.text)
