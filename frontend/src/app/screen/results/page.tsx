"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ShieldCheck, AlertCircle, Check, X, User, Minus, AlertTriangle, Cpu, FileText, ScanLine, ScanText, ShieldAlert } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { motion } from 'framer-motion';
import { cn, formatCaseId } from '@/lib/utils';
import { ScreeningReport } from '@/types';
import { apiService } from '@/services/api';

export default function ResultsPage() {
  const router = useRouter();
  const [report, setReport] = useState<ScreeningReport | null>(null);
  const [identityLinks, setIdentityLinks] = useState<any>(null);
  const [loadingLinks, setLoadingLinks] = useState(false);

  useEffect(() => {
    if (report && !identityLinks && !loadingLinks) {
      setLoadingLinks(true);
      apiService.getIdentityLinks(report.id)
        .then(data => setIdentityLinks(data))
        .catch(err => setIdentityLinks({ error: true }))
        .finally(() => setLoadingLinks(false));
    }
  }, [report, identityLinks, loadingLinks]);

  useEffect(() => {
    const stored = sessionStorage.getItem('screeningReport');
    if (!stored) {
      router.push('/screen');
      return;
    }
    setReport(JSON.parse(stored));
  }, [router]);

  if (!report) {
    return <div className="min-h-screen pt-32 text-center text-muted-foreground flex items-center justify-center">Loading screening results...</div>;
  }

  const isHighRisk = report.status === 'HIGH RISK';
  const isReview = report.status === 'REVIEW REQUIRED';
  const isClear = report.status === 'CLEAR';

  const generateFlags = () => {
    const flags = [];
    if (!report.validation.isValid) {
      flags.push("Document validation failed or returned anomalies.");
    }
    if (!report.documentType.includes('PAN') && !report.documentType.includes('Aadhaar') && !report.mrz.isValid) {
      flags.push("MRZ checksum validation failed or data was missing.");
    }
    if (!report.tampering.isAuthentic) {
      flags.push("Tampering indicators require review.");
    }
    if (report.face.status !== 'NOT_PERFORMED' && !report.face.isMatch) {
      flags.push("Face verification requires review.");
    }
    if (identityLinks && (identityLinks.status === 'potential_match' || identityLinks.status === 'multiple_potential_matches')) {
      flags.push("Potential identity link detected.");
    }
    return flags;
  };

  const flags = generateFlags();

  return (
    <div className="container mx-auto px-4 pt-28 pb-20 max-w-5xl">
      {/* 1. CASE / DOCUMENT HEADER */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4 border-b border-border pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Screening Result</h1>
          <p className="text-muted-foreground mt-1 font-mono text-sm uppercase">CASE: {formatCaseId(report.id)} • {new Date(report.date).toLocaleString()}</p>
        </div>
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={() => router.push('/screen')}>New Verification</Button>
        </div>
      </div>

      <div className="space-y-6">
        {/* 2. OVERALL SCREENING RESULT */}
        <Card className={cn("border", isClear ? "border-success/50 bg-success/5" : isHighRisk ? "border-destructive/50 bg-destructive/5" : "border-warning/50 bg-warning/5")}>
          <CardContent className="p-6 md:p-8 flex flex-col md:flex-row items-center gap-8">
            <div className="relative w-32 h-32 flex items-center justify-center shrink-0">
              <svg className="w-full h-full transform -rotate-90">
                <circle cx="64" cy="64" r="56" fill="transparent" stroke="var(--border)" strokeWidth="10" />
                <motion.circle 
                  initial={{ strokeDasharray: "0 351" }}
                  animate={{ strokeDasharray: `${(100 - report.risk.score) * 3.51} 351` }}
                  transition={{ duration: 1.5, ease: "easeOut" }}
                  cx="64" cy="64" r="56" fill="transparent" stroke={isClear ? "var(--success)" : isHighRisk ? "var(--destructive)" : "var(--warning)"} strokeWidth="10" strokeLinecap="round" 
                />
              </svg>
              <div className="absolute flex flex-col items-center">
                <span className="text-3xl font-bold text-foreground">{report.risk.score}</span>
                <span className="text-[10px] text-muted-foreground font-mono uppercase tracking-widest">/ 100</span>
              </div>
            </div>
            
            <div className="flex-1 text-center md:text-left space-y-2">
              <div className="flex items-center justify-center md:justify-start gap-3 mb-2">
                <Badge variant={isClear ? 'success' : isHighRisk ? 'destructive' : 'warning'} className="text-base px-4 py-1.5 font-bold uppercase tracking-widest text-white shadow-lg">
                  {report.status}
                </Badge>
              </div>
              <h3 className="text-xl font-semibold text-foreground">
                {isClear ? "Identity verified successfully" : "Further review recommended"}
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed max-w-lg">
                This risk assessment is based on multiple deterministic forensic and validation signals. {isClear ? "No significant anomalies were detected during the screening pipeline." : "The pipeline detected anomalies requiring manual verification."}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* 3. WHY WAS THIS FLAGGED? */}
        {!isClear && flags.length > 0 && (
          <Card className="border-destructive/30 bg-card">
            <CardHeader className="pb-3 border-b border-border/50 bg-destructive/5">
              <CardTitle className="text-lg flex items-center gap-2 text-destructive">
                <AlertTriangle className="w-5 h-5" />
                WHY WAS THIS FLAGGED?
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <ul className="space-y-3">
                {flags.map((flag, idx) => (
                  <li key={idx} className="flex items-start gap-3">
                    <div className="w-1.5 h-1.5 rounded-full bg-destructive mt-2 shrink-0"></div>
                    <span className="text-foreground text-sm font-medium">{flag}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {isClear && flags.length === 0 && (
          <Card className="border-success/30 bg-card">
             <CardContent className="p-4 flex items-center gap-3">
               <ShieldCheck className="w-5 h-5 text-success" />
               <span className="text-sm text-foreground font-medium">All verification checks passed. No anomalies detected.</span>
             </CardContent>
          </Card>
        )}

        {/* 4. EVIDENCE OVERVIEW (PIPELINE) */}
        <div className="py-4">
          <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-widest mb-6">Evidence Overview</h3>
          <div className="grid grid-cols-2 md:grid-cols-6 gap-2">
             <div className="flex flex-col items-center gap-2 text-center p-3 rounded-md bg-muted/20 border border-border">
               <FileText className="w-5 h-5 text-primary" />
               <span className="text-[10px] font-mono uppercase text-muted-foreground">Document</span>
               <Check className="w-4 h-4 text-success" />
             </div>
             <div className="flex flex-col items-center gap-2 text-center p-3 rounded-md bg-muted/20 border border-border">
               <ScanText className="w-5 h-5 text-primary" />
               <span className="text-[10px] font-mono uppercase text-muted-foreground">OCR</span>
               <Check className="w-4 h-4 text-success" />
             </div>
             <div className="flex flex-col items-center gap-2 text-center p-3 rounded-md bg-muted/20 border border-border">
               <ShieldCheck className="w-5 h-5 text-primary" />
               <span className="text-[10px] font-mono uppercase text-muted-foreground">Validation</span>
               {report.validation.isValid ? <Check className="w-4 h-4 text-success" /> : <X className="w-4 h-4 text-destructive" />}
             </div>
             <div className="flex flex-col items-center gap-2 text-center p-3 rounded-md bg-muted/20 border border-border">
               <ShieldAlert className="w-5 h-5 text-primary" />
               <span className="text-[10px] font-mono uppercase text-muted-foreground">Forensics</span>
               {report.tampering.isAuthentic ? <Check className="w-4 h-4 text-success" /> : <AlertTriangle className="w-4 h-4 text-warning" />}
             </div>
             <div className="flex flex-col items-center gap-2 text-center p-3 rounded-md bg-muted/20 border border-border">
               <User className="w-5 h-5 text-primary" />
               <span className="text-[10px] font-mono uppercase text-muted-foreground">Face</span>
               {report.face.status === 'NOT_PERFORMED' ? <Minus className="w-4 h-4 text-muted-foreground" /> : report.face.isMatch ? <Check className="w-4 h-4 text-success" /> : <AlertTriangle className="w-4 h-4 text-warning" />}
             </div>
             <div className="flex flex-col items-center gap-2 text-center p-3 rounded-md bg-muted/20 border border-border">
               <Cpu className="w-5 h-5 text-primary" />
               <span className="text-[10px] font-mono uppercase text-muted-foreground">Links</span>
               {loadingLinks ? <div className="w-4 h-4 rounded-full border-2 border-primary border-t-transparent animate-spin" /> : 
                 (identityLinks && (identityLinks.status === 'potential_match' || identityLinks.status === 'multiple_potential_matches')) ? 
                 <AlertTriangle className="w-4 h-4 text-warning" /> : <Check className="w-4 h-4 text-success" />
               }
             </div>
          </div>
        </div>

        {/* 5. DOCUMENT INFORMATION & 6. OCR */}
        <Card>
          <CardHeader className="border-b border-border bg-muted/10 pb-4">
             <CardTitle className="text-lg flex items-center justify-between">
               <span>OCR Extraction & Document Data</span>
               <Badge variant="outline">{report.documentType}</Badge>
             </CardTitle>
             <CardDescription>Extracted with {report.ocr.confidence}% overall confidence.</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
             <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-border">
               {report.ocr.extractedData.map((field: any, i: number) => (
                  <div key={i} className="flex justify-between items-center p-4 border-b border-border/50">
                    <span className="text-sm text-muted-foreground">{field.label}</span>
                    <span className="text-sm font-semibold font-mono">{field.value}</span>
                  </div>
               ))}
             </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 7. VALIDATION */}
          <Card>
            <CardHeader className="border-b border-border bg-muted/10 pb-4">
              <CardTitle className="text-base flex items-center justify-between">
                <span>Document Validation</span>
                {report.validation.isValid ? <Badge variant="success">PASS</Badge> : <Badge variant="destructive">FAIL</Badge>}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Logically valid dates</span>
                {report.validation.checks.datesValid === 'NOT_ASSESSED' ? <Minus className="w-4 h-4 text-muted-foreground" /> : report.validation.checks.datesValid ? <Check className="w-4 h-4 text-success"/> : <X className="w-4 h-4 text-destructive"/>}
              </div>
              {!report.documentType.includes('PAN') && !report.documentType.includes('Aadhaar') && (
                <>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">MRZ checksums</span>
                    {report.mrz.checksumPassed ? <Check className="w-4 h-4 text-success"/> : <X className="w-4 h-4 text-destructive"/>}
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Visual & MRZ consistency</span>
                    {report.validation.checks.visualMrzConsistency === 'NOT_ASSESSED' ? <Minus className="w-4 h-4 text-muted-foreground" /> : report.validation.checks.visualMrzConsistency ? <Check className="w-4 h-4 text-success"/> : <X className="w-4 h-4 text-destructive"/>}
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* 8. TAMPERING */}
          <Card>
            <CardHeader className="border-b border-border bg-muted/10 pb-4">
              <CardTitle className="text-base flex items-center justify-between">
                <span>Tampering Analysis</span>
                {report.tampering.isAuthentic ? <Badge variant="success">PASS</Badge> : <Badge variant="warning">REVIEW</Badge>}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Authenticity Score</span>
                <span className="font-mono text-sm">{100 - report.tampering.tamperingScore}%</span>
              </div>
              <div className="text-sm">
                {report.tampering.isAuthentic ? (
                   <span className="text-success">No significant tampering evidence detected.</span>
                ) : (
                   <span className="text-warning">Anomalies detected requiring manual review.</span>
                )}
              </div>
              {report.tampering.anomalies.length > 0 && (
                 <ul className="text-xs text-muted-foreground list-disc pl-4 space-y-1">
                   {report.tampering.anomalies.map((anom, i) => <li key={i}>{anom}</li>)}
                 </ul>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 9. FACE VERIFICATION */}
          <Card>
            <CardHeader className="border-b border-border bg-muted/10 pb-4">
              <CardTitle className="text-base flex items-center justify-between">
                <span>Face Verification</span>
                {report.face.status === 'NOT_PERFORMED' ? <Badge variant="outline">N/A</Badge> : report.face.isMatch ? <Badge variant="success">MATCH</Badge> : <Badge variant="warning">REVIEW</Badge>}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4">
              {report.face.status === 'NOT_PERFORMED' ? (
                 <p className="text-sm text-muted-foreground">Face verification was not performed for this document.</p>
              ) : (
                 <div className="space-y-4">
                   <div className="flex items-center justify-between">
                     <span className="text-sm text-muted-foreground">Similarity Score</span>
                                          <span className="font-mono text-sm">{report.face.matchScore}%</span>
                   </div>
                   <p className="text-sm text-foreground">
                      {report.face.status === 'MATCH' && "The reference face matched the face detected in the document."}
                      {report.face.status === 'NO_MATCH' && "The reference face did not match the face detected in the document."}
                      {report.face.status === 'NO_FACE_DOCUMENT' && "No face was detected in the document."}
                      {report.face.status === 'MULTIPLE_FACES_DOCUMENT' && "Multiple faces were detected in the document."}
                      {report.face.status === 'NO_FACE_REFERENCE' && "No face was detected in the reference image."}
                      {report.face.status === 'MULTIPLE_FACES_REFERENCE' && "Multiple faces were detected in the reference image."}
                      {report.face.status === 'QUALITY_FAILURE' && "Face image quality is too low for verification."}
                      {report.face.status === 'ERROR' && "An error occurred during face verification."}
                   </p>
                 </div>
              )}
            </CardContent>
          </Card>

          {/* 10. IDENTITY LINK ANALYSIS */}
          <Card>
            <CardHeader className="border-b border-border bg-muted/10 pb-4">
              <CardTitle className="text-base flex items-center justify-between">
                <span>Identity Link Analysis</span>
                {loadingLinks ? <Badge variant="outline">LOADING</Badge> : (identityLinks && (identityLinks.status === 'potential_match' || identityLinks.status === 'multiple_potential_matches')) ? <Badge variant="warning">REVIEW</Badge> : <Badge variant="success">PASS</Badge>}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4">
              {loadingLinks ? (
                <div className="text-sm text-muted-foreground animate-pulse">Analyzing historical records...</div>
              ) : identityLinks ? (
                <div className="space-y-4">
                  {(identityLinks.status === 'not_assessed' || identityLinks.status === 'no_face' || identityLinks.status === 'no_previous_identities' || identityLinks.status === 'error' || identityLinks.error) ? (
                    <p className="text-sm text-muted-foreground">{identityLinks.message || "Identity link analysis unavailable."}</p>
                  ) : identityLinks.status === 'no_match' ? (
                    <p className="text-sm text-success">No potential identity links found in authorized historical records.</p>
                  ) : (
                    <div>
                      <p className="text-sm text-warning font-medium mb-3">
                        {identityLinks.status === 'potential_match' ? "Potential identity link detected — review recommended" : "Multiple potential identity links detected"}
                      </p>
                      
                      <div className="space-y-2 max-h-32 overflow-y-auto">
                        {identityLinks.matches.map((match: any, idx: number) => (
                          <div key={idx} className="flex justify-between items-center p-2 bg-muted/20 border border-border rounded">
                            <div>
                              <div className="text-xs font-medium font-mono">{match.document_id}</div>
                            </div>
                            <Badge variant="warning" className="text-[10px]">SIM: {(match.similarity * 100).toFixed(1)}%</Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="pt-2 border-t border-border/50 mt-4">
                    <p className="text-[10px] text-muted-foreground leading-tight italic">
                      Face similarity exceeded the configured review threshold against a previous authorized verification case. This signal does not establish that the identities are the same person or that fraud occurred.
                    </p>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Unable to retrieve identity links.</p>
              )}
            </CardContent>
          </Card>
        </div>

      </div>
    </div>
  );
}
