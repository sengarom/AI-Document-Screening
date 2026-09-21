"use client";

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { UploadCloud, File as FileIcon, AlertCircle, Loader2, Camera } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { apiService } from '@/services/api';
import { setTemporaryReferenceFile } from '@/lib/store';

export default function ScreenPage() {
  const router = useRouter();
  
  const [documentType, setDocumentType] = useState<string>('');
  
  const [docDragActive, setDocDragActive] = useState(false);
  const [docFile, setDocFile] = useState<File | null>(null);
  const docInputRef = useRef<HTMLInputElement>(null);
  
  const [refDragActive, setRefDragActive] = useState(false);
  const [refFile, setRefFile] = useState<File | null>(null);
  const refInputRef = useRef<HTMLInputElement>(null);

  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const validateFile = (file: File) => {
    const validTypes = ['image/jpeg', 'image/png', 'application/pdf'];
    if (!validTypes.includes(file.type)) {
      setError("Unsupported format. Please upload JPG, PNG, or PDF.");
      return false;
    }
    if (file.size > 10 * 1024 * 1024) {
      setError("File is too large. Maximum size is 10MB.");
      return false;
    }
    return true;
  };

  const validateImage = (file: File) => {
    const validTypes = ['image/jpeg', 'image/png'];
    if (!validTypes.includes(file.type)) {
      setError("Unsupported format. Please upload JPG or PNG for selfies.");
      return false;
    }
    if (file.size > 10 * 1024 * 1024) {
      setError("File is too large. Maximum size is 10MB.");
      return false;
    }
    return true;
  };

  const handleDocDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDocDragActive(false);
    setError(null);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      if (validateFile(e.dataTransfer.files[0])) setDocFile(e.dataTransfer.files[0]);
    }
  };

  const handleRefDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setRefDragActive(false);
    setError(null);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      if (validateImage(e.dataTransfer.files[0])) setRefFile(e.dataTransfer.files[0]);
    }
  };

  const handleContinue = async () => {
    if (!documentType) {
        setError("Please select a document type.");
        return;
    }
    if (!docFile) return;
    
    setError(null);
    setIsUploading(true);
    
    try {
      const response = await apiService.uploadDocument(docFile, documentType);
      
      sessionStorage.setItem('currentDocumentId', response.document_id);
      sessionStorage.setItem('currentDocumentType', documentType);
      
      if (refFile) {
        setTemporaryReferenceFile(refFile);
      }
      
      router.push('/screen/analyze');
    } catch (err: any) {
      setError(err.message || "Failed to upload document.");
      setIsUploading(false);
    }
  };

  const docTypes = ['Passport', 'Visa', 'PAN Card', 'Aadhaar Card'];

  return (
    <div className="max-w-4xl mx-auto pt-32 pb-20 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-100">Identity Verification</h1>
        <p className="text-slate-400 mt-2">Upload identity documents for automated verification</p>
      </div>

      <div className="space-y-6">
        <Card className="p-6">
            <h3 className="text-sm font-semibold text-slate-100 uppercase tracking-wider mb-4">1. Select Document Type</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {docTypes.map((type) => (
                    <button
                        key={type}
                        onClick={() => setDocumentType(type)}
                        className={cn(
                            "px-4 py-3 rounded-lg border-2 text-sm font-medium transition-colors",
                            documentType === type 
                                ? "border-blue-500 bg-blue-900/30 text-blue-300" 
                                : "border-slate-700 text-slate-400 hover:border-slate-500 hover:bg-slate-800"
                        )}
                    >
                        {type}
                    </button>
                ))}
            </div>
        </Card>
      
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className={cn(
            "p-8 transition-colors text-center border-2 border-dashed",
            docDragActive ? "border-blue-500 bg-blue-900/20" : "border-slate-700",
            docFile ? "border-slate-600 bg-slate-800/50" : ""
          )}
          onDragOver={(e) => { e.preventDefault(); setDocDragActive(true); }}
          onDragLeave={() => setDocDragActive(false)}
          onDrop={handleDocDrop}>
            <input
              ref={docInputRef}
              type="file"
              className="hidden"
              accept=".jpg,.jpeg,.png,.pdf"
              onChange={(e) => {
                setError(null);
                if (e.target.files?.[0] && validateFile(e.target.files[0])) setDocFile(e.target.files[0]);
              }}
            />
            
            <AnimatePresence mode="wait">
              {!docFile ? (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-4">
                  <div className="w-16 h-16 mx-auto rounded-full bg-slate-800 flex items-center justify-center">
                    <UploadCloud className="w-8 h-8 text-slate-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-slate-100">2. Upload Document</h3>
                    <p className="text-sm text-slate-400 mt-1">Drag and drop or click to browse</p>
                  </div>
                  <Button variant="outline" onClick={() => docInputRef.current?.click()}>
                    Browse Files
                  </Button>
                </motion.div>
              ) : (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
                  <div className="w-16 h-16 mx-auto rounded-full bg-emerald-900/30 flex items-center justify-center">
                    <FileIcon className="w-8 h-8 text-emerald-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-slate-100">{docFile.name}</h3>
                    <p className="text-sm text-slate-400 mt-1">{(docFile.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
                  <Button variant="outline" onClick={() => setDocFile(null)}>Remove</Button>
                </motion.div>
              )}
            </AnimatePresence>
          </Card>

          <Card className={cn(
            "p-8 transition-colors text-center border-2 border-dashed",
            refDragActive ? "border-blue-500 bg-blue-900/20" : "border-slate-700",
            refFile ? "border-slate-600 bg-slate-800/50" : ""
          )}
          onDragOver={(e) => { e.preventDefault(); setRefDragActive(true); }}
          onDragLeave={() => setRefDragActive(false)}
          onDrop={handleRefDrop}>
            <input
              ref={refInputRef}
              type="file"
              className="hidden"
              accept=".jpg,.jpeg,.png"
              onChange={(e) => {
                setError(null);
                if (e.target.files?.[0] && validateImage(e.target.files[0])) setRefFile(e.target.files[0]);
              }}
            />
            
            <AnimatePresence mode="wait">
              {!refFile ? (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-4">
                  <div className="w-16 h-16 mx-auto rounded-full bg-slate-800 flex items-center justify-center">
                    <Camera className="w-8 h-8 text-slate-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-slate-100">3. Reference Selfie (Optional)</h3>
                    <p className="text-sm text-slate-400 mt-1">Upload for Face Verification</p>
                  </div>
                  <Button variant="outline" onClick={() => refInputRef.current?.click()}>
                    Browse Image
                  </Button>
                </motion.div>
              ) : (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
                  <div className="w-16 h-16 mx-auto rounded-full bg-emerald-900/30 flex items-center justify-center">
                    <Camera className="w-8 h-8 text-emerald-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-slate-100">{refFile.name}</h3>
                    <p className="text-sm text-slate-400 mt-1">{(refFile.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
                  <Button variant="outline" onClick={() => setRefFile(null)}>Remove</Button>
                </motion.div>
              )}
            </AnimatePresence>
          </Card>
        </div>
      </div>

      {error && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-6 p-4 rounded-lg bg-red-900/30 text-red-400 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p className="text-sm font-medium">{error}</p>
        </motion.div>
      )}

      <div className="mt-8 flex justify-end">
        <Button 
          size="lg" 
          onClick={handleContinue} 
          disabled={!docFile || !documentType || isUploading}
        >
          {isUploading ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Uploading...
            </>
          ) : (
            'Continue to Analysis'
          )}
        </Button>
      </div>
    </div>
  );
}

