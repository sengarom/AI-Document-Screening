from typing import Tuple, List
import numpy as np
from app.schemas.tampering import ForensicSignal, SuspiciousRegion, TamperingStatus

class MLDetector:
    """
    Interface for ML-based pixel-level tampering localization.
    Implementation will be swappable and added in later phases.
    """
    def __init__(self):
        # Do NOT download or load weights here yet.
        pass
        
    def analyze(self, image: np.ndarray) -> Tuple[ForensicSignal, List[SuspiciousRegion]]:
        """
        Analyzes the image for tampering.
        Returns:
            ForensicSignal: The normalized score, confidence, and explanation.
            List[SuspiciousRegion]: Any localized anomalies.
        """
        return ForensicSignal(
            status=TamperingStatus.PASSED,
            score=0.0,
            confidence=0.0,
            explanation="ML detector not integrated."
        ), []
