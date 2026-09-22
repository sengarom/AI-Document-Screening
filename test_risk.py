import urllib.request
import json
import uuid

base = 'http://localhost:8000'

req = urllib.request.Request(f'{base}/api/auth/login', data=json.dumps({'email': 'user@example.com', 'password': 'User@123'}).encode(), headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as response:
    cookie = response.headers.get('Set-Cookie').split(';')[0]
print('Cookie:', cookie)

def post_json(url, data=None):
    body = json.dumps(data).encode() if data else b''
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json', 'Cookie': cookie})
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())

doc_id = 'test-doc-id'

val = {
    "document_id": doc_id,
    "valid": True,
    "status": "passed",
    "checks": [],
    "authenticity_warning": "warning"
}
tamp = {
    "document_id": doc_id,
    "tampering_score": 0.0,
    "severity": "LOW",
    "signals": []
}

payload = {
    'validation_result': val,
    'tampering_result': tamp,
    'face_result': None
}

try:
    risk = post_json(f'{base}/api/documents/{doc_id}/risk-score', payload)
    print('Risk:', risk)
except urllib.error.HTTPError as e:
    print('Error:', e.code, e.read())
