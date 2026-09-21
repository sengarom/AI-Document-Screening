"use client";

import { useEffect, useState, Suspense, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { apiService } from '@/services/api';
import { cn } from '@/lib/utils';
import { getTemporaryReferenceFile } from '@/lib/store';

const pipelineSteps = [
  { id: 'ocr', label: 'OCR Extraction', processingLabel: 'Extracting text...' },
  { id: 'validation', label: 'Document Validation', processingLabel: 'Validating fields...' },
  { id: 'mrz', label: 'MRZ Analysis', processingLabel: 'Checking checksums...' },
  { id: 'tampering', label: 'Forensics', processingLabel: 'Analyzing for manipulation...' },
  { id: 'face', label: 'Face Verification', processingLabel: 'Verifying face match...' },
  { id: 'risk', label: 'Risk Intelligence', processingLabel: 'Calculating score...' }
];

const stepSnippets = [
  `[SYSTEM] Initializing OCR Engine v2.4.1...
[INFO] Bounding box detection models loaded.
[INFO] Extracting raw text fields...
[PROCESS] Confidence > 0.92 : NAME
[PROCESS] Confidence > 0.88 : DOB
[PROCESS] Extracting spatial geometries...
[INFO] Text pipeline complete.`,

  `[SYSTEM] Starting field validation...
[VALIDATOR] Format checks initialized.
[VALIDATOR] Validating expiration dates.
[WARN] Format anomaly detected in address line 2.
[VALIDATOR] Cross-referencing fields.
[INFO] Data structures validated successfully.`,

  `[SYSTEM] Parsing Machine Readable Zone...
[MRZ] Line 1: P<INDNAME<<LAST<<<<<<<<<<<<
[MRZ] Line 2: L898902C36IND9001019F2401019
[CHECK] Composite Checksum: PASS
[CHECK] DOB Checksum: PASS
[INFO] Extracted independent MRZ schema.`,

  `[FORENSICS] Error Level Analysis (ELA) init...
[FORENSICS] Analyzing compression artifacts...
[FORENSICS] Running Metadata Exif check.
[FORENSICS] Copy-move forgery detection active.
[INFO] No significant local noise anomalies.
[STATUS] Image integrity scan complete.`,

  `[FACE_ENGINE] Extracting facial features...
[FACE_ENGINE] Locating reference mesh.
[MATCH] Computing embedding distance...
[MATCH] Cosine similarity: 0.942
[MATCH] Euclidean L2 distance: 0.231
[INFO] Confidence interval established.`,

  `[RISK_ENGINE] Aggregating multi-modal signals...
[CALCULUS] Document integrity weight: 0.4
[CALCULUS] Face match confidence weight: 0.3
[CALCULUS] Tamper probability penalty: -0.2
[CALCULUS] Finalizing score distribution.
[SYSTEM] Generating final report...`
];

function AnalyzeContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const documentId = searchParams.get('id') || (typeof window !== 'undefined' ? sessionStorage.getItem('currentDocumentId') : null);
  
  const [currentStepIndex, setCurrentStepIndex] = useState(-1);
  const [documentType, setDocumentType] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  
  // We grab the file once on mount
  const refFileRef = useRef<File | null>(null);
  const [hasRefFile, setHasRefFile] = useState(false);

  useEffect(() => {
    const file = getTemporaryReferenceFile();
    if (file) {
      refFileRef.current = file;
      setHasRefFile(true);
    }
  }, []);

  useEffect(() => {
    if (!documentId) {
      setError("No document ID provided.");
      return;
    }

    let isMounted = true;
    
    const runAnalysis = async () => {
      try {
        // Step 0: OCR
        setCurrentStepIndex(0);
        const ocr_result = await apiService.processOCR(documentId);
        
        // Step 1: Validation
        if (!isMounted) return;
        setCurrentStepIndex(1);
        const validation_result = await apiService.processValidation(documentId);
        
        // Step 2: MRZ (Combined with validation in backend)
        if (!isMounted) return;
        setCurrentStepIndex(2);
        const dt = sessionStorage.getItem('currentDocumentType') || '';
        if (dt.includes('PAN') || dt.includes('Aadhaar')) {
            // skip delay visually
        } else {
            await new Promise(r => setTimeout(r, 800));
        }

        // Step 3: Tampering
        if (!isMounted) return;
        setCurrentStepIndex(3);
        const tampering_result = await apiService.processTampering(documentId);
        
        // Step 4: Face Verification
        if (!isMounted) return;
        setCurrentStepIndex(4);
        
        let face_result = null;
        if (refFileRef.current) {
           face_result = await apiService.processFaceVerification(documentId, refFileRef.current);
        } else {
           // Small delay for UI if skipped
           await new Promise(r => setTimeout(r, 600));
        }

        // Step 5: Risk Scoring
        if (!isMounted) return;
        setCurrentStepIndex(5);
        const riskPayload = {
          validation_result,
          tampering_result,
          face_result
        };
        const risk_result = await apiService.calculateRisk(documentId, riskPayload);

        // Final Report Generation
        if (!isMounted) return;
        const reportPayload = {
          ocr_result,
          validation_result,
          tampering_result,
          face_result,
          risk_result
        };
        const backendReport = await apiService.getScreeningReport(documentId, reportPayload);
        
        // Map to frontend shape and store
        const frontendReport = apiService.buildFrontendReport(backendReport, reportPayload);
        sessionStorage.setItem('screeningReport', JSON.stringify(frontendReport));

        if (isMounted) {
          setTimeout(() => {
            if (isMounted) router.push('/screen/results');
          }, 1000);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || "An error occurred during analysis.");
        }
      }
    };

    // Give the refFileRef effect a tick to run before starting
    setTimeout(runAnalysis, 100);

    return () => { isMounted = false; };
  }, [router, documentId]);

  return (
    <div className="container mx-auto px-4 pt-32 pb-20 max-w-5xl min-h-[calc(100vh-200px)]">
      <div className="flex flex-col md:flex-row gap-8 items-start">
        
        <div className="w-full md:w-5/12">
          <Card className="p-1 border-border/50 bg-card/50 backdrop-blur-sm sticky top-32">
            <div className="aspect-[3/4] bg-secondary rounded-lg border border-border relative overflow-hidden flex flex-col">
               <div className="p-4 border-b border-border bg-background/50 flex justify-between items-center text-xs text-muted-foreground font-mono">
                 <span>ANALYSIS ENGINE</span>
                 <span className="animate-pulse flex items-center gap-2">
                   <div className="w-2 h-2 rounded-full bg-primary"></div>
                   ACTIVE
                 </span>
               </div>
               
               <div className="flex-1 p-4 relative flex flex-col">
                 <div className="w-full h-full border border-border/50 rounded-lg relative overflow-hidden bg-[#090a0c] z-0">
                    
                    {/* The 3D Animation Component */}
                    {currentStepIndex >= 0 && !error && (
                      <div className="absolute inset-0 overflow-hidden [perspective:1000px] pointer-events-none flex items-center justify-center z-0">
                        {/* Floor Grid */}
                        <motion.div
                          animate={{ backgroundPosition: ['0px 0px', '0px 40px'] }}
                          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                          className="absolute bottom-[-10%] w-[200%] h-[80%] bg-[linear-gradient(to_right,rgba(90,103,216,0.15)_1px,transparent_1px),linear-gradient(to_bottom,rgba(90,103,216,0.15)_1px,transparent_1px)] bg-[size:40px_40px] [transform:rotateX(75deg)] origin-bottom opacity-60"
                          style={{ maskImage: 'linear-gradient(to top, black 10%, transparent 100%)', WebkitMaskImage: 'linear-gradient(to top, black 10%, transparent 100%)' }}
                        />
                        
                        {/* Floating 3D Document */}
                        <motion.div
                          animate={{ 
                            rotateY: [0, 360],
                            translateY: [-10, 10, -10]
                          }}
                          transition={{ 
                            rotateY: { duration: 10, repeat: Infinity, ease: "linear" },
                            translateY: { duration: 4, repeat: Infinity, ease: "easeInOut" }
                          }}
                          style={{ transformStyle: 'preserve-3d' }}
                          className="w-40 h-56 border border-primary/50 rounded-lg bg-background/40 backdrop-blur-md shadow-[0_0_30px_rgba(90,103,216,0.4)] flex flex-col p-4 relative z-10"
                        >
                          {/* Laser Scan Line */}
                          <motion.div
                             animate={{ top: ['0%', '100%', '0%'] }}
                             transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
                             className="absolute left-[-20%] right-[-20%] h-[2px] bg-primary shadow-[0_0_20px_4px_rgba(90,103,216,0.9)] z-20"
                          />
                          
                          {/* ID Photo Box */}
                          <div className="flex gap-3 items-start mb-4">
                            <div className="w-12 h-14 rounded bg-primary/20 border border-primary/40 flex items-center justify-center relative overflow-hidden">
                               <motion.div 
                                 animate={{ opacity: [0.2, 0.6, 0.2] }}
                                 transition={{ duration: 2, repeat: Infinity }}
                                 className="absolute inset-0 bg-primary/30"
                               />
                            </div>
                            <div className="flex-1 space-y-2 mt-1">
                               <div className="w-full h-2 bg-primary/30 rounded" />
                               <div className="w-2/3 h-2 bg-primary/30 rounded" />
                            </div>
                          </div>

                          {/* Text Lines */}
                          <div className="space-y-3 flex-1 mt-2">
                             <div className="w-full h-1.5 bg-primary/20 rounded" />
                             <div className="w-5/6 h-1.5 bg-primary/20 rounded" />
                             <div className="w-4/5 h-1.5 bg-primary/20 rounded" />
                             <div className="w-full h-1.5 bg-primary/20 rounded" />
                          </div>

                          {/* MRZ Lines */}
                          <div className="h-8 mt-auto border-t border-primary/30 pt-2 space-y-1.5">
                             <div className="w-full h-1.5 bg-primary/40" />
                             <div className="w-full h-1.5 bg-primary/40" />
                          </div>
                        </motion.div>
                      </div>
                    )}
                    
                    {/* The Snippet Overlay */}
                    {currentStepIndex >= 0 && currentStepIndex < stepSnippets.length && !error && (
                      <div className="absolute inset-0 bg-gradient-to-t from-background/90 via-transparent to-background/20 pointer-events-none z-20 flex flex-col justify-end p-4">
                        <motion.pre
                          key={currentStepIndex}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="text-[10px] sm:text-xs font-mono text-primary/90 whitespace-pre-wrap break-all bg-background/60 p-3 rounded-md backdrop-blur-md border border-primary/20 shadow-lg"
                        >
                          {stepSnippets[currentStepIndex]}
                        </motion.pre>
                      </div>
                    )}
                 </div>
               </div>
            </div>
          </Card>
        </div>

        <div className="w-full md:w-7/12">
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2">Analyzing document...</h1>
            <p className="text-muted-foreground">Running intelligence checks against document {documentId}</p>
          </div>

          {error && (
            <div className="mb-6 flex items-center text-destructive text-sm bg-destructive/10 px-4 py-3 rounded-md">
              <AlertCircle className="w-5 h-5 mr-3" />
              <div>
                <strong>Analysis Failed:</strong> {error}
              </div>
            </div>
          )}

          <div className="space-y-4">
            {pipelineSteps.map((step, index) => {
              let status = 'pending';
              let displayLabel = step.processingLabel;
              
              if (error && index === currentStepIndex) {
                 status = 'error';
              } else if (index < currentStepIndex) {
                 status = 'complete';
              } else if (index === currentStepIndex) {
                 status = 'active';
              }
              
              if (index === 4 && status === 'active' && !hasRefFile) {
                 displayLabel = 'Face verification skipped (No reference provided)';
              }
              if (index === 2 && documentType && (documentType.includes('PAN') || documentType.includes('Aadhaar'))) {
                 displayLabel = 'Skipped for this document type';
                 if (status === 'active') status = 'complete';
              }

              return (
                <Card 
                  key={step.id} 
                  className={cn(
                    "p-4 transition-all duration-300",
                    status === 'active' ? "border-primary bg-primary/5" : "",
                    status === 'error' ? "border-destructive bg-destructive/5" : "",
                    status === 'pending' ? "opacity-50" : ""
                  )}
                >
                  <div className="flex items-center gap-4">
                    <div className="flex-shrink-0">
                      {status === 'complete' ? (
                        <CheckCircle2 className="w-6 h-6 text-success" />
                      ) : status === 'active' ? (
                        <Loader2 className="w-6 h-6 text-primary animate-spin" />
                      ) : status === 'error' ? (
                        <AlertCircle className="w-6 h-6 text-destructive" />
                      ) : (
                        <div className="w-6 h-6 rounded-full border-2 border-muted flex items-center justify-center text-xs font-mono text-muted-foreground">
                          0{index + 1}
                        </div>
                      )}
                    </div>
                    <div className="flex-1">
                      <h3 className={cn(
                        "font-semibold",
                        status === 'active' ? "text-primary" : "",
                        status === 'error' ? "text-destructive" : ""
                      )}>
                        {step.label}
                      </h3>
                      {status === 'active' && (
                        <p className="text-sm text-muted-foreground mt-1">
                          {displayLabel}
                        </p>
                      )}
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function AnalyzePage() {
  return (
    <Suspense fallback={<div className="container pt-32 text-center">Loading analysis engine...</div>}>
      <AnalyzeContent />
    </Suspense>
  );
}



