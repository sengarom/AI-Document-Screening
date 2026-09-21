"use client";
import * as React from "react";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { GlassPanel } from "@/components/ui/GlassPanel";
import { Button } from "@/components/ui/Button";
import { Upload, ScanText, FileCheck, Fingerprint, ShieldAlert, Cpu, FileText, ChevronRight, ChevronLeft, RotateCcw, X, Image as ImageIcon, ScanLine, Activity, AlertTriangle, Maximize, Minimize } from "lucide-react";
import Image from "next/image";

type DemoStep = "upload" | "ocr" | "validation" | "mrz" | "forensics" | "face" | "risk" | "report";

const steps: { id: DemoStep; title: string; label: string; icon: React.ElementType }[] = [
  { id: "upload", title: "DOCUMENT UPLOAD", label: "01 — DOCUMENT UPLOAD", icon: Upload },
  { id: "ocr", title: "OCR & FIELD EXTRACTION", label: "02 — OCR & FIELD EXTRACTION", icon: ScanText },
  { id: "validation", title: "FIELD VALIDATION", label: "03 — FIELD VALIDATION", icon: FileCheck },
  { id: "mrz", title: "MRZ ANALYSIS", label: "04 — MRZ ANALYSIS", icon: ScanLine },
  { id: "forensics", title: "TAMPERING ANALYSIS", label: "05 — TAMPERING ANALYSIS", icon: ShieldAlert },
  { id: "face", title: "FACE VERIFICATION", label: "06 — FACE VERIFICATION", icon: Fingerprint },
  { id: "risk", title: "RISK SCORING", label: "07 — RISK SCORING", icon: Cpu },
  { id: "report", title: "SCREENING REPORT", label: "08 — SCREENING REPORT", icon: FileText },
];

export function DemoMode() {
  const [isOpen, setIsOpen] = useState(false);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [imageError, setImageError] = useState(false);
  const [isFocusMode, setIsFocusMode] = useState(false);

  const currentStep = steps[currentStepIndex];

  const startDemo = () => {
    setIsOpen(true);
    setCurrentStepIndex(0);
    setIsFocusMode(false);
  };

  const nextStep = React.useCallback(() => {
    setCurrentStepIndex(prev => prev < steps.length - 1 ? prev + 1 : prev);
  }, []);

  const prevStep = React.useCallback(() => {
    setCurrentStepIndex(prev => prev > 0 ? prev - 1 : prev);
  }, []);

  const restartDemo = () => {
    setCurrentStepIndex(0);
    setIsFocusMode(false);
  };

  const closeDemo = () => {
    setIsOpen(false);
    setTimeout(() => {
      setCurrentStepIndex(0);
      setIsFocusMode(false);
    }, 500);
  };

  const toggleFocusMode = () => setIsFocusMode(prev => !prev);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;
      if (e.key === "ArrowRight") nextStep();
      if (e.key === "ArrowLeft") prevStep();
      if (e.key === "Escape") closeDemo();
      if (e.key === "f") toggleFocusMode();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, currentStepIndex, nextStep, prevStep]);

  return (
    <>
      <div className="flex justify-center py-12">
        <Button onClick={startDemo} size="lg" className="h-12 px-8 text-base bg-white/10 hover:bg-white/20 text-white border border-white/20 backdrop-blur-md shadow-[0_0_20px_rgba(255,255,255,0.1)] transition-all duration-300 hover:shadow-[0_0_30px_rgba(255,255,255,0.2)] hover:scale-105">
          Explore Interactive Demo
        </Button>
      </div>

      <AnimatePresence>
        {isOpen && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center bg-background/95 backdrop-blur-xl p-0 md:p-4">
            <motion.div
              initial={{ opacity: 0, y: 20, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 20, scale: 0.98 }}
              transition={{ duration: 0.4, ease: "easeOut" }}
              className="w-full max-w-7xl h-full md:h-[90vh] flex flex-col relative bg-[#050505] md:rounded-2xl border border-white/10 overflow-hidden shadow-[0_0_100px_rgba(0,0,0,0.8)]"
            >
              {/* Header */}
              <div className="flex justify-between items-center p-4 md:px-8 md:py-6 border-b border-white/5 bg-white/[0.02]">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-primary/20 border border-primary/30 flex items-center justify-center shadow-[0_0_15px_rgba(90,103,216,0.3)]">
                    <ScanLine className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h2 className="text-xl md:text-2xl font-bold text-white tracking-tight">Interactive Screening Demo</h2>
                    <p className="text-white/40 text-xs font-mono uppercase tracking-widest mt-0.5">
                      Simulated Data • Illustrative Output
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <button onClick={toggleFocusMode} className="hidden md:flex items-center gap-2 px-3 py-2 rounded-md bg-white/5 hover:bg-white/10 border border-white/10 text-white/70 hover:text-white transition-colors" title="Toggle Focus Mode (F)">
                    {isFocusMode ? <><Minimize className="w-4 h-4" /><span className="text-xs font-mono">Exit Focus</span></> : <><Maximize className="w-4 h-4" /><span className="text-xs font-mono">Focus Mode</span></>}
                  </button>
                  <button onClick={closeDemo} className="w-10 h-10 rounded-full flex items-center justify-center bg-white/5 text-white/50 hover:bg-white/10 hover:text-white transition-colors border border-white/5 hover:rotate-90 duration-300">
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Main Content Area */}
              <div className="flex-1 flex flex-col lg:flex-row overflow-hidden relative">
                
                {/* LEFT: Document Preview & Visualization */}
                <div className={cn("relative flex items-center justify-center p-4 md:p-8 bg-black/40 overflow-hidden border-b lg:border-b-0 lg:border-r border-white/5 transition-all duration-500 ease-in-out", isFocusMode ? "w-full lg:w-full h-full" : "w-full lg:w-2/3 h-[50vh] lg:h-full")}>
                  
                  {/* Background Accents */}
                  <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.03)_0%,transparent_100%)]"></div>
                  
                  <div className="relative w-full max-w-2xl aspect-[1.4/1] flex items-center justify-center">
                    {/* Document Viewer Frame */}
                    <div className="absolute inset-0 rounded-xl border border-white/10 bg-white/[0.02] shadow-[0_0_50px_rgba(0,0,0,0.5)] backdrop-blur-md overflow-hidden flex items-center justify-center p-2">
                      
                      {/* Document Label */}
                      <div className="absolute top-4 left-4 z-20 flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/60 backdrop-blur-md border border-white/10">
                        <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
                        <span className="text-[10px] font-bold tracking-widest text-white/80">DEMO DOCUMENT / SIMULATED SCREENING</span>
                      </div>

                      {/* Actual Document Image or Fallback */}
                      <div className="relative w-full h-full rounded-lg overflow-hidden bg-black/50 border border-white/5 flex items-center justify-center">
                        {!imageError ? (
                          <Image
                            src="/real-passport.png"
                            alt="Sample Demo Passport"
                            fill
                            className={cn(
                              "object-contain transition-all duration-700 ease-in-out",
                              currentStep.id === "upload" ? "scale-95 opacity-0 animate-in fade-in zoom-in fill-mode-forwards duration-1000" : "scale-100 opacity-100",
                              currentStep.id === "forensics" ? "brightness-75 contrast-125 saturate-50" : ""
                            )}
                            onError={() => setImageError(true)}
                            priority
                          />
                        ) : (
                          <div className="w-full h-full flex flex-col items-center justify-center text-white/20">
                            <ImageIcon className="w-16 h-16 mb-4" />
                            <p className="text-sm font-mono">DOCUMENT PREVIEW UNAVAILABLE</p>
                          </div>
                        )}

                        {/* OVERLAYS BASED ON CURRENT STEP */}
                        <AnimatePresence mode="wait">
                          
                          {/* OCR Step Overlay */}
                          {currentStep.id === "ocr" && !imageError && (
                            <motion.div key="ocr" initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} className="absolute inset-0 z-10 pointer-events-none">
                              {/* Illustrative Bounding Boxes */}
                              <motion.div initial={{opacity:0, scale:1.1}} animate={{opacity:1, scale:1}} transition={{delay:0.2}} className="absolute top-[30%] left-[32%] w-[35%] h-[5%] border-2 border-blue-400 bg-blue-400/20 rounded-sm"></motion.div>
                              <motion.div initial={{opacity:0, scale:1.1}} animate={{opacity:1, scale:1}} transition={{delay:0.4}} className="absolute top-[41%] left-[32%] w-[15%] h-[5%] border-2 border-blue-400 bg-blue-400/20 rounded-sm"></motion.div>
                              <motion.div initial={{opacity:0, scale:1.1}} animate={{opacity:1, scale:1}} transition={{delay:0.6}} className="absolute top-[51%] left-[32%] w-[40%] h-[5%] border-2 border-blue-400 bg-blue-400/20 rounded-sm"></motion.div>
                              <motion.div initial={{opacity:0, scale:1.1}} animate={{opacity:1, scale:1}} transition={{delay:0.8}} className="absolute top-[15%] right-[8%] w-[20%] h-[6%] border-2 border-blue-400 bg-blue-400/20 rounded-sm"></motion.div>
                              
                              <div className="absolute inset-0 bg-blue-500/5 mix-blend-overlay"></div>
                              <motion.div animate={{ top: ['0%', '100%', '0%'] }} transition={{ duration: 3, repeat: Infinity, ease: "linear" }} className="absolute left-0 right-0 h-[2px] bg-blue-400/80 shadow-[0_0_15px_rgba(96,165,250,0.8)] z-20" />
                            </motion.div>
                          )}

                          {/* Validation Step Overlay */}
                          {currentStep.id === "validation" && !imageError && (
                            <motion.div key="val" initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} className="absolute inset-0 z-10 pointer-events-none bg-black/20 backdrop-blur-[1px]">
                               <div className="absolute inset-0 flex items-center justify-center">
                                  <div className="w-24 h-24 rounded-full border border-emerald-400/50 flex items-center justify-center relative bg-emerald-400/10">
                                    <motion.div animate={{ rotate: 360 }} transition={{ duration: 4, repeat: Infinity, ease: "linear" }} className="absolute inset-0 rounded-full border-t-2 border-emerald-400"></motion.div>
                                    <FileCheck className="w-8 h-8 text-emerald-400" />
                                  </div>
                               </div>
                            </motion.div>
                          )}

                          {/* MRZ Step Overlay */}
                          {currentStep.id === "mrz" && !imageError && (
                            <motion.div key="mrz" initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} className="absolute inset-0 z-10 pointer-events-none flex flex-col justify-end pb-[7%] px-[5%]">
                              <motion.div initial={{height:0, opacity:0}} animate={{height:"18%", opacity:1}} className="w-full border-2 border-emerald-400 bg-emerald-400/20 rounded-sm relative overflow-hidden flex items-center justify-center backdrop-blur-sm">
                                <motion.div animate={{ left: ['-20%', '120%'] }} transition={{ duration: 2, repeat: Infinity, ease: "linear" }} className="absolute top-0 bottom-0 w-16 bg-emerald-300/40 blur-md transform skew-x-[-20deg]" />
                              </motion.div>
                            </motion.div>
                          )}

                          {/* Forensics Step Overlay */}
                          {currentStep.id === "forensics" && !imageError && (
                            <motion.div key="for" initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} className="absolute inset-0 z-10 pointer-events-none">
                              {/* Magnifier / Inspection Effect */}
                              <motion.div animate={{ x: [0, 100, -50, 0], y: [0, -50, 50, 0] }} transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }} className="absolute top-[40%] left-[40%] w-48 h-48 border border-violet-500/50 rounded-full backdrop-blur-sm bg-violet-500/10 flex items-center justify-center">
                                <div className="w-1 h-1 bg-violet-400 rounded-full"></div>
                                <div className="absolute inset-2 border border-dashed border-violet-500/30 rounded-full animate-[spin_10s_linear_infinite]"></div>
                              </motion.div>
                              
                              <div className="absolute inset-4 border border-violet-500/20">
                                <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-violet-500/80"></div>
                                <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-violet-500/80"></div>
                                <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-violet-500/80"></div>
                                <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-violet-500/80"></div>
                              </div>
                            </motion.div>
                          )}

                          {/* Face Step Overlay */}
                          {currentStep.id === "face" && !imageError && (
                            <motion.div key="fac" initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} className="absolute inset-0 z-10 pointer-events-none bg-black/40 backdrop-blur-[2px]">
                              {/* Portrait Highlight Box (Illustrative) */}
                              <motion.div initial={{scale:1.2, opacity:0}} animate={{scale:1, opacity:1}} className="absolute top-[18%] left-[3%] w-[26%] h-[39%] border-2 border-amber-400 bg-amber-400/10 rounded-md flex items-center justify-center overflow-hidden">
                                <motion.div animate={{ top: ['-10%', '110%'] }} transition={{ duration: 2, repeat: Infinity, ease: "linear" }} className="absolute left-0 right-0 h-[4px] bg-amber-400/80 shadow-[0_0_15px_rgba(251,191,36,0.8)] z-20" />
                              </motion.div>
                            </motion.div>
                          )}

                          {/* Risk Step Overlay */}
                          {currentStep.id === "risk" && !imageError && (
                            <motion.div key="rsk" initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} className="absolute inset-0 z-10 pointer-events-none bg-black/60 backdrop-blur-sm flex items-center justify-center">
                               <div className="w-full max-w-sm aspect-square relative flex items-center justify-center">
                                 <motion.div animate={{rotate:360}} transition={{duration:20, repeat:Infinity, ease:"linear"}} className="absolute inset-0 border border-dashed border-white/20 rounded-full"></motion.div>
                                 <div className="w-32 h-32 rounded-full bg-white/5 border border-white/10 flex items-center justify-center backdrop-blur-md">
                                   <Activity className="w-10 h-10 text-white/50" />
                                 </div>
                               </div>
                            </motion.div>
                          )}

                          {/* Report Step Overlay */}
                          {currentStep.id === "report" && !imageError && (
                            <motion.div key="rep" initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} className="absolute inset-0 z-10 pointer-events-none bg-black/70 backdrop-blur-md flex items-center justify-center p-8">
                               <GlassPanel variant="heavy" className="w-full max-w-sm text-center p-8 border-white/10 shadow-2xl">
                                  <FileText className="w-16 h-16 text-white/20 mx-auto mb-4" />
                                  <h3 className="text-xl font-bold text-white mb-2 tracking-widest">SCREENING SUMMARY</h3>
                                  <p className="text-xs text-white/50 uppercase tracking-widest mb-6">Demo Simulation Complete</p>
                                  <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                                    <motion.div initial={{width:0}} animate={{width:"100%"}} transition={{duration:1, ease:"easeOut"}} className="h-full bg-white/30"></motion.div>
                                  </div>
                               </GlassPanel>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    </div>
                  </div>

                  {/* Focus Mode Floating Controls */}
                  <AnimatePresence>
                    {isFocusMode && (
                      <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 20 }}
                        className="absolute bottom-8 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 p-2 rounded-full bg-black/60 backdrop-blur-xl border border-white/10 shadow-2xl"
                      >
                         <button onClick={prevStep} disabled={currentStepIndex === 0} className="w-10 h-10 rounded-full flex items-center justify-center bg-white/5 hover:bg-white/10 text-white disabled:opacity-30 transition-colors">
                           <ChevronLeft className="w-5 h-5" />
                         </button>
                         <div className="px-4 text-xs font-mono text-white/80 tracking-widest">
                           {currentStepIndex + 1} / {steps.length}
                         </div>
                         {currentStepIndex === steps.length - 1 ? (
                           <button onClick={restartDemo} className="w-10 h-10 rounded-full flex items-center justify-center bg-primary/20 hover:bg-primary/30 text-primary transition-colors">
                             <RotateCcw className="w-4 h-4" />
                           </button>
                         ) : (
                           <button onClick={nextStep} className="w-10 h-10 rounded-full flex items-center justify-center bg-primary text-white hover:bg-primary/90 transition-colors">
                             <ChevronRight className="w-5 h-5" />
                           </button>
                         )}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

                {/* RIGHT: Step Information & Navigation */}
                <div className={cn("w-full flex flex-col bg-[#080808] z-20 transition-all duration-500 ease-in-out origin-right", isFocusMode ? "lg:w-0 h-0 lg:h-full opacity-0 overflow-hidden pointer-events-none" : "lg:w-1/3 h-[50vh] lg:h-full opacity-100")}>
                  
                  {/* Progress Timeline Header */}
                  <div className="px-6 py-5 border-b border-white/5 bg-white/[0.01]">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-xs font-mono text-white/40 uppercase tracking-widest">Demo Progress</span>
                      <span className="text-xs font-mono text-white/60">{currentStepIndex + 1} / {steps.length}</span>
                    </div>
                    <div className="flex gap-1">
                      {steps.map((s, i) => (
                        <button key={s.id} onClick={() => setCurrentStepIndex(i)} className="h-1 flex-1 rounded-full bg-white/10 overflow-hidden outline-none hover:bg-white/20 transition-colors">
                          <motion.div 
                            className="h-full bg-primary"
                            initial={{ width: 0 }}
                            animate={{ width: i < currentStepIndex ? "100%" : i === currentStepIndex ? "100%" : "0%" }}
                            transition={{ duration: 0.3 }}
                          />
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Step Content */}
                  <div className="flex-1 overflow-y-auto p-6 flex flex-col">
                    <AnimatePresence mode="wait">
                      <motion.div
                        key={currentStep.id}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        transition={{ duration: 0.3 }}
                        className="flex-1 flex flex-col"
                      >
                        <div className="flex items-center gap-3 mb-6">
                           <div className="w-10 h-10 shrink-0 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center">
                             <currentStep.icon className="w-5 h-5 text-white/80" />
                           </div>
                           <h3 className="text-lg font-bold text-white tracking-widest leading-tight">{currentStep.title}</h3>
                        </div>

                        {/* Step Specific Details */}
                        <div className="space-y-6 flex-1">
                          
                          {currentStep.id === "upload" && (
                            <div className="space-y-4">
                              <p className="text-sm text-white/60 leading-relaxed">Sample document loaded for demonstration.</p>
                              <div className="p-4 rounded-lg bg-white/5 border border-white/10">
                                <span className="text-[10px] uppercase tracking-widest text-white/40 block mb-1">Status</span>
                                <span className="text-xs font-mono text-white/80">DEMO READY</span>
                              </div>
                              <p className="text-xs text-white/30 italic">Note: No real upload API is used in this simulation.</p>
                            </div>
                          )}

                          {currentStep.id === "ocr" && (
                            <div className="space-y-4">
                              <p className="text-sm text-white/60 leading-relaxed">Demonstration of illustrative OCR field extraction on the sample document.</p>
                              <div className="p-4 rounded-lg bg-white/5 border border-white/10 flex flex-col gap-3">
                                <span className="text-[10px] uppercase tracking-widest text-white/40 block mb-1 border-b border-white/10 pb-2">Illustrative Fields</span>
                                <div className="flex justify-between items-center"><span className="text-xs text-white/60">Full Name</span><span className="text-xs font-mono text-white/90">KAUR, HARMANPREET</span></div>
                                <div className="flex justify-between items-center"><span className="text-xs text-white/60">Date of Birth</span><span className="text-xs font-mono text-white/90">1996-01-22</span></div>
                                <div className="flex justify-between items-center"><span className="text-xs text-white/60">Document Number</span><span className="text-xs font-mono text-white/90">W9592099</span></div>
                                <div className="flex justify-between items-center"><span className="text-xs text-white/60">Nationality</span><span className="text-xs font-mono text-white/90">INDIAN</span></div>
                                <div className="flex justify-between items-center"><span className="text-xs text-white/60">Expiry Date</span><span className="text-xs font-mono text-white/90">2029-03-05</span></div>
                              </div>
                              <div className="flex items-start gap-2">
                                <AlertTriangle className="w-4 h-4 text-warning shrink-0 mt-0.5" />
                                <span className="text-[10px] text-white/40 uppercase tracking-wider">Simulated Demo / Data is illustrative</span>
                              </div>
                            </div>
                          )}

                          {currentStep.id === "validation" && (
                            <div className="space-y-4">
                              <p className="text-sm text-white/60 leading-relaxed">Validation workflow simulation checking extracted document fields.</p>
                              <div className="p-4 rounded-lg bg-white/5 border border-white/10 flex flex-col gap-3">
                                <div className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-white/20"></div><span className="text-xs text-white/70">Required fields</span></div>
                                <div className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-white/20"></div><span className="text-xs text-white/70">Date format validation</span></div>
                                <div className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-white/20"></div><span className="text-xs text-white/70">Document number structure</span></div>
                                <div className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-white/20"></div><span className="text-xs text-white/70">Field consistency check</span></div>
                              </div>
                              <div className="p-3 rounded-lg bg-white/5 border border-white/10 flex justify-between items-center">
                                <span className="text-[10px] uppercase tracking-widest text-white/40">Status</span>
                                <span className="text-xs font-mono text-white/60 text-right leading-tight">AWAITING BACKEND<br/>VALIDATION</span>
                              </div>
                            </div>
                          )}

                          {currentStep.id === "mrz" && (
                            <div className="space-y-4">
                              <p className="text-sm text-white/60 leading-relaxed">Illustrative Machine Readable Zone (MRZ) inspection.</p>
                              <div className="p-4 rounded-lg bg-white/5 border border-white/10 overflow-hidden">
                                <span className="text-[10px] uppercase tracking-widest text-white/40 block mb-2">Simulated MRZ Data</span>
                                <div className="font-mono text-[10px] md:text-xs text-white/50 leading-relaxed break-all">
                                  P&lt;IND&lt;&lt;HARMANPREET&lt;KAUR&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;<br/>
                                  W9592099&lt;5IND9601226F29030570075150500324&lt;48
                                </div>
                              </div>
                              <div className="p-3 rounded-lg bg-white/5 border border-white/10 flex justify-between items-center">
                                <span className="text-[10px] uppercase tracking-widest text-white/40">Status</span>
                                <span className="text-xs font-mono text-white/60">DEMO / AWAITING BACKEND</span>
                              </div>
                            </div>
                          )}

                          {currentStep.id === "forensics" && (
                            <div className="space-y-4">
                              <p className="text-sm text-white/60 leading-relaxed">Illustrative inspection of document regions for potential tampering or manipulation.</p>
                              <div className="p-4 rounded-lg bg-white/5 border border-white/10 flex flex-col gap-2">
                                <div className="flex justify-between items-center border-b border-white/5 pb-2"><span className="text-xs text-white/60">Image Integrity</span><span className="text-xs text-white/40">Pending</span></div>
                                <div className="flex justify-between items-center border-b border-white/5 py-2"><span className="text-xs text-white/60">Font Analysis</span><span className="text-xs text-white/40">Pending</span></div>
                                <div className="flex justify-between items-center pt-2"><span className="text-xs text-white/60">Copy/Paste Detection</span><span className="text-xs text-white/40">Pending</span></div>
                              </div>
                              <div className="p-3 rounded-lg bg-white/5 border border-white/10 flex justify-between items-center">
                                <span className="text-[10px] uppercase tracking-widest text-white/40">Status</span>
                                <span className="text-xs font-mono text-white/60">SIMULATED DEMO</span>
                              </div>
                            </div>
                          )}

                          {currentStep.id === "face" && (
                            <div className="space-y-4">
                              <p className="text-sm text-white/60 leading-relaxed">Document portrait detected for demonstration. A reference image or live selfie would be required for actual comparison.</p>
                              <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 rounded-lg bg-white/5 border border-white/10 flex flex-col items-center justify-center text-center">
                                  <span className="text-[10px] uppercase tracking-widest text-white/40 mb-1">Doc Portrait</span>
                                  <span className="text-xs text-white/80">Detected</span>
                                </div>
                                <div className="p-4 rounded-lg bg-white/5 border border-white/10 flex flex-col items-center justify-center text-center">
                                  <span className="text-[10px] uppercase tracking-widest text-white/40 mb-1">Live Selfie</span>
                                  <span className="text-xs text-white/40">Not Provided</span>
                                </div>
                              </div>
                              <div className="p-3 rounded-lg bg-white/5 border border-white/10 flex justify-between items-center">
                                <span className="text-[10px] uppercase tracking-widest text-white/40">Result</span>
                                <span className="text-xs font-mono text-white/60">NOT EVALUATED</span>
                              </div>
                            </div>
                          )}

                          {currentStep.id === "risk" && (
                            <div className="space-y-4">
                              <p className="text-sm text-white/60 leading-relaxed">Combines available screening signals into a unified risk assessment.</p>
                              <div className="p-8 rounded-lg bg-white/5 border border-white/10 flex flex-col items-center justify-center text-center">
                                <Cpu className="w-8 h-8 text-white/20 mb-3" />
                                <span className="text-xs font-mono text-white/40 uppercase tracking-widest mb-1">Risk Score</span>
                                <span className="text-lg font-bold text-white/30">NOT AVAILABLE</span>
                              </div>
                              <div className="p-3 rounded-lg bg-white/5 border border-white/10 flex justify-between items-center">
                                <span className="text-[10px] uppercase tracking-widest text-white/40">Status</span>
                                <span className="text-xs font-mono text-white/60">AWAITING ANALYSIS INPUT</span>
                              </div>
                            </div>
                          )}

                          {currentStep.id === "report" && (
                            <div className="space-y-4">
                              <p className="text-sm text-white/60 leading-relaxed">Simulated premium report preview detailing all findings and evidence.</p>
                              <div className="p-4 rounded-lg bg-white/5 border border-white/10 flex flex-col gap-3">
                                <div className="flex justify-between items-center"><span className="text-xs text-white/60">Document Reference</span><span className="text-xs font-mono text-white/80">DEMO-REQ-001</span></div>
                                <div className="flex justify-between items-center"><span className="text-xs text-white/60">Analysis</span><span className="text-xs font-mono text-white/60">SIMULATED</span></div>
                                <div className="flex justify-between items-center"><span className="text-xs text-white/60">Backend</span><span className="text-xs font-mono text-white/40">NOT CONNECTED</span></div>
                              </div>
                              
                              <Button variant="outline" className="w-full bg-white/5 hover:bg-white/10 border-white/10 text-white mt-4" onClick={() => alert("Simulated detailed report preview would open here.")}>
                                View Report Preview
                              </Button>
                            </div>
                          )}

                        </div>
                      </motion.div>
                    </AnimatePresence>
                  </div>

                  {/* Navigation Controls */}
                  <div className="p-4 md:p-6 border-t border-white/5 bg-black/40 flex justify-between items-center gap-3 md:gap-4 shrink-0">
                     <Button 
                       variant="outline" 
                       onClick={prevStep}
                       disabled={currentStepIndex === 0}
                       className="bg-transparent border-white/10 text-white hover:bg-white/5 px-3 md:px-4 h-12"
                     >
                       <ChevronLeft className="w-4 h-4 md:mr-2" /> <span className="hidden md:inline">Previous</span>
                     </Button>

                     {currentStepIndex === steps.length - 1 ? (
                       <Button 
                         onClick={restartDemo}
                         className="flex-1 bg-white/10 text-white hover:bg-white/20 border border-white/20 h-12"
                       >
                         <RotateCcw className="w-4 h-4 mr-2" /> Restart Demo
                       </Button>
                     ) : (
                       <Button 
                         onClick={nextStep}
                         className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90 h-12 shadow-[0_0_15px_rgba(var(--primary),0.3)]"
                       >
                         Next Step <ChevronRight className="w-4 h-4 ml-2" />
                       </Button>
                     )}
                  </div>
                  
                </div>
              </div>

            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}
