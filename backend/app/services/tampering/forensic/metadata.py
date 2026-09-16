from typing import Dict, Any
from PIL import Image
from PIL.ExifTags import TAGS

from app.schemas.tampering import ForensicSignal, TamperingStatus

# Known image editing software signatures
SUSPICIOUS_SOFTWARE = ["photoshop", "gimp", "lightroom", "pixelmator", "affinity"]

def analyze_metadata(image_path: str) -> ForensicSignal:
    """
    Analyzes EXIF metadata for software signatures indicating editing.
    Missing EXIF is treated as benign (normal for web/uploaded images).
    """
    try:
        with Image.open(image_path) as img:
            exif_data = img.getexif()
            if not exif_data:
                return ForensicSignal(
                    status=TamperingStatus.PASSED,
                    score=0.0,
                    confidence=1.0,
                    explanation="No EXIF metadata found (benign/common)."
                )
                
            metadata = {}
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                metadata[tag] = str(value).lower()
                
            software = metadata.get("Software", "")
            
            for sus in SUSPICIOUS_SOFTWARE:
                if sus in software:
                    return ForensicSignal(
                        status=TamperingStatus.WARNING,
                        score=0.4, # Moderate signal, editing doesn't necessarily mean identity forgery
                        confidence=0.9,
                        explanation=f"Image editing software detected in metadata: {software}"
                    )
            
            return ForensicSignal(
                status=TamperingStatus.PASSED,
                score=0.0,
                confidence=1.0,
                explanation="EXIF metadata present. No suspicious software tags detected."
            )
            
    except Exception as e:
        return ForensicSignal(
            status=TamperingStatus.PASSED,
            score=0.0,
            confidence=0.0,
            explanation=f"Could not parse EXIF: {str(e)}"
        )
