"use client";

import { useState } from 'react';
import Link from 'next/link';
import { ShieldCheck, Loader2, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { authService } from '@/services/auth';
import { useToast } from '@/contexts/ToastContext';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { motion, AnimatePresence } from 'framer-motion';

export default function ForgotPasswordPage() {
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [userId, setUserId] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // Simulate sending a code or verifying user existence
    setTimeout(() => {
      setIsLoading(false);
      setStep(2);
    }, 800);
  };

  const handleReset = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      toast('Passwords do not match', 'error');
      return;
    }
    
    setIsLoading(true);
    try {
      await authService.resetPassword(userId, verificationCode, newPassword);
      setStep(3);
    } catch (err: any) {
      toast(err.message || 'Verification failed', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  // Basic requirements validation
  const meetsLength = newPassword.length >= 8;
  const hasUpper = /[A-Z]/.test(newPassword);
  const hasNumber = /[0-9]/.test(newPassword);
  const hasSpecial = /[^A-Za-z0-9]/.test(newPassword);

  return (
    <div className="min-h-screen flex items-center justify-center pt-20 px-4 relative overflow-hidden">
      <div className="absolute inset-0 z-[-1] pointer-events-none overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary/5 rounded-full blur-[120px]" />
      </div>

      <Card className="w-full max-w-md bg-card/60 backdrop-blur-xl border-white/5 shadow-2xl relative">
        <div className="absolute -top-10 left-1/2 -translate-x-1/2 z-10">
          <div className="bg-background border border-border p-3 rounded-2xl shadow-xl">
            <ShieldCheck className="w-8 h-8 text-primary" />
          </div>
        </div>
        
        <CardContent className="pt-12 pb-8 px-8 min-h-[400px] flex flex-col relative">
          <AnimatePresence mode="wait">
            
            {step === 1 && (
              <motion.div
                key="step1"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
                className="flex-1 flex flex-col"
              >
                <div className="text-center mb-8">
                  <h1 className="text-2xl font-bold tracking-tight mb-2">Verify your account</h1>
                  <p className="text-sm text-muted-foreground">Enter your account details to continue.</p>
                  <p className="text-xs text-warning mt-2 font-bold">(Demo limitation: This is a simulated UI. No actual emails will be sent.)</p>
                </div>

                <form onSubmit={handleVerify} className="flex flex-col gap-5 flex-1">
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-medium text-muted-foreground">User ID</label>
                    <input
                      type="text"
                      value={userId}
                      onChange={(e) => setUserId(e.target.value)}
                      placeholder="Enter your user ID"
                      className="w-full bg-background border border-white/10 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all placeholder:text-muted-foreground/50"
                      required
                    />
                  </div>
                  
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-medium text-muted-foreground">Verification Code</label>
                    <input
                      type="text"
                      value={verificationCode}
                      onChange={(e) => setVerificationCode(e.target.value)}
                      placeholder="Enter verification code (mock: 123456)"
                      className="w-full bg-background border border-white/10 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all placeholder:text-muted-foreground/50"
                      required
                    />
                  </div>

                  <div className="mt-auto">
                    <Button
                      type="submit"
                      disabled={isLoading || !userId || !verificationCode}
                      className="h-12 w-full text-sm font-medium shadow-none hover:shadow-[0_0_20px_rgba(90,103,216,0.3)] transition-all"
                    >
                      {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Continue"}
                    </Button>
                    <div className="mt-4 text-center">
                      <Link href="/login" className="text-xs text-muted-foreground hover:text-white inline-flex items-center gap-1 transition-colors">
                        <ArrowLeft className="w-3 h-3" /> Back to login
                      </Link>
                    </div>
                  </div>
                </form>
              </motion.div>
            )}

            {step === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
                className="flex-1 flex flex-col"
              >
                <div className="text-center mb-6">
                  <h1 className="text-2xl font-bold tracking-tight mb-2">Create a new password</h1>
                  <p className="text-sm text-muted-foreground">Secure your account with a strong password.</p>
                </div>

                <form onSubmit={handleReset} className="flex flex-col gap-4 flex-1">
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-medium text-muted-foreground">New Password</label>
                    <input
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="Enter new password"
                      className="w-full bg-background border border-white/10 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all placeholder:text-muted-foreground/50"
                      required
                    />
                  </div>
                  
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-medium text-muted-foreground">Confirm Password</label>
                    <input
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Confirm new password"
                      className="w-full bg-background border border-white/10 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all placeholder:text-muted-foreground/50"
                      required
                    />
                  </div>

                  {/* Password Strength Indicators */}
                  <div className="bg-white/5 p-3 rounded-md border border-white/5 flex flex-col gap-1.5 mt-2">
                    <div className={`text-[11px] flex items-center gap-2 ${meetsLength ? 'text-success' : 'text-muted-foreground'}`}>
                      <CheckCircle2 className="w-3 h-3" /> At least 8 characters
                    </div>
                    <div className={`text-[11px] flex items-center gap-2 ${hasUpper ? 'text-success' : 'text-muted-foreground'}`}>
                      <CheckCircle2 className="w-3 h-3" /> One uppercase letter
                    </div>
                    <div className={`text-[11px] flex items-center gap-2 ${hasNumber ? 'text-success' : 'text-muted-foreground'}`}>
                      <CheckCircle2 className="w-3 h-3" /> One number
                    </div>
                    <div className={`text-[11px] flex items-center gap-2 ${hasSpecial ? 'text-success' : 'text-muted-foreground'}`}>
                      <CheckCircle2 className="w-3 h-3" /> One special character
                    </div>
                  </div>

                  <div className="mt-auto pt-4">
                    <Button
                      type="submit"
                      disabled={isLoading || !newPassword || !confirmPassword || !meetsLength}
                      className="h-12 w-full text-sm font-medium shadow-none hover:shadow-[0_0_20px_rgba(90,103,216,0.3)] transition-all"
                    >
                      {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Reset password"}
                    </Button>
                    <div className="mt-4 text-center">
                      <button type="button" onClick={() => setStep(1)} className="text-xs text-muted-foreground hover:text-white inline-flex items-center gap-1 transition-colors">
                        <ArrowLeft className="w-3 h-3" /> Back
                      </button>
                    </div>
                  </div>
                </form>
              </motion.div>
            )}

            {step === 3 && (
              <motion.div
                key="step3"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex-1 flex flex-col items-center justify-center text-center py-8"
              >
                <div className="w-16 h-16 bg-success/10 rounded-full flex items-center justify-center mb-6">
                  <CheckCircle2 className="w-8 h-8 text-success" />
                </div>
                <h1 className="text-2xl font-bold tracking-tight mb-2">Password updated</h1>
                <p className="text-sm text-muted-foreground mb-8">Your account password has been successfully reset. You can now log in with your new credentials.</p>
                
                <Button asChild className="w-full h-12 shadow-[0_0_20px_rgba(90,103,216,0.2)]">
                  <Link href="/login">Back to login</Link>
                </Button>
              </motion.div>
            )}
            
          </AnimatePresence>
        </CardContent>
      </Card>
    </div>
  );
}
