import requests
import json
import base64

# Use the images from the repo tests
doc_image_path = 'E:/AI-Document-Screening/backend/tests/fixtures/synthetic_face_a.jpg'
ref_image_path = 'E:/AI-Document-Screening/backend/tests/fixtures/synthetic_face_b.jpg'

# 1. Upload doc
print("1. Uploading document...")
with open(doc_image_path, 'rb') as f:
    res = requests.post('http://localhost:8000/api/documents/upload', files={'file': f}, data={'document_type': 'PASSPORT'})
doc_id = res.json()['document_id']
print(f"Document ID: {doc_id}")

# 2. OCR
print("2. OCR...")
res = requests.post(f'http://localhost:8000/api/documents/{doc_id}/ocr')
ocr_res = res.json()

# 3. Validate
print("3. Validate...")
res = requests.post(f'http://localhost:8000/api/documents/{doc_id}/validate')
val_res = res.json()

# 4. Tampering
print("4. Tampering...")
res = requests.post(f'http://localhost:8000/api/documents/{doc_id}/tampering')
tamp_res = res.json()

# 5. Face
print("5. Face Verification...")
with open(ref_image_path, 'rb') as f:
    res = requests.post(f'http://localhost:8000/api/documents/{doc_id}/face-verification', files={'reference_image': f})
face_res = res.json()
print("FACE RESULT:")
print(json.dumps(face_res, indent=2))

# 6. Risk
print("6. Risk Score...")
risk_payload = {
    'validation_result': val_res,
    'tampering_result': tamp_res,
    'face_result': face_res,
    'identity_link_result': None
}
res = requests.post(f'http://localhost:8000/api/documents/{doc_id}/risk-score', json=risk_payload)
risk_res = res.json()
print("RISK RESULT:")
print(json.dumps(risk_res, indent=2))

# 7. Report
print("7. Report...")
report_payload = {
    'ocr_result': ocr_res,
    'validation_result': val_res,
    'tampering_result': tamp_res,
    'face_result': face_res,
    'identity_link_result': None,
    'risk_result': risk_res
}
res = requests.post(f'http://localhost:8000/api/documents/{doc_id}/screening-report', json=report_payload)
report_res = res.json()
print("FINAL REPORT:")
print(json.dumps(report_res, indent=2))
