import cv2
import numpy as np
from app.schemas.tampering import ForensicSignal, TamperingStatus

def analyze_noise(image: np.ndarray) -> ForensicSignal:
    """
    Estimates image noise variance.
    Significant inconsistencies in local noise often indicate splicing or photo replacement.
    """
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Estimate noise using Laplacian (variance of Laplacian)
        # This gives a global blur/noise metric. 
        # Use smaller blocks (e.g. 32x32) to isolate spliced regions from the surrounding baseline.
        h, w = gray.shape
        block_size = 32
        
        variances = []
        for y in range(0, h - block_size + 1, block_size):
            for x in range(0, w - block_size + 1, block_size):
                block = gray[y:y+block_size, x:x+block_size]
                # Variance of Laplacian estimates local high-frequency noise + edges
                laplacian_var = cv2.Laplacian(block, cv2.CV_64F).var()
                variances.append(laplacian_var)
                
        if not variances:
             return ForensicSignal(status=TamperingStatus.PASSED, score=0.0, confidence=0.0, explanation="Image too small.")
             
        # Calculate ratio of max variance to median variance
        med_var = np.median(variances)
        max_var = np.max(variances)
        min_var = np.min(variances)
        
        med_var = max(med_var, 1.0) # avoid div by zero
        
        # We look for unusually high variance (noisy splice)
        ratio = max_var / med_var
        
        score = 0.0
        status = TamperingStatus.PASSED
        explanation = f"Consistent local noise/sharpness (Max Anomaly Ratio: {ratio:.2f})."
        
        # Documents naturally have high variance regions (text) and low variance regions (blank paper).
        # We expect ratio to be naturally high (e.g., 20-50) for typical documents.
        # We only flag extreme outliers where a block is >80x different from the median.
        if ratio > 80.0:
            score = min(1.0, (ratio - 80.0) / 100.0)
            status = TamperingStatus.WARNING if score < 0.7 else TamperingStatus.FAILED
            explanation = f"Inconsistent local noise/sharpness detected (Anomaly Ratio: {ratio:.2f}), suggesting regional manipulation."
            
        return ForensicSignal(
            status=status,
            score=score,
            confidence=0.7, # Lower confidence, as depth of field or lighting can cause this naturally
            explanation=explanation
        )
        
    except Exception as e:
         return ForensicSignal(
            status=TamperingStatus.PASSED,
            score=0.0,
            confidence=0.0,
            explanation=f"Noise analysis failed: {str(e)}"
        )
