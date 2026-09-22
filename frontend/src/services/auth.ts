export interface User {
  id: string;
  email: string;
  role: 'USER' | 'ADMIN';
}

export interface AuditLog {
  id: string;
  timestamp: string;
  event: string;
  actor: string;
  target?: string;
}

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  (typeof window !== 'undefined' && window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : '');

export const authService = {
  async login(email: string, password: string):Promise<void> {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) {
        let msg = "Login failed";
        try {
            const body = await res.json();
            if (body.detail) msg = body.detail;
        } catch(e){}
        throw new Error(msg);
    }
  },
  
  async logout():Promise<void> {
    await fetch(`${API_BASE}/api/auth/logout`, {
      method: 'POST',
      credentials: 'include',
    });
  },

  async getMe():Promise<User> {
    const res = await fetch(`${API_BASE}/api/auth/me`, {
      method: 'GET',
      credentials: 'include',
    });
    if (!res.ok) {
      throw new Error("Not authenticated");
    }
    return res.json();
  },

  async changePassword(current: string, newPass: string): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 500));
    if (newPass.length < 8) throw new Error('PASSWORD DOES NOT MEET SECURITY REQUIREMENTS');
  },

  async updateUsername(newUsername: string): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 500));
    if (newUsername.length < 3) throw new Error('Username too short');
  },

  async getAuditLogs(): Promise<AuditLog[]> {
    return [
      { id: '1', timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(), event: 'USER_LOGIN', actor: 'user_104' },
      { id: '2', timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(), event: 'VERIFICATION_STARTED', actor: 'user_104', target: 'case_892' },
      { id: '3', timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(), event: 'PASSWORD_CHANGED', actor: 'user_104' },
      { id: '4', timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), event: 'USER_CREATED', actor: 'admin_01', target: 'user_105' },
    ];
  },

  async getUsers(): Promise<User[]> {
    return [
      { id: 'admin_01', email: 'admin@example.com', role: 'ADMIN' },
      { id: 'user_104', email: 'user@example.com', role: 'USER' },
    ];
  },
  
  async toggleUserStatus(userId: string): Promise<void> {
  },

  async resetPassword(userId: string, verificationCode: string, newPass: string): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 500));
  }
}
