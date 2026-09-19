# Frontend-Backend Integration Plan

## 1. Architecture Overview
- **Frontend Framework**: Next.js App Router (`src/app/`)
- **Backend Framework**: FastAPI (`backend/app/`)
- **API Base URL**: Configured via `.env.local` as `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000` (Next.js requires `NEXT_PUBLIC_` prefix for client-side access).
- **Service Layer**: A new centralized API client (`src/services/api.ts`) will replace `mockServices.ts`.

## 2. API Mapping & Request Payloads
1. **Upload (`POST /api/documents/upload`)**
   - **Payload**: `FormData` containing the `file` object.
   - **Response**: Returns `document_id`.

2. **OCR (`POST /api/documents/{document_id}/ocr`)**
   - **Payload**: None.
   - **Response**: `OCRResponse` containing `extracted_data` and `confidence`.

3. **Validation & MRZ (`POST /api/documents/{document_id}/validate`)**
   - **Payload**: None.
   - **Response**: `ValidationResponse` (contains `valid`, `status`, and `checks`). Note: The backend combines MRZ analysis into validation, so the frontend's separate MRZ step will be adapted to utilize the unified validation response.

4. **Tampering (`POST /api/documents/{document_id}/tampering`)**
   - **Payload**: None.
   - **Response**: `TamperingResponse` (contains `is_authentic`, `manipulation_probability`, `anomalies`).

5. **Face Verification (`POST /api/documents/{document_id}/face-verification`)**
   - **Status**: **Omitted/Mocked**. The current frontend design lacks a selfie upload UI. Modifying the upload screen to handle multiple files breaks the UI constraints ("Do NOT invent a large new UI unnecessarily"). The backend supports `FaceVerificationResponse` as optional in downstream calls. The frontend UI will display a "skipped" or default face response to preserve layout.

6. **Risk Score (`POST /api/documents/{document_id}/risk-score`)**
   - **Payload**: JSON containing `{ validation_result, tampering_result, face_result: null }`.
   - **Response**: `RiskScoreResponse`.

7. **Screening Report (`POST /api/documents/{document_id}/screening-report`)**
   - **Payload**: JSON containing all previous results (`ocr_result`, `validation_result`, `tampering_result`, `face_result: null`, `risk_result`).
   - **Response**: `ScreeningReportResponse`.

## 3. Document ID and State Flow
Since the backend API is stateless and does not persist upstream results to a database between calls, the frontend must collect the payloads sequentially.
- `screen/page.tsx`: Uploads the file, obtains `document_id`, navigates to `/screen/analyze?id=<document_id>`.
- `screen/analyze/page.tsx`:
  - Retrieves `document_id`.
  - Executes API calls sequentially via `api.ts`.
  - Collects results in a local object.
  - Saves the combined final `ScreeningReport` to `sessionStorage` (e.g., `sessionStorage.setItem('reportData', JSON.stringify(frontendReport))`).
  - Navigates to `/screen/results`.
- `screen/results/page.tsx`:
  - Loads the report from `sessionStorage`.
  - Displays actual backend data instead of `mockService.getRecentReports()`.

## 4. Error Handling and Loading States
- Error handling logic will be added to the centralized `api.ts` file to throw readable errors.
- `screen/page.tsx` will display upload errors gracefully below the upload component.
- `screen/analyze/page.tsx` will halt the pipeline and display an error message if any sequential backend call fails, preventing raw Python stack traces from surfacing.

## 5. Environment & CORS
- The backend `main.py` CORS config has been updated to include `http://localhost:3000` and `http://127.0.0.1:3000` (Next.js default ports).
- We will create `project/.env.local` setting `NEXT_PUBLIC_API_BASE_URL`.

## 6. Required Modifications
**Frontend (`project/`):**
- `src/services/api.ts` (New file)
- `src/app/screen/page.tsx` (Add upload logic)
- `src/app/screen/analyze/page.tsx` (Use real API sequential calls and save to storage)
- `src/app/screen/results/page.tsx` (Load from storage and render)
- `project/.env.local` (New file)

**Backend (`backend/`):**
- Only `main.py` was modified for CORS compatibility. Working backend logic remains strictly untouched.
