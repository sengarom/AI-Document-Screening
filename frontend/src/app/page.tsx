"use client";

import { useRef } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import { ShieldAlert, Cpu, Fingerprint, FileCheck, ScanLine } from 'lucide-react';
import { IdentityIntelligenceGrid } from '@/components/screening/IdentityIntelligenceGrid';
import { DemoMode } from '@/components/screening/DemoMode';

export default function Home() {
  const heroRef = useRef<HTMLDivElement>(null);
  
  return (
    <div className="flex flex-col min-h-screen">
      {/* HERO SECTION */}
      <section 
        ref={heroRef}
        className="relative pt-32 pb-20 md:pt-48 md:pb-32 overflow-hidden flex flex-col items-center text-center px-4"
      >
        {/* Ambient Lighting Layer */}
        <div className="absolute inset-0 -z-10 pointer-events-none">
          <div className="absolute inset-0 bg-[#090a0c]" />
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[120%] md:w-[800px] h-[600px] bg-[radial-gradient(ellipse_at_top,rgba(90,103,216,0.25)_0%,transparent_70%)] opacity-70" />
          <div className="absolute top-[20%] right-[-10%] w-[500px] h-[500px] bg-[radial-gradient(circle_at_center,rgba(90,103,216,0.15)_0%,transparent_60%)] opacity-60 mix-blend-screen" />
          <div className="absolute bottom-[-10%] left-[-10%] w-[600px] h-[600px] bg-[radial-gradient(circle_at_center,rgba(46,59,78,0.4)_0%,transparent_60%)] opacity-50" />
        </div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="max-w-4xl mx-auto space-y-6 relative z-10"
        >
          <div className="inline-flex items-center rounded-full border border-primary/20 bg-primary/[0.08] backdrop-blur-xl px-3 py-1.5 text-sm font-medium text-primary-foreground mb-4 shadow-[0_4px_24px_rgba(90,103,216,0.2)]">
            <ScanLine className="mr-2 h-4 w-4 opacity-80" />
            <span className="opacity-90">Next-Generation Identity Intelligence</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-white/95 leading-[1.1] drop-shadow-2xl">
            VERIFY <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-200 via-primary to-violet-300 drop-shadow-lg">WHAT&apos;S REAL.</span>
          </h1>
          
          <p className="text-lg md:text-xl text-white/70 max-w-2xl mx-auto pt-4 font-light leading-relaxed">
            AI-powered identity and document screening for detecting inconsistencies, manipulation and identity mismatch. Built for certainty.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-8 mb-16 relative">
            <Button asChild size="lg" className="w-full sm:w-auto h-12 px-8 text-base">
              <Link href="/screen" className="flex items-center justify-center">
                Start Screening
              </Link>
            </Button>
            <Button asChild variant="secondary" size="lg" className="w-full sm:w-auto h-12 px-8 text-base">
              <Link href="#capabilities">
                Explore Verification
              </Link>
            </Button>
          </div>
        </motion.div>

        {/* Hero Visual: Identity Intelligence Grid */}
        <div className="w-full mt-12 mb-8 flex flex-col items-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-center mb-12"
          >
            <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-white mb-2 uppercase tracking-widest">
              See the signals behind every verification.
            </h2>
            <p className="text-muted-foreground">
              Explore the layers of document intelligence used to support identity screening.
            </p>
          </motion.div>
          
          <IdentityIntelligenceGrid />
        </div>
      </section>

      {/* CAPABILITY STRIP */}
      <section id="capabilities" className="py-16 relative overflow-hidden bg-black/20 backdrop-blur-2xl border-y border-white/[0.03] shadow-[0_0_40px_rgba(0,0,0,0.5)]">
        <div className="absolute inset-0 bg-gradient-to-b from-primary/[0.02] to-transparent pointer-events-none" />
        <div className="absolute inset-0 opacity-[0.2] mix-blend-overlay pointer-events-none" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=%220 0 200 200%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noiseFilter%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.65%22 numOctaves=%223%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noiseFilter)%22/%3E%3C/svg%3E")' }} />
        
        <div className="container mx-auto px-4 relative z-10">
          <div className="flex flex-wrap justify-center gap-8 md:gap-16 opacity-90">
            {[
              { icon: FileCheck, text: "DOCUMENT" },
              { icon: ScanLine, text: "OCR" },
              { icon: ShieldAlert, text: "VALIDATION" },
              { icon: Cpu, text: "FORENSICS" },
              { icon: Fingerprint, text: "FACE" },
              { icon: Fingerprint, text: "IDENTITY LINKS" },
              { icon: Cpu, text: "RISK" },
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-3 group cursor-default">
                <item.icon className="w-5 h-5 text-white/40 group-hover:text-primary transition-colors duration-500 group-hover:drop-shadow-[0_0_8px_rgba(90,103,216,0.8)]" />
                <span className="text-sm font-semibold tracking-widest text-white/40 group-hover:text-white transition-colors duration-500">{item.text}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* DEMO MODE SECTION */}
      <div className="relative py-24 pb-32">
        {/* Soft atmospheric glow connecting the sections */}
        <div className="absolute -top-32 left-1/2 -translate-x-1/2 w-[120%] md:w-[1000px] h-[400px] bg-[radial-gradient(ellipse_at_top,rgba(90,103,216,0.08)_0%,transparent_70%)] pointer-events-none" />
        
        <div className="relative z-10">
          <DemoMode />
        </div>
      </div>

    </div>
  );
}
