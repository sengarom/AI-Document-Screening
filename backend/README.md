# Backend

The FastAPI backend currently provides only a health endpoint. AI-assisted screening modules are intentionally unimplemented during this setup phase.

## Run locally

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/api/health` or the interactive API documentation at `http://127.0.0.1:8000/docs`.
