import * as React from "react"
import { cn } from "@/lib/utils"

const GlassPanel = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { 
    variant?: "primary" | "secondary" | "floating" | "heavy",
    interactive?: boolean 
  }
>(({ className, variant = "secondary", interactive = false, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "relative rounded-2xl transition-all duration-500 overflow-hidden group border",
      
      // Variants
      variant === "primary" && "bg-[#121418]/60 backdrop-blur-3xl border-white/[0.08] shadow-[0_8px_32px_rgba(0,0,0,0.5)]",
      variant === "secondary" && "bg-white/[0.02] backdrop-blur-xl border-white/[0.04] shadow-[0_4px_24px_rgba(0,0,0,0.2)]",
      variant === "floating" && "bg-white/[0.01] backdrop-blur-md border-white/[0.02] shadow-[0_12px_40px_rgba(0,0,0,0.3)]",
      variant === "heavy" && "bg-black/60 backdrop-blur-3xl border-white/[0.1] shadow-2xl",
      
      // Interactive styling
      interactive && "hover:bg-white/[0.05] hover:border-white/[0.15] hover:shadow-[0_8px_32px_rgba(90,103,216,0.15)] hover:-translate-y-1 cursor-pointer",
      
      className
    )}
    {...props}
  >
    {/* Inner Edge Highlight */}
    <div className="absolute inset-0 rounded-2xl pointer-events-none border border-white/10 [mask-image:linear-gradient(to_bottom,white,transparent)] mix-blend-overlay opacity-70 group-hover:opacity-100 transition-opacity duration-500" />
    
    {/* Subtle Surface Gradient & Noise */}
    <div className="absolute inset-0 bg-gradient-to-br from-white/[0.03] to-transparent pointer-events-none" />
    <div className="absolute inset-0 opacity-[0.15] mix-blend-overlay pointer-events-none" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=%220 0 200 200%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noiseFilter%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.65%22 numOctaves=%223%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noiseFilter)%22/%3E%3C/svg%3E")' }} />
    
    {/* Animated Light Reflection (Hover) */}
    {interactive && (
      <div className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/[0.05] to-transparent group-hover:translate-x-full duration-1000 ease-in-out transition-transform pointer-events-none motion-reduce:hidden" />
    )}
    
    <div className="relative z-10 h-full">{props.children}</div>
  </div>
))
GlassPanel.displayName = "GlassPanel"

const GlassPanelHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-5 pb-3", className)}
    {...props}
  />
))
GlassPanelHeader.displayName = "GlassPanelHeader"

const GlassPanelTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-sm font-semibold tracking-widest text-white/90 uppercase",
      className
    )}
    {...props}
  />
))
GlassPanelTitle.displayName = "GlassPanelTitle"

const GlassPanelContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-5 pt-0 text-muted-foreground text-sm", className)} {...props} />
))
GlassPanelContent.displayName = "GlassPanelContent"

export { GlassPanel, GlassPanelHeader, GlassPanelTitle, GlassPanelContent }
