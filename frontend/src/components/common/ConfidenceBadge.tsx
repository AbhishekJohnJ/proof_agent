import React from 'react';
import { ConfidenceLevel } from '../../types';
import { ShieldCheck, ShieldAlert, ShieldX } from 'lucide-react';
import { cn } from '../../lib/utils';

interface ConfidenceBadgeProps {
  confidence: ConfidenceLevel;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  showText?: boolean;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({
  confidence,
  size = 'md',
  className,
  showText = true,
}) => {
  const config = {
    high: {
      label: 'High Confidence',
      icon: ShieldCheck,
      styles: 'bg-[#E64A32]/20 text-[#E64A32] border-[#E64A32]/40',
    },
    medium: {
      label: 'Medium Confidence',
      icon: ShieldAlert,
      styles: 'bg-[#E18230]/20 text-[#E18230] border-[#E18230]/40',
    },
    low: {
      label: 'Low Confidence',
      icon: ShieldX,
      styles: 'bg-[#3C3B39] text-[#F4F5EC]/70 border-[#3C3B39]',
    },
  }[confidence];

  const Icon = config.icon;

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs gap-1',
    md: 'px-2.5 py-1 text-xs gap-1.5',
    lg: 'px-3 py-1.5 text-sm gap-2 font-semibold',
  }[size];

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-md border font-medium transition-colors',
        config.styles,
        sizeStyles,
        className
      )}
    >
      <Icon className={cn(size === 'sm' ? 'w-3 h-3' : size === 'lg' ? 'w-4 h-4' : 'w-3.5 h-3.5')} />
      {showText && config.label}
    </span>
  );
};
