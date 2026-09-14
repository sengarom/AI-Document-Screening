"""Safe local storage orchestration for document-image uploads."""

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from app.core.config import MAX_IMAGE_DIMENSION, MAX_UPLOAD_SIZE_BYTES
from app.services.document.preprocessing_service import (
    PreprocessingError,
    PreprocessingResult,
    preprocess_image,
)


ALLOWED_FORMATS = {
    "JPEG": {"suffix": ".jpg", "mime_type": "image/jpeg"},
    "PNG": {"suffix": ".png", "mime_type": "image/png"},
    "WEBP": {"suffix": ".webp", "mime_type": "image/webp"},
}


@dataclass(frozen=True)
class StoredUpload:
    """Storage and processing details for one accepted upload."""

    document_id: str
    filename: str
    original_filename: str
    content_type: str
    file_size: int
    preprocessing: PreprocessingResult


def _validation_error(message: str, status_code: int) -> HTTPException:
    return HTTPException(status_code=status_code, detail=message)


def _safe_suffix(original_filename: str) -> str:
    return Path(original_filename or "").suffix.lower()


def _validate_declared_type(upload: UploadFile) -> None:
    suffix = _safe_suffix(upload.filename or "")
    allowed_suffixes = {values["suffix"] for values in ALLOWED_FORMATS.values()} | {".jpeg"}
    allowed_mime_types = {values["mime_type"] for values in ALLOWED_FORMATS.values()}

    if suffix not in allowed_suffixes:
        raise _validation_error("Unsupported file type. Use JPG, JPEG, PNG, or WEBP.", status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    if upload.content_type not in allowed_mime_types:
        raise _validation_error("Unsupported image content type.", status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


def _detect_image_format(file_path: Path) -> str:
    try:
        with Image.open(file_path) as image:
            image.verify()
        with Image.open(file_path) as image:
            detected_format = image.format
    except (UnidentifiedImageError, OSError, ValueError) as error:
        raise _validation_error("The uploaded file is not a valid image.", status.HTTP_422_UNPROCESSABLE_CONTENT) from error

    if detected_format not in ALLOWED_FORMATS:
        raise _validation_error("Invalid image format.", status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    return detected_format


def _validate_detected_type(detected_format: str, upload: UploadFile) -> None:
    """Require the filename and declared MIME type to agree with image bytes."""
    expected = ALLOWED_FORMATS[detected_format]
    valid_suffixes = {expected["suffix"]}
    if detected_format == "JPEG":
        valid_suffixes.add(".jpeg")

    if upload.content_type != expected["mime_type"] or _safe_suffix(upload.filename or "") not in valid_suffixes:
        raise _validation_error(
            "The filename or declared content type does not match the image content.",
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )


async def store_and_preprocess_upload(
    upload: UploadFile,
    originals_dir: Path,
    processed_dir: Path,
    max_upload_size: int = MAX_UPLOAD_SIZE_BYTES,
    max_image_dimension: int = MAX_IMAGE_DIMENSION,
) -> StoredUpload:
    """Validate, save, and preprocess an uploaded image without trusting its name."""
    _validate_declared_type(upload)
    originals_dir.mkdir(parents=True, exist_ok=True)
    generated_stem = uuid4().hex
    temporary_path = originals_dir / f"{generated_stem}.uploading"
    file_size = 0

    try:
        with temporary_path.open("wb") as destination:
            while chunk := await upload.read(1024 * 1024):
                file_size += len(chunk)
                if file_size > max_upload_size:
                    raise _validation_error(
                        "File is too large. The maximum upload size is 10 MB.",
                        status.HTTP_413_CONTENT_TOO_LARGE,
                    )
                destination.write(chunk)

        if file_size == 0:
            raise _validation_error("The uploaded file is empty.", status.HTTP_422_UNPROCESSABLE_CONTENT)

        detected_format = _detect_image_format(temporary_path)
        _validate_detected_type(detected_format, upload)
        final_suffix = ALLOWED_FORMATS[detected_format]["suffix"]
        original_path = originals_dir / f"{generated_stem}{final_suffix}"
        temporary_path.replace(original_path)
        processed_path = processed_dir / f"{generated_stem}_processed.png"

        try:
            preprocessing = preprocess_image(original_path, processed_path, max_image_dimension)
        except PreprocessingError as error:
            raise _validation_error(
                "The image could not be preprocessed.", status.HTTP_422_UNPROCESSABLE_CONTENT
            ) from error

        return StoredUpload(
            document_id=generated_stem,
            filename=original_path.name,
            original_filename=Path(upload.filename or "upload").name,
            content_type=ALLOWED_FORMATS[detected_format]["mime_type"],
            file_size=file_size,
            preprocessing=preprocessing,
        )
    except HTTPException:
        raise
    except OSError as error:
        raise _validation_error(
            "The upload could not be stored.", status.HTTP_500_INTERNAL_SERVER_ERROR
        ) from error
    finally:
        await upload.close()
        if temporary_path.exists():
            temporary_path.unlink()
