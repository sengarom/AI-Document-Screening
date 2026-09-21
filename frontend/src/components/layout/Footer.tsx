import Link from 'next/link';
import { ShieldCheck } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-background border-t border-border py-12 mt-auto">
      <div className="container mx-auto px-6 md:px-12 flex flex-col md:flex-row justify-between items-start md:items-center gap-8">
        <div className="flex flex-col gap-4 max-w-sm">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="bg-primary/10 p-1.5 rounded-lg group-hover:bg-primary/20 transition-colors">
              <ShieldCheck className="w-5 h-5 text-primary" />
            </div>
            <span className="text-lg font-bold tracking-tight">VERIDEX</span>
          </Link>
          <p className="text-sm text-muted-foreground">
            Built for trustworthy digital identity. AI-powered identity and document screening for detecting inconsistencies, manipulation and identity mismatch.
          </p>
        </div>
        
        <div className="flex gap-12 sm:gap-24">
          <div className="flex flex-col gap-3">
            <h4 className="font-semibold text-sm">Platform</h4>
            <Link href="/" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Product</Link>
            <Link href="/screen" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Verification</Link>
            <Link href="/dashboard" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Dashboard</Link>
          </div>
          
          <div className="flex flex-col gap-3">
            <h4 className="font-semibold text-sm">Legal</h4>
            <Link href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Privacy</Link>
            <Link href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Security</Link>
            <Link href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Terms</Link>
          </div>
        </div>
      </div>
      
      <div className="container mx-auto px-6 md:px-12 mt-12 pt-8 border-t border-border flex flex-col md:flex-row items-center justify-between gap-4">
        <p className="text-xs text-muted-foreground">
          © {new Date().getFullYear()} Veridex Systems. All rights reserved.
        </p>
        <div className="flex gap-4">
          {/* Social icons placeholder */}
          <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-muted-foreground hover:text-foreground cursor-pointer transition-colors">
            <span className="text-xs font-bold">X</span>
          </div>
          <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-muted-foreground hover:text-foreground cursor-pointer transition-colors">
            <span className="text-xs font-bold">IN</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
