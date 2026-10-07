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
  CheckCircle2,
  User,
} from 'lucide-react';
import { cn } from '../../lib/utils';

export const Sidebar: React.FC = () => {
  const navItems = [
    { label: 'Overview', path: '/dashboard', icon: LayoutGrid },
    { label: 'Data Sources', path: '/data', icon: Database },
    { label: 'Analysis', path: '/analysis', icon: Terminal },
    { label: 'Evidence', path: '/evidence', icon: FileCheck },
    { label: 'Analysis Runs', path: '/runs', icon: Activity },
    { label: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col h-screen sticky top-0 shrink-0 select-none z-30">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400 shadow-xs">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white tracking-tight flex items-center gap-1.5">
              ProofAI
            </h1>
            <p className="text-[11px] font-medium text-slate-400 tracking-wide uppercase">
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
                    ? 'bg-indigo-600/15 text-indigo-300 border border-indigo-500/30 shadow-xs'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                )
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Bottom Section */}
      <div className="p-3 border-t border-slate-800/80 space-y-3 bg-slate-900/60">
        {/* Verification Engine Status */}
        <div className="bg-emerald-950/40 border border-emerald-500/20 rounded-lg p-2.5 flex items-center gap-2.5">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse-emerald shrink-0" />
          <div className="text-xs">
            <div className="font-semibold text-emerald-300 flex items-center gap-1">
              Engine Online
              <CheckCircle2 className="w-3 h-3 text-emerald-400 inline" />
            </div>
            <div className="text-[10px] text-emerald-400/70">Deterministic Sandbox</div>
          </div>
        </div>

        {/* User Profile */}
        <div className="flex items-center gap-3 p-2 rounded-lg bg-slate-800/40 border border-slate-800">
          <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-slate-300 font-semibold text-xs border border-slate-600/50">
            <User className="w-4 h-4 text-slate-300" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-semibold text-slate-200 truncate">Dr. Alex Vance</div>
            <div className="text-[10px] text-slate-400 truncate">Lead Data Auditor</div>
          </div>
        </div>
      </div>
    </aside>
  );
};
