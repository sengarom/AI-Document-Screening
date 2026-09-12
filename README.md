# AI-Based Fake Identity & Document Screening System

**Problem Statement ID:** 26188

An educational/hackathon prototype for AI-assisted screening of identity and travel documents. The objective is to help a human reviewer identify document signals that may need attention and present an explainable risk assessment. It must not make automatic real-world immigration, border, or security decisions.

Only synthetic, public, or explicitly consented data may be used. This repository must never contain real identity documents, biometric data, credentials, or connections to government/border-security databases. Any verification or blacklist data will be simulated locally.

## Planned modules

1. Document upload
2. Document image preprocessing
3. Document type detection
4. OCR extraction
5. MRZ detection and parsing
6. Document validation
7. Simulated verification database
8. Tampering/manipulation detection
9. Face verification
10. Risk scoring
11. Explainable screening report
12. React dashboard

## Technology stack

- Backend: Python, FastAPI, OpenCV, OCR tooling, PyTorch/scikit-learn as needed, SQLite
- Frontend: React, Vite, Tailwind CSS

## Current capability: document upload and preprocessing

POST /api/documents/upload accepts one multipart/form-data field named file.
Supported images are JPG/JPEG, PNG, and WEBP, with a maximum size of 10 MB.
The API validates the filename extension, declared MIME type, actual image content,
and file size before storing it under a generated filename.

The original is stored locally under the ignored uploads/originals/ directory.
Its processed derivative is stored separately under uploads/processed/; the
original is never overwritten. Preprocessing uses EXIF orientation correction when
available, aspect-ratio-preserving resizing for images larger than 2000 pixels on
their longest side, grayscale conversion, gentle denoising, and moderate CLAHE
contrast enhancement. This prepares a future OCR input without implementing OCR.

## Repository structure

```text
backend/       FastAPI application and backend tests
frontend/      React/Vite application scaffold
datasets/      Dataset-use policy (data is ignored by Git)
models/        Model-artifact policy (weights are ignored by Git)
docs/          Architecture, methodology, and API notes
tests/         Cross-project test notes
uploads/       Ignored local development upload storage
```

## Basic setup

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/api/health`. Expected response:

```json
{"status":"ok","service":"AI Document Screening System"}
```

To test uploads in Swagger, open http://127.0.0.1:8000/docs, expand
POST /api/documents/upload, click **Try it out**, and choose a synthetic,
public, or explicitly consented image.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite (normally `http://localhost:5173`).
Start the backend first; the upload interface sends real requests to
http://127.0.0.1:8000/api/documents/upload.

### Automated backend tests

```powershell
cd backend
pip install -r requirements-dev.txt
pytest -q
```
