import * as React from "react"
import { cn } from "@/lib/utils"

const GlassPanel = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { variant?: "default" | "heavy" }
>(({ className, variant = "default", ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "relative rounded-2xl border bg-white/[0.02] shadow-2xl transition-all duration-300",
      variant === "default" 
        ? "backdrop-blur-xl border-white/5 hover:border-white/10 hover:bg-white/[0.03] shadow-[0_8px_30px_rgba(0,0,0,0.12)]" 
        : "backdrop-blur-3xl border-white/10 bg-[#0a0a0a]/80 shadow-[0_8px_32px_rgba(0,0,0,0.3)]",
      className
    )}
    {...props}
  >
    {/* Subtle top edge highlight for glass effect */}
    <div className="absolute inset-0 rounded-2xl pointer-events-none border border-white/5 [mask-image:linear-gradient(to_bottom,white,transparent)]" />
    {props.children}
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
