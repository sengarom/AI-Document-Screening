"use client";

import { use } from 'react';
import ResultsPage from '@/app/screen/results/page';

export default function ReportDetailPage({ params }: { params: Promise<{ id: string }> }) {
  // We use the same Results component, but in a real app we'd fetch the specific ID
  // For the sake of the hackathon mock, we reuse the ResultsPage
  const { id } = use(params);
  
  return (
    <div>
      <div className="bg-muted text-muted-foreground text-center py-2 text-xs border-b border-border">
        Viewing archived report: {id}
      </div>
      <ResultsPage />
    </div>
  );
}
