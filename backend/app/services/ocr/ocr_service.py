import re
from typing import List, Optional
import paddle

from app.schemas.ocr import OCRDetection, OCRExtractedFields, OCRResponse
from app.services.ocr.paddle_engine import get_ocr_engine

def extract_text(file_path: str, document_id: str) -> OCRResponse:
    """Run OCR extraction using PaddleOCR without logging sensitive data."""
    engine = get_ocr_engine()
    
    # Run prediction
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
            
    extracted_fields = _extract_fields(detections)
    
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

def _extract_fields(detections: List[OCRDetection]) -> OCRExtractedFields:
    """Conservatively extract key passport fields using layout-aware spatial associations."""
    fields = OCRExtractedFields()
    valid_detections = [d for d in detections if d.confidence > 0.5 and d.bbox != [0,0,0,0]]
    consumed = set()
    
    def score_candidate(lbl_bbox, val_bbox):
        l_x1, l_y1, l_x2, l_y2 = lbl_bbox
        v_x1, v_y1, v_x2, v_y2 = val_bbox
        l_cx, l_cy = (l_x1 + l_x2) / 2, (l_y1 + l_y2) / 2
        v_cx, v_cy = (v_x1 + v_x2) / 2, (v_y1 + v_y2) / 2
        
        dist = ((v_cx - l_cx)**2 + (v_cy - l_cy)**2)**0.5
        
        y_overlap = min(l_y2, v_y2) - max(l_y1, v_y1)
        x_overlap = min(l_x2, v_x2) - max(l_x1, v_x1)
        
        # Must be strictly to the right with vertical overlap (same line)
        is_right = (v_cx > l_cx) and (y_overlap > -(l_y2-l_y1)*0.2)
        
        # Must be strictly below with horizontal overlap (same column)
        is_below = (v_cy > l_cy) and (x_overlap > -(l_x2-l_x1)*0.2)
        
        # If it's both right and below (diagonal), we should prefer direct right or direct below.
        # But if it's perfectly right, it's the best.
        if is_right and not is_below:
            return dist
        if is_below and not is_right:
            return dist * 2.0
            
        if is_right and is_below:
            # It's diagonally down-right. This happens if the column is misaligned.
            return dist * 3.0
            
        return float('inf')

    def find_field(label_regex, val_regex=None):
        best_label_idx = -1
        best_label_match = None
        
        for i, d in enumerate(valid_detections):
            if i in consumed: continue
            match = re.search(label_regex, d.text, re.IGNORECASE)
            if match:
                best_label_idx = i
                best_label_match = match
                break
                
        if best_label_idx == -1:
            return None
            
        lbl_det = valid_detections[best_label_idx]
        
        # Same line/detection value?
        remainder = lbl_det.text[best_label_match.end():].strip(" :;-\n")
        if remainder:
            if val_regex is None:
                consumed.add(best_label_idx)
                return remainder
            else:
                m = re.search(val_regex, remainder, re.IGNORECASE)
                if m:
                    consumed.add(best_label_idx)
                    return m.group(1) if m.groups() else remainder
                
        # Spatial search among unused detections
        best_cand_idx = -1
        best_score = float('inf')
        
        for i, d in enumerate(valid_detections):
            if i == best_label_idx or i in consumed:
                continue
                
            val_text = d.text.strip()
            
            # Never consume another known label as a generic value
            if re.search(r'^(?:NAME|SURNAME|GIVEN NAME(?:S)?|DOB|DATE OF BIRTH|DATE OF ISSUE|DATE OF EXPIRY|ISSUE DATE|EXPIRY DATE|PASSPORT NO|DOCUMENT NO|PASSPORT NUMBER|TYPE|SEX(?: \/ GENRE)?|GENDER(?:E)?|NATIONALITY|COUNTRY(?: CODE)?)\s*[:;]?$', val_text, re.IGNORECASE):
                continue
                
            if val_regex:
                m = re.search(val_regex, val_text, re.IGNORECASE)
                if not m:
                    continue
                
            score = score_candidate(lbl_det.bbox, d.bbox)
            if score < best_score:
                best_score = score
                best_cand_idx = i
                
        if best_cand_idx != -1:
            consumed.add(best_label_idx)
            consumed.add(best_cand_idx)
            val_text = valid_detections[best_cand_idx].text.strip()
            
            if val_regex:
                m = re.search(val_regex, val_text, re.IGNORECASE)
                if m and m.groups():
                    return m.group(1)
            return val_text
            
        return None

    # Strict field validation regexes
    date_val = r'(\d{2}.*\d{4})'
    
    fields.date_of_birth = find_field(r'\b(?:DATE OF BIRTH|DOB)\b', date_val)
    fields.issue_date = find_field(r'\b(?:DATE OF ISSUE|ISSUE DATE)\b', date_val)
    fields.expiry_date = find_field(r'\b(?:DATE OF EXPIRY|EXPIRY DATE)\b', date_val)
    
    gender_raw = find_field(r'\b(?:SEX(?: \/ GENRE)?|GENDER(?:E)?)\b', r'\b(M|F|MALE|FEMALE)\b')
    if gender_raw:
        fields.gender = "M" if gender_raw.upper().startswith("M") else "F"
        
    fields.passport_number = find_field(r'\b(?:PASSPORT NO|DOCUMENT NO|DOC NO|PASSPORT NUMBER)\b', r'([A-Z0-9]{6,12})')
    
    fields.nationality = find_field(r'\b(?:NATIONALITY)\b', r'([A-Z]{3,})')
    if not fields.nationality:
        fields.nationality = find_field(r'\b(?:COUNTRY(?: CODE)?)\b', r'([A-Z]{3,})')
        
    surname = find_field(r'\b(?:SURNAME)\b', None)
    given = find_field(r'\b(?:GIVEN NAME(?:S)?)\b', None)
    
    if surname and given:
        fields.name = f"{given} {surname}".strip()
    elif surname:
        fields.name = surname
    elif given:
        fields.name = given
    else:
        fields.name = find_field(r'\b(?:NAME)\b', None)
        
    return fields
