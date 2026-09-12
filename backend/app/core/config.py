"""Small, explicit configuration values for local development."""

from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent
UPLOADS_DIR = PROJECT_ROOT / "uploads"
ORIGINAL_UPLOADS_DIR = UPLOADS_DIR / "originals"
PROCESSED_UPLOADS_DIR = UPLOADS_DIR / "processed"
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024
MAX_IMAGE_DIMENSION = 2000
