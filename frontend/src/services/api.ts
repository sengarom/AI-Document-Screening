const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';
import { ScreeningReport } from '@/types';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let msg = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      if (body.detail) msg = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail);
    } catch (e) {}
    throw new ApiError(res.status, msg);
  }
  return res.json();
}

export const apiService = {
  async uploadDocument(file: File, documentType: string = 'PASSPORT'): Promise<{ document_id: string; filename: string }> {
    const formData = new FormData();
    formData.append('file', file);
    let backendType = 'PASSPORT';
    if (documentType.includes('PAN')) backendType = 'PAN';
    else if (documentType.includes('Aadhaar')) backendType = 'AADHAAR';
    else if (documentType.includes('Visa')) backendType = 'VISA';
    formData.append('document_type', backendType);
    const res = await fetch(`${API_BASE}/api/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(res);
  },

  async processOCR(documentId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/api/documents/${documentId}/ocr`, { method: 'POST' });
    return handleResponse(res);
  },

  async processValidation(documentId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/api/documents/${documentId}/validate`, { method: 'POST' });
    return handleResponse(res);
  },

  async processTampering(documentId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/api/documents/${documentId}/tampering`, { method: 'POST' });
    return handleResponse(res);
  },

  async processFaceVerification(documentId: string, referenceFile: File): Promise<any> {
    const formData = new FormData();
    formData.append('reference_image', referenceFile);
    const res = await fetch(`${API_BASE}/api/documents/${documentId}/face-verification`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(res);
  },

  async calculateRisk(documentId: string, payload: any): Promise<any> {
    const res = await fetch(`${API_BASE}/api/documents/${documentId}/risk-score`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse(res);
  },

  async getScreeningReport(documentId: string, payload: any): Promise<any> {
    const res = await fetch(`${API_BASE}/api/documents/${documentId}/screening-report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse(res);
  },

  buildFrontendReport(backendReport: any, payloads: any): ScreeningReport {
    const ocr = payloads.ocr_result;
    const val = payloads.validation_result;
    const tamp = payloads.tampering_result;
    const face = payloads.face_result;
    const risk = payloads.risk_result;
    
    let uiStatus: 'CLEAR' | 'REVIEW REQUIRED' | 'HIGH RISK' = 'REVIEW REQUIRED';
    if (backendReport.overall_status === 'clear') uiStatus = 'CLEAR';
    if (backendReport.overall_status === 'high_risk') uiStatus = 'HIGH RISK';

    // MRZ / Validation Checks Mapping
    const hasPassedCheck = (checkName: string) => {
      const c = val.checks.find((x: any) => x.check === checkName);
      return c ? c.status === 'passed' : false;
    };
    const hasAnyCheck = (checkNames: string[]) => {
      for (const cn of checkNames) {
         const c = val.checks.find((x: any) => x.check === cn);
         if (c && c.status === 'passed') return true;
      }
      return false;
    };

    const isMrzDetected = val.checks.find((x: any) => x.check === 'mrz_detected');
    const mrzValid = isMrzDetected ? isMrzDetected.status === 'passed' : false;
    const mrzChecksumsPassed = hasPassedCheck('mrz_composite_checksum');

    const checkExists = (checkName: string) => val.checks.find((x: any) => x.check === checkName);
    
    // Evaluate three-state logic: true (PASS), false (FAIL), or 'NOT_ASSESSED'
    const evaluateChecks = (checkNames: string[]) => {
      const statuses = checkNames.map(cn => checkExists(cn)?.status);
      if (statuses.every(s => s === undefined)) return 'NOT_ASSESSED';
      if (statuses.some(s => s === 'failed' || s === 'warning')) return false;
      return true;
    };

    const visualMrzConsistency = evaluateChecks(['visual_mrz_passport_number_match', 'visual_mrz_dob_match']);
    const datesValid = evaluateChecks(['date_of_birth_logic', 'issue_date_logic', 'expiry_date_logic']);
    
    let ocrConf = 0;
    if (ocr.detections && ocr.detections.length > 0) {
      ocrConf = ocr.detections.reduce((sum: number, d: any) => sum + d.confidence, 0) / ocr.detections.length;
    }

    const docInfo = backendReport.document_information || {};
    const docType = docInfo.document_type || "Unknown Document";
    
    let validKeys: string[] = [];
    if (docType === "PASSPORT") {
      validKeys = ["name", "passport_number", "nationality", "date_of_birth", "gender", "issue_date", "expiry_date", "fathers_name", "address"];
    } else if (docType === "PAN") {
      validKeys = ["name", "fathers_name", "date_of_birth", "pan_number"];
    } else if (docType === "AADHAAR") {
      validKeys = ["name", "date_of_birth", "year_of_birth", "gender", "aadhaar_number", "address"];
    } else {
      validKeys = Object.keys(docInfo).filter(k => k !== 'document_type');
    }

    const uiExtracted = Object.entries(docInfo)
      .filter(([k, v]) => validKeys.includes(k) && v !== null && v !== undefined && v !== "")
      .map(([k, v]: [string, any]) => ({
        label: k,
        value: String(v),
        confidence: Math.round(ocrConf * 100)
      }));

    // Tampering mapping
    const isAuthentic = tamp.overall_status === 'passed';
    const tamperingScore = tamp.tampering_score * 100;
    
    // Map suspicious regions and failed signals to anomalies
    const anomalies: string[] = [];
    if (tamp.suspicious_regions) {
       tamp.suspicious_regions.forEach((r: any) => anomalies.push(`Region anomaly (${r.type}) detected`));
    }
    if (tamp.signals) {
       Object.values(tamp.signals).forEach((s: any) => {
          if (s.status === 'failed') anomalies.push(s.explanation);
       });
    }

    return {
      id: backendReport.document_id,
      date: backendReport.timestamp,
      documentType: backendReport.document_information?.document_type || "Unknown Document",
      status: uiStatus,
      ocr: {
        confidence: Math.round(ocrConf * 100),
        fieldsDetected: uiExtracted.length,
        totalFields: validKeys.length,
        extractedData: uiExtracted
      },
      validation: {
        isValid: val.valid,
        checks: {
          requiredFieldsDetected: val.valid, // Simplified for UI
          datesValid: datesValid,
          documentNumberValid: hasPassedCheck('passport_number_format'),
          mrzValid: mrzValid,
          visualMrzConsistency: visualMrzConsistency
        }
      },
      mrz: {
        isValid: mrzValid,
        checksumPassed: mrzChecksumsPassed,
        mrzString: "" 
      },
      tampering: {
        isAuthentic: isAuthentic,
        tamperingScore: Math.round(tamperingScore),
        anomalies: anomalies
      },
      face: {
        faceDetected: face ? face.face_detected : false,
        singleFaceDetected: face ? face.single_face_detected : false,
        matchScore: face && face.match_score ? Math.round(face.match_score * 100) : 0,
        isMatch: face ? face.is_match : false,
        status: face ? face.status : 'NOT_PERFORMED'
      },
      risk: {
        score: risk.risk_score,
        level: risk.risk_level as any
      }
    };
  }
};

