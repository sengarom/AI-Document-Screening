"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface IntelligenceNodeProps {
  id: string;
  label: string;
  isActive: boolean;
  color: string;
  onClick?: () => void;
  positionClass: string;
  delay?: number;
}

export function IntelligenceNode({
  label,
  isActive,
  color,
  onClick,
  positionClass,
  delay = 0,
}: IntelligenceNodeProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, delay, ease: "easeOut" }}
      className={cn(
        "absolute z-20 flex items-center gap-3 cursor-pointer group",
        positionClass
      )}
      onClick={onClick}
    >
      <div
        className={cn(
          "w-3 h-3 rounded-full transition-all duration-300 relative shadow-lg z-10",
          isActive ? "scale-125" : "bg-white/20 group-hover:bg-white/40 group-hover:scale-110"
        )}
        style={{
          backgroundColor: isActive ? color : undefined,
          boxShadow: isActive ? `0 0 20px ${color}` : undefined,
        }}
      >
        {isActive && (
          <motion.div
            layoutId="active-node-ring"
            className="absolute inset-[-6px] rounded-full border border-white/50 animate-[spin_3s_linear_infinite]"
            style={{ borderTopColor: color }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
          />
        )}
      </div>
      <span
        className={cn(
          "text-[10px] font-semibold tracking-widest transition-all duration-300 px-2 py-1 rounded-sm",
          isActive ? "text-white bg-white/10 backdrop-blur-md" : "text-white/40 group-hover:text-white/70 bg-transparent"
        )}
      >
        {label}
      </span>
    </motion.div>
  );
}
