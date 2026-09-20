from app.schemas.ocr import OCRDetection
from app.services.ocr.passport_extractor import extract_passport_fields_v2

def test_adversarial_distractors():
    # Correct values mixed with distractors. NO MRZ fallback provided here, so visual must stand on its own based on labels.
    detections = [
        # Distractors (high confidence, valid formats, but wrong spatial/label contexts)
        OCRDetection(text="1999", confidence=0.99, bbox=[10, 10, 50, 20]),
        OCRDetection(text="01/01/2050", confidence=0.99, bbox=[10, 30, 80, 40]), # distractor date
        OCRDetection(text="USA", confidence=0.99, bbox=[100, 10, 130, 20]), # distractor nationality
        OCRDetection(text="GBR", confidence=0.99, bbox=[140, 10, 170, 20]), # distractor nationality
        OCRDetection(text="ABCDEFGH", confidence=0.99, bbox=[200, 10, 280, 20]), # distractor passport no
        OCRDetection(text="JOHN SMITH", confidence=0.99, bbox=[10, 50, 100, 60]), # distractor name
        
        # Actual labelled fields
        OCRDetection(text="NAME", confidence=0.99, bbox=[10, 100, 50, 110]),
        OCRDetection(text="ALICE MEHRA", confidence=0.99, bbox=[10, 120, 100, 130]),
        
        OCRDetection(text="DOB", confidence=0.99, bbox=[150, 100, 180, 110]),
        OCRDetection(text="01/01/1990", confidence=0.99, bbox=[150, 120, 220, 130]),
        
        OCRDetection(text="ISSUE DATE", confidence=0.99, bbox=[250, 100, 320, 110]),
        OCRDetection(text="01/01/2020", confidence=0.99, bbox=[250, 120, 320, 130]),
        
        OCRDetection(text="EXPIRY DATE", confidence=0.99, bbox=[10, 150, 90, 160]),
        OCRDetection(text="01/01/2030", confidence=0.99, bbox=[10, 170, 80, 180]),
        
        OCRDetection(text="NATIONALITY", confidence=0.99, bbox=[150, 150, 230, 160]),
        OCRDetection(text="IND", confidence=0.99, bbox=[150, 170, 180, 180]),
        
        OCRDetection(text="PASSPORT NO", confidence=0.99, bbox=[250, 150, 330, 160]),
        OCRDetection(text="P1234567", confidence=0.99, bbox=[250, 170, 320, 180]),
        
        OCRDetection(text="SEX", confidence=0.99, bbox=[10, 200, 40, 210]),
        OCRDetection(text="F", confidence=0.99, bbox=[10, 220, 20, 230]),
    ]
    
    fields = extract_passport_fields_v2(detections)
    
    assert fields.name == "ALICE MEHRA"
    assert fields.date_of_birth == "01/01/1990"
    assert fields.issue_date == "01/01/2020"
    assert fields.expiry_date == "01/01/2030"
    assert fields.nationality == "IND"
    assert fields.passport_number == "P1234567"
    assert fields.gender == "F"
    
    # All these should be visually extracted
    assert fields.provenance["name"]["final_source"] == "visual_only"
    assert fields.provenance["date_of_birth"]["final_source"] == "visual_only"
    assert fields.provenance["nationality"]["final_source"] == "visual_only"


def test_mrz_cross_validation_conflict():
    # Visual candidate = WRONGVALUE (but physically near the label)
    # MRZ value = CORRECTVALUE
    # We expect visual_only_conflict and final_value = WRONGVALUE because visual_only overrides MRZ fallback if visual is strong.
    detections = [
        OCRDetection(text="NAME", confidence=0.99, bbox=[10, 100, 50, 110]),
        OCRDetection(text="WRONGVALUE", confidence=0.99, bbox=[10, 120, 100, 130]), # High spatial, high format -> visual strong
        OCRDetection(text="P<INDCORRECTVALUE<<<<<<<<<<<<<<<<<<<<<<<<<<<", confidence=0.99, bbox=[10, 200, 400, 210]),
        OCRDetection(text="L898902C36IND9001019M2401019<<<<<<<<<<<<<<00", confidence=0.99, bbox=[10, 220, 400, 230]),
    ]
    fields = extract_passport_fields_v2(detections)
    assert fields.name == "WRONGVALUE"
    assert fields.provenance["name"]["final_source"] == "visual_only_conflict"
    assert fields.provenance["name"]["mrz_value"] == "CORRECTVALUE"
    
def test_mrz_cross_validation_agreement():
    # Visual candidate = CORRECTVALUE
    # MRZ value = CORRECTVALUE
    detections = [
        OCRDetection(text="NAME", confidence=0.99, bbox=[10, 100, 50, 110]),
        OCRDetection(text="CORRECTVALUE", confidence=0.99, bbox=[10, 120, 100, 130]), 
        OCRDetection(text="P<INDCORRECTVALUE<<<<<<<<<<<<<<<<<<<<<<<<<<<", confidence=0.99, bbox=[10, 200, 400, 210]),
        OCRDetection(text="L898902C36IND9001019M2401019<<<<<<<<<<<<<<00", confidence=0.99, bbox=[10, 220, 400, 230]),
    ]
    fields = extract_passport_fields_v2(detections)
    assert fields.name == "CORRECTVALUE"
    assert fields.provenance["name"]["final_source"] == "visual_and_mrz"

def test_missing_labels_not_assessed():
    # If labels are completely missing, AND there is no MRZ, dates/names should NOT be assigned randomly.
    detections = [
        OCRDetection(text="01/01/1990", confidence=0.99, bbox=[10, 30, 80, 40]),
        OCRDetection(text="01/01/2020", confidence=0.99, bbox=[100, 30, 180, 40]),
        OCRDetection(text="01/01/2030", confidence=0.99, bbox=[200, 30, 280, 40]),
        OCRDetection(text="ALICE", confidence=0.99, bbox=[10, 60, 50, 70]),
        OCRDetection(text="USA", confidence=0.99, bbox=[10, 90, 40, 100]),
    ]
    fields = extract_passport_fields_v2(detections)
    
    assert fields.date_of_birth is None
    assert fields.provenance["date_of_birth"]["final_source"] == "not_assessed"
    assert fields.issue_date is None
    assert fields.expiry_date is None
    assert fields.name is None
    assert fields.nationality is None

def test_name_concatenation_logic():
    # Surname + Given name in separate tokens WITH labels
    detections = [
        OCRDetection(text="SURNAME", confidence=0.99, bbox=[10, 10, 80, 20]),
        OCRDetection(text="THAPLIYAL", confidence=0.99, bbox=[10, 30, 100, 40]),
        OCRDetection(text="GIVEN NAME", confidence=0.99, bbox=[150, 10, 230, 20]),
        OCRDetection(text="GARIMA", confidence=0.99, bbox=[150, 30, 210, 40]),
    ]
    fields = extract_passport_fields_v2(detections)
    assert fields.name == "GARIMA THAPLIYAL"
    assert fields.provenance["name"]["final_source"] == "visual_only"
