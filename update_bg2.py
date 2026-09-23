content = """\"use client\";

import { usePathname } from 'next/navigation';
import { motion, useReducedMotion } from 'framer-motion';
import { useEffect, useState } from 'react';

export function AnimatedDocumentBackground() {
  const pathname = usePathname();
  const shouldReduceMotion = useReducedMotion();
  const [mounted, setMounted] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    setMounted(true);
    setIsMobile(window.innerWidth < 768);
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  if (!mounted) return null;

  // Use current pathname or fallback to /
  const path = pathname || '/';

  // Prevent returning null/empty
  let config = {
    count: isMobile ? 3 : 8,
    opacityMult: 1,
    isLanding: false
  };

  if (path === '/') {
    config.count = isMobile ? 4 : 8;
    config.opacityMult = 1.0;
    config.isLanding = true;
  } else if (path === '/login') {
    config.count = isMobile ? 2 : 5;
    config.opacityMult = 0.8;
  } else if (path === '/dashboard' || path === '/admin' || path === '/analyze' || path === '/results') {
    config.count = isMobile ? 2 : 4;
    config.opacityMult = 0.6;
  } else if (path.includes('/screen')) {
    config.count = isMobile ? 3 : 5;
    config.opacityMult = 0.7;
  } else {
    config.count = isMobile ? 2 : 4;
    config.opacityMult = 0.4;
  }

  // Ensure minimums
  if (!isMobile && config.count < 4) config.count = 4;
  if (isMobile && config.count < 2) config.count = 2;

  const docTypes = ['passport', 'idcard', 'certificate', 'generic', 'idcard', 'passport', 'generic', 'certificate'];
  
  const cards = Array.from({ length: config.count }).map((_, i) => {
    const type = docTypes[i % docTypes.length];
    
    // Depth: 0 (foreground) to 2 (background)
    const depth = i % 3; 
    
    // Size based on depth
    let scale = 1.0;
    if (depth === 0) scale = 1.15; // ~320px
    else if (depth === 1) scale = 0.9; // ~250px
    else scale = 0.7; // ~195px
    
    // Opacity based on depth
    let baseOpacity = 0.08;
    if (depth === 0) baseOpacity = 0.12 + (i % 3) * 0.01;
    else if (depth === 1) baseOpacity = 0.08 + (i % 2) * 0.02;
    else baseOpacity = 0.05 + (i % 2) * 0.01;
    
    const finalOpacity = baseOpacity * config.opacityMult;
    
    // Blur based on depth
    let depthBlur = 0;
    if (depth === 0) depthBlur = 0; // 0px
    else if (depth === 1) depthBlur = 1; // 1px
    else depthBlur = 3; // 3px

    // Base rotation
    const baseRotations = [-8, 4, -3, 7, -6, 5, -4, 3];
    const initialRotate = baseRotations[i % baseRotations.length];
    
    // Landing page specific positioning (around center, NOT behind hero)
    let startX = 0;
    let startY = 0;
    
    if (config.isLanding && !isMobile) {
      // 0: left middle (passport) - depth 0
      // 1: right bottom (id card) - depth 1
      // 2: top right (certificate) - depth 2
      // 3: far left bottom - depth 0
      // 4: left top - depth 1
      // 5: right top - depth 2
      // 6: right middle - depth 0
      // 7: left bottom - depth 1
      const positions = [
        { x: 15, y: 35 }, // left middle
        { x: 80, y: 75 }, // right bottom
        { x: 75, y: 15 }, // top right
        { x: 10, y: 80 }, // far left bottom
        { x: 25, y: 10 }, // left top
        { x: 60, y: 10 }, // middle right top
        { x: 85, y: 45 }, // right middle
        { x: 35, y: 85 }, // middle left bottom
      ];
      startX = positions[i % positions.length].x;
      startY = positions[i % positions.length].y;
    } else {
      // General distribution
      const generalPositions = [
        { x: 15, y: 20 },
        { x: 85, y: 80 },
        { x: 20, y: 80 },
        { x: 80, y: 20 },
        { x: 50, y: 10 },
        { x: 10, y: 50 },
        { x: 90, y: 50 },
        { x: 50, y: 90 },
      ];
      startX = generalPositions[i % generalPositions.length].x;
      startY = generalPositions[i % generalPositions.length].y;
    }

    // Movement params
    const duration = shouldReduceMotion ? 0 : 30 + ((i * 10) % 30); // 30-60s
    
    // Give each card a slightly different animation path
    let animateVariant = {};
    if (i % 3 === 0) {
      animateVariant = {
        x: [`-50%`, `calc(-50% + 40px)`, `-50%`],
        y: [`-50%`, `calc(-50% + 20px)`, `-50%`],
        rotate: [initialRotate, initialRotate + 4, initialRotate]
      };
    } else if (i % 3 === 1) {
      animateVariant = {
        x: [`-50%`, `calc(-50% - 20px)`, `-50%`],
        y: [`-50%`, `calc(-50% - 30px)`, `-50%`],
        rotate: [initialRotate, initialRotate - 3, initialRotate]
      };
    } else {
      animateVariant = {
        x: [`-50%`, `calc(-50% - 30px)`, `-50%`],
        y: [`-50%`, `calc(-50% + 30px)`, `-50%`],
        rotate: [initialRotate, initialRotate + 5, initialRotate]
      };
    }

    return {
      id: i, type, startX, startY, scale, depthBlur, duration, initialRotate, finalOpacity, depth, animateVariant
    };
  });

  return (
    <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden" aria-hidden="true">
      {cards.map(card => (
        <motion.div
          key={card.id}
          className="absolute"
          style={{
            left: `${card.startX}%`,
            top: `${card.startY}%`,
            filter: `blur(${card.depthBlur}px)`,
            opacity: card.finalOpacity,
            x: '-50%',
            y: '-50%',
          }}
          initial={{ 
            rotate: card.initialRotate, 
            scale: card.scale 
          }}
          animate={shouldReduceMotion ? {} : card.animateVariant}
          transition={{
            duration: card.duration,
            repeat: Infinity,
            ease: "easeInOut",
            repeatType: "mirror"
          }}
        >
          <DocumentVisual type={card.type} depth={card.depth} />
        </motion.div>
      ))}
    </div>
  );
}

function DocumentVisual({ type, depth }: { type: string, depth: number }) {
  // subtle edge logic
  const borderClass = depth === 0 
    ? 'border border-[rgba(100,120,255,0.25)] shadow-[0_0_40px_rgba(100,120,255,0.08)]' 
    : depth === 1
    ? 'border border-[rgba(100,120,255,0.15)] shadow-[0_0_30px_rgba(100,120,255,0.04)]'
    : 'border border-[rgba(100,120,255,0.1)] shadow-[0_0_20px_rgba(100,120,255,0.02)]';

  if (type === 'passport') {
    return (
      <div className={`w-[280px] h-[360px] rounded-xl ${borderClass} bg-primary/10 flex flex-col p-5`}>
        <div className="flex justify-between items-center mb-6">
          <div className="h-6 w-32 bg-primary/30 rounded"></div>
          <div className="w-10 h-10 rounded-full border border-primary/40 flex items-center justify-center">
            <div className="w-5 h-5 bg-primary/30 rounded-sm"></div>
          </div>
        </div>
        <div className="flex gap-5">
          <div className="w-24 h-32 bg-primary/30 rounded-md"></div>
          <div className="flex-1 flex flex-col gap-3">
            <div className="h-3 w-full bg-primary/30 rounded"></div>
            <div className="h-3 w-3/4 bg-primary/30 rounded"></div>
            <div className="h-3 w-1/2 bg-primary/30 rounded"></div>
            <div className="h-3 w-2/3 bg-primary/30 rounded mt-4"></div>
            <div className="h-3 w-4/5 bg-primary/30 rounded"></div>
          </div>
        </div>
        <div className="mt-auto flex flex-col gap-2">
          <div className="h-3 w-full bg-primary/40 rounded font-mono text-[10px] text-primary/50 flex items-center px-2 overflow-hidden">
            P&lt;UTO&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;
          </div>
          <div className="h-3 w-full bg-primary/40 rounded font-mono text-[10px] text-primary/50 flex items-center px-2 overflow-hidden">
            1234567890UTO7408122F1204159&lt;&lt;&lt;&lt;&lt;&lt;0
          </div>
        </div>
      </div>
    );
  }
  
  if (type === 'idcard') {
    return (
      <div className={`w-[340px] h-[220px] rounded-xl ${borderClass} bg-indigo-500/10 flex flex-col p-5`}>
        <div className="flex justify-between items-center mb-5">
          <div className="h-5 w-40 bg-indigo-500/30 rounded"></div>
          <div className="h-4 w-16 bg-indigo-500/30 rounded"></div>
        </div>
        <div className="flex gap-5 items-start">
          <div className="w-24 h-28 bg-indigo-500/30 rounded-md flex-shrink-0"></div>
          <div className="flex-1 grid grid-cols-2 gap-x-4 gap-y-3">
            <div className="h-3 w-full bg-indigo-500/30 rounded"></div>
            <div className="h-3 w-3/4 bg-indigo-500/30 rounded"></div>
            <div className="h-3 w-4/5 bg-indigo-500/30 rounded"></div>
            <div className="h-3 w-full bg-indigo-500/30 rounded"></div>
            <div className="h-3 w-2/3 bg-indigo-500/30 rounded"></div>
            <div className="h-3 w-1/2 bg-indigo-500/30 rounded"></div>
          </div>
        </div>
        <div className="mt-auto h-6 w-full border-t border-indigo-500/30 pt-3 flex justify-between">
          <div className="h-2 w-1/3 bg-indigo-500/30 rounded"></div>
          <div className="h-2 w-1/4 bg-indigo-500/30 rounded"></div>
        </div>
      </div>
    );
  }

  if (type === 'certificate') {
    return (
      <div className={`w-[300px] h-[380px] rounded-sm ${borderClass} bg-white/5 flex flex-col items-center p-8`}>
        <div className="w-20 h-20 border-4 border-white/20 rounded-full flex items-center justify-center mb-8">
          <div className="w-14 h-14 border-2 border-white/20 rounded-full"></div>
        </div>
        <div className="h-6 w-56 bg-white/30 rounded mb-10"></div>
        <div className="h-3 w-full bg-white/30 rounded mb-4"></div>
        <div className="h-3 w-full bg-white/30 rounded mb-4"></div>
        <div className="h-3 w-5/6 bg-white/30 rounded mb-10"></div>
        <div className="mt-auto w-full flex justify-between items-end">
          <div className="flex flex-col gap-2 items-center">
            <div className="h-px w-24 bg-white/40"></div>
            <div className="h-2 w-16 bg-white/30 rounded"></div>
          </div>
          <div className="w-14 h-14 bg-white/10 rotate-45 border border-white/30 flex items-center justify-center">
             <div className="w-10 h-10 border border-white/30"></div>
          </div>
        </div>
      </div>
    );
  }

  // generic
  return (
    <div className={`w-[280px] h-[360px] rounded-lg ${borderClass} bg-violet-500/10 flex flex-col p-6`}>
      <div className="h-5 w-1/3 bg-violet-500/30 rounded mb-8"></div>
      <div className="flex flex-col gap-4 mb-8">
        <div className="h-3 w-full bg-violet-500/30 rounded"></div>
        <div className="h-3 w-full bg-violet-500/30 rounded"></div>
        <div className="h-3 w-3/4 bg-violet-500/30 rounded"></div>
      </div>
      <div className="flex gap-4 mb-auto">
        <div className="w-1/2 h-24 bg-violet-500/20 rounded border border-violet-500/30"></div>
        <div className="w-1/2 h-24 bg-violet-500/20 rounded border border-violet-500/30"></div>
      </div>
      <div className="w-full flex justify-end">
        <div className="h-10 w-10 rounded-full border border-violet-500/40 flex items-center justify-center">
           <div className="w-5 h-5 bg-violet-500/30 rounded-sm rotate-45"></div>
        </div>
      </div>
    </div>
  );
}
"""

with open('frontend/src/components/background/AnimatedDocumentBackground.tsx', 'w') as f:
    f.write(content)
