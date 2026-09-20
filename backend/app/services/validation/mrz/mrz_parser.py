import re
from typing import List, Optional
from app.schemas.ocr import OCRDetection
from app.schemas.validation import MRZParsedData

def group_detections_into_lines(detections: List[OCRDetection]) -> List[List[OCRDetection]]:
    if not detections:
        return []
    detections_sorted = sorted(detections, key=lambda d: (d.bbox[1] + d.bbox[3]) / 2)
    lines = []
    current_line = [detections_sorted[0]]
    
    for d in detections_sorted[1:]:
        avg_y = sum((c.bbox[1] + c.bbox[3]) / 2 for c in current_line) / len(current_line)
        d_y = (d.bbox[1] + d.bbox[3]) / 2
        d_h = max(1, d.bbox[3] - d.bbox[1])
        
        if abs(d_y - avg_y) < d_h * 0.5:
            current_line.append(d)
        else:
            lines.append(current_line)
            current_line = [d]
    if current_line:
        lines.append(current_line)
        
    for line in lines:
        line.sort(key=lambda d: (d.bbox[0] + d.bbox[2]) / 2)
        
    return lines

def extract_mrz_lines(detections: List[OCRDetection]) -> List[str]:
    """Finds and reconstructs candidate MRZ lines from OCR detections using spatial layout."""
    lines = group_detections_into_lines(detections)
    
    mrz_candidates = []
    for line in lines:
        text = "".join(d.text.replace(" ", "").upper() for d in line)
        text = text.replace("«", "<").replace("(", "<").replace(")", "<")
        
        valid_chars = sum(1 for c in text if c.isalnum() or c == '<')
        if len(text) >= 30 and (valid_chars / max(len(text), 1)) > 0.9 and (text.count('<') >= 2 or text.startswith('P<') or text.startswith('V<')):
            mrz_candidates.append((text, line[0].bbox[1]))
            
    mrz_candidates.sort(key=lambda x: x[1])
    mrz_texts = [x[0] for x in mrz_candidates]
    
    normalized = []
    for i, text in enumerate(mrz_texts[:2]):
        if len(text) < 44:
            if i == 0:
                text = text.ljust(44, '<')
            elif i == 1:
                match = re.search(r'<+', text)
                if match:
                    num_missing = 44 - len(text)
                    text = text[:match.start()] + ('<' * (len(match.group()) + num_missing)) + text[match.end():]
                else:
                    text = text.ljust(44, '<')
        elif len(text) > 44:
            text = text[:44]
            
        normalized.append(text)
        
    return normalized

def parse_mrz(lines: List[str]) -> Optional[MRZParsedData]:
    """Parses a 2-line TD3 MRZ into fields."""
    if len(lines) != 2:
        return None
        
    line1 = lines[0].ljust(44, '<')[:44]
    line2 = lines[1].ljust(44, '<')[:44]
    
    def fix_country(c: str) -> str:
        return c.replace('0', 'O').replace('1', 'I')
    
    data = MRZParsedData()
    data.document_type = line1[0:2].replace("<", "")
    data.issuing_country = fix_country(line1[2:5].replace("<", ""))
    
    name_field = line1[5:]
    if "<<" in name_field:
        parts = name_field.split("<<", 1)
        surname = parts[0].replace("<", " ").strip()
        given = parts[1].replace("<", " ").strip()
        data.name = f"{given} {surname}".strip()
    else:
        data.name = name_field.replace("<", " ").strip()
        
    def format_mrz_date(yymmdd: str, is_dob: bool = False) -> str:
        if len(yymmdd) != 6 or not yymmdd.isdigit():
            return yymmdd
        yy, mm, dd = int(yymmdd[0:2]), yymmdd[2:4], yymmdd[4:6]
        from datetime import datetime
        current_year = datetime.now().year
        current_yy = current_year % 100
        
        century = 2000
        if is_dob and yy > current_yy:
            century = 1900
            
        return f"{dd}/{mm}/{century + yy}"

    data.passport_number = line2[0:9].replace("<", "")
    data.nationality = fix_country(line2[10:13].replace("<", ""))
    data.date_of_birth = format_mrz_date(line2[13:19], is_dob=True)
    data.sex = line2[20].replace("<", "X")
    data.expiry_date = format_mrz_date(line2[21:27], is_dob=False)
    
    return data


