"use client";

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { ShieldCheck, Users, Activity, Clock, ShieldAlert, KeyRound, Lock, Search } from 'lucide-react';
import { authService, User, AuditLog } from '@/services/auth';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';

export default function AdminPage() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [users, setUsers] = useState<User[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [u, logs] = await Promise.all([
          authService.getUsers(),
          authService.getAuditLogs()
        ]);
        setUsers(u);
        setAuditLogs(logs);
      } catch (e) {
        toast('Failed to load admin data', 'error');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [toast]);

  const toggleUser = async (id: string) => {
    toast(`Demo limitation: User toggling is disabled.`, 'error');
  };

  return (
    <div className="container mx-auto px-4 pt-32 pb-20 max-w-7xl min-h-screen">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Admin control center</h1>
          <p className="text-muted-foreground">System overview, user management, and security controls.</p>
        </div>
      </div>

      {/* OVERVIEW */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card className="bg-card/50">
          <CardHeader className="pb-2 flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total users (Demo)</CardTitle>
            <Users className="w-4 h-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{users.length}</div>
            <p className="text-xs text-muted-foreground mt-1">Registered accounts</p>
          </CardContent>
        </Card>
        
        <Card className="bg-card/50">
          <CardHeader className="pb-2 flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium text-muted-foreground">Active sessions (Demo)</CardTitle>
            <Activity className="w-4 h-4 text-success" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">12</div>
            <p className="text-xs text-muted-foreground mt-1">Currently online</p>
          </CardContent>
        </Card>

        <Card className="bg-card/50">
          <CardHeader className="pb-2 flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total screenings (Demo)</CardTitle>
            <ShieldCheck className="w-4 h-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">1,492</div>
            <p className="text-xs text-muted-foreground mt-1">Last 30 days</p>
          </CardContent>
        </Card>

        <Card className="bg-card/50">
          <CardHeader className="pb-2 flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium text-muted-foreground">System alerts (Demo)</CardTitle>
            <ShieldAlert className="w-4 h-4 text-warning" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-warning">0</div>
            <p className="text-xs text-muted-foreground mt-1">Requires attention</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* LEFT COLUMN: USER MGMT & SECURITY */}
        <div className="lg:col-span-2 flex flex-col gap-8">
          {/* USER MANAGEMENT */}
          <Card>
            <div className="p-4 border-b border-border flex flex-col sm:flex-row justify-between items-center gap-4">
              <h3 className="font-bold">User management</h3>
              <div className="relative w-full sm:w-64">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input 
                  type="text" 
                  placeholder="Search users..." 
                  className="w-full bg-background border border-border rounded-md pl-9 pr-4 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-muted-foreground bg-muted/50">
                  <tr>
                    <th className="px-4 py-3 font-medium">User ID</th>
                    <th className="px-4 py-3 font-medium">Role</th>
                    <th className="px-4 py-3 font-medium">Status</th>
                    <th className="px-4 py-3 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {loading ? (
                    <tr>
                      <td colSpan={4} className="px-4 py-6 text-center text-muted-foreground">Loading users...</td>
                    </tr>
                  ) : users.map((u) => (
                    <tr key={u.id} className="hover:bg-muted/30 transition-colors">
                      <td className="px-4 py-3 font-mono font-medium">{u.email || (u as any).username} <span className="text-xs text-muted-foreground ml-2">({u.id})</span></td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-[10px] font-bold ${u.role === 'ADMIN' ? 'bg-primary/20 text-primary' : 'bg-white/10'}`}>
                          {u.role.charAt(0).toUpperCase() + u.role.slice(1).toLowerCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-success text-xs font-medium flex items-center gap-1.5 mt-1">
                        <div className="w-1.5 h-1.5 rounded-full bg-success"></div> Active
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <Button variant="outline" size="sm" className="h-7 text-[10px]" onClick={() => toggleUser(u.id)}>
                            Disable
                          </Button>
                          <Button variant="outline" size="sm" className="h-7 text-[10px]">
                            Reset password
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* SECURITY CONTROLS */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Security settings</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex flex-col gap-4">
                <h4 className="text-sm font-semibold text-muted-foreground flex items-center gap-2"><KeyRound className="w-4 h-4"/> Authentication policy</h4>
                <div className="flex justify-between items-center bg-white/5 px-4 py-3 rounded-lg border border-white/5">
                  <span className="text-sm">Password minimum length</span>
                  <span className="font-mono text-sm bg-background px-2 py-1 rounded border border-border">12 chars</span>
                </div>
                <div className="flex justify-between items-center bg-white/5 px-4 py-3 rounded-lg border border-white/5">
                  <span className="text-sm">MFA requirement</span>
                  <span className="font-mono text-sm text-primary">Required for admins</span>
                </div>
              </div>
              <div className="flex flex-col gap-4">
                <h4 className="text-sm font-semibold text-muted-foreground flex items-center gap-2"><Lock className="w-4 h-4"/> Access & sessions</h4>
                <div className="flex justify-between items-center bg-white/5 px-4 py-3 rounded-lg border border-white/5">
                  <span className="text-sm">Session timeout</span>
                  <span className="font-mono text-sm bg-background px-2 py-1 rounded border border-border">30 mins</span>
                </div>
                <div className="flex justify-between items-center bg-white/5 px-4 py-3 rounded-lg border border-white/5">
                  <span className="text-sm">Max login attempts</span>
                  <span className="font-mono text-sm bg-background px-2 py-1 rounded border border-border">5 attempts</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* RIGHT COLUMN: AUDIT LOGS */}
        <div className="flex flex-col h-full">
          <Card className="h-full flex flex-col">
            <CardHeader className="pb-3 border-b border-border">
              <CardTitle className="text-lg flex items-center justify-between">
                <span>Audit logs</span>
                <Clock className="w-4 h-4 text-muted-foreground" />
              </CardTitle>
            </CardHeader>
            <div className="flex-1 p-0 overflow-y-auto max-h-[600px]">
              {loading ? (
                <div className="p-6 text-center text-muted-foreground text-sm">Loading logs...</div>
              ) : (
                <div className="flex flex-col divide-y divide-border">
                  {auditLogs.map((log) => (
                    <div key={log.id} className="p-4 hover:bg-muted/20 transition-colors">
                      <div className="flex justify-between items-start mb-1">
                        <span className="text-xs font-mono font-bold text-primary">{log.event.charAt(0).toUpperCase() + log.event.slice(1).toLowerCase().replace(/_/g, ' ')}</span>
                        <span className="text-[10px] text-muted-foreground font-mono">
                          {new Date(log.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <div className="text-sm">
                        Actor: <span className="font-mono text-muted-foreground">{log.actor}</span>
                      </div>
                      {log.target && (
                        <div className="text-xs text-muted-foreground mt-1">
                          Target: <span className="font-mono">{log.target}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="p-3 border-t border-border bg-muted/20 text-center">
              <Button variant="link" size="sm" className="text-xs text-muted-foreground hover:text-white">View full audit history</Button>
            </div>
          </Card>
        </div>

      </div>
    </div>
  );
}
