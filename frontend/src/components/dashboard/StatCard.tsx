import React from 'react';
import { Card } from '../common/Card';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  icon: LucideIcon;
  trend?: string;
  accentColor?: 'emerald' | 'indigo' | 'amber' | 'slate' | 'red' | 'orange';
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  subtext,
  icon: Icon,
  trend,
  accentColor = 'red',
}) => {
  const iconColor = {
    red: 'text-[#E64A32] bg-[#E64A32]/15 border-[#E64A32]/30',
    orange: 'text-[#E18230] bg-[#E18230]/15 border-[#E18230]/30',
    amber: 'text-[#E18230] bg-[#E18230]/15 border-[#E18230]/30',
    emerald: 'text-[#E64A32] bg-[#E64A32]/15 border-[#E64A32]/30',
    indigo: 'text-[#E64A32] bg-[#E64A32]/15 border-[#E64A32]/30',
    slate: 'text-[#F4F5EC] bg-[#3C3B39] border-[#3C3B39]',
  }[accentColor];

  return (
    <Card className="flex items-start justify-between">
      <div>
        <p className="text-xs font-semibold text-[#F4F5EC]/60 uppercase tracking-wider">{label}</p>
        <h3 className="text-2xl font-bold text-[#F4F5EC] mt-1 font-mono tracking-tight">{value}</h3>
        {subtext && <p className="text-xs text-[#F4F5EC]/60 mt-1">{subtext}</p>}
        {trend && (
          <span className="inline-block text-[11px] font-bold text-[#E64A32] mt-1.5 bg-[#E64A32]/15 px-2 py-0.5 rounded border border-[#E64A32]/30">
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
