content = """\"use client\";

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { ShieldCheck, Users, Search, Plus, Key, Ban, CheckCircle2 } from 'lucide-react';
import { authService, User } from '@/services/auth';
import { useToast } from '@/contexts/ToastContext';

export default function AdminPage() {
  const { toast } = useToast();
  const [users, setUsers] = useState<User[]>([]);
  
  const [loading, setLoading] = useState(true);
  const [reportCount, setReportCount] = useState(0);

  const fetchUsers = async () => {
    try {
      const u = await authService.getUsers();
      // Map user_id to id if backend uses user_id
      const mapped = u.map(x => ({...x, id: x.id || (x as any).user_id}));
      setUsers(mapped);
    } catch (e: any) {
      toast(e.message || 'Failed to load admin data', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
    
    const storedReports = sessionStorage.getItem('screeningReports');
    const storedReport = sessionStorage.getItem('screeningReport');
    if (storedReports) {
      try { setReportCount(JSON.parse(storedReports).length); } catch(e) {}
    } else if (storedReport) {
      setReportCount(1);
    }
  }, [toast]);

  const [userSearch, setUserSearch] = useState('');
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [addForm, setAddForm] = useState({email:'', password:'', role:'USER'});

  const [passModalOpen, setPassModalOpen] = useState(false);
  const [passUser, setPassUser] = useState<User | null>(null);
  const [passForm, setPassForm] = useState({newPass:'', confirmPass:''});

  const [statusModalOpen, setStatusModalOpen] = useState(false);
  const [statusUser, setStatusUser] = useState<User | null>(null);

  const handleAddUser = async () => {
    if(!addForm.email || !addForm.password) return toast('Fill all fields', 'error');
    try {
      await authService.createUser(addForm.email, addForm.password, addForm.role);
      toast('User created successfully', 'success');
      setAddModalOpen(false);
      setAddForm({email:'', password:'', role:'USER'});
      fetchUsers();
    } catch(e: any) {
      toast(e.message || 'Failed to create user', 'error');
    }
  };

  const handlePassChange = async () => {
    if(passForm.newPass.length < 8) return toast('Minimum 8 chars', 'error');
    if(passForm.newPass !== passForm.confirmPass) return toast('Passwords do not match', 'error');
    try {
      await authService.updateUserPassword(passUser!.id, passForm.newPass);
      toast('Password updated successfully', 'success');
      setPassModalOpen(false);
      setPassForm({newPass:'', confirmPass:''});
    } catch(e: any) {
      toast(e.message || 'Failed to change password', 'error');
    }
  };

  const handleStatusChange = async () => {
    try {
      const newStatus = statusUser!.status === 'DISABLED' ? 'ACTIVE' : 'DISABLED';
      await authService.updateUserStatus(statusUser!.id, newStatus);
      toast(`User status updated`, 'success');
      setStatusModalOpen(false);
      fetchUsers();
    } catch(e: any) {
      toast(e.message || 'Failed to change status', 'error');
    }
  };

  const filteredUsers = users.filter(u => {
    if (!userSearch) return true;
    const s = userSearch.toLowerCase();
    const st = u.status || 'ACTIVE';
    return (u.email && u.email.toLowerCase().includes(s)) || 
           (u.id && u.id.toLowerCase().includes(s)) ||
           (u.role && u.role.toLowerCase().includes(s)) ||
           (st.toLowerCase().includes(s));
  });

  return (
    <div className="container mx-auto px-4 pt-32 pb-20 max-w-7xl min-h-screen">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Admin control center</h1>
          <p className="text-muted-foreground">System overview and user management.</p>
        </div>
      </div>

      {/* OVERVIEW */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8 max-w-4xl mx-auto">
        <Card className="bg-card/50">
          <CardHeader className="pb-2 flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total users</CardTitle>
            <Users className="w-4 h-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{users.length}</div>
            <p className="text-xs text-muted-foreground mt-1">Registered accounts</p>
          </CardContent>
        </Card>
        
        <Card className="bg-card/50">
          <CardHeader className="pb-2 flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total screenings</CardTitle>
            <ShieldCheck className="w-4 h-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{reportCount}</div>
            <p className="text-xs text-muted-foreground mt-1">Current session</p>
          </CardContent>
        </Card>
      </div>

      <div className="max-w-4xl mx-auto flex flex-col gap-8">
        {/* USER MGMT */} 
        <div className="flex flex-col gap-8">
          <Card>
            <div className="p-4 border-b border-border flex flex-col sm:flex-row justify-between items-center gap-4">
              <h3 className="font-bold">User management</h3>
              <div className="flex items-center gap-4 w-full sm:w-auto">
                <div className="relative flex-1 sm:w-64">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <input 
                    type="text" 
                    value={userSearch}
                    onChange={(e) => setUserSearch(e.target.value)}
                    placeholder="Search users..." 
                    className="w-full bg-background border border-border rounded-md pl-9 pr-4 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                </div>
                <Button onClick={() => setAddModalOpen(true)} size="sm" className="whitespace-nowrap"><Plus className="w-4 h-4 mr-2"/> Add User</Button>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-muted-foreground bg-muted/50">
                  <tr>
                    <th className="px-4 py-3 font-medium">User</th>
                    <th className="px-4 py-3 font-medium">Role</th>
                    <th className="px-4 py-3 font-medium">Status</th>
                    <th className="px-4 py-3 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {loading ? (
                    <tr>
                      <td colSpan={4} className="px-4 py-6 text-center text-muted-foreground">Loading users...</td>
                    </tr>
                  ) : filteredUsers.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="px-4 py-6 text-center text-muted-foreground">No users found.</td>
                    </tr>
                  ) : filteredUsers.map((u) => (
                    <tr key={u.id} className="hover:bg-muted/30 transition-colors">
                      <td className="px-4 py-3 font-mono font-medium">{u.email || (u as any).username} <span className="text-xs text-muted-foreground ml-2">({u.id})</span></td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-[10px] font-bold ${u.role === 'ADMIN' ? 'bg-primary/20 text-primary' : 'bg-white/10'}`}>
                          {u.role.charAt(0).toUpperCase() + u.role.slice(1).toLowerCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-xs font-medium">
                        {(!u.status || u.status === 'ACTIVE') ? (
                           <div className="flex items-center gap-1.5 text-success"><div className="w-1.5 h-1.5 rounded-full bg-success"></div> Active</div>
                        ) : (
                           <div className="flex items-center gap-1.5 text-muted-foreground"><div className="w-1.5 h-1.5 rounded-full bg-muted-foreground"></div> Disabled</div>
                        )}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button variant="outline" size="sm" className="h-7 text-[10px]" onClick={() => {setPassUser(u); setPassModalOpen(true);}}>
                            Change Password
                          </Button>
                          <Button variant="outline" size="sm" className="h-7 text-[10px]" onClick={() => {setStatusUser(u); setStatusModalOpen(true);}}>
                            {(!u.status || u.status === 'ACTIVE') ? 'Disable' : 'Enable'}
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      </div>

      {addModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Add User</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-xs font-bold text-muted-foreground mb-1 block">Email</label>
                <input type="email" value={addForm.email} onChange={e => setAddForm({...addForm, email: e.target.value})} className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm" />
              </div>
              <div>
                <label className="text-xs font-bold text-muted-foreground mb-1 block">Password</label>
                <input type="password" value={addForm.password} onChange={e => setAddForm({...addForm, password: e.target.value})} className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm" />
              </div>
              <div>
                <label className="text-xs font-bold text-muted-foreground mb-1 block">Role</label>
                <select value={addForm.role} onChange={e => setAddForm({...addForm, role: e.target.value})} className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm">
                  <option value="USER">USER</option>
                  <option value="ADMIN">ADMIN</option>
                </select>
              </div>
              <div className="flex justify-end gap-2 pt-4">
                <Button variant="outline" onClick={() => setAddModalOpen(false)}>Cancel</Button>
                <Button onClick={handleAddUser}>Create User</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {passModalOpen && passUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>CHANGE PASSWORD</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-xs font-bold text-muted-foreground mb-1 block">New Password</label>
                <input type="password" value={passForm.newPass} onChange={e => setPassForm({...passForm, newPass: e.target.value})} className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm" />
              </div>
              <div>
                <label className="text-xs font-bold text-muted-foreground mb-1 block">Confirm Password</label>
                <input type="password" value={passForm.confirmPass} onChange={e => setPassForm({...passForm, confirmPass: e.target.value})} className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm" />
              </div>
              <div className="flex justify-end gap-2 pt-4">
                <Button variant="outline" onClick={() => setPassModalOpen(false)}>Cancel</Button>
                <Button onClick={handlePassChange}>Update Password</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {statusModalOpen && statusUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>{(!statusUser.status || statusUser.status === 'ACTIVE') ? 'Disable User?' : 'Enable User?'}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm">
                {(!statusUser.status || statusUser.status === 'ACTIVE') 
                  ? `Disable ${statusUser.email}? This user will no longer be able to authenticate.` 
                  : `Enable ${statusUser.email}? This user will regain access.`}
              </p>
              <div className="flex justify-end gap-2 pt-4">
                <Button variant="outline" onClick={() => setStatusModalOpen(false)}>Cancel</Button>
                <Button onClick={handleStatusChange}>{(!statusUser.status || statusUser.status === 'ACTIVE') ? 'Disable User' : 'Enable User'}</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

    </div>
  );
}
"""

with open('frontend/src/app/admin/page.tsx', 'w') as f:
    f.write(content)
