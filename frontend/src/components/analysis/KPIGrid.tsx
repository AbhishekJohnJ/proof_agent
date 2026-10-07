import React from 'react';
import { Card } from '../common/Card';

interface KPIGridProps {
  kpis?: { label: string; value: string }[];
}

export const KPIGrid: React.FC<KPIGridProps> = ({ kpis }) => {
  if (!kpis || kpis.length === 0) return null;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {kpis.map((kpi, idx) => (
        <Card key={idx} className="p-4 bg-[#242726] border-[#3C3B39]">
          <p className="text-xs font-semibold text-[#F4F5EC]/60 uppercase tracking-wider">{kpi.label}</p>
          <p className="text-xl font-bold text-[#E64A32] mt-1 font-mono tracking-tight">{kpi.value}</p>
        </Card>
      ))}
    </div>
  );
};
