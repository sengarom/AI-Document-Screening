# API

## Document upload

POST /api/documents/upload

Submit multipart/form-data with a single file image field.

- Allowed formats: JPG/JPEG, PNG, WEBP
- Maximum size: 10 MB
- Validation: extension, declared MIME type, image content, empty files, and
  OpenCV/Pillow decoding
- Storage: generated filenames only; original and processed images are stored
  separately in Git-ignored local upload directories

Successful response: 201 Created

```json
{
  "success": true,
  "document_id": "9ae72fc36dc847db8cc6383515f4fb28",
  "filename": "9ae72fc36dc847db8cc6383515f4fb28.jpg",
  "original_filename": "synthetic-example.jpg",
  "content_type": "image/jpeg",
  "file_size": 12345,
  "original_width": 1600,
  "original_height": 900,
  "processed_width": 1600,
  "processed_height": 900,
  "preprocessing_status": "completed"
}
```

The preprocessing pipeline corrects orientation when possible, limits only
excessively large images, converts to grayscale, performs gentle denoising, and
uses moderate contrast enhancement. It does not implement OCR, MRZ, face,
tampering, or risk analysis.

Typical validation responses are 415 Unsupported Media Type,
413 Content Too Large, and 422 Unprocessable Content. Error responses do not
expose internal paths or stack traces.

## OCR Extraction

`POST /api/documents/{document_id}/ocr`

Run PaddleOCR extraction on a previously uploaded and processed document. The OCR extraction runs in an asynchronous threadpool to prevent blocking the event loop.

Successful response: 200 OK

```json
{
  "success": true,
  "document_id": "generated-id.jpg",
  "engine": "paddleocr-3.7.0",
  "device": "gpu",
  "detections": [
    {
      "text": "Extracted Text",
      "confidence": 0.98,
      "bbox": [10, 10, 100, 30]
    }
  ],
  "extracted_fields": {
    "name": "JOHN DOE",
    "passport_number": "U12345678",
    "nationality": "UTO",
    "date_of_birth": "01 JAN 1990",
    "gender": "M",
    "issue_date": null,
    "expiry_date": null
  },
  "raw_output": null,
  "authenticity_warning": "OCR extraction does not establish document authenticity."
}
```

**Privacy & Security Note**:
OCR output might contain sensitive PII. Ensure raw outputs are not logged to the terminal or saved persistently beyond the API response payload. OCR extraction does not establish document authenticity.

## Health check

`GET /api/health`

Response:

```json
{
  "status": "ok",
  "service": "AI Document Screening System"
}
```
