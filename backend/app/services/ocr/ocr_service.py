import re
from typing import List, Optional
import paddle

from app.schemas.ocr import OCRDetection, OCRExtractedFields, OCRResponse
from app.services.ocr.paddle_engine import get_ocr_engine
from app.services.ocr.passport_extractor import extract_passport_fields_v2

def extract_text(file_path: str, document_id: str, document_type: str = "PASSPORT") -> OCRResponse:
    """Run OCR extraction using PaddleOCR without logging sensitive data."""
    engine = get_ocr_engine()
    
    result_list = list(engine.predict(file_path))
    
    detections: List[OCRDetection] = []
    
    if result_list and len(result_list) > 0 and isinstance(result_list[0], dict):
        res = result_list[0]
        texts = res.get('rec_texts', [])
        scores = res.get('rec_scores', [])
        polys = res.get('dt_polys', [])
        
        for i, text in enumerate(texts):
            score = float(scores[i]) if i < len(scores) else 0.0
            poly = polys[i] if i < len(polys) else []
            
            if len(poly) == 4:
                xs = [float(p[0]) for p in poly]
                ys = [float(p[1]) for p in poly]
                bbox = [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))]
            else:
                bbox = [0, 0, 0, 0]
                
            detections.append(OCRDetection(text=str(text), confidence=score, bbox=bbox))
            
    if document_type == "PAN":
        extracted_fields = _extract_pan_fields(detections)
    elif document_type == "AADHAAR":
        extracted_fields = _extract_aadhaar_fields(detections)
    else:
        extracted_fields = extract_passport_fields_v2(detections)
    
    try:
        device = "gpu" if paddle.device.is_compiled_with_cuda() else "cpu"
    except Exception:
        device = "cpu"
        
    return OCRResponse(
        success=True,
        document_id=document_id,
        device=device,
        detections=detections,
        extracted_fields=extracted_fields,
        raw_output=None
    )

def _extract_pan_fields(detections: List[OCRDetection]) -> OCRExtractedFields:
    fields = OCRExtractedFields()
    valid_detections = [d for d in detections if d.confidence > 0.5 and d.bbox != [0,0,0,0]]
    
    for i, d in enumerate(valid_detections):
        text = d.text.strip().upper()
        clean_text = re.sub(r'[^A-Z0-9]', '', text)
        if re.fullmatch(r'[A-Z]{5}[0-9]{4}[A-Z]', clean_text):
            fields.pan_number = clean_text
        
        m_date = re.search(r'(\d{2}[/.\-]\d{2}[/.\-]\d{4})', text)
        if m_date:
            fields.date_of_birth = m_date.group(1)
            
        if "NAME" in text and "FATHER" not in text:
            if i + 1 < len(valid_detections):
                fields.name = valid_detections[i+1].text.strip()
        elif "FATHER" in text:
            if i + 1 < len(valid_detections):
                fields.fathers_name = valid_detections[i+1].text.strip()
                
    if not fields.name and valid_detections:
        for i, d in enumerate(valid_detections):
            text = d.text.strip().upper()
            if "INCOME TAX" in text or "GOVT" in text or "INDIA" in text:
                continue
            if re.match(r'^[A-Z\s]+$', text) and len(text) > 4 and "FATHER" not in text:
                fields.name = text
                break
                
    return fields

def _extract_aadhaar_fields(detections: List[OCRDetection]) -> OCRExtractedFields:
    fields = OCRExtractedFields()
    valid_detections = [d for d in detections if d.confidence > 0.5 and d.bbox != [0,0,0,0]]
    
    for i, d in enumerate(valid_detections):
        text = d.text.strip().upper()
        clean_text = re.sub(r'\s+', '', text)
        
        if re.fullmatch(r'\d{12}', clean_text):
            fields.aadhaar_number = clean_text
            
        m_date = re.search(r'(\d{2}[/.\-]\d{2}[/.\-]\d{4})', text)
        m_yob = re.search(r'\b(19|20)\d{2}\b', text)
        if m_date:
            fields.date_of_birth = m_date.group(1)
        elif m_yob and ("YOB" in text or "YEAR" in text):
            fields.year_of_birth = m_yob.group(0)
            
        if re.search(r'\b(MALE|FEMALE)\b', text, re.IGNORECASE):
            fields.gender = "F" if "FEMALE" in text else "M"
            
    for d in valid_detections:
        text = d.text.strip().upper()
        if "GOVERNMENT" in text or "INDIA" in text or "DOB" in text or "MALE" in text or "YEAR" in text:
            continue
        if re.match(r'^[A-Z\s]{4,}$', text):
            fields.name = text
            break
            
    return fields
