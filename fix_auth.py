import re

with open('frontend/src/services/auth.ts', 'r') as f:
    content = f.read()

# I will replace the end of the file manually
end_str = """
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
  },

  async resetPassword(userId: string, verificationCode: string, newPass: string): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 500));
  }
};
"""

content = re.sub(r'async getUsers\(\): Promise<User\[\]> \{.*', end_str.strip(), content, flags=re.DOTALL)

with open('frontend/src/services/auth.ts', 'w') as f:
    f.write(content)
