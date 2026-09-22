import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default: "relative overflow-hidden bg-primary/80 backdrop-blur-md text-primary-foreground border border-primary/50 shadow-[0_0_20px_rgba(90,103,216,0.3)] hover:shadow-[0_0_30px_rgba(90,103,216,0.6)] hover:bg-primary/90 hover:-translate-y-0.5 transition-all duration-300 group after:absolute after:inset-0 after:-translate-x-full after:bg-gradient-to-r after:from-transparent after:via-white/[0.15] after:to-transparent hover:after:translate-x-full after:duration-1000 after:ease-in-out after:transition-transform motion-reduce:after:hidden motion-reduce:transition-none",
        destructive:
          "bg-destructive/90 text-destructive-foreground hover:bg-destructive shadow-sm",
        outline:
          "border border-white/10 bg-white/[0.02] backdrop-blur-md hover:bg-white/[0.06] hover:border-white/20 hover:text-white hover:shadow-[0_0_15px_rgba(255,255,255,0.05)] hover:-translate-y-0.5 transition-all duration-300 text-white/80",
        secondary:
          "bg-white/[0.05] text-white/90 backdrop-blur-md border border-white/5 hover:bg-white/[0.1] hover:border-white/10 hover:shadow-[0_0_20px_rgba(255,255,255,0.08)] hover:-translate-y-0.5 transition-all duration-300",
        ghost: "hover:bg-white/[0.05] hover:text-white transition-all duration-300",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-12 rounded-md px-8 text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
