from typing import List, Optional, Dict, Any, Tuple
import re
import math
from app.schemas.ocr import OCRDetection, OCRExtractedFields
from app.services.validation.mrz.mrz_parser import extract_mrz_lines, parse_mrz
from pydantic import BaseModel

VALID_ALPHA3_CODES = {
    "AFG","ALB","DZA","ASM","AND","AGO","AIA","ATA","ATG","ARG","ARM","ABW","AUS","AUT","AZE","BHS","BHR","BGD","BRB","BLR","BEL","BLZ","BEN","BMU","BTN","BOL","BES","BIH","BWA","BVT","BRA","IOT","BRN","BGR","BFA","BDI","CPV","KHM","CMR","CAN","CYM","CAF","TCD","CHL","CHN","CXR","CCK","COL","COM","COD","COG","COK","CRI","CIV","HRV","CUB","CUW","CYP","CZE","DNK","DJI","DMA","DOM","ECU","EGY","SLV","GNQ","ERI","EST","SWZ","ETH","FLK","FRO","FJI","FIN","FRA","GUF","PYF","ATF","GAB","GMB","GEO","DEU","GHA","GIB","GRC","GRL","GRD","GLP","GUM","GTM","GGY","GIN","GNB","GUY","HTI","HMD","VAT","HND","HKG","HUN","ISL","IND","IDN","IRN","IRQ","IRL","IMN","ISR","ITA","JAM","JPN","JEY","JOR","KAZ","KEN","KIR","PRK","KOR","KWT","KGZ","LAO","LVA","LBN","LSO","LBR","LBY","LIE","LTU","LUX","MAC","MDG","MWI","MYS","MDV","MLI","MLT","MHL","MTQ","MRT","MUS","MYT","MEX","FSM","MDA","MCO","MNG","MNE","MSR","MAR","MOZ","MMR","NAM","NRU","NPL","NLD","NCL","NZL","NIC","NER","NGA","NIU","NFK","MKD","MNP","NOR","OMN","PAK","PLW","PSE","PAN","PNG","PRY","PER","PHL","PCN","POL","PRT","PRI","QAT","REU","ROU","RUS","RWA","BLM","SHN","KNA","LCA","MAF","SPM","VCT","WSM","SMR","STP","SAU","SEN","SRB","SYC","SLE","SGP","SXM","SVK","SVN","SLB","SOM","ZAF","SGS","SSD","ESP","LKA","SDN","SUR","SJM","SWE","CHE","SYR","TWN","TJK","TZA","THA","TLS","TGO","TKL","TON","TTO","TUN","TUR","TKM","TCA","TUV","UGA","UKR","ARE","GBR","USA","UMI","URY","UZB","VUT","VEN","VNM","VGB","VIR","WLF","ESH","YEM","ZMB","ZWE","UTO"
}

class FieldCandidate(BaseModel):
    value: str
    confidence: float
    bbox: List[int]
    evidence: Dict[str, float]
    score_visual_only: float
    mrz_match: bool

def distance(b1, b2):
    c1x, c1y = (b1[0] + b1[2]) / 2, (b1[1] + b1[3]) / 2
    c2x, c2y = (b2[0] + b2[2]) / 2, (b2[1] + b2[3]) / 2
    return math.hypot(c1x - c2x, c1y - c2y)

def is_below_or_right(l_bbox, v_bbox):
    l_x1, l_y1, l_x2, l_y2 = l_bbox
    v_x1, v_y1, v_x2, v_y2 = v_bbox
    l_cx, l_cy = (l_x1 + l_x2) / 2, (l_y1 + l_y2) / 2
    v_cx, v_cy = (v_x1 + v_x2) / 2, (v_y1 + v_y2) / 2
    
    y_overlap = min(l_y2, v_y2) - max(l_y1, v_y1)
    x_overlap = min(l_x2, v_x2) - max(l_x1, v_x1)
    
    is_right = (v_cx > l_cx) and (y_overlap > -(l_y2-l_y1)*0.5)
    is_below = (v_cy > l_cy) and (x_overlap > -(l_x2-l_x1)*0.5)
    return is_right or is_below

def find_labels(detections, label_regex):
    return [d for d in detections if re.search(label_regex, d.text, re.IGNORECASE)]

def normalize_visual_date(val_text):
    m = re.search(r'(\d{2,4})[\s/.-]*([A-Za-z]{3}|\d{2})[\s/.-]*(\d{2,4})', val_text)
    if not m: return None
    p1, p2, p3 = m.groups()
    if len(p1) == 4: # YYYY MM DD
        return f"{p3.zfill(2)}/{p2}/{p1}".upper()
    else: # DD MM YYYY
        return f"{p1.zfill(2)}/{p2}/{p3.zfill(4) if len(p3)<4 else p3}".upper()

def normalize_for_compare(val):
    if not val: return ""
    return re.sub(r'[^A-Z0-9]', '', str(val).upper())

def check_date_match(visual_text, mrz_date):
    if not mrz_date: return False
    vis_norm = normalize_for_compare(normalize_visual_date(visual_text) or visual_text)
    mrz_norm = normalize_for_compare(mrz_date)
    day_v, yr_v = vis_norm[:2], vis_norm[-4:] if len(vis_norm) >= 4 else ""
    day_m, yr_m = mrz_norm[:2], mrz_norm[-4:] if len(mrz_norm) >= 4 else ""
    return (day_v == day_m) and (yr_v == yr_m) and bool(day_v) and bool(yr_v)

def name_overlap(visual_text, mrz_name):
    if not mrz_name: return 0.0
    v_parts = [normalize_for_compare(p) for p in visual_text.split() if p]
    m_parts = [normalize_for_compare(p) for p in mrz_name.split() if p]
    if not v_parts or not m_parts: return 0.0
    match_count = sum(1 for vp in v_parts if any(vp in mp or mp in vp for mp in m_parts))
    return float(match_count) / max(len(v_parts), len(m_parts))

def score_candidates(detections, doc_max_dim, format_regex, label_regex, mrz_value, is_date=False, is_name=False, require_evidence=False):
    candidates = []
    labels = find_labels(detections, label_regex)
    
    for d in detections:
        val_text = d.text.strip()
        evidence = {}
        
        # 1. Reject MRZ fragments
        if re.search(r'<.*<', val_text): continue
        if len(val_text.replace('<', '')) > 20 and '<' in val_text: continue
            
        # 2. Reject known labels
        label_pattern = r'^(?:NAME|FULL NAME|FATHER[\W_]*S?[\W_]*NAME|SURNAME|GIVEN NAME(?:S)?|DOB|DATE OF BIRTH|DATE OF ISSUE|DATE OF EXPIRY|ISSUE DATE|EXPIRY DATE|PASSPORT NO|DOCUMENT NO|PASSPORT NUMBER|TYPE|SEX(?: \/ GENRE)?|GENDER(?:E)?|NATIONALITY|COUNTRY(?: CODE)?)\s*[:;]?$'
        if not is_name and re.match(label_pattern, val_text, re.IGNORECASE): continue
        if is_name and re.match(label_pattern, val_text, re.IGNORECASE): continue
            
        # 3. Format check
        format_score = 0.0
        match_val = val_text
        inline_match = None
        
        if is_name:
            inline_match = re.search(r'^(?:NAME|FULL NAME|FATHER[\W_]*S?[\W_]*NAME|SURNAME|GIVEN NAME(?:S)?)\s*[:;]?\s*(.+)$', val_text, re.IGNORECASE)
            if inline_match:
                match_val = inline_match.group(1).strip()
                format_score = 0.9
            elif len(val_text) > 2 and re.match(r'^[A-Z\s]+$', val_text, re.IGNORECASE):
                format_score = 0.8
            else:
                continue
        elif format_regex:
            inline_match = re.search(r'^(?:DOB|DATE OF BIRTH|DATE OF ISSUE|DATE OF EXPIRY|ISSUE DATE|EXPIRY DATE|PASSPORT NO|DOCUMENT NO|PASSPORT NUMBER|TYPE|SEX(?: \/ GENRE)?|GENDER(?:E)?|NATIONALITY|COUNTRY(?: CODE)?)\s*[:;]?\s*(.+)$', val_text, re.IGNORECASE)
            if inline_match:
                m2 = re.search(format_regex, inline_match.group(1), re.IGNORECASE)
                if m2:
                    format_score = 0.9
                    match_val = m2.group(1) if m2.groups() else m2.group(0)
                else:
                    m = re.search(format_regex, val_text, re.IGNORECASE)
                    if m:
                        format_score = 1.0
                        match_val = m.group(1) if m.groups() else m.group(0)
                    else:
                        continue
            else:
                m = re.search(format_regex, val_text, re.IGNORECASE)
                if m:
                    format_score = 1.0
                    match_val = m.group(1) if m.groups() else m.group(0)
                else:
                    continue
        else:
            format_score = 0.5
                
        # 4. MRZ match
        mrz_match = False
        if mrz_value:
            if is_date:
                mrz_match = check_date_match(match_val, mrz_value)
            elif is_name:
                mrz_match = name_overlap(match_val, mrz_value) > 0.5
            else:
                v_norm = normalize_for_compare(match_val)
                m_norm = normalize_for_compare(mrz_value)
                mrz_match = bool(v_norm and m_norm and (m_norm == v_norm or m_norm in v_norm or v_norm in m_norm))
                
        # 5. Spatial label proximity
        spatial_score = 0.0
        min_dist = float('inf')
        for l in labels:
            if l.bbox == d.bbox: continue
            if is_below_or_right(l.bbox, d.bbox):
                dist = distance(l.bbox, d.bbox)
                if dist < min_dist:
                    min_dist = dist
                    
        if min_dist < float('inf') and doc_max_dim > 0:
            norm_dist = min_dist / doc_max_dim
            spatial_score = max(0.0, 1.0 - (norm_dist * 2.0))
            
        evidence['format'] = format_score
        evidence['spatial'] = spatial_score
        evidence['ocr'] = d.confidence
        if inline_match: evidence['inline_label'] = 1.0
        
        score_visual = (format_score * 0.4) + (spatial_score * 0.4) + (d.confidence * 0.2)
        if inline_match: score_visual += 0.5
        
        # 6. Require evidence
        if require_evidence and (spatial_score < 0.1 and not inline_match and not mrz_match):
            continue
            
        if is_date:
            match_val = normalize_visual_date(match_val) or match_val
            
        candidates.append(FieldCandidate(
            value=match_val,
            confidence=d.confidence,
            bbox=d.bbox,
            evidence=evidence,
            score_visual_only=score_visual,
            mrz_match=mrz_match
        ))
        
    candidates.sort(key=lambda x: (x.score_visual_only + (0.5 if x.mrz_match else 0.0)), reverse=True)
    return candidates

def resolve_field(candidates, mrz_value, visual_threshold=0.65):
    provenance = {
        "visual_value": None,
        "visual_confidence": 0.0,
        "visual_evidence": {},
        "mrz_value": mrz_value,
        "final_value": None,
        "final_source": None
    }
    
    best_vis = None
    if candidates:
        c = candidates[0]
        # Accept if high visual score, OR if it matches MRZ and has a weak visual score
        if c.score_visual_only >= visual_threshold or (c.mrz_match and c.score_visual_only >= 0.3):
            best_vis = c
        
    if best_vis:
        provenance["visual_value"] = best_vis.value
        provenance["visual_confidence"] = best_vis.confidence
        provenance["visual_evidence"] = best_vis.evidence
        
        if mrz_value:
            if best_vis.mrz_match:
                provenance["final_value"] = best_vis.value
                provenance["final_source"] = "visual_and_mrz"
            else:
                provenance["final_value"] = best_vis.value
                provenance["final_source"] = "visual_only_conflict"
        else:
            provenance["final_value"] = best_vis.value
            provenance["final_source"] = "visual_only"
    else:
        if mrz_value:
            provenance["final_value"] = mrz_value
            provenance["final_source"] = "mrz_fallback"
        else:
            provenance["final_value"] = None
            provenance["final_source"] = "not_assessed"
            
    return provenance["final_value"], provenance

def resolve_name(fullname_cands, surname_cands, given_cands, mrz_name):
    provenance = {
        "visual_value": None,
        "visual_confidence": 0.0,
        "visual_evidence": {},
        "mrz_value": mrz_name,
        "final_value": None,
        "final_source": None
    }
    
    def check(c):
        return c if c and (c.score_visual_only >= 0.65 or (c.mrz_match and c.score_visual_only >= 0.3)) else None
        
    fn = check(fullname_cands[0] if fullname_cands else None)
    sn = check(surname_cands[0] if surname_cands else None)
    gn = check(given_cands[0] if given_cands else None)
    
    if fn:
        provenance['visual_value'] = fn.value
        provenance['visual_evidence'] = fn.evidence
    elif sn and gn:
        provenance['visual_value'] = f"{gn.value} {sn.value}".strip()
    elif sn:
        provenance['visual_value'] = sn.value
    elif gn:
        provenance['visual_value'] = gn.value
        
    if provenance['visual_value']:
        provenance['final_value'] = provenance['visual_value']
        if ((fn and fn.mrz_match) or (sn and sn.mrz_match) or (gn and gn.mrz_match)):
            provenance['final_source'] = "visual_and_mrz"
        elif mrz_name:
            provenance['final_source'] = "visual_only_conflict"
        else:
            provenance['final_source'] = "visual_only"
    elif mrz_name:
        provenance['final_value'] = mrz_name
        provenance['final_source'] = "mrz_fallback"
    else:
        provenance['final_source'] = "not_assessed"
        
    return provenance['final_value'], provenance

def extract_passport_fields_v2(detections: List[OCRDetection]) -> OCRExtractedFields:
    fields = OCRExtractedFields()
    fields.provenance = {}
    valid_detections = [d for d in detections if d.confidence > 0.5 and d.bbox != [0,0,0,0]]
    
    doc_max_dim = 1.0
    if valid_detections:
        max_x = max(d.bbox[2] for d in valid_detections)
        max_y = max(d.bbox[3] for d in valid_detections)
        doc_max_dim = max(max_x, max_y, 1.0)
    
    mrz_lines = extract_mrz_lines(detections)
    mrz_data = parse_mrz(mrz_lines) if mrz_lines else None
        
    date_regex = r'(\d{2,4}[\s/.-]*(?:[A-Za-z]{3}|\d{2})[\s/.-]*\d{2,4})'
    
    # DOB
    dob_cands = score_candidates(valid_detections, doc_max_dim, date_regex, r'^(?:DATE OF BIRTH|DOB)\s*[:;]?$', getattr(mrz_data, 'date_of_birth', None), is_date=True)
    fields.date_of_birth, fields.provenance['date_of_birth'] = resolve_field(dob_cands, getattr(mrz_data, 'date_of_birth', None))
        
    # Issue Date (MRZ has no issue date)
    issue_cands = score_candidates(valid_detections, doc_max_dim, date_regex, r'^(?:DATE OF ISSUE|ISSUE DATE)\s*[:;]?$', None, is_date=True)
    issue_cands = [c for c in issue_cands if c.value != fields.date_of_birth]
    fields.issue_date, fields.provenance['issue_date'] = resolve_field(issue_cands, None)
            
    # Expiry Date
    exp_cands = score_candidates(valid_detections, doc_max_dim, date_regex, r'^(?:DATE OF EXPIRY|EXPIRY DATE)\s*[:;]?$', getattr(mrz_data, 'expiry_date', None), is_date=True)
    exp_cands = [c for c in exp_cands if c.value != fields.date_of_birth and c.value != fields.issue_date]
    fields.expiry_date, fields.provenance['expiry_date'] = resolve_field(exp_cands, getattr(mrz_data, 'expiry_date', None))
            
    # Gender
    mrz_sex = getattr(mrz_data, 'sex', None)
    gen_cands = score_candidates(valid_detections, doc_max_dim, r'\b(M|F|MALE|FEMALE|X)\b', r'^(?:SEX(?: \/ GENRE)?|GENDER(?:E)?)\s*[:;]?$', mrz_sex)
    raw_gen, fields.provenance['gender'] = resolve_field(gen_cands, mrz_sex)
    if raw_gen:
        fields.gender = "M" if raw_gen.upper().startswith("M") else ("F" if raw_gen.upper().startswith("F") else "X")
        
    # Passport Number
    mrz_ppt = getattr(mrz_data, 'passport_number', None)
    ppt_cands = score_candidates(valid_detections, doc_max_dim, r'([A-Z0-9]{6,12})', r'^(?:PASSPORT NO|DOCUMENT NO|DOC NO|PASSPORT NUMBER)\s*[:;]?$', mrz_ppt, require_evidence=True)
    ppt_cands = [c for c in ppt_cands if not re.match(date_regex, c.value)]
    fields.passport_number, fields.provenance['passport_number'] = resolve_field(ppt_cands, mrz_ppt)
            
    # Nationality
    mrz_nat = getattr(mrz_data, 'nationality', None)
    nat_cands = score_candidates(valid_detections, doc_max_dim, r'([A-Z]{3})', r'^(?:NATIONALITY|COUNTRY(?: CODE)?)\s*[:;]?$', mrz_nat)
    nat_cands = [c for c in nat_cands if c.value in VALID_ALPHA3_CODES]
    fields.nationality, fields.provenance['nationality'] = resolve_field(nat_cands, mrz_nat)
            
    # Name
    mrz_name = getattr(mrz_data, 'name', None)
    fullname_cands = score_candidates(valid_detections, doc_max_dim, r'^[A-Z\s]+$', r'^(?:NAME|FULL NAME)\s*[:;]?$', mrz_name, is_name=True)
    surname_cands = score_candidates(valid_detections, doc_max_dim, r'^[A-Z\s]+$', r'^(?:SURNAME)\s*[:;]?$', mrz_name, is_name=True)
    given_cands = score_candidates(valid_detections, doc_max_dim, r'^[A-Z\s]+$', r'^(?:GIVEN NAME(?:S)?)\s*[:;]?$', mrz_name, is_name=True)
    
    fields.name, fields.provenance['name'] = resolve_name(fullname_cands, surname_cands, given_cands, mrz_name)
        
    # Fathers Name
    father_cands = score_candidates(valid_detections, doc_max_dim, r'^[A-Z\s]+$', r'^FATHER[\W_]*S?[\W_]*NAME\s*[:;]?$', None, is_name=True)
    fields.fathers_name, fields.provenance['fathers_name'] = resolve_field(father_cands, None)

    return fields
