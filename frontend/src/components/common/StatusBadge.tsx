import React from 'react';
import { AnalysisStatus } from '../../types';
import { CheckCircle2, AlertTriangle, XCircle, Clock } from 'lucide-react';
import { cn } from '../../lib/utils';

interface StatusBadgeProps {
  status: AnalysisStatus;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md', className }) => {
  const config = {
    verified: {
      label: 'Verified',
      icon: CheckCircle2,
      styles: 'bg-emerald-950/60 text-emerald-400 border-emerald-500/30',
    },
    warning: {
      label: 'Warning',
      icon: AlertTriangle,
      styles: 'bg-amber-950/60 text-amber-400 border-amber-500/30',
    },
    refused: {
      label: 'Refused',
      icon: XCircle,
      styles: 'bg-rose-950/60 text-rose-400 border-rose-500/30',
    },
    failed: {
      label: 'Failed',
      icon: XCircle,
      styles: 'bg-rose-950/60 text-rose-400 border-rose-500/30',
    },
    processing: {
      label: 'Processing',
      icon: Clock,
      styles: 'bg-sky-950/60 text-sky-400 border-sky-500/30 animate-pulse',
    },
  }[status] || {
    label: status,
    icon: AlertTriangle,
    styles: 'bg-slate-800 text-slate-300 border-slate-700',
  };

  const Icon = config.icon;

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs gap-1',
    md: 'px-2.5 py-1 text-xs gap-1.5',
    lg: 'px-3 py-1.5 text-sm gap-2 font-medium',
  }[size];

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-md border font-medium tracking-wide transition-colors',
        config.styles,
        sizeStyles,
        className
      )}
    >
      <Icon className={cn(size === 'sm' ? 'w-3 h-3' : size === 'lg' ? 'w-4 h-4' : 'w-3.5 h-3.5')} />
      {config.label}
    </span>
  );
};
