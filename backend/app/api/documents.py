"""Document upload API route."""

from fastapi import APIRouter, File, UploadFile, status

from app.core.config import ORIGINAL_UPLOADS_DIR, PROCESSED_UPLOADS_DIR
from app.schemas.documents import DocumentUploadResponse
from app.services.document.upload_service import store_and_preprocess_upload
from app.services.ocr.ocr_service import extract_text
from app.schemas.ocr import OCRResponse
from app.schemas.validation import ValidationResponse
from app.services.validation.validation_service import validate_document
from app.schemas.tampering import TamperingResponse
from app.services.tampering.tampering_service import analyze_document
from app.schemas.face import FaceVerificationResponse
from app.services.face.face_service import verify_faces
from fastapi.concurrency import run_in_threadpool
from pathlib import Path

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
        document_id=stored_upload.document_id,
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

@router.post("/{document_id}/ocr", response_model=OCRResponse, status_code=status.HTTP_200_OK)
async def run_ocr_on_document(document_id: str) -> OCRResponse:
    """Run PaddleOCR extraction on a previously uploaded and processed document."""
    # Find the processed image
    stem = Path(document_id).stem
    processed_file = PROCESSED_UPLOADS_DIR / f"{stem}_processed.png"

    if not processed_file.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Document not found or not processed.")

    # Run OCR in threadpool to prevent blocking the async event loop
    try:
        result = await run_in_threadpool(extract_text, str(processed_file), document_id)
        return result
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{document_id}/validate", response_model=ValidationResponse, status_code=status.HTTP_200_OK)
async def validate_document_endpoint(document_id: str) -> ValidationResponse:
    """Run Document Validation on a previously uploaded document."""
    # Obtain OCR data internally
    ocr_result = await run_ocr_on_document(document_id)
    
    # Run validation
    validation_result = validate_document(document_id, ocr_result)
    return validation_result

@router.post("/{document_id}/tampering", response_model=TamperingResponse, status_code=status.HTTP_200_OK)
async def run_tampering_analysis(document_id: str) -> TamperingResponse:
    """Run Document Tampering Detection on the original uploaded document."""
    from fastapi import HTTPException
    
    stem = Path(document_id).stem
    # Tampering MUST run on the original unaltered image (for EXIF, ELA, noise, etc.)
    original_files = list(ORIGINAL_UPLOADS_DIR.glob(f"{stem}.*"))
    original_files = [f for f in original_files if f.is_file() and not f.name.endswith(".uploading")]

    if not original_files:
        raise HTTPException(status_code=404, detail="Original document not found.")
        
    original_file = original_files[0]
        
    try:
        # Run in threadpool to prevent blocking the async loop for heavy classical CV operations
        result = await run_in_threadpool(analyze_document, document_id, str(original_file))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{document_id}/face-verification", response_model=FaceVerificationResponse, status_code=status.HTTP_200_OK)
async def verify_document_face(document_id: str, reference_image: UploadFile = File(...)) -> FaceVerificationResponse:
    """Verify the face in the document against a supplied reference selfie."""
    from fastapi import HTTPException
    
    stem = Path(document_id).stem
    # Use the original unaltered image for best quality
    original_files = list(ORIGINAL_UPLOADS_DIR.glob(f"{stem}.*"))
    original_files = [f for f in original_files if f.is_file() and not f.name.endswith(".uploading")]

    if not original_files:
        raise HTTPException(status_code=404, detail="Original document not found.")
        
    original_file = original_files[0]
    
    # Read reference image into memory
    ref_bytes = await reference_image.read()
    if not ref_bytes:
        raise HTTPException(status_code=400, detail="Reference image is empty.")
        
    try:
        # Run in threadpool to prevent blocking the async loop
        result = await run_in_threadpool(verify_faces, document_id, str(original_file), ref_bytes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
