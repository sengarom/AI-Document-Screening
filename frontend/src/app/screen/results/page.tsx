"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ShieldCheck, AlertCircle, Check, X, User, Minus } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { ScreeningReport } from '@/types';

export default function ResultsPage() {
  const router = useRouter();
  const [report, setReport] = useState<ScreeningReport | null>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem('screeningReport');
    if (!stored) {
      router.push('/screen');
      return;
    }
    setReport(JSON.parse(stored));
  }, [router]);

  if (!report) {
    return <div className="min-h-screen pt-32 text-center">Loading results...</div>;
  }

  const renderCheck = (status: boolean | 'NOT_ASSESSED') => {
    if (status === 'NOT_ASSESSED') return <Minus className="w-4 h-4 text-muted-foreground" />;
    return status ? <Check className="w-4 h-4 text-success" /> : <X className="w-4 h-4 text-destructive" />;
  };

  return (
    <div className="container mx-auto px-4 pt-32 pb-20 max-w-6xl">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold">Screening Report</h1>
          <p className="text-muted-foreground mt-1">ID: {report.id} • {new Date(report.date).toLocaleString()}</p>
        </div>
        <div className="flex items-center gap-4">
          <Badge variant={
            report.status === 'CLEAR' ? 'success' : 
            report.status === 'REVIEW REQUIRED' ? 'warning' : 'destructive'
          } className="text-sm px-3 py-1 text-white">
            {report.status}
          </Badge>
          <Button variant="outline" onClick={() => router.push('/screen')}>New Screening</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* LEFT: Overview & Risk */}
        <div className="md:col-span-1 space-y-6">
          <Card>
            <CardHeader className="pb-4">
              <CardTitle>Screening Risk Score</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center justify-center py-6">
                <div className="relative w-40 h-40 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle cx="80" cy="80" r="70" fill="transparent" stroke="var(--border)" strokeWidth="12" />
                    <motion.circle 
                      initial={{ strokeDasharray: "0 440" }}
                      animate={{ strokeDasharray: `${(100 - report.risk.score) * 4.4} 440` }}
                      transition={{ duration: 1.5, ease: "easeOut" }}
                      cx="80" cy="80" r="70" fill="transparent" stroke={report.status === 'CLEAR' ? "var(--success)" : "var(--destructive)"} strokeWidth="12" strokeLinecap="round" 
                    />
                  </svg>
                  <div className="absolute flex flex-col items-center">
                    <span className="text-4xl font-bold">{report.risk.score}</span>
                    <span className="text-xs text-muted-foreground font-mono">/ 100</span>
                  </div>
                </div>
                <div className="mt-4 text-center">
                  <Badge variant={report.status === 'CLEAR' ? 'success' : 'destructive'}>
                    {report.risk.level} RISK
                  </Badge>
                </div>
              </div>
              
              <div className="space-y-3 mt-4 border-t border-border pt-4">
                 <div className="flex justify-between items-center text-sm">
                   <span className="text-muted-foreground flex items-center gap-2">
                     {report.validation.isValid ? <Check className="w-4 h-4 text-success"/> : <X className="w-4 h-4 text-destructive"/>}
                     Document Valid
                   </span>
                 </div>
{!report.documentType.includes('PAN') && !report.documentType.includes('Aadhaar') && (<div className="flex justify-between items-center text-sm"><span className="text-muted-foreground flex items-center gap-2">{report.mrz.isValid ? <Check className="w-4 h-4 text-success"/> : <X className="w-4 h-4 text-destructive"/>}MRZ Detected</span></div>)}
                 <div className="flex justify-between items-center text-sm">
                   <span className="text-muted-foreground flex items-center gap-2">
                     {report.tampering.isAuthentic ? <Check className="w-4 h-4 text-success"/> : <X className="w-4 h-4 text-destructive"/>}
                     No Tampering Evidence
                   </span>
                 </div>
                 <div className="flex justify-between items-center text-sm">
                   <span className="text-muted-foreground flex items-center gap-2">
                     {report.face.status === 'NOT_PERFORMED' ? (
                       <X className="w-4 h-4 text-muted-foreground"/>
                     ) : report.face.isMatch ? (
                       <Check className="w-4 h-4 text-success"/>
                     ) : (
                       <X className="w-4 h-4 text-destructive"/>
                     )}
                     {report.face.status === 'NOT_PERFORMED' ? 'Face Verification Not Performed' : 'Face Verification Performed'}
                   </span>
                 </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* RIGHT: Detailed Breakdown */}
        <div className="md:col-span-2 space-y-6">
           <Card>
             <CardHeader className="border-b border-border bg-card/50">
               <CardTitle>Identity Extraction</CardTitle>
               <CardDescription>OCR data extracted with {report.ocr.confidence}% overall confidence.</CardDescription>
             </CardHeader>
             <CardContent className="p-0">
               <div className="divide-y divide-border">
                  {report.ocr.extractedData.map((field: any, i: number) => (
                    <div key={i} className="flex justify-between items-center p-4 hover:bg-muted/30 transition-colors">
                      <span className="text-sm font-medium text-muted-foreground">{field.label}</span>
                      <span className="text-sm font-bold font-mono">{field.value}</span>
                    </div>
                  ))}
               </div>
             </CardContent>
           </Card>

           <Card>
             <CardHeader className="border-b border-border bg-card/50">
               <CardTitle>Validation & Forensics</CardTitle>
             </CardHeader>
             <CardContent className="p-6 space-y-6">
                <div>
                  <h4 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wider">Document Validation</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                      <div className="flex items-center gap-2">
                        {renderCheck(report.validation.checks.datesValid)}
                        <span className={report.validation.checks.datesValid === 'NOT_ASSESSED' ? 'text-muted-foreground' : ''}>Dates are logically valid</span>
                      </div>
{!report.documentType.includes('PAN') && !report.documentType.includes('Aadhaar') && (<><div className="flex items-center gap-2">{report.mrz.checksumPassed ? <Check className="w-4 h-4 text-success"/> : <X className="w-4 h-4 text-destructive"/>}MRZ checksums passed</div><div className="flex items-center gap-2">{renderCheck(report.validation.checks.visualMrzConsistency)}<span className={report.validation.checks.visualMrzConsistency === 'NOT_ASSESSED' ? 'text-muted-foreground' : ''}>Visual & MRZ data matches</span></div></>)}
                  </div>
                </div>
                
                <div className="pt-4 border-t border-border">
                  <h4 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wider">Tampering Analysis</h4>
                  <div className="flex items-center gap-4">
                    <div className={cn("p-3 rounded-full", report.tampering.isAuthentic ? "bg-success/10 text-success" : "bg-destructive/10 text-destructive")}>
                      {report.tampering.isAuthentic ? <ShieldCheck className="w-6 h-6" /> : <AlertCircle className="w-6 h-6" />}
                    </div>
                    <div>
                      <p className="font-medium">
                        {report.tampering.isAuthentic ? "No significant tampering evidence detected" : "Tampering evidence detected"}
                      </p>
                      <p className="text-sm text-muted-foreground">Tampering Evidence Score: {report.tampering.tamperingScore}%</p>
                    </div>
                  </div>
                  {report.tampering.anomalies.length > 0 && (
                     <div className="mt-4 bg-muted/50 p-4 rounded text-sm text-muted-foreground">
                        <ul className="list-disc pl-4 space-y-1">
                          {report.tampering.anomalies.map((anom, i) => (
                            <li key={i}>{anom}</li>
                          ))}
                        </ul>
                     </div>
                  )}
                </div>
                
                {/* Face Verification Section */}
                <div className="pt-4 border-t border-border">
                  <h4 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wider">Face Verification</h4>
                  {report.face.status === 'NOT_PERFORMED' ? (
                     <div className="text-sm text-muted-foreground">
                       Face Verification Not Performed
                     </div>
                  ) : (
                     <div className="flex items-center gap-4">
                        <div className={cn("p-3 rounded-full", report.face.isMatch ? "bg-success/10 text-success" : "bg-destructive/10 text-destructive")}>
                          <User className="w-6 h-6" />
                        </div>
                        <div>
                          <p className="font-medium">
                            {report.face.status === 'MATCH' && "Face Match"}
                            {report.face.status === 'NO_MATCH' && "No Face Match"}
                            {report.face.status === 'NO_FACE_DOCUMENT' && "No Face Detected in Document"}
                            {report.face.status === 'MULTIPLE_FACES_DOCUMENT' && "Multiple Faces Detected in Document"}
                            {report.face.status === 'NO_FACE_REFERENCE' && "No Face Detected in Reference Image"}
                            {report.face.status === 'MULTIPLE_FACES_REFERENCE' && "Multiple Faces Detected in Reference Image"}
                            {report.face.status === 'QUALITY_FAILURE' && "Face Image Quality Failure"}
                            {report.face.status === 'ERROR' && "Face Verification Error"}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {report.face.status === 'MATCH' && "The reference face matched the face detected in the document."}
                            {report.face.status === 'NO_MATCH' && "The reference face did not match the face detected in the document."}
                            {(report.face.status === 'MATCH' || report.face.status === 'NO_MATCH') && (
                               <span className="block mt-1">Similarity score: {report.face.matchScore}%</span>
                            )}
                          </p>
                        </div>
                     </div>
                  )}
                </div>

             </CardContent>
           </Card>
        </div>

      </div>
    </div>
  );
}

