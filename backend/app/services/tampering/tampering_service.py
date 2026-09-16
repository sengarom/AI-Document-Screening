import time
from typing import Dict, List
import cv2
import numpy as np

from app.schemas.tampering import TamperingResponse, ForensicSignal, SuspiciousRegion, TamperingStatus
from app.services.tampering.forensic.metadata import analyze_metadata
from app.services.tampering.forensic.ela import analyze_ela
from app.services.tampering.forensic.noise import analyze_noise
from app.services.tampering.forensic.copy_move import analyze_copy_move

def aggregate_signals(signals: Dict[str, ForensicSignal]) -> float:
    """
    Aggregates forensic signals into a single evidence score [0, 1].
    Uses the maximum independent signal score to prevent compounding correlated weak signals.
    """
    if not signals:
        return 0.0
        
    effective_scores = []
    for signal in signals.values():
        if signal.score > 0:
            effective_scores.append(signal.score * signal.confidence)
            
    if not effective_scores:
        return 0.0
        
    return min(1.0, max(0.0, max(effective_scores)))

def analyze_document(document_id: str, image_path: str) -> TamperingResponse:
    """
    Analyzes a document image for tampering using independent forensic signals.
    """
    start_time = time.time()
    
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image for tampering analysis: {image_path}")
    
    signals: Dict[str, ForensicSignal] = {}
    regions: List[SuspiciousRegion] = []
    
    # 1. Classical Forensics (Phase B)
    signals["metadata"] = analyze_metadata(image_path)
    signals["error_level_analysis"] = analyze_ela(image)
    signals["noise_analysis"] = analyze_noise(image)
    signals["copy_move"] = analyze_copy_move(image)
    
    # 2. ML Detector (Phase E - interface only, no weights yet)
    # ml_signal, ml_regions = ml_detector.analyze(image)
    
    # 3. Aggregation (Phase C)
    tampering_score = aggregate_signals(signals)
    
    if tampering_score >= 0.7:
        severity = "HIGH"
        overall_status = TamperingStatus.FAILED
    elif tampering_score >= 0.3:
        severity = "MODERATE"
        overall_status = TamperingStatus.WARNING
    else:
        severity = "LOW"
        overall_status = TamperingStatus.PASSED
    
    processing_time_ms = int((time.time() - start_time) * 1000)
    
    return TamperingResponse(
        document_id=document_id,
        overall_status=overall_status,
        tampering_score=tampering_score,
        severity=severity,
        signals=signals,
        suspicious_regions=regions,
        processing_time_ms=processing_time_ms
    )
