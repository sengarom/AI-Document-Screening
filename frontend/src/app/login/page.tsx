"use client";

import { useState } from 'react';
import Link from 'next/link';
import { ShieldCheck, Loader2 } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const { toast } = useToast();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await login(email, password);
      // Navigation is handled in AuthContext
    } catch (err: any) {
      toast(err.message || 'Authentication failed', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center pt-20 px-4 relative overflow-hidden">
      {/* Ambient background effect specific to login */}
      <div className="absolute inset-0 z-[-1] pointer-events-none overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary/5 rounded-full blur-[120px]" />
      </div>

      <Card className="w-full max-w-md bg-card/60 backdrop-blur-xl border-white/5 shadow-2xl relative">
        <div className="absolute -top-10 left-1/2 -translate-x-1/2">
          <div className="bg-background border border-border p-3 rounded-2xl shadow-xl">
            <ShieldCheck className="w-8 h-8 text-primary" />
          </div>
        </div>
        
        <CardContent className="pt-12 pb-8 px-8">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold tracking-tight mb-2">Sign in to Veridex</h1>
            <p className="text-sm text-muted-foreground">Authenticate to access the verification platform.</p>
          </div>

          <form onSubmit={handleLogin} className="flex flex-col gap-5">
            <div className="flex flex-col gap-2">
              <label className="text-xs font-medium text-muted-foreground">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter Email Address"
                className="w-full bg-background border border-white/10 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all placeholder:text-muted-foreground/50"
                required
              />
            </div>
            
            <div className="flex flex-col gap-2">
              <label className="text-xs font-medium text-muted-foreground">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter Password"
                className="w-full bg-background border border-white/10 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all placeholder:text-muted-foreground/50"
                required
              />
              <div className="flex justify-end mt-1">
                <Link href="/forgot-password" className="text-[11px] text-muted-foreground hover:text-primary transition-colors">
                  Forgot password?
                </Link>
              </div>
            </div>

            <Button
              type="submit"
              disabled={isLoading}
              className="mt-4 h-12 w-full text-sm font-medium shadow-none hover:shadow-[0_0_20px_rgba(90,103,216,0.3)] transition-all"
            >
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Authenticate"}
            </Button>
          </form>

          <div className="mt-8 text-center border-t border-border pt-6">
            <p className="text-xs text-muted-foreground">
              Mock Demo Access:
              <br />
              User: <strong className="text-white">user@example.com / User@123</strong> &nbsp;&bull;&nbsp; Admin: <strong className="text-white">admin@example.com / Admin@123</strong>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
