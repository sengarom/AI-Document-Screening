"use client";

import { useAuth } from '@/contexts/AuthContext';
import { SecuritySettings } from '@/components/dashboard/SecuritySettings';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function AccountPage() {
  const { user } = useAuth();
  
  if (!user || user.role !== 'USER') {
    return null; // AuthContext will handle redirect
  }

  return (
    <div className="container mx-auto px-4 pt-32 pb-20 max-w-4xl min-h-screen">
      <div className="mb-8">
        <Link href="/dashboard" className="text-sm text-muted-foreground hover:text-white flex items-center gap-2 mb-4 w-fit">
          <ArrowLeft className="w-4 h-4" /> Back to dashboard
        </Link>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Account & security</h1>
        <p className="text-muted-foreground">Manage your verification credentials and account settings.</p>
      </div>

      <SecuritySettings />
    </div>
  );
}
