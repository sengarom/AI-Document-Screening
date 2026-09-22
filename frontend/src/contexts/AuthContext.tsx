"use client";

import React, { createContext, useContext, useEffect, useState } from 'react';
import { authService } from '@/services/auth';
import { useRouter, usePathname } from 'next/navigation';

interface User {
  id: string;
  email: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  const checkAuth = async () => {
    try {
      const me = await authService.getMe();
      setUser(me);
    } catch (e) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  // Route Protection
  useEffect(() => {
    if (!loading) {
      if (pathname.startsWith('/admin') && (!user || user.role !== 'ADMIN')) {
        router.replace(user ? '/dashboard' : '/login');
      }
      if ((pathname.startsWith('/dashboard') || pathname.startsWith('/screen') || pathname.startsWith('/account')) && !user) {
        router.replace('/login');
      }
      if (pathname === '/login' && user) {
        router.replace(user.role === 'ADMIN' ? '/admin' : '/dashboard');
      }
    }
  }, [user, loading, pathname, router]);

  const login = async (email: string, pass: string) => {
    await authService.login(email, pass);
    const me = await authService.getMe();
    setUser(me);
    router.push(me.role === 'ADMIN' ? '/admin' : '/dashboard');
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
    router.push('/');
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
