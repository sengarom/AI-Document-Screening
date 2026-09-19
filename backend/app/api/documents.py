"""Document upload API route."""

from fastapi import APIRouter, File, UploadFile, Form, status, HTTPException
from fastapi.concurrency import run_in_threadpool
from pathlib import Path

from app.core.config import ORIGINAL_UPLOADS_DIR, PROCESSED_UPLOADS_DIR
from app.schemas.documents import DocumentUploadResponse
from app.services.document.upload_service import store_and_preprocess_upload
from app.services.document.metadata_service import save_document_metadata, get_document_metadata
from app.services.ocr.ocr_service import extract_text
from app.schemas.ocr import OCRResponse
from app.schemas.validation import ValidationResponse
from app.services.validation.validation_service import validate_document
from app.schemas.tampering import TamperingResponse
from app.services.tampering.tampering_service import analyze_document
from app.schemas.risk import RiskScoreRequest, RiskScoreResponse
from app.services.risk.risk_service import calculate_risk
from app.schemas.face import FaceVerificationResponse
from app.services.face.face_service import verify_faces
from app.schemas.report import ScreeningReportRequest, ScreeningReportResponse
from app.services.report.report_service import generate_screening_report

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...), document_type: str = Form("PASSPORT")) -> DocumentUploadResponse:
    """Store a safe image upload and create its separate processed derivative."""
    if document_type.upper() not in ["PASSPORT", "VISA", "PAN", "AADHAAR"]:
        raise HTTPException(status_code=400, detail="Unsupported document type.")

    stored_upload = await store_and_preprocess_upload(
        upload=file,
        originals_dir=ORIGINAL_UPLOADS_DIR,
        processed_dir=PROCESSED_UPLOADS_DIR,
    )
    
    save_document_metadata(stored_upload.document_id, document_type.upper())

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
    stem = Path(document_id).stem
    processed_file = PROCESSED_UPLOADS_DIR / f"{stem}_processed.png"

    if not processed_file.exists():
        raise HTTPException(status_code=404, detail="Document not found or not processed.")

    doc_meta = get_document_metadata(document_id)
    doc_type = doc_meta.get("document_type", "PASSPORT")

    try:
        result = await run_in_threadpool(extract_text, str(processed_file), document_id, doc_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Risk scoring failed due to an internal server error.")

@router.post("/{document_id}/validate", response_model=ValidationResponse, status_code=status.HTTP_200_OK)
async def validate_document_endpoint(document_id: str) -> ValidationResponse:
    """Run Document Validation on a previously uploaded document."""
    ocr_result = await run_ocr_on_document(document_id)
    
    doc_meta = get_document_metadata(document_id)
    doc_type = doc_meta.get("document_type", "PASSPORT")

    validation_result = validate_document(document_id, ocr_result, doc_type)
    return validation_result

@router.post("/{document_id}/tampering", response_model=TamperingResponse, status_code=status.HTTP_200_OK)
async def run_tampering_analysis(document_id: str) -> TamperingResponse:
    """Run Document Tampering Detection on the original uploaded document."""
    stem = Path(document_id).stem
    original_files = list(ORIGINAL_UPLOADS_DIR.glob(f"{stem}.*"))
    original_files = [f for f in original_files if f.is_file() and not f.name.endswith(".uploading") and not f.name.endswith(".meta.json")]

    if not original_files:
        raise HTTPException(status_code=404, detail="Original document not found.")

    original_file = original_files[0]

    try:
        result = await run_in_threadpool(analyze_document, document_id, str(original_file))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Risk scoring failed due to an internal server error.")

@router.post("/{document_id}/face-verification", response_model=FaceVerificationResponse, status_code=status.HTTP_200_OK)
async def verify_document_face(document_id: str, reference_image: UploadFile = File(...)) -> FaceVerificationResponse:
    stem = Path(document_id).stem
    processed_file = PROCESSED_UPLOADS_DIR / f"{stem}_processed.png"

    if not processed_file.exists():
        raise HTTPException(status_code=404, detail="Processed document not found for face verification.")

    try:
        ref_bytes = await reference_image.read()
        result = await run_in_threadpool(verify_faces, document_id, str(processed_file), ref_bytes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Risk scoring failed due to an internal server error.")

@router.post("/{document_id}/risk-score", response_model=RiskScoreResponse, status_code=status.HTTP_200_OK)
async def calculate_risk_endpoint(document_id: str, payload: RiskScoreRequest) -> RiskScoreResponse:
    try:
        result = calculate_risk(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Risk scoring failed due to an internal server error.")

@router.post("/{document_id}/screening-report", response_model=ScreeningReportResponse, status_code=status.HTTP_200_OK)
async def generate_report_endpoint(document_id: str, payload: ScreeningReportRequest) -> ScreeningReportResponse:
    if payload.ocr_result.document_id != document_id:
        raise HTTPException(status_code=400, detail="Document ID does not match ocr_result document_id.")
    if payload.validation_result.document_id != document_id:
        raise HTTPException(status_code=400, detail="Document ID does not match validation_result document_id.")
    if payload.tampering_result.document_id != document_id:
        raise HTTPException(status_code=400, detail="Document ID does not match tampering_result document_id.")
    if payload.risk_result.document_id != document_id:
        raise HTTPException(status_code=400, detail="Document ID does not match risk_result document_id.")
    if payload.face_result and payload.face_result.document_id != document_id:
        raise HTTPException(status_code=400, detail="Document ID does not match face_result document_id.")

    doc_meta = get_document_metadata(document_id)
    doc_type = doc_meta.get("document_type", "PASSPORT")
    
    try:
        result = generate_screening_report(document_id, payload, doc_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


    doc_meta = get_document_metadata(document_id)
    doc_type = doc_meta.get("document_type", "PASSPORT")
    
    try:
        result = generate_screening_report(document_id, payload, doc_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")




