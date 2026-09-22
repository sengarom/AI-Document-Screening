"use client";

import { useEffect, useState } from "react";
import { motion, useSpring, useMotionTemplate } from "framer-motion";

export function MouseLight() {
  const [isTouchDevice, setIsTouchDevice] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  
  const mouseX = useSpring(0, { stiffness: 30, damping: 30 });
  const mouseY = useSpring(0, { stiffness: 30, damping: 30 });

  useEffect(() => {
    // Check if device is touch-based or respects reduced motion
    const isTouch = window.matchMedia("(pointer: coarse)").matches;
    const isReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    
    if (isTouch || isReducedMotion) {
      setIsTouchDevice(true);
      return;
    }

    const updateMousePosition = (e: MouseEvent) => {
      mouseX.set(e.clientX);
      mouseY.set(e.clientY);
      if (!isVisible) setIsVisible(true);
    };

    const handleMouseLeave = () => {
      setIsVisible(false);
    };

    window.addEventListener("mousemove", updateMousePosition);
    document.addEventListener("mouseleave", handleMouseLeave);

    return () => {
      window.removeEventListener("mousemove", updateMousePosition);
      document.removeEventListener("mouseleave", handleMouseLeave);
    };
  }, [mouseX, mouseY, isVisible]);

  if (isTouchDevice) return null;

  return (
    <motion.div
      className="pointer-events-none fixed inset-0 z-30 transition-opacity duration-700"
      style={{
        opacity: isVisible ? 1 : 0,
      }}
    >
      <motion.div 
        className="absolute inset-0 pointer-events-none mix-blend-screen"
        style={{
          background: useMotionTemplate`radial-gradient(1200px circle at ${mouseX}px ${mouseY}px, rgba(90, 103, 216, 0.08), transparent 50%)`
        }}
      />
    </motion.div>
  );
}
