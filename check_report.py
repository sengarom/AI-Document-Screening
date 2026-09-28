import requests
import json

doc_id = "test_doc"

res = requests.get(f"http://localhost:8000/api/documents/{doc_id}/report")
print(res.status_code)
print(res.text)
