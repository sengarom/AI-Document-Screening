"use client";

import { useRef } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import { ScanLine, FileCheck, Fingerprint, ShieldAlert, Cpu } from 'lucide-react';
import { ScrollStory } from '@/components/screening/ScrollStory';
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
        <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/15 via-[#050505] to-[#050505]"></div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="max-w-4xl mx-auto space-y-6"
        >
          <div className="inline-flex items-center rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-sm font-medium text-primary mb-4">
            <ScanLine className="mr-2 h-4 w-4" />
            Next-Generation Identity Intelligence
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-foreground leading-[1.1]">
            VERIFY <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-400">WHAT&apos;S REAL.</span>
          </h1>
          
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto pt-4">
            AI-powered identity and document screening for detecting inconsistencies, manipulation and identity mismatch. Built for certainty.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-8 mb-16">
            <Button asChild size="lg" className="w-full sm:w-auto h-12 px-8 text-base bg-primary text-primary-foreground hover:bg-primary/90 shadow-[0_0_15px_rgba(90,103,216,0.5)] hover:shadow-[0_0_25px_rgba(90,103,216,0.8)] transition-all duration-300">
              <Link href="/screen" className="flex items-center justify-center">
                Start Screening
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="w-full sm:w-auto h-12 px-8 text-base bg-white/5 border-white/10 hover:bg-white/10">
              <Link href="#capabilities">
                Explore Verification
              </Link>
            </Button>
          </div>
        </motion.div>

        {/* Hero Visual: Identity Intelligence Grid */}
        <div className="w-full mt-12 mb-8 flex flex-col items-center">
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
      <section id="capabilities" className="py-12 border-y border-white/5 bg-black/40 backdrop-blur-sm">
        <div className="container mx-auto px-4">
          <div className="flex flex-wrap justify-center gap-8 md:gap-16 opacity-70">
            {[
              { icon: FileCheck, text: "OCR EXTRACTION" },
              { icon: ScanLine, text: "MRZ VALIDATION" },
              { icon: ShieldAlert, text: "DOCUMENT FORENSICS" },
              { icon: Fingerprint, text: "FACE VERIFICATION" },
              { icon: Cpu, text: "RISK SCORING" },
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-3">
                <item.icon className="w-5 h-5 text-muted-foreground" />
                <span className="text-sm font-semibold tracking-wider text-muted-foreground">{item.text}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* SCROLL STORY SECTION */}
      <div className="bg-[#050505]">
        <ScrollStory />
      </div>

      {/* DEMO MODE SECTION */}
      <div className="bg-[#050505] pb-32">
        <DemoMode />
      </div>

    </div>
  );
}
