from fastapi.testclient import TestClient
from app.main import app
from app.api.auth import get_current_user
import json
import os

client = TestClient(app)

app.dependency_overrides[get_current_user] = lambda: {"id": "test_user", "role": "admin"}

def run_flow(doc_image_path, ref_image_path):
    print(f"--- RUNNING FLOW WITH DOC={os.path.basename(doc_image_path)}, REF={os.path.basename(ref_image_path)} ---")
    
    # 1. Upload doc
    with open(doc_image_path, 'rb') as f:
        res = client.post('/api/documents/upload', files={'file': f}, data={'document_type': 'PASSPORT'})
    if res.status_code not in (200, 201):
        print("Upload failed:", res.text)
        return
    doc_id = res.json()['document_id']
    
    # 2. OCR
    res = client.post(f'/api/documents/{doc_id}/ocr')
    if res.status_code not in (200, 201):
        print("OCR failed:", res.text)
        return
    ocr_res = res.json()
    
    # 3. Validate
    res = client.post(f'/api/documents/{doc_id}/validate')
    if res.status_code not in (200, 201):
        print("Val failed:", res.text)
        return
    val_res = res.json()
    
    # 4. Tampering
    res = client.post(f'/api/documents/{doc_id}/tampering')
    if res.status_code not in (200, 201):
        print("Tamp failed:", res.text)
        return
    tamp_res = res.json()
    
    # 5. Face
    with open(ref_image_path, 'rb') as f:
        res = client.post(f'/api/documents/{doc_id}/face-verification', files={'reference_image': f})
    if res.status_code not in (200, 201):
        print("Face failed:", res.text)
        return
    face_res = res.json()
    
    print(f"FACE RESULT:")
    print(json.dumps(face_res, indent=2))
    
    # 6. Risk
    risk_payload = {
        'validation_result': val_res,
        'tampering_result': tamp_res,
        'face_result': face_res,
        'identity_link_result': None
    }
    res = client.post(f'/api/documents/{doc_id}/risk-score', json=risk_payload)
    if res.status_code not in (200, 201):
        print("Risk failed:", res.text)
        return
    risk_res = res.json()
    print(f"\nRISK RESULT:")
    print(json.dumps(risk_res, indent=2))
    
    # 7. Report
    report_payload = {
        'ocr_result': ocr_res,
        'validation_result': val_res,
        'tampering_result': tamp_res,
        'face_result': face_res,
        'identity_link_result': None,
        'risk_result': risk_res
    }
    res = client.post(f'/api/documents/{doc_id}/screening-report', json=report_payload)
    if res.status_code not in (200, 201):
        print("Report failed:", res.text)
        return
    report_res = res.json()
    print(f"\nFINAL REPORT:")
    print(json.dumps(report_res, indent=2))
    print("-" * 50)

# Same person (using same synthetic face twice, wait, do we have two matching faces?)
# We can just use synthetic_face_a.jpg for both doc and ref, it will match!
run_flow(
    'E:/AI-Document-Screening/backend/tests/fixtures/synthetic_face_a.jpg',
    'E:/AI-Document-Screening/backend/tests/fixtures/synthetic_face_a.jpg'
)

# Different person
run_flow(
    'E:/AI-Document-Screening/backend/tests/fixtures/synthetic_face_a.jpg',
    'E:/AI-Document-Screening/backend/tests/fixtures/synthetic_face_b.jpg'
)
