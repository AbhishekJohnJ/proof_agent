import React from 'react';
import { cn } from '../../lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  className,
  children,
  disabled,
  ...props
}) => {
  const baseStyles =
    'inline-flex items-center justify-center font-semibold rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-[#E64A32]/50 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer active:scale-[0.99]';

  const variants = {
    primary:
      'bg-[#E64A32] hover:bg-[#D03B23] text-[#F4F5EC] shadow-sm border border-[#E64A32]',
    secondary:
      'bg-[#3C3B39] hover:bg-[#4D4B48] text-[#F4F5EC] border border-[#3C3B39] shadow-xs',
    outline:
      'bg-transparent hover:bg-[#3C3B39]/60 text-[#F4F5EC] border border-[#3C3B39]',
    ghost: 'bg-transparent hover:bg-[#3C3B39]/50 text-[#F4F5EC]/70 hover:text-[#F4F5EC]',
    danger:
      'bg-rose-950/80 hover:bg-rose-900 text-rose-200 border border-rose-800/60 shadow-xs',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-xs gap-1.5',
    md: 'px-4 py-2 text-sm gap-2',
    lg: 'px-5 py-2.5 text-base gap-2.5 font-bold',
  };

  return (
    <button
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};
