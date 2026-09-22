import urllib.request
import urllib.parse
import json
import codecs
import mimetypes
import uuid

base = 'http://localhost:8000'

req = urllib.request.Request(f'{base}/api/auth/login', data=json.dumps({'email': 'user@example.com', 'password': 'User@123'}).encode(), headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as response:
    cookie = response.headers.get('Set-Cookie').split(';')[0]
print('Cookie:', cookie)

def post_multipart(url, filename, filepath, cookie):
    boundary = uuid.uuid4().hex
    headers = {'Content-Type': f'multipart/form-data; boundary={boundary}', 'Cookie': cookie}
    with open(filepath, 'rb') as f:
        file_data = f.read()
    
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name=\"document_type\"\r\n\r\n'
        f'PASSPORT\r\n'
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\n'
        f'Content-Type: image/jpeg\r\n\r\n'
    ).encode('utf-8') + file_data + f'\r\n--{boundary}--\r\n'.encode('utf-8')
    
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())

print('Uploading...')
upload_res = post_multipart(f'{base}/api/documents/upload', 'passport_test.jpg', 'backend/tests/fixtures/document_images/passport_test.jpg', cookie)
doc_id = upload_res['document_id']
print('Upload doc_id:', doc_id)

def post_json(url, data=None):
    body = json.dumps(data).encode() if data else b''
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json', 'Cookie': cookie})
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())

print('OCR...')
ocr = post_json(f'{base}/api/documents/{doc_id}/ocr')
print('Validation...')
val = post_json(f'{base}/api/documents/{doc_id}/validate')
print('Tampering...')
tamp = post_json(f'{base}/api/documents/{doc_id}/tampering')

print('Risk...')
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
