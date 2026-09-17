import React from "react";
import { createRoot } from "react-dom/client";
import "./index.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
const SUPPORTED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"];

function App() {
  const [selectedFile, setSelectedFile] = React.useState(null);
  const [previewUrl, setPreviewUrl] = React.useState(null);
  const [isUploading, setIsUploading] = React.useState(false);
  const [uploadResult, setUploadResult] = React.useState(null);
  const [errorMessage, setErrorMessage] = React.useState(null);

  // OCR State
  const [isOcrRunning, setIsOcrRunning] = React.useState(false);
  const [ocrResult, setOcrResult] = React.useState(null);
  const [ocrError, setOcrError] = React.useState(null);

  // Validation State
  const [isValidating, setIsValidating] = React.useState(false);
  const [validationResult, setValidationResult] = React.useState(null);
  const [validationError, setValidationError] = React.useState(null);

  // Tampering State
  const [isTamperingRunning, setIsTamperingRunning] = React.useState(false);
  const [tamperingResult, setTamperingResult] = React.useState(null);
  const [tamperingError, setTamperingError] = React.useState(null);

  // Face Verification State
  const [referenceFile, setReferenceFile] = React.useState(null);
  const [referencePreviewUrl, setReferencePreviewUrl] = React.useState(null);
  const [isFaceVerifying, setIsFaceVerifying] = React.useState(false);
  const [faceResult, setFaceResult] = React.useState(null);
  const [faceError, setFaceError] = React.useState(null);

  function selectFile(event) {
    const file = event.target.files?.[0] ?? null;
    setUploadResult(null);
    setErrorMessage(null);
    setOcrResult(null);
    setOcrError(null);
    setValidationResult(null);
    setValidationError(null);
    setTamperingResult(null);
    setTamperingError(null);
    setFaceResult(null);
    setFaceError(null);
    setReferenceFile(null);
    if (referencePreviewUrl) URL.revokeObjectURL(referencePreviewUrl);
    setReferencePreviewUrl(null);
    setSelectedFile(file);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(file ? URL.createObjectURL(file) : null);
  }

  async function uploadDocument() {
    if (!selectedFile) {
      setErrorMessage("Choose a JPG, PNG, or WEBP image first.");
      return;
    }
    if (!SUPPORTED_IMAGE_TYPES.includes(selectedFile.type)) {
      setErrorMessage("Choose a JPG, PNG, or WEBP image.");
      return;
    }
    setIsUploading(true);
    setUploadResult(null);
    setErrorMessage(null);
    setValidationResult(null);
    setValidationError(null);
    setTamperingResult(null);
    setTamperingError(null);
    const formData = new FormData();
    formData.append("file", selectedFile);
    try {
      const response = await fetch(API_BASE_URL + "/api/documents/upload", {
        method: "POST",
        body: formData,
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail ?? "The upload could not be completed.");
      setUploadResult(payload);
    } catch (error) {
      setErrorMessage(
        error instanceof TypeError
          ? "Backend unavailable. Start the FastAPI server and try again."
          : error.message,
      );
    } finally {
      setIsUploading(false);
    }
  }

  async function runOCR() {
    if (!uploadResult?.document_id) return;

    setIsOcrRunning(true);
    setOcrResult(null);
    setOcrError(null);
    setValidationResult(null);
    setValidationError(null);
    setTamperingResult(null);
    setTamperingError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/documents/${uploadResult.document_id}/ocr`, {
        method: "POST",
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail ?? "OCR processing failed.");
      setOcrResult(payload);
    } catch (error) {
      setOcrError(error.message);
    } finally {
      setIsOcrRunning(false);
    }
  }

  async function runValidation() {
    if (!uploadResult?.document_id) return;

    setIsValidating(true);
    setValidationResult(null);
    setValidationError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/documents/${uploadResult.document_id}/validate`, {
        method: "POST",
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail ?? "Validation failed.");
      setValidationResult(payload);
    } catch (error) {
      setValidationError(error.message);
    } finally {
      setIsValidating(false);
    }
  }

  async function runTampering() {
    if (!uploadResult?.document_id) return;

    setIsTamperingRunning(true);
    setTamperingResult(null);
    setTamperingError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/documents/${uploadResult.document_id}/tampering`, {
        method: "POST",
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail ?? "Tampering detection failed.");
      setTamperingResult(payload);
    } catch (error) {
      setTamperingError(error.message);
    } finally {
      setIsTamperingRunning(false);
    }
  }

  function selectReferenceFile(event) {
    const file = event.target.files?.[0] ?? null;
    setFaceResult(null);
    setFaceError(null);
    setReferenceFile(file);
    if (referencePreviewUrl) URL.revokeObjectURL(referencePreviewUrl);
    setReferencePreviewUrl(file ? URL.createObjectURL(file) : null);
  }

  async function runFaceVerification() {
    if (!uploadResult?.document_id || !referenceFile) return;

    setIsFaceVerifying(true);
    setFaceResult(null);
    setFaceError(null);

    const formData = new FormData();
    formData.append("reference_image", referenceFile);

    try {
      const response = await fetch(`${API_BASE_URL}/api/documents/${uploadResult.document_id}/face-verification`, {
        method: "POST",
        body: formData,
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail ?? "Face verification failed.");
      setFaceResult(payload);
    } catch (error) {
      setFaceError(error.message);
    } finally {
      setIsFaceVerifying(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 px-5 py-12 text-slate-900">
      <section className="mx-auto max-w-2xl rounded-2xl bg-white p-7 shadow-sm ring-1 ring-slate-200">
        <p className="text-sm font-semibold tracking-wide text-blue-700">MODULE 1 & 2 · UPLOAD & OCR</p>
        <h1 className="mt-2 text-3xl font-bold">AI Document Screening System</h1>
        <p className="mt-3 text-slate-600">Upload only synthetic, public, or explicitly consented document images.</p>
        <label className="mt-7 block rounded-xl border-2 border-dashed border-slate-300 p-6 text-center hover:border-blue-500">
          <span className="block font-medium">Choose a document image</span>
          <span className="mt-1 block text-sm text-slate-500">JPG, PNG, or WEBP · maximum 10 MB</span>
          <input className="mt-4 block w-full text-sm" type="file" accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp" onChange={selectFile} />
        </label>
        {selectedFile && <p className="mt-4 text-sm">Selected: <strong>{selectedFile.name}</strong></p>}
        {previewUrl && <img className="mt-4 max-h-72 w-full rounded-lg object-contain ring-1 ring-slate-200" src={previewUrl} alt="Selected document preview" />}
        <button className="mt-5 w-full rounded-lg bg-blue-700 px-4 py-3 font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-400" type="button" disabled={!selectedFile || isUploading} onClick={uploadDocument}>
          {isUploading ? "Uploading and preprocessing…" : "Upload document"}
        </button>
        {errorMessage && <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700" role="alert">{errorMessage}</p>}
        {uploadResult && (
          <section className="mt-5 rounded-lg bg-emerald-50 p-4 text-sm text-emerald-950" aria-live="polite">
            <h2 className="font-bold">Upload complete</h2>
            <dl className="mt-2 grid grid-cols-2 gap-x-4 gap-y-2">
              <dt>Document ID</dt><dd className="break-all font-medium">{uploadResult.document_id}</dd>
              <dt>Stored filename</dt><dd className="break-all font-medium">{uploadResult.filename}</dd>
              <dt>Content type</dt><dd className="font-medium">{uploadResult.content_type}</dd>
              <dt>File size</dt><dd className="font-medium">{uploadResult.file_size} bytes</dd>
              <dt>Original size</dt><dd className="font-medium">{uploadResult.original_width} × {uploadResult.original_height}</dd>
              <dt>Processed size</dt><dd className="font-medium">{uploadResult.processed_width} × {uploadResult.processed_height}</dd>
              <dt>Status</dt><dd className="font-medium">{uploadResult.preprocessing_status}</dd>
            </dl>

            <div className="mt-6 border-t border-emerald-200 pt-4">
              <button
                className="w-full rounded-lg bg-indigo-600 px-4 py-3 font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-400"
                type="button"
                disabled={isOcrRunning}
                onClick={runOCR}
              >
                {isOcrRunning ? "Running OCR..." : "Run OCR"}
              </button>
            </div>

            {ocrError && <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700" role="alert">{ocrError}</p>}

            {ocrResult && (
              <div className="mt-6 rounded-lg bg-indigo-50 p-4 text-indigo-950">
                <h3 className="font-bold text-lg border-b border-indigo-200 pb-2 mb-3">OCR Results</h3>

                <div className="mb-4">
                  <span className="text-xs font-semibold uppercase text-indigo-700">Warning:</span>
                  <span className="text-sm ml-2">{ocrResult.authenticity_warning}</span>
                </div>

                <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm mb-4 bg-white p-3 rounded-md shadow-sm">
                  <dt className="text-slate-500">Engine</dt><dd className="font-medium">{ocrResult.engine}</dd>
                  <dt className="text-slate-500">Device</dt><dd className="font-medium uppercase">{ocrResult.device}</dd>
                </dl>

                <h4 className="font-semibold text-md mt-4 mb-2">Extracted Fields</h4>
                <div className="bg-white p-3 rounded-md shadow-sm mb-4">
                  {Object.entries(ocrResult.extracted_fields || {}).map(([key, value]) => (
                    <div key={key} className="flex border-b border-slate-100 last:border-0 py-1">
                      <span className="w-1/2 text-slate-500 capitalize">{key.replace(/_/g, ' ')}</span>
                      <span className="w-1/2 font-medium">{value || <span className="text-slate-300 italic">Not detected</span>}</span>
                    </div>
                  ))}
                </div>

                <h4 className="font-semibold text-md mt-4 mb-2">Raw Text Detections</h4>
                <div className="bg-white p-3 rounded-md shadow-sm max-h-48 overflow-y-auto text-xs font-mono">
                  {ocrResult.detections?.length > 0 ? (
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="border-b border-slate-200">
                          <th className="py-1">Text</th>
                          <th className="py-1 text-right">Confidence</th>
                        </tr>
                      </thead>
                      <tbody>
                        {ocrResult.detections.map((d, i) => (
                          <tr key={i} className="border-b border-slate-100 last:border-0">
                            <td className="py-1 pr-2">{d.text}</td>
                            <td className="py-1 text-right text-slate-500">{(d.confidence * 100).toFixed(1)}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="text-slate-500 italic">No text detected</p>
                  )}
                </div>
                
                <div className="mt-6 border-t border-indigo-200 pt-4">
                  <button
                    className="w-full rounded-lg bg-purple-600 px-4 py-3 font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-400"
                    type="button"
                    disabled={isValidating}
                    onClick={runValidation}
                  >
                    {isValidating ? "Validating Document..." : "Validate Document"}
                  </button>
                </div>
                
                {validationError && <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700" role="alert">{validationError}</p>}
                
                {validationResult && (
                  <div className="mt-6 rounded-lg bg-purple-50 p-4 text-purple-950">
                    <h3 className="font-bold text-lg border-b border-purple-200 pb-2 mb-3 flex items-center justify-between">
                      Validation Results
                      <span className={`px-2 py-1 text-xs font-bold uppercase rounded-md ${validationResult.valid ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'}`}>
                        {validationResult.status}
                      </span>
                    </h3>
                    
                    <div className="mb-4 text-sm font-medium">
                      Overall Valid: {validationResult.valid ? <span className="text-green-700">YES</span> : <span className="text-red-700">NO</span>}
                    </div>
                    
                    <h4 className="font-semibold text-md mb-2">Checks</h4>
                    <div className="bg-white p-3 rounded-md shadow-sm mb-4 space-y-2 max-h-64 overflow-y-auto">
                      {validationResult.checks?.map((check, i) => (
                        <div key={i} className={`p-2 rounded border text-sm ${check.status === 'passed' ? 'bg-green-50 border-green-200 text-green-900' : check.status === 'warning' ? 'bg-yellow-50 border-yellow-200 text-yellow-900' : 'bg-red-50 border-red-200 text-red-900'}`}>
                          <div className="flex justify-between font-semibold mb-1">
                            <span className="capitalize">{check.check.replace(/_/g, ' ')}</span>
                            <span className="uppercase text-xs">{check.status}</span>
                          </div>
                          <div className="text-xs">{check.message}</div>
                        </div>
                      ))}
                    </div>
                    
                    <div className="mt-6 border-t border-purple-200 pt-4">
                      <button
                        className="w-full rounded-lg bg-orange-600 px-4 py-3 font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-400"
                        type="button"
                        disabled={isTamperingRunning}
                        onClick={runTampering}
                      >
                        {isTamperingRunning ? "Running Tampering Detection..." : "Run Tampering Detection"}
                      </button>
                    </div>

                    {tamperingError && <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700" role="alert">{tamperingError}</p>}

                    {tamperingResult && (
                      <div className="mt-6 rounded-lg bg-orange-50 p-4 text-orange-950">
                        <h3 className="font-bold text-lg border-b border-orange-200 pb-2 mb-3 flex items-center justify-between">
                          Tampering Detection
                          <span className={`px-2 py-1 text-xs font-bold uppercase rounded-md ${tamperingResult.severity === 'LOW' ? 'bg-green-200 text-green-800' : tamperingResult.severity === 'MODERATE' ? 'bg-yellow-200 text-yellow-800' : 'bg-red-200 text-red-800'}`}>
                            {tamperingResult.severity} RISK
                          </span>
                        </h3>
                        
                        <div className="mb-4 text-sm font-medium flex items-center gap-4">
                          <div>Evidence Score: <span className="text-lg font-bold">{(tamperingResult.tampering_score * 100).toFixed(0)}</span>/100</div>
                          <div>Status: <span className="uppercase">{tamperingResult.overall_status}</span></div>
                        </div>

                        <div className="w-full bg-orange-200 rounded-full h-2.5 mb-6">
                          <div className={`h-2.5 rounded-full ${tamperingResult.tampering_score < 0.3 ? 'bg-green-600' : tamperingResult.tampering_score < 0.7 ? 'bg-yellow-500' : 'bg-red-600'}`} style={{ width: `${Math.min(100, Math.max(0, tamperingResult.tampering_score * 100))}%` }}></div>
                        </div>

                        <h4 className="font-semibold text-md mb-2">Forensic Signals</h4>
                        <div className="bg-white p-3 rounded-md shadow-sm space-y-2">
                          {Object.entries(tamperingResult.signals || {}).map(([key, signal]) => (
                            <div key={key} className={`p-2 rounded border text-sm ${signal.status === 'passed' ? 'bg-slate-50 border-slate-200' : signal.status === 'warning' ? 'bg-yellow-50 border-yellow-200' : 'bg-red-50 border-red-200'}`}>
                              <div className="flex justify-between font-semibold mb-1">
                                <span className="capitalize">{key.replace(/_/g, ' ')}</span>
                                <span className="text-xs">Score: {(signal.score * 100).toFixed(0)} (Conf: {(signal.confidence * 100).toFixed(0)}%)</span>
                              </div>
                              <div className="text-xs text-slate-700">{signal.explanation}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* MODULE 5 - FACE VERIFICATION TEMPORARY UI */}
            <div className="mt-8 border-t-2 border-slate-200 pt-6">
              <h3 className="text-xl font-bold text-slate-800 mb-2">MODULE 5 — FACE VERIFICATION</h3>
              <p className="text-sm text-slate-500 mb-4">Temporary Testing UI</p>
              
              <label className="block rounded-xl border-2 border-dashed border-slate-300 p-4 text-center hover:border-blue-500 bg-white">
                <span className="block font-medium">Choose Reference / Selfie Image</span>
                <input className="mt-2 block w-full text-sm" type="file" accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp" onChange={selectReferenceFile} />
              </label>
              
              {referencePreviewUrl && (
                <div className="mt-4">
                  <img className="max-h-48 rounded-lg object-contain ring-1 ring-slate-200 mx-auto" src={referencePreviewUrl} alt="Reference preview" />
                </div>
              )}
              
              <button 
                className="mt-4 w-full rounded-lg bg-teal-600 px-4 py-3 font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-400" 
                type="button" 
                disabled={!referenceFile || isFaceVerifying} 
                onClick={runFaceVerification}
              >
                {isFaceVerifying ? "Verifying..." : "RUN FACE VERIFICATION"}
              </button>

              {faceError && <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700" role="alert">{faceError}</p>}

              {faceResult && (
                <div className="mt-6 rounded-lg bg-slate-800 p-5 text-slate-100">
                  <h4 className="font-bold text-lg border-b border-slate-600 pb-2 mb-3">RESULT</h4>
                  <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                    <dt className="text-slate-400">Status:</dt>
                    <dd className="font-bold font-mono">{faceResult.status}</dd>
                    
                    <dt className="text-slate-400">Verified:</dt>
                    <dd className="font-medium">{faceResult.verified ? "true" : "false"}</dd>
                    
                    <dt className="text-slate-400">Similarity Score:</dt>
                    <dd className="font-medium">{faceResult.similarity_score?.toFixed(4) ?? "N/A"}</dd>
                    
                    <dt className="text-slate-400">Processing:</dt>
                    <dd className="font-medium">{faceResult.processing_time_ms} ms</dd>
                  </dl>
                  
                  <div className="mt-4 pt-3 border-t border-slate-600">
                    <p className="text-slate-400 text-xs mb-1">Message:</p>
                    <p className="text-sm font-medium">{faceResult.message}</p>
                  </div>
                  <p className="mt-3 text-xs text-slate-500 italic">Cosine similarity — not probability</p>
                </div>
              )}
            </div>
            
          </section>
        )}
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
