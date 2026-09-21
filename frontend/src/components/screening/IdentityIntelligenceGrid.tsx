"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { IntelligenceNode } from "./IntelligenceNode";
import { GlassPanel, GlassPanelHeader, GlassPanelTitle, GlassPanelContent } from "@/components/ui/GlassPanel";

const nodes = [
  {
    id: "ocr",
    label: "OCR EXTRACTION",
    color: "#60a5fa", // blue-400
    positionClass: "top-[10%] left-[5%] md:left-[15%]",
    description: "Extracts text and structured fields from an uploaded document.",
    state: "AWAITING DOCUMENT",
    source: "Not connected"
  },
  {
    id: "mrz",
    label: "MACHINE READABLE ZONE",
    color: "#34d399", // emerald-400
    positionClass: "top-[30%] left-[2%] md:left-[10%]",
    description: "Validates the standardized Machine Readable Zone data.",
    state: "AWAITING DOCUMENT",
    source: "Not connected"
  },
  {
    id: "forensics",
    label: "IMAGE INTEGRITY",
    color: "#a78bfa", // violet-400
    positionClass: "bottom-[25%] left-[5%] md:left-[15%]",
    description: "Analyzes potential image manipulation and integrity signals.",
    state: "ANALYSIS NOT STARTED",
    source: "Not connected"
  },
  {
    id: "face",
    label: "IDENTITY COMPARISON",
    color: "#fbbf24", // amber-400
    positionClass: "top-[20%] right-[2%] md:right-[15%]",
    description: "Compares a document portrait with a reference image when provided.",
    state: "NOT EVALUATED",
    source: "Not connected"
  },
  {
    id: "validation",
    label: "DOCUMENT CONSISTENCY",
    color: "#38bdf8", // sky-400
    positionClass: "top-[50%] right-[1%] md:right-[10%]",
    description: "Checks internal consistency of structured document information.",
    state: "AWAITING DOCUMENT",
    source: "Not connected"
  },
  {
    id: "risk",
    label: "DECISION SUPPORT",
    color: "#f87171", // red-400
    positionClass: "bottom-[30%] right-[5%] md:right-[15%]",
    description: "Combines available signals into an explainable screening assessment.",
    state: "AWAITING INPUT",
    source: "Not connected"
  },
  {
    id: "report",
    label: "SCREENING EVIDENCE",
    color: "#a3e635", // lime-400
    positionClass: "bottom-[10%] right-[10%] md:right-[25%]",
    description: "Presents findings, evidence, and relevant warnings.",
    state: "REPORT NOT GENERATED",
    source: "Not connected"
  }
];

export function IdentityIntelligenceGrid() {
  const [activeNodeId, setActiveNodeId] = useState<string | null>(null);

  const activeNode = nodes.find(n => n.id === activeNodeId);

  return (
    <div className="relative w-full max-w-6xl mx-auto min-h-[600px] flex items-center justify-center perspective-1000">
      
      {/* Central Abstract Document */}
      <div className="relative z-10 w-[260px] h-[380px] md:w-[320px] md:h-[460px] transform-gpu">
        <GlassPanel variant="heavy" className="w-full h-full relative p-6 flex flex-col justify-between">
          
          <div className="absolute inset-0 opacity-[0.03] bg-[linear-gradient(rgba(255,255,255,1)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,1)_1px,transparent_1px)] bg-[size:32px_32px]"></div>
          
          {/* Abstract Document Structure */}
          <div className="relative z-10 w-full h-full border-2 border-dashed border-white/10 rounded-xl p-4 flex flex-col gap-4">
            <div className="flex justify-between items-start">
              <div className="w-20 h-24 border border-white/10 bg-white/5 rounded-md flex items-center justify-center">
                 <div className="w-8 h-8 rounded-full border border-white/10 opacity-50"></div>
              </div>
              <div className="flex flex-col gap-2 items-end">
                <div className="w-24 h-2 bg-white/5 rounded-full"></div>
                <div className="w-16 h-2 bg-white/5 rounded-full"></div>
              </div>
            </div>

            <div className="flex flex-col gap-3 mt-4">
              <div className="w-full h-2 bg-white/5 rounded-full"></div>
              <div className="w-3/4 h-2 bg-white/5 rounded-full"></div>
              <div className="w-5/6 h-2 bg-white/5 rounded-full"></div>
            </div>

            <div className="mt-auto">
               <div className="w-full h-12 border border-white/10 bg-white/5 rounded-md flex flex-col justify-center gap-2 p-2">
                 <div className="w-full h-1.5 bg-white/10 rounded-full"></div>
                 <div className="w-4/5 h-1.5 bg-white/10 rounded-full"></div>
               </div>
            </div>
          </div>
        </GlassPanel>

        {/* Status Badge */}
        <div className="absolute -bottom-5 left-1/2 -translate-x-1/2 flex items-center gap-3 px-5 py-2 rounded-full bg-white/10 border border-white/10 backdrop-blur-xl shadow-lg whitespace-nowrap z-30">
          <div className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse shadow-[0_0_8px_rgba(129,140,248,0.8)]"></div>
          <span className="text-[10px] font-bold tracking-[0.2em] text-indigo-100/90">READY FOR SCREENING</span>
        </div>
        
        <div className="absolute -top-6 left-1/2 -translate-x-1/2 whitespace-nowrap z-30">
           <span className="text-[9px] font-bold tracking-[0.2em] text-white/30 uppercase">Illustrative Workflow</span>
        </div>

        {/* Connections SVG */}
        <svg className="absolute inset-[-200px] md:inset-[-300px] pointer-events-none z-0" style={{ width: 'calc(100% + 400px)', height: 'calc(100% + 400px)', marginLeft: '-200px', marginTop: '-200px' }}>
           {/* Center anchor point logic can be complex in pure SVG without knowing exact DOM rects, so we'll use a simplified CSS/absolute positioned approach for the nodes and rely on the grid visual layout. */}
           <defs>
             <linearGradient id="line-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
               <stop offset="0%" stopColor="rgba(255,255,255,0)" />
               <stop offset="50%" stopColor="rgba(255,255,255,0.2)" />
               <stop offset="100%" stopColor="rgba(255,255,255,0)" />
             </linearGradient>
           </defs>
        </svg>

      </div>

      {/* Render Nodes */}
      {nodes.map((node, i) => (
        <IntelligenceNode
          key={node.id}
          {...node}
          isActive={activeNodeId === node.id}
          onClick={() => setActiveNodeId(activeNodeId === node.id ? null : node.id)}
          delay={0.1 * i}
        />
      ))}

      {/* Information Panel */}
      <AnimatePresence>
        {activeNode && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="absolute bottom-4 left-1/2 -translate-x-1/2 md:bottom-auto md:top-12 md:left-[20px] md:translate-x-0 z-50 w-[90%] md:w-[320px]"
          >
            <GlassPanel variant="heavy">
              <GlassPanelHeader>
                <GlassPanelTitle style={{ color: activeNode.color }}>{activeNode.label}</GlassPanelTitle>
              </GlassPanelHeader>
              <GlassPanelContent className="space-y-4">
                <p>{activeNode.description}</p>
                
                <div className="space-y-2 pt-2 border-t border-white/10">
                  <div className="flex flex-col">
                    <span className="text-[10px] uppercase tracking-wider text-white/40">Current State</span>
                    <span className="text-xs font-mono text-white/80">{activeNode.state}</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[10px] uppercase tracking-wider text-white/40">Data Source</span>
                    <span className="text-xs text-white/80">{activeNode.source}</span>
                  </div>
                </div>
              </GlassPanelContent>
            </GlassPanel>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
}
