import cv2
import numpy as np
from app.schemas.tampering import ForensicSignal, TamperingStatus

def analyze_ela(image: np.ndarray, quality: int = 90) -> ForensicSignal:
    """
    Performs Error Level Analysis (ELA) to detect differential JPEG compression.
    Uniform high variance means the whole image was re-saved (benign).
    Locally concentrated high variance compared to the rest implies a splice.
    """
    try:
        # Encode original image to JPEG
        _, encoded_img = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, quality])
        
        # Decode back
        compressed_img = cv2.imdecode(encoded_img, cv2.IMREAD_COLOR)
        
        # Compute absolute difference
        diff = np.abs(image.astype(np.float32) - compressed_img.astype(np.float32))
        
        # Convert to single channel (mean of RGB) to evaluate overall error magnitude
        diff_gray = np.mean(diff, axis=2)
        
        # Block-based analysis to detect *localized* anomalies (splices) against the surrounding baseline
        h, w = diff_gray.shape
        block_size = 32
        
        block_means = []
        for y in range(0, h - block_size + 1, block_size):
            for x in range(0, w - block_size + 1, block_size):
                block = diff_gray[y:y+block_size, x:x+block_size]
                block_means.append(np.mean(block))
                
        if not block_means:
            return ForensicSignal(status=TamperingStatus.PASSED, score=0.0, confidence=0.0, explanation="Image too small for ELA.")
            
        med_ela = np.median(block_means)
        max_ela = np.max(block_means)
        min_ela = np.min(block_means)
        
        if med_ela == 0 and max_ela == 0:
            return ForensicSignal(
                status=TamperingStatus.PASSED,
                score=0.0,
                confidence=0.9,
                explanation="No compression difference (lossless)."
            )
            
        # If median is very low (e.g. synthetic image), pad it slightly to prevent infinity ratio
        med_ela = max(med_ela, 1.0)
        min_ela = max(min_ela, 0.1) # prevent div by zero
        
        # Ratio of max local ELA to the baseline (median) ELA
        ratio = max_ela / med_ela
        
        score = 0.0
        status = TamperingStatus.PASSED
        explanation = f"Uniform ELA (Max Anomaly Ratio: {ratio:.2f})."
        
        # If a block has >3x the compression error of the baseline, it's highly suspicious
        if ratio > 3.0:
            score = min(1.0, (ratio - 3.0) / 7.0) # Caps at ratio 10.0
            status = TamperingStatus.WARNING if score < 0.7 else TamperingStatus.FAILED
            explanation = f"Localized ELA anomaly detected (Anomaly Ratio: {ratio:.2f}), suggesting differential compression/splicing."
            
        return ForensicSignal(
            status=status,
            score=score,
            confidence=0.8,
            explanation=explanation
        )
        
    except Exception as e:
        return ForensicSignal(
            status=TamperingStatus.PASSED,
            score=0.0,
            confidence=0.0,
            explanation=f"ELA failed: {str(e)}"
        )
