"use client";

import { useRef, useState, useEffect } from 'react';
import { motion, } from 'framer-motion';

import { cn } from '@/lib/utils';
import { Upload, ScanText, Fingerprint, ShieldAlert, BadgeCheck, FileWarning, CheckCircle } from 'lucide-react';

const steps = [
  {
    id: 1,
    title: "Upload Document",
    description: "Securely upload identity documents. We support passports, national IDs, and driver's licenses from over 190 countries.",
    icon: Upload
  },
  {
    id: 2,
    title: "OCR Extraction",
    description: "Advanced optical character recognition extracts all textual fields instantly with 99.8% accuracy.",
    icon: ScanText
  },
  {
    id: 3,
    title: "Document Validation",
    description: "Multi-layered validation checks required fields, dates, document numbers, and checksums in the Machine Readable Zone (MRZ).",
    icon: CheckCircle
  },
  {
    id: 4,
    title: "Tampering Detection",
    description: "Forensic analysis detects digital manipulation, font inconsistencies, and metadata anomalies.",
    icon: ShieldAlert
  },
  {
    id: 5,
    title: "Face Verification",
    description: "Biometric analysis extracts the document portrait and compares it to a live selfie for identity matching.",
    icon: Fingerprint
  },
  {
    id: 6,
    title: "Risk Intelligence",
    description: "An aggregate risk score is calculated from all signals to give you a definitive recommendation.",
    icon: FileWarning
  },
  {
    id: 7,
    title: "Final Decision",
    description: "Get a clear VERIFIED, REVIEW REQUIRED, or HIGH RISK status in seconds.",
    icon: BadgeCheck
  }
];

export function ScrollStory() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [activeStep, setActiveStep] = useState(1);

  // Use an IntersectionObserver approach or simple scroll tracking for performance
  useEffect(() => {
    const handleScroll = () => {
      if (!containerRef.current) return;
      
      const elements = containerRef.current.querySelectorAll('.step-content');
      let currentStep = 1;
      
      elements.forEach((el, index) => {
        const rect = el.getBoundingClientRect();
        // If the element is near the vertical center of the screen
        if (rect.top < window.innerHeight * 0.6 && rect.bottom > window.innerHeight * 0.4) {
          currentStep = index + 1;
        }
      });
      
      setActiveStep(currentStep);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll(); // Initial check
    
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <section className="py-24 bg-background relative" ref={containerRef}>
      <div className="container mx-auto px-4 md:px-8 mb-16 text-center max-w-3xl">
        <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-6">
          One document.<br/>
          Seven layers of intelligence.
        </h2>
        <p className="text-lg text-muted-foreground">
          Scroll to see how our AI breaks down and verifies every element of an identity document in real-time.
        </p>
      </div>

      <div className="container mx-auto px-4 md:px-8">
        <div className="flex flex-col md:flex-row gap-8 md:gap-16">
          
          {/* LEFT SIDE: STICKY VISUALIZATION */}
          <div className="w-full md:w-1/2 relative">
            <div className="sticky top-32 h-[500px] rounded-2xl border border-border bg-card/30 overflow-hidden flex items-center justify-center p-8 transition-all duration-500 shadow-2xl">
              <VisualizationEngine activeStep={activeStep} />
            </div>
          </div>

          {/* RIGHT SIDE: SCROLLING CONTENT */}
          <div className="w-full md:w-1/2 pt-16 md:pt-[20vh] pb-[30vh]">
            {steps.map((step) => (
              <div 
                key={step.id} 
                className={cn(
                  "step-content min-h-[50vh] flex flex-col justify-center transition-all duration-500 pr-4",
                  activeStep === step.id ? "opacity-100" : "opacity-30"
                )}
              >
                <div className="flex items-center gap-4 mb-4 text-primary">
                  <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center border border-primary/20">
                    <step.icon className="w-6 h-6" />
                  </div>
                  <span className="font-mono font-bold tracking-widest text-sm">STEP 0{step.id}</span>
                </div>
                <h3 className="text-3xl font-bold mb-4">{step.title}</h3>
                <p className="text-xl text-muted-foreground leading-relaxed">
                  {step.description}
                </p>
              </div>
            ))}
          </div>

        </div>
      </div>
    </section>
  );
}

// Visual engine component that switches state based on the active step
function VisualizationEngine({ activeStep }: { activeStep: number }) {
  return (
    <div className="w-full h-full relative flex items-center justify-center">
      {/* Base Document Outline */}
      <motion.div 
        className={cn(
          "w-full max-w-[320px] aspect-[1/1.4] rounded-xl border-2 shadow-2xl relative overflow-hidden transition-all duration-700 backdrop-blur-xl",
          activeStep >= 1 ? "border-white/10 bg-white/[0.02]" : "border-dashed border-white/10 bg-transparent"
        )}
        initial={false}
        animate={{
          scale: activeStep === 1 ? 0.9 : 1,
          opacity: 1
        }}
      >
        {/* Step 1: Upload (Just document fading in) */}
        
        {/* Step 2: OCR */}
        <AnimatePresence mode="wait">
          {activeStep === 2 && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 p-4"
            >
              {/* Bounding boxes */}
              <div className="w-24 h-32 bg-white/5 border border-blue-400/30 absolute top-4 left-4 rounded-sm"></div>
              <div className="w-32 h-4 bg-white/5 border border-blue-400/30 absolute top-6 left-32 rounded-sm"></div>
              <div className="w-48 h-6 bg-white/5 border border-blue-400/30 absolute top-14 left-32 rounded-sm"></div>
              <div className="w-40 h-6 bg-white/5 border border-blue-400/30 absolute top-24 left-32 rounded-sm"></div>
              
              {/* Scanning line */}
              <motion.div 
                animate={{ top: ['0%', '100%', '0%'] }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                className="absolute left-0 right-0 h-[1px] bg-blue-400 shadow-[0_0_12px_2px_rgba(96,165,250,0.8)] z-10"
              />

              <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-white/5 text-blue-300 text-[10px] font-bold px-3 py-1 rounded border border-white/10 tracking-widest whitespace-nowrap">
                AWAITING DOCUMENT
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Step 3: MRZ & Validation */}
        <AnimatePresence mode="wait">
          {activeStep === 3 && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 p-4 flex flex-col justify-end pb-6"
            >
              {/* MRZ Area Highlight */}
              <div className="w-full h-16 bg-emerald-400/5 border border-emerald-400/30 rounded-sm relative overflow-hidden flex flex-col justify-center gap-2 p-2">
                <div className="w-full h-2 bg-emerald-400/20 rounded-full"></div>
                <div className="w-11/12 h-2 bg-emerald-400/20 rounded-full"></div>
                
                <motion.div 
                  initial={{ x: '-100%' }}
                  animate={{ x: '100%' }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                  className="absolute top-0 bottom-0 w-8 bg-emerald-400/20 shadow-[0_0_15px_rgba(52,211,153,0.3)] z-10 skew-x-[-20deg]"
                />
              </div>
              <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-white/5 text-emerald-300 text-[10px] font-bold px-3 py-1 rounded border border-white/10 tracking-widest whitespace-nowrap">
                VALIDATION ENGINE IDLE
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Step 4: Tampering */}
        <AnimatePresence mode="wait">
          {activeStep === 4 && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 p-4"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-violet-500/10 mix-blend-overlay"></div>
              
              <div className="w-24 h-32 absolute top-4 left-4 border border-violet-400/30 bg-violet-400/5"></div>
              
              <motion.div 
                animate={{ opacity: [0.1, 0.5, 0.1] }}
                transition={{ duration: 3, repeat: Infinity }}
                className="w-16 h-8 absolute top-20 left-40 border border-violet-400/50 bg-violet-400/10 rounded-sm"
              />
              
              <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-white/5 text-violet-300 text-[10px] font-bold px-3 py-1 rounded border border-white/10 tracking-widest whitespace-nowrap">
                ANALYSIS NOT STARTED
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Step 5: Face */}
        <AnimatePresence mode="wait">
          {activeStep === 5 && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 p-4 flex flex-col items-center justify-center bg-black/40 z-20 backdrop-blur-sm gap-6"
            >
              <div className="flex gap-4 items-center w-full justify-center">
                <div className="w-20 h-28 bg-white/5 rounded border border-amber-400/30 flex items-center justify-center relative overflow-hidden">
                   <Fingerprint className="w-8 h-8 text-amber-400/30" />
                </div>
                
                <div className="w-8 h-[1px] bg-amber-400/30 border border-dashed"></div>

                <div className="w-20 h-28 bg-white/5 rounded border border-amber-400/30 flex items-center justify-center relative overflow-hidden">
                   <Fingerprint className="w-8 h-8 text-amber-400/30" />
                </div>
              </div>
              
              <div className="bg-white/5 text-amber-300 text-[10px] font-bold px-3 py-1 rounded border border-white/10 tracking-widest whitespace-nowrap">
                NOT EVALUATED
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Step 6: Risk Score */}
        <AnimatePresence mode="wait">
          {activeStep === 6 && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 p-4 flex flex-col items-center justify-center bg-black/40 z-30 backdrop-blur-sm"
            >
              <div className="relative w-32 h-32 flex items-center justify-center mb-8">
                <svg className="w-full h-full transform -rotate-90">
                  <circle cx="64" cy="64" r="56" fill="transparent" stroke="rgba(255,255,255,0.1)" strokeWidth="4" />
                </svg>
                <div className="absolute flex flex-col items-center">
                  <span className="text-3xl font-bold text-white/20">--</span>
                </div>
              </div>
              
              <div className="bg-white/5 text-white/50 text-[10px] font-bold px-3 py-1 rounded border border-white/10 tracking-widest whitespace-nowrap">
                AWAITING INPUT
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Step 7: Decision */}
        <AnimatePresence mode="wait">
          {activeStep >= 7 && (
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 p-4 flex flex-col items-center justify-center bg-black/60 z-40 backdrop-blur-md"
            >
              <div className="w-16 h-16 rounded-full border-2 border-dashed border-white/20 flex items-center justify-center mb-6">
                <FileWarning className="w-6 h-6 text-white/20" />
              </div>
              <h3 className="text-xl font-bold text-white/40 mb-2 tracking-widest">REPORT PREVIEW</h3>
              
              <div className="absolute bottom-8 bg-white/5 text-white/50 text-[10px] font-bold px-3 py-1 rounded border border-white/10 tracking-widest whitespace-nowrap">
                REPORT NOT GENERATED
              </div>
            </motion.div>
          )}
        </AnimatePresence>

      </motion.div>
    </div>
  );
}

// Minimal stub for AnimatePresence to work smoothly
import { AnimatePresence } from 'framer-motion';
