export type DocumentType = 'Passport' | 'Visa' | 'PAN Card' | 'Aadhaar Card' | 'Unknown Document';

export interface ExtractedField {
  label: string;
  value: string;
  confidence: number;
}

export interface OCRResult {
  confidence: number;
  fieldsDetected: number;
  totalFields: number;
  extractedData: ExtractedField[];
}

export interface ValidationResult {
  isValid: boolean;
  checks: {
    requiredFieldsDetected: boolean;
    datesValid: boolean | 'NOT_ASSESSED';
    documentNumberValid: boolean;
    mrzValid: boolean;
    visualMrzConsistency: boolean | 'NOT_ASSESSED';
  };
}

export interface MRZResult {
  isValid: boolean;
  checksumPassed: boolean;
  mrzString: string;
}

export interface TamperingResult {
  isAuthentic: boolean;
  tamperingScore: number;
  anomalies: string[];
}

export interface FaceVerificationResult {
  faceDetected: boolean;
  singleFaceDetected: boolean;
  matchScore: number;
  isMatch: boolean;
  status: 'MATCH' | 'NO_MATCH' | 'NO_FACE_DOCUMENT' | 'MULTIPLE_FACES_DOCUMENT' | 'NO_FACE_REFERENCE' | 'MULTIPLE_FACES_REFERENCE' | 'QUALITY_FAILURE' | 'ERROR' | 'NOT_PERFORMED';
}

export interface RiskScore {
  score: number; // 0 - 100
  level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
}

export interface ScreeningReport {
  id: string;
  date: string;
  documentType: DocumentType;
  status: 'CLEAR' | 'REVIEW REQUIRED' | 'HIGH RISK';
  ocr: OCRResult;
  validation: ValidationResult;
  mrz: MRZResult;
  tampering: TamperingResult;
  face: FaceVerificationResult;
  risk: RiskScore;
}

