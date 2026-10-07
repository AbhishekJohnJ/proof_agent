import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutGrid,
  Database,
  Terminal,
  FileCheck,
  Activity,
  Settings,
  ShieldCheck,
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { useTheme } from '../../context/ThemeContext';

export const Sidebar: React.FC = () => {
  const { theme } = useTheme();

  const navItems = [
    { label: 'Overview', path: '/dashboard', icon: LayoutGrid },
    { label: 'Data Sources', path: '/data', icon: Database },
    { label: 'Analysis', path: '/analysis', icon: Terminal },
    { label: 'Evidence', path: '/evidence', icon: FileCheck },
    { label: 'Analysis Runs', path: '/runs', icon: Activity },
    { label: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <aside className="w-64 theme-main border-r theme-border flex flex-col h-screen sticky top-0 shrink-0 select-none z-30 transition-colors">
      {/* Brand Header */}
      <div className="p-5 border-b theme-border">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-[#E64A32]/15 border border-[#E64A32]/40 flex items-center justify-center text-[#E64A32] shadow-xs">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-bold tracking-tight flex items-center gap-1.5 font-sans">
              ProofAI
            </h1>
            <p className="text-[10px] font-semibold text-[#E18230] tracking-wider uppercase">
              Verified Data Intelligence
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
                  isActive
                    ? 'bg-[#E64A32]/15 text-[#E64A32] border border-[#E64A32]/30 shadow-xs'
                    : theme === 'light'
                    ? 'text-gray-700 hover:text-black hover:bg-gray-200/60'
                    : 'text-[#F4F5EC]/70 hover:text-[#F4F5EC] hover:bg-[#3C3B39]/50'
                )
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
};
