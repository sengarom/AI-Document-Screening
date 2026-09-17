import threading
import cv2
from pathlib import Path
from typing import Tuple, Any

_detector_instance = None
_recognizer_instance = None
_engine_lock = threading.Lock()

def get_face_engines() -> Tuple[Any, Any]:
    """
    Initialize and return singleton instances of OpenCV's FaceDetectorYN and FaceRecognizerSF.
    Uses thread-safe lazy initialization to avoid load overhead on API startup.
    """
    global _detector_instance, _recognizer_instance
    if _detector_instance is None or _recognizer_instance is None:
        with _engine_lock:
            if _detector_instance is None or _recognizer_instance is None:
                base_dir = Path(__file__).resolve().parent.parent.parent.parent / "models"
                detector_path = str(base_dir / "face_detection_yunet_2023mar.onnx")
                recognizer_path = str(base_dir / "face_recognition_sface_2021dec.onnx")
                
                if not Path(detector_path).exists():
                    raise FileNotFoundError(f"Missing YuNet model at {detector_path}")
                if not Path(recognizer_path).exists():
                    raise FileNotFoundError(f"Missing SFace model at {recognizer_path}")
                
                # Input size for detector is just a dummy (320, 320), it needs to be set dynamically per image
                _detector_instance = cv2.FaceDetectorYN_create(
                    model=detector_path,
                    config="",
                    input_size=(320, 320),
                    score_threshold=0.8,
                    nms_threshold=0.3,
                    top_k=5000
                )
                
                _recognizer_instance = cv2.FaceRecognizerSF_create(
                    model=recognizer_path,
                    config=""
                )
                
    return _detector_instance, _recognizer_instance
