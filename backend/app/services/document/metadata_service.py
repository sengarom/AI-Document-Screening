import json
from pathlib import Path
from app.core.config import ORIGINAL_UPLOADS_DIR

def save_document_metadata(document_id: str, document_type: str):
    """Save document metadata to a JSON file alongside the original upload."""
    meta_path = ORIGINAL_UPLOADS_DIR / f"{document_id}.meta.json"
    meta_data = {"document_type": document_type.upper()}
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_data, f)

def get_document_metadata(document_id: str) -> dict:
    """Retrieve document metadata. Defaults to PASSPORT if not found for backward compatibility."""
    meta_path = ORIGINAL_UPLOADS_DIR / f"{document_id}.meta.json"
    if meta_path.exists():
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"document_type": "PASSPORT"}
