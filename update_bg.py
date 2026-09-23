content = """\"use client\";

import { usePathname } from 'next/navigation';
import { motion, useReducedMotion } from 'framer-motion';
import { useEffect, useState } from 'react';

export function AnimatedDocumentBackground() {
  const pathname = usePathname() || '/';
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

  let config = {
    count: isMobile ? 3 : 8,
    opacityMult: 1,
    isLanding: false
  };

  if (pathname === '/') {
    config.count = isMobile ? 5 : 9;
    config.opacityMult = 1.3;
    config.isLanding = true;
  } else if (pathname === '/login') {
    config.count = isMobile ? 2 : 5;
    config.opacityMult = 0.9;
  } else if (pathname === '/dashboard' || pathname === '/admin' || pathname === '/analyze' || pathname === '/results') {
    config.count = isMobile ? 2 : 4;
    config.opacityMult = 0.6;
  } else if (pathname.includes('/screen')) {
    config.count = isMobile ? 3 : 6;
    config.opacityMult = 0.8;
  } else {
    config.count = isMobile ? 2 : 4;
    config.opacityMult = 0.4;
  }

  const docTypes = ['passport', 'idcard', 'certificate', 'generic', 'passport', 'idcard', 'generic', 'certificate', 'passport'];
  
  const cards = Array.from({ length: config.count }).map((_, i) => {
    const type = docTypes[i % docTypes.length];
    
    // Depth: 0 (foreground) to 2 (background)
    const depth = i % 3; 
    
    // Size based on depth
    // Foreground: ~320px scale
    // Middle: ~260px scale
    // Background: ~200px scale
    let scale = 1.0;
    if (depth === 0) scale = 1.2;
    else if (depth === 1) scale = 0.9;
    else scale = 0.6;
    
    // Opacity based on depth
    // Foreground: 0.11 - 0.14
    // Normal: 0.08 - 0.11
    // Far: 0.06 - 0.08
    let baseOpacity = 0.08;
    if (depth === 0) baseOpacity = 0.12 + (i % 3) * 0.01;
    else if (depth === 1) baseOpacity = 0.09 + (i % 2) * 0.01;
    else baseOpacity = 0.06 + (i % 2) * 0.01;
    
    const finalOpacity = Math.min(baseOpacity * config.opacityMult, 0.25);
    
    // Blur based on depth
    let depthBlur = 0;
    if (depth === 0) depthBlur = 0; // 0px
    else if (depth === 1) depthBlur = 1; // 1px
    else depthBlur = 3; // 3px

    // Base rotation
    const baseRotations = [-8, 4, -3, 7, -6, 5, -4, 3, -7];
    const initialRotate = baseRotations[i % baseRotations.length];
    
    // Landing page specific positioning (around center)
    let startX = 0;
    let startY = 0;
    
    if (config.isLanding && !isMobile) {
      // 0: left middle (passport)
      // 1: right bottom (id card)
      // 2: top right (certificate)
      // 3: far left bottom
      // 4: far top left
      // 5: middle top
      const positions = [
        { x: 15, y: 40 },
        { x: 80, y: 70 },
        { x: 75, y: 20 },
        { x: 10, y: 80 },
        { x: 20, y: 15 },
        { x: 50, y: 10 },
        { x: 85, y: 45 },
        { x: 30, y: 85 },
        { x: 60, y: 80 },
      ];
      startX = positions[i % positions.length].x;
      startY = positions[i % positions.length].y;
    } else {
      // General distribution
      startX = 10 + (i * 37) % 80;
      startY = 10 + (i * 29) % 80;
    }

    // Movement params
    const duration = shouldReduceMotion ? 0 : 50 + ((i * 17) % 40); // 50-90s
    const moveX = ((i % 2 === 0) ? 1 : -1) * (5 + (i * 5) % 15); // -5 to 20vw
    const moveY = ((i % 3 === 0) ? 1 : -1) * (5 + (i * 7) % 15); // -5 to 20vh
    const rotateMove = initialRotate + (((i % 2 === 0) ? 1 : -1) * 5); 

    return {
      id: i, type, startX, startY, scale, depthBlur, duration, moveX, moveY, initialRotate, rotateMove, finalOpacity, depth
    };
  });

  return (
    <div className="fixed inset-0 z-[-1] pointer-events-none overflow-hidden" aria-hidden="true">
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
          animate={shouldReduceMotion ? {} : {
            x: [`-50%`, `calc(-50% + ${card.moveX}vw)`, `-50%`],
            y: [`-50%`, `calc(-50% + ${card.moveY}vh)`, `-50%`],
            rotate: [card.initialRotate, card.rotateMove, card.initialRotate],
          }}
          transition={{
            duration: card.duration,
            repeat: Infinity,
            ease: "linear",
            repeatType: "loop"
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
    ? 'border-2 border-[rgba(100,120,255,0.18)] shadow-[0_0_40px_rgba(100,120,255,0.05)]' 
    : 'border border-[rgba(100,120,255,0.12)] shadow-[0_0_30px_rgba(90,103,216,0.02)]';

  if (type === 'passport') {
    return (
      <div className={`w-[260px] h-[340px] rounded-xl ${borderClass} bg-primary/5 flex flex-col p-5`}>
        <div className="flex justify-between items-center mb-6">
          <div className="h-6 w-28 bg-primary/20 rounded"></div>
          <div className="w-10 h-10 rounded-full border-2 border-primary/30 flex items-center justify-center">
            <div className="w-5 h-5 bg-primary/20 rounded-sm"></div>
          </div>
        </div>
        <div className="flex gap-4">
          <div className="w-24 h-32 bg-primary/20 rounded-md"></div>
          <div className="flex-1 flex flex-col gap-3">
            <div className="h-3 w-full bg-primary/20 rounded"></div>
            <div className="h-3 w-3/4 bg-primary/20 rounded"></div>
            <div className="h-3 w-1/2 bg-primary/20 rounded"></div>
            <div className="h-3 w-2/3 bg-primary/20 rounded mt-4"></div>
            <div className="h-3 w-4/5 bg-primary/20 rounded"></div>
          </div>
        </div>
        <div className="mt-auto flex flex-col gap-2">
          <div className="h-3 w-full bg-primary/30 rounded font-mono text-[10px] text-primary/40 flex items-center px-2 overflow-hidden">
            P&lt;UTO&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;
          </div>
          <div className="h-3 w-full bg-primary/30 rounded font-mono text-[10px] text-primary/40 flex items-center px-2 overflow-hidden">
            1234567890UTO7408122F1204159&lt;&lt;&lt;&lt;&lt;&lt;0
          </div>
        </div>
      </div>
    );
  }
  
  if (type === 'idcard') {
    return (
      <div className={`w-[320px] h-[200px] rounded-xl ${borderClass} bg-indigo-500/5 flex flex-col p-5`}>
        <div className="flex justify-between items-center mb-5">
          <div className="h-5 w-36 bg-indigo-500/20 rounded"></div>
          <div className="h-4 w-16 bg-indigo-500/20 rounded"></div>
        </div>
        <div className="flex gap-5 items-start">
          <div className="w-24 h-28 bg-indigo-500/20 rounded-md flex-shrink-0"></div>
          <div className="flex-1 grid grid-cols-2 gap-x-4 gap-y-3">
            <div className="h-3 w-full bg-indigo-500/20 rounded"></div>
            <div className="h-3 w-3/4 bg-indigo-500/20 rounded"></div>
            <div className="h-3 w-4/5 bg-indigo-500/20 rounded"></div>
            <div className="h-3 w-full bg-indigo-500/20 rounded"></div>
            <div className="h-3 w-2/3 bg-indigo-500/20 rounded"></div>
            <div className="h-3 w-1/2 bg-indigo-500/20 rounded"></div>
          </div>
        </div>
        <div className="mt-auto h-6 w-full border-t border-indigo-500/20 pt-3 flex justify-between">
          <div className="h-2 w-1/3 bg-indigo-500/20 rounded"></div>
          <div className="h-2 w-1/4 bg-indigo-500/20 rounded"></div>
        </div>
      </div>
    );
  }

  if (type === 'certificate') {
    return (
      <div className={`w-[280px] h-[360px] rounded-sm ${borderClass} bg-white/5 flex flex-col items-center p-8`}>
        <div className="w-20 h-20 border-4 border-white/20 rounded-full flex items-center justify-center mb-8">
          <div className="w-14 h-14 border-2 border-white/20 rounded-full"></div>
        </div>
        <div className="h-6 w-56 bg-white/20 rounded mb-10"></div>
        <div className="h-3 w-full bg-white/20 rounded mb-4"></div>
        <div className="h-3 w-full bg-white/20 rounded mb-4"></div>
        <div className="h-3 w-5/6 bg-white/20 rounded mb-10"></div>
        <div className="mt-auto w-full flex justify-between items-end">
          <div className="flex flex-col gap-2 items-center">
            <div className="h-px w-24 bg-white/30"></div>
            <div className="h-2 w-16 bg-white/20 rounded"></div>
          </div>
          <div className="w-14 h-14 bg-white/10 rotate-45 border border-white/20 flex items-center justify-center">
             <div className="w-10 h-10 border border-white/20"></div>
          </div>
        </div>
      </div>
    );
  }

  // generic
  return (
    <div className={`w-[260px] h-[340px] rounded-lg ${borderClass} bg-violet-500/5 flex flex-col p-6`}>
      <div className="h-5 w-1/3 bg-violet-500/20 rounded mb-8"></div>
      <div className="flex flex-col gap-4 mb-8">
        <div className="h-3 w-full bg-violet-500/20 rounded"></div>
        <div className="h-3 w-full bg-violet-500/20 rounded"></div>
        <div className="h-3 w-3/4 bg-violet-500/20 rounded"></div>
      </div>
      <div className="flex gap-4 mb-auto">
        <div className="w-1/2 h-24 bg-violet-500/10 rounded border border-violet-500/20"></div>
        <div className="w-1/2 h-24 bg-violet-500/10 rounded border border-violet-500/20"></div>
      </div>
      <div className="w-full flex justify-end">
        <div className="h-10 w-10 rounded-full border-2 border-violet-500/30 flex items-center justify-center">
           <div className="w-5 h-5 bg-violet-500/20 rounded-sm rotate-45"></div>
        </div>
      </div>
    </div>
  );
}
"""

with open('frontend/src/components/background/AnimatedDocumentBackground.tsx', 'w') as f:
    f.write(content)
