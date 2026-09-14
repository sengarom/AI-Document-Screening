import threading
from typing import Any

_engine_instance = None
_engine_lock = threading.Lock()

def get_ocr_engine() -> Any:
    """Initialize and return a singleton PaddleOCR engine."""
    global _engine_instance
    if _engine_instance is None:
        with _engine_lock:
            if _engine_instance is None:
                # Deferred import ensures PaddleOCR is only loaded when actually needed,
                # keeping standard API tests fast and avoiding GPU/download overhead.
                import paddleocr
                _engine_instance = paddleocr.PaddleOCR(
                    use_textline_orientation=True, 
                    lang='en'
                )
    return _engine_instance
