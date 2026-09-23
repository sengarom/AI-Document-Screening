"use client";
import * as React from "react";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { GlassPanel } from "@/components/ui/GlassPanel";
import { Button } from "@/components/ui/Button";
import { Upload, ScanText, FileCheck, Fingerprint, ShieldAlert, Cpu, FileText, ChevronRight, ChevronLeft, RotateCcw, X, Image as ImageIcon, ScanLine, Activity, AlertTriangle, Maximize, Minimize } from "lucide-react";
import Image from "next/image";

type DemoStep = "upload" | "ocr" | "validation" | "forensics" | "face" | "identity_links" | "risk" | "report";

const steps: { id: DemoStep; title: string; label: string; icon: React.ElementType }[] = [
  { id: "upload", title: "DOCUMENT INGESTION", label: "01 — DOCUMENT INGESTION", icon: Upload },
  { id: "ocr", title: "OCR EXTRACTION", label: "02 — OCR EXTRACTION", icon: ScanText },
  { id: "validation", title: "DOCUMENT VALIDATION", label: "03 — DOCUMENT VALIDATION", icon: FileCheck },
  { id: "forensics", title: "IMAGE FORENSICS", label: "04 — IMAGE FORENSICS", icon: ShieldAlert },
  { id: "face", title: "FACE VERIFICATION", label: "05 — FACE VERIFICATION", icon: Fingerprint },
  { id: "identity_links", title: "IDENTITY LINK ANALYSIS", label: "06 — IDENTITY LINK ANALYSIS", icon: ScanLine },
  { id: "risk", title: "RISK ASSESSMENT", label: "07 — RISK ASSESSMENT", icon: Cpu },
  { id: "report", title: "SCREENING REPORT", label: "08 — SCREENING REPORT", icon: FileText },
];

export function DemoMode() {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [imageError, setImageError] = useState(false);
  const [isFocusMode, setIsFocusMode] = useState(false);
  const isTransitioning = React.useRef(false);

  const currentStep = steps[currentStepIndex];

  const nextStep = React.useCallback(() => {
    if (isTransitioning.current) return;
    isTransitioning.current = true;
    setTimeout(() => { isTransitioning.current = false; }, 400); // Debounce
    setCurrentStepIndex(prev => prev < steps.length - 1 ? prev + 1 : prev);
  }, []);

  const prevStep = React.useCallback(() => {
    if (isTransitioning.current) return;
    isTransitioning.current = true;
    setTimeout(() => { isTransitioning.current = false; }, 400);
    setCurrentStepIndex(prev => prev > 0 ? prev - 1 : prev);
  }, []);

  const restartDemo = () => {
    setCurrentStepIndex(0);
    setIsFocusMode(false);
  };

  const toggleFocusMode = () => setIsFocusMode(prev => !prev);

  // Reliable Auto-progress Timer
  useEffect(() => {
    let timer: NodeJS.Timeout;

    if (currentStepIndex >= steps.length - 1) {
      // At final stage: wait longer, then loop back to start
      timer = setTimeout(() => {
        setCurrentStepIndex(0);
      }, 5000);
    } else {
      // Normal progression
      timer = setTimeout(() => {
        setCurrentStepIndex(prev => prev + 1);
      }, 3500);
    }

    // Cleanup always clears the timer when step changes or component unmounts
    return () => clearTimeout(timer);
  }, [currentStepIndex]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight") nextStep();
      if (e.key === "ArrowLeft") prevStep();
      if (e.key === "f") toggleFocusMode();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [nextStep, prevStep]);

  return (
    <div className="container mx-auto px-4 md:px-8 relative z-10">
      <div
        className="w-full max-w-7xl h-[80vh] md:h-[85vh] mx-auto flex flex-col relative bg-[#090a0c]/80 backdrop-blur-3xl md:rounded-3xl border border-white/10 overflow-hidden shadow-[0_0_80px_rgba(0,0,0,0.8),_inset_0_1px_1px_rgba(255,255,255,0.1)] transition-all duration-500"
      >
              {/* Header */}
              <div className="flex justify-between items-center p-4 md:px-8 md:py-6 border-b border-white/10 bg-white/[0.03]">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-primary/20 border border-primary/30 flex items-center justify-center shadow-[0_0_20px_rgba(90,103,216,0.4)]">
                    <ScanLine className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h2 className="text-xl md:text-2xl font-bold text-white tracking-tight drop-shadow-md">Interactive Screening Demo</h2>
                    <p className="text-white/50 text-xs font-mono uppercase tracking-widest mt-0.5">
                      Simulated Data • Illustrative Output
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <button onClick={toggleFocusMode} className="hidden md:flex items-center gap-2 px-3 py-2 rounded-md bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 text-white/70 hover:text-white transition-all shadow-sm" title="Toggle Focus Mode (F)">
                    {isFocusMode ? <><Minimize className="w-4 h-4" /><span className="text-xs font-mono">Exit Focus</span></> : <><Maximize className="w-4 h-4" /><span className="text-xs font-mono">Focus Mode</span></>}
                  </button>
                </div>
              </div>

              {/* Main Content Area */}
              <div className="flex-1 flex flex-col lg:flex-row overflow-hidden relative">
                
                {/* LEFT: Document Preview & Visualization */}
                <div className={cn("relative flex items-center justify-center p-4 md:p-8 bg-black/30 overflow-hidden border-b lg:border-b-0 lg:border-r border-white/10 transition-all duration-500 ease-in-out", isFocusMode ? "w-full lg:w-full h-full" : "w-full lg:w-2/3 h-[50vh] lg:h-full")}>
                  
                  {/* Background Accents */}
                  <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(90,103,216,0.08)_0%,transparent_70%)]"></div>
                  <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:40px_40px] opacity-30"></div>
                  
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

                          {/* Identity Links Step Overlay */}
                          {currentStep.id === "identity_links" && !imageError && (
                            <motion.div key="idl" initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} className="absolute inset-0 z-10 pointer-events-none bg-black/40 backdrop-blur-[1px] flex items-center justify-center">
                              <div className="w-32 h-32 rounded-full border border-blue-500/30 flex items-center justify-center relative">
                                <motion.div animate={{ rotate: 360 }} transition={{ duration: 3, repeat: Infinity, ease: "linear" }} className="absolute inset-0 rounded-full border-t-2 border-blue-400"></motion.div>
                                <ScanLine className="w-8 h-8 text-blue-400" />
                              </div>
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
                               <GlassPanel variant="primary" className="w-full max-w-sm text-center p-8 border-white/10 shadow-2xl">
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
                <div className={cn("w-full flex flex-col bg-white/[0.01] z-20 transition-all duration-500 ease-in-out origin-right", isFocusMode ? "lg:w-0 h-0 lg:h-full opacity-0 overflow-hidden pointer-events-none" : "lg:w-1/3 h-[50vh] lg:h-full opacity-100")}>
                  
                  {/* Progress Timeline Header */}
                  <div className="px-6 py-5 border-b border-white/5 bg-white/[0.02]">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-xs font-mono text-white/50 uppercase tracking-widest">Demo Progress</span>
                      <span className="text-xs font-mono text-white/70">{currentStepIndex + 1} / {steps.length}</span>
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

                          {currentStep.id === "identity_links" && (
                            <div className="space-y-4">
                              <p className="text-sm text-white/60 leading-relaxed">Comparing face embedding against previous authorized verification cases.</p>
                              <div className="p-4 rounded-lg bg-white/5 border border-white/10 flex flex-col gap-3">
                                <div className="flex justify-between items-center"><span className="text-xs text-white/60">Historical Search</span><span className="text-xs font-mono text-white/80">IN PROGRESS</span></div>
                                <div className="flex justify-between items-center"><span className="text-xs text-white/60">Matches Found</span><span className="text-xs font-mono text-white/40">CALCULATING</span></div>
                              </div>
                              <div className="p-3 rounded-lg bg-white/5 border border-white/10 flex justify-between items-center">
                                <span className="text-[10px] uppercase tracking-widest text-white/40">Status</span>
                                <span className="text-xs font-mono text-white/60">SIMULATED DEMO</span>
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
                  <div className="p-4 md:p-6 border-t border-white/5 bg-white/[0.02] flex justify-between items-center gap-3 md:gap-4 shrink-0">
                     <Button 
                       variant="outline" 
                       onClick={prevStep}
                       disabled={currentStepIndex === 0}
                       className="bg-white/[0.02] border-white/10 text-white hover:bg-white/[0.05] hover:border-white/20 hover:shadow-[0_0_15px_rgba(255,255,255,0.05)] hover:-translate-y-[1px] transition-all duration-300 px-3 md:px-4 h-12"
                     >
                       <ChevronLeft className="w-4 h-4 md:mr-2" /> <span className="hidden md:inline">Previous</span>
                     </Button>

                     {currentStepIndex === steps.length - 1 ? (
                       <Button 
                         onClick={restartDemo}
                         className="flex-1 bg-white/10 text-white hover:bg-white/20 border border-white/20 hover:shadow-[0_0_20px_rgba(255,255,255,0.1)] hover:-translate-y-[1px] transition-all duration-300 h-12"
                       >
                         <RotateCcw className="w-4 h-4 mr-2" /> Restart Demo
                       </Button>
                     ) : (
                       <Button 
                         onClick={nextStep}
                         className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90 h-12 shadow-[0_0_15px_rgba(var(--primary),0.3)] hover:shadow-[0_0_25px_rgba(90,103,216,0.6)] hover:-translate-y-[1px] transition-all duration-300 border border-primary/20"
                       >
                         Next Step <ChevronRight className="w-4 h-4 ml-2" />
                       </Button>
                     )}
                  </div>
                  
                </div>
              </div>

      </div>
    </div>
  );
}
