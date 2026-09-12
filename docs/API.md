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
  "filename": "generated-id.jpg",
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

## Health check

`GET /api/health`

Response:

```json
{
  "status": "ok",
  "service": "AI Document Screening System"
}
```
