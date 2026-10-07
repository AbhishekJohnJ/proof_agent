import React from 'react';
import { Card } from '../common/Card';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  icon: LucideIcon;
  trend?: string;
  accentColor?: 'emerald' | 'indigo' | 'amber' | 'slate';
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  subtext,
  icon: Icon,
  trend,
  accentColor = 'indigo',
}) => {
  const iconColor = {
    emerald: 'text-emerald-400 bg-emerald-950/50 border-emerald-500/30',
    indigo: 'text-indigo-400 bg-indigo-950/50 border-indigo-500/30',
    amber: 'text-amber-400 bg-amber-950/50 border-amber-500/30',
    slate: 'text-slate-300 bg-slate-800 border-slate-700',
  }[accentColor];

  return (
    <Card className="flex items-start justify-between">
      <div>
        <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{label}</p>
        <h3 className="text-2xl font-bold text-white mt-1 font-mono tracking-tight">{value}</h3>
        {subtext && <p className="text-xs text-slate-400 mt-1">{subtext}</p>}
        {trend && (
          <span className="inline-block text-[11px] font-medium text-emerald-400 mt-1.5 bg-emerald-950/40 px-1.5 py-0.5 rounded border border-emerald-500/20">
            {trend}
          </span>
        )}
      </div>
      <div className={`p-2.5 rounded-lg border ${iconColor}`}>
        <Icon className="w-5 h-5" />
      </div>
    </Card>
  );
};
