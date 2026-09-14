"""Response schemas for the document-upload API."""

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    """Metadata returned after a document image is stored and processed."""

    success: bool
    document_id: str
    filename: str
    original_filename: str
    content_type: str
    file_size: int
    original_width: int
    original_height: int
    processed_width: int
    processed_height: int
    preprocessing_status: str
