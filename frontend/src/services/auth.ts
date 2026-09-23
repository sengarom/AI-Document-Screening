export interface User {
  id: string;
  email: string;
  role: 'USER' | 'ADMIN';
  status?: string;
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

  async getUsers(): Promise<User[]> {
    const res = await fetch(`${API_BASE}/api/admin/users`, { method: 'GET', credentials: 'include' });
    if (!res.ok) throw new Error('Failed to fetch users');
    return res.json();
  },

  async createUser(email: string, password: string, role: string): Promise<User> {
    const res = await fetch(`${API_BASE}/api/admin/users`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, role })
    });
    if (!res.ok) {
      let msg = 'Failed';
      try { const body = await res.json(); if(body.detail) msg = body.detail; } catch(e){}
      throw new Error(msg);
    }
    return res.json();
  },

  async updateUserPassword(userId: string, password: string): Promise<void> {
    const res = await fetch(`${API_BASE}/api/admin/users/${userId}/password`, {
      method: 'PATCH',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password })
    });
    if (!res.ok) throw new Error('Failed to change password');
  },

  async updateUserStatus(userId: string, status: string): Promise<void> {
    const res = await fetch(`${API_BASE}/api/admin/users/${userId}/status`, {
      method: 'PATCH',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    if (!res.ok) {
        let msg = 'Failed to change status';
        try { const body = await res.json(); if (body.detail) msg = body.detail; } catch(e){}
        throw new Error(msg);
    }
  }
};