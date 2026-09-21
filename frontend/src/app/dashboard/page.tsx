"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { ScreeningReport } from '@/types';
import { Search, Filter, ArrowRight, Shield, AlertTriangle, ShieldAlert } from 'lucide-react';

export default function DashboardPage() {
  const [reports, setReports] = useState<ScreeningReport[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Only one report is stored in sessionStorage at the moment.
    const storedReport = sessionStorage.getItem('screeningReport');
    if (storedReport) {
      try {
        const parsed = JSON.parse(storedReport);
        setReports([parsed]);
      } catch (e) {
        setReports([]);
      }
    } else {
      setReports([]);
    }
    setLoading(false);
  }, []);

  const total = reports.length;
  const clear = reports.filter(r => r.status === 'CLEAR').length;
  const review = reports.filter(r => r.status === 'REVIEW REQUIRED').length;
  const highRisk = reports.filter(r => r.status === 'HIGH RISK').length;

  return (
    <div className="container mx-auto px-4 pt-32 pb-20 max-w-7xl min-h-screen">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Overview Dashboard</h1>
          <p className="text-muted-foreground">Monitor real-time identity screenings and alerts in this session.</p>
        </div>
        <Button asChild>
          <Link href="/screen">New Screening</Link>
        </Button>
      </div>

      {/* STATS */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card className="bg-card/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Documents Screened</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{total}</div>
            <p className="text-xs text-muted-foreground mt-1">Current session</p>
          </CardContent>
        </Card>
        
        <Card className="bg-card/50">
          <CardHeader className="pb-2 flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium text-muted-foreground">Clear</CardTitle>
            <Shield className="w-4 h-4 text-success" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{clear}</div>
            <p className="text-xs text-success mt-1">Low screening risk</p>
          </CardContent>
        </Card>
        
        <Card className="bg-card/50">
          <CardHeader className="pb-2 flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium text-muted-foreground">Review Required</CardTitle>
            <AlertTriangle className="w-4 h-4 text-warning" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{review}</div>
            <p className="text-xs text-warning mt-1">Needs manual check</p>
          </CardContent>
        </Card>

        <Card className="bg-card/50 border-destructive/20">
          <CardHeader className="pb-2 flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium text-muted-foreground">High Risk</CardTitle>
            <ShieldAlert className="w-4 h-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-destructive">{highRisk}</div>
            <p className="text-xs text-destructive mt-1">Critical alerts</p>
          </CardContent>
        </Card>
      </div>

      <div className="text-center text-sm text-muted-foreground mb-4">
        Statistics are based on screening reports generated in this session.
      </div>

      {/* DATA TABLE */}
      <Card>
        <div className="p-4 border-b border-border flex flex-col sm:flex-row justify-between gap-4">
          <div className="relative w-full max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search ID, name, or document..." 
              className="w-full bg-background border border-border rounded-md pl-9 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="h-9">
              <Filter className="w-4 h-4 mr-2" /> Filter
            </Button>
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-muted-foreground uppercase bg-muted/50">
              <tr>
                <th className="px-6 py-3 font-medium">ID / Date</th>
                <th className="px-6 py-3 font-medium">Document</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium">Risk Score</th>
                <th className="px-6 py-3 font-medium">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {loading ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-muted-foreground">Loading recent screenings...</td>
                </tr>
              ) : reports.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-muted-foreground">No screening reports yet. Run a document screening analysis to see results here.</td>
                </tr>
              ) : reports.map((report) => (
                <tr key={report.id} className="hover:bg-muted/30 transition-colors">
                  <td className="px-6 py-4">
                    <div className="font-mono text-foreground font-medium">{report.id}</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {new Date(report.date).toLocaleString(undefined, {
                        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                      })}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-muted-foreground">{report.documentType}</td>
                  <td className="px-6 py-4">
                    <StatusBadge status={report.status} />
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-full max-w-[60px] h-1.5 bg-secondary rounded-full overflow-hidden">
                        <div 
                          className="h-full rounded-full" 
                          style={{ 
                            width: `${Math.min(report.risk.score, 100)}%`,
                            backgroundColor: report.status === 'CLEAR' ? 'var(--success)' : report.status === 'HIGH RISK' ? 'var(--destructive)' : 'var(--warning)'
                          }}
                        ></div>
                      </div>
                      <span className="text-xs font-mono">{report.risk.score}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <Button variant="ghost" size="sm" asChild className="h-8 text-xs">
                      <Link href={`/screen/results`}>
                        View <ArrowRight className="ml-1 w-3 h-3" />
                      </Link>
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
