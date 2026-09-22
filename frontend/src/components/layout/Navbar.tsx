"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ShieldCheck, Menu, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const { user, loading, logout } = useAuth();
  
  const navLinks = [
    { name: 'Product', href: '/' },
    { name: 'Walkthrough', href: '/layers' },
  ];

  return (
    <header
      className={cn(
        'fixed top-0 w-full z-50 transition-all duration-300',
        scrolled 
          ? 'bg-[#090a0c]/70 backdrop-blur-xl border-b border-white/[0.05] shadow-[0_4px_30px_rgba(0,0,0,0.3)] py-3' 
          : 'bg-transparent py-5'
      )}
    >
      <div className="container mx-auto px-6 md:px-12 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <div className="bg-primary/10 p-2 rounded-lg group-hover:bg-primary/20 transition-colors">
            <ShieldCheck className="w-6 h-6 text-primary" />
          </div>
          <span className="text-xl font-bold tracking-tight">VERIDEX</span>
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              href={link.href}
              className={cn(
                'text-sm font-medium transition-all duration-300 relative group',
                pathname === link.href ? 'text-primary' : 'text-muted-foreground hover:text-white'
              )}
            >
              <span className="relative z-10 group-hover:-translate-y-0.5 inline-block transition-transform duration-300">{link.name}</span>
              <span className="absolute -inset-x-3 -inset-y-2 bg-white/0 group-hover:bg-white/[0.03] rounded-lg -z-0 transition-colors duration-300 pointer-events-none border border-transparent group-hover:border-white/5"></span>
            </Link>
          ))}
          
          <Link
            href="/screen"
            className={cn(
              'text-sm font-medium transition-all duration-300 relative group flex items-center gap-1.5',
              pathname.startsWith('/screen') ? 'text-primary' : 'text-muted-foreground hover:text-white'
            )}
          >
            <span className="relative z-10 group-hover:-translate-y-0.5 inline-block transition-transform duration-300 flex items-center gap-1.5">
              {!loading && !user && <span className="text-xs opacity-70">🔒</span>}
              {!loading && user && <span className="text-xs text-primary/80">✓</span>}
              Verification
            </span>
            <span className="absolute -inset-x-3 -inset-y-2 bg-white/0 group-hover:bg-white/[0.03] rounded-lg -z-0 transition-colors duration-300 pointer-events-none border border-transparent group-hover:border-white/5"></span>
          </Link>
        </nav>

        {/* Desktop Actions */}
        <div className="hidden md:flex items-center gap-4">
          {!loading && (
            <>
              {user ? (
                <div className="relative group/account h-full flex items-center">
                  <button className="flex items-center gap-1 text-sm font-medium text-foreground hover:text-primary transition-colors py-2 mr-2">
                    {user.role === 'ADMIN' ? 'Admin' : 'User'} ▾
                  </button>
                  <div className="absolute right-0 top-full mt-1 w-48 bg-card border border-border rounded-md shadow-2xl opacity-0 invisible group-hover/account:opacity-100 group-hover/account:visible transition-all flex flex-col py-2 z-50">
                    <div className="px-4 py-2 mb-1 border-b border-border">
                      <p className="text-xs text-muted-foreground">Signed in as</p>
                      <p className="text-sm font-medium truncate">{user.email}</p>
                    </div>
                    {user.role === 'ADMIN' ? (
                      <>
                        <Link href="/admin" className="px-4 py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-white/5 transition-colors">Admin dashboard</Link>
                      </>
                    ) : (
                      <>
                        <Link href="/dashboard" className="px-4 py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-white/5 transition-colors">Dashboard</Link>
                        <Link href="/account" className="px-4 py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-white/5 transition-colors">Account settings</Link>
                      </>
                    )}
                    <div className="border-t border-border mt-1 pt-1">
                      <button onClick={logout} className="w-full text-left px-4 py-2 text-sm text-destructive hover:bg-destructive/10 transition-colors">Logout</button>
                    </div>
                  </div>
                </div>
              ) : (
                <Link 
                  href="/login"
                  className="text-sm font-medium text-muted-foreground hover:text-white transition-colors"
                >
                  Login
                </Link>
              )}
            </>
          )}
          <Link 
            href="/screen" 
            className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-all duration-300 shadow-[0_0_15px_rgba(90,103,216,0.2)] hover:shadow-[0_0_25px_rgba(90,103,216,0.5)] hover:-translate-y-0.5 border border-primary/20 hover:border-primary/50"
          >
            Start screening
          </Link>
        </div>

        {/* Mobile Toggle */}
        <button 
          className="md:hidden p-2 text-foreground"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="md:hidden absolute top-full left-0 w-full bg-background border-b border-border py-4 px-6 flex flex-col gap-4 shadow-xl"
          >
            {navLinks.map((link) => (
              <Link
                key={link.name}
                href={link.href}
                onClick={() => setMobileMenuOpen(false)}
                className={cn(
                  'text-lg font-medium transition-colors',
                  pathname === link.href ? 'text-primary' : 'text-muted-foreground'
                )}
              >
                {link.name}
              </Link>
            ))}
            
            <Link
              href="/screen"
              onClick={() => setMobileMenuOpen(false)}
              className={cn(
                'text-lg font-medium transition-colors flex items-center gap-2',
                pathname.startsWith('/screen') ? 'text-primary' : 'text-muted-foreground hover:text-white'
              )}
            >
              {!loading && !user && <span className="text-sm opacity-70">🔒</span>}
              {!loading && user && <span className="text-sm text-primary/80">✓</span>}
              Verification
            </Link>
            
            {!loading && (
              <>
                {user ? (
                  <div className="flex flex-col gap-4 mt-2 pt-4 border-t border-border">
                    <p className="text-xs text-muted-foreground uppercase tracking-widest">{user.role} Menu</p>
                    {user.role === 'ADMIN' ? (
                      <>
                        <Link href="/admin" onClick={() => setMobileMenuOpen(false)} className="text-lg font-medium transition-colors text-muted-foreground hover:text-white">Admin dashboard</Link>
                      </>
                    ) : (
                      <>
                        <Link href="/dashboard" onClick={() => setMobileMenuOpen(false)} className="text-lg font-medium transition-colors text-muted-foreground hover:text-white">Dashboard</Link>
                        <Link href="/account" onClick={() => setMobileMenuOpen(false)} className="text-lg font-medium transition-colors text-muted-foreground hover:text-white">Account settings</Link>
                      </>
                    )}
                    <button onClick={() => { logout(); setMobileMenuOpen(false); }} className="text-lg font-medium text-left text-destructive hover:text-destructive/80 transition-colors mt-2">
                      Logout
                    </button>
                  </div>
                ) : (
                  <div className="flex flex-col gap-4 mt-2 pt-4 border-t border-border">
                    <Link
                      href="/login"
                      onClick={() => setMobileMenuOpen(false)}
                      className="text-lg font-medium transition-colors text-muted-foreground hover:text-white"
                    >
                      Login
                    </Link>
                  </div>
                )}
              </>
            )}

            <Link 
              href="/screen" 
              onClick={() => setMobileMenuOpen(false)}
              className="mt-2 text-center px-4 py-3 text-sm font-medium bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
            >
              Start screening
            </Link>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
