"""Conservative image preprocessing for later OCR consumption."""

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError


class PreprocessingError(Exception):
    """Raised when a stored upload cannot be decoded or processed."""


@dataclass(frozen=True)
class PreprocessingResult:
    """Dimensions and output location of a processed image."""

    original_width: int
    original_height: int
    processed_width: int
    processed_height: int
    processed_path: Path


def _load_oriented_image(image_path: Path) -> tuple[np.ndarray, int, int]:
    """Decode an image while respecting an EXIF orientation tag when present."""
    try:
        with Image.open(image_path) as opened_image:
            original_width, original_height = opened_image.size
            oriented_image = ImageOps.exif_transpose(opened_image).convert("RGB")
            image_array = np.array(oriented_image)
    except (UnidentifiedImageError, OSError, ValueError) as error:
        raise PreprocessingError("The uploaded file is not a valid image.") from error

    decoded_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
    if decoded_image is None or decoded_image.size == 0:
        raise PreprocessingError("OpenCV could not decode the uploaded image.")

    return decoded_image, original_width, original_height


def _resize_if_needed(image: np.ndarray, maximum_dimension: int) -> np.ndarray:
    """Limit oversized images without changing their aspect ratio."""
    height, width = image.shape[:2]
    largest_dimension = max(width, height)
    if largest_dimension <= maximum_dimension:
        return image

    scale = maximum_dimension / largest_dimension
    resized_width = max(1, round(width * scale))
    resized_height = max(1, round(height * scale))
    return cv2.resize(image, (resized_width, resized_height), interpolation=cv2.INTER_AREA)


def preprocess_image(
    original_path: Path,
    processed_path: Path,
    maximum_dimension: int,
) -> PreprocessingResult:
    """Create a separate, gently enhanced grayscale image for later OCR."""
    image, original_width, original_height = _load_oriented_image(original_path)
    resized_image = _resize_if_needed(image, maximum_dimension)
    grayscale_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

    # Mild denoising and low-clip CLAHE retain fine document features.
    denoised_image = cv2.fastNlMeansDenoising(grayscale_image, None, h=5)
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
    processed_image = clahe.apply(denoised_image)

    processed_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(processed_path), processed_image):
        raise PreprocessingError("The processed image could not be saved.")

    processed_height, processed_width = processed_image.shape[:2]
    return PreprocessingResult(
        original_width=original_width,
        original_height=original_height,
        processed_width=processed_width,
        processed_height=processed_height,
        processed_path=processed_path,
    )
