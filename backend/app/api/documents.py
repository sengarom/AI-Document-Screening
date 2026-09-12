"""Document upload API route."""

from fastapi import APIRouter, File, UploadFile, status

from app.core.config import ORIGINAL_UPLOADS_DIR, PROCESSED_UPLOADS_DIR
from app.schemas.documents import DocumentUploadResponse
from app.services.document.upload_service import store_and_preprocess_upload

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)) -> DocumentUploadResponse:
    """Store a safe image upload and create its separate processed derivative."""
    stored_upload = await store_and_preprocess_upload(
        upload=file,
        originals_dir=ORIGINAL_UPLOADS_DIR,
        processed_dir=PROCESSED_UPLOADS_DIR,
    )
    return DocumentUploadResponse(
        success=True,
        filename=stored_upload.filename,
        original_filename=stored_upload.original_filename,
        content_type=stored_upload.content_type,
        file_size=stored_upload.file_size,
        original_width=stored_upload.preprocessing.original_width,
        original_height=stored_upload.preprocessing.original_height,
        processed_width=stored_upload.preprocessing.processed_width,
        processed_height=stored_upload.preprocessing.processed_height,
        preprocessing_status="completed",
    )
