import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldAlert, X, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface ReportPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ReportPreviewModal({ isOpen, onClose }: ReportPreviewModalProps) {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleEsc);
    }
    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleEsc);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 md:p-12">
        <motion.div 
          initial={{ opacity: 0 }} 
          animate={{ opacity: 1 }} 
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0 bg-background/80 backdrop-blur-sm"
        />
        
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.95 }}
          className="relative w-full max-w-3xl bg-card border border-border shadow-2xl rounded-xl overflow-hidden flex flex-col max-h-[90vh]"
        >
          {/* Header */}
          <div className="flex justify-between items-center p-4 border-b border-border bg-muted/30">
            <div className="flex items-center gap-3">
              <ShieldAlert className="w-5 h-5 text-primary" />
              <h2 className="font-bold tracking-tight">VERIDEX SCREENING REPORT</h2>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-primary/20 text-primary uppercase tracking-wider">
                SIMULATED / DEMO
              </span>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-colors text-muted-foreground hover:text-foreground">
              <X className="w-5 h-5" />
            </button>
          </div>
          
          {/* Scrollable Content */}
          <div className="p-6 overflow-y-auto space-y-8 flex-1">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-xs text-muted-foreground mb-1">Case ID</p>
                <p className="font-mono font-medium">VRX-DEMO-0001</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-1">Document</p>
                <p className="font-medium">Passport</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-1">Status</p>
                <p className="font-medium text-warning flex items-center gap-1.5"><AlertTriangle className="w-4 h-4"/> REVIEW REQUIRED</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-1">Risk Score</p>
                <p className="font-medium font-mono text-warning">62 / 100</p>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-bold border-b border-border pb-2 mb-4 uppercase tracking-wider text-muted-foreground">Screening Signals</h3>
              <div className="grid gap-2 text-sm font-mono">
                <div className="flex justify-between items-center bg-muted/30 p-2 rounded"><span className="text-muted-foreground">DOCUMENT INGESTION</span><span className="text-success">COMPLETE</span></div>
                <div className="flex justify-between items-center bg-muted/30 p-2 rounded"><span className="text-muted-foreground">OCR EXTRACTION</span><span className="text-success">COMPLETE</span></div>
                <div className="flex justify-between items-center bg-muted/30 p-2 rounded"><span className="text-muted-foreground">DOCUMENT VALIDATION</span><span className="text-success">PASS</span></div>
                <div className="flex justify-between items-center bg-muted/30 p-2 rounded"><span className="text-muted-foreground">IMAGE FORENSICS</span><span className="text-warning">REVIEW</span></div>
                <div className="flex justify-between items-center bg-muted/30 p-2 rounded"><span className="text-muted-foreground">FACE VERIFICATION</span><span className="text-success">PASS</span></div>
                <div className="flex justify-between items-center bg-muted/30 p-2 rounded"><span className="text-muted-foreground">IDENTITY LINKS</span><span className="text-muted-foreground">NO MATCH</span></div>
                <div className="flex justify-between items-center bg-muted/30 p-2 rounded"><span className="text-muted-foreground">RISK ASSESSMENT</span><span className="text-warning">REVIEW</span></div>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-bold border-b border-border pb-2 mb-4 uppercase tracking-wider text-muted-foreground">Evidence Summary</h3>
              <div className="space-y-4 text-sm">
                <div><span className="font-medium">Document:</span> <span className="text-muted-foreground">Successfully ingested for screening.</span></div>
                <div><span className="font-medium">OCR:</span> <span className="text-muted-foreground">Identity fields extracted successfully.</span></div>
                <div><span className="font-medium">Validation:</span> <span className="text-muted-foreground">Structural and checksum validation completed.</span></div>
                <div><span className="font-medium">Forensics:</span> <span className="text-warning">Demo scenario contains image-forensic indicators requiring review.</span></div>
                <div><span className="font-medium">Face:</span> <span className="text-muted-foreground">Reference face comparison completed.</span></div>
                <div><span className="font-medium">Identity Links:</span> <span className="text-muted-foreground">No potential historical identity link detected.</span></div>
                <div><span className="font-medium">Risk:</span> <span className="text-warning">Combined screening signals result in REVIEW REQUIRED.</span></div>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-bold border-b border-border pb-2 mb-4 uppercase tracking-wider text-muted-foreground">Recommended Action</h3>
              <p className="font-bold text-lg text-warning">MANUAL REVIEW</p>
            </div>
            
            <div className="bg-muted/50 p-4 rounded-lg border border-border/50">
              <p className="text-xs text-muted-foreground text-center italic">
                This simulated report is for demonstration purposes and does not establish document authenticity, identity ownership, or fraud.
              </p>
            </div>
          </div>
          
          <div className="p-4 border-t border-border bg-muted/10 flex justify-end">
            <Button variant="outline" onClick={onClose}>Close</Button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
