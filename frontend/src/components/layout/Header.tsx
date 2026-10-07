import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Plus, Database, Sparkles, Bell } from 'lucide-react';
import { Button } from '../common/Button';

export const Header: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const getPageTitle = () => {
    const path = location.pathname;
    if (path.startsWith('/dashboard')) return 'Dashboard Overview';
    if (path.startsWith('/data')) return 'Data Sources & Auditing';
    if (path.startsWith('/analysis/')) return 'Analysis Verification Result';
    if (path.startsWith('/analysis')) return 'Analysis Workspace';
    if (path.startsWith('/evidence')) return 'Document & Evidence Library';
    if (path.startsWith('/runs')) return 'Analysis Audit Runs';
    if (path.startsWith('/settings')) return 'System Settings';
    return 'Workspace';
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-20">
      <div className="flex items-center gap-3">
        <h2 className="text-base font-semibold text-slate-100">{getPageTitle()}</h2>
        <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-slate-800 text-slate-400 border border-slate-700/60">
          proofai-v1.4
        </span>
      </div>

      <div className="flex items-center gap-3">
        {/* Quick Active Dataset Badge */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/80 text-xs text-slate-300">
          <Database className="w-3.5 h-3.5 text-indigo-400" />
          <span>Active:</span>
          <span className="font-mono font-medium text-white">sales_data.csv</span>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={() => navigate('/data')}
          className="hidden sm:flex items-center gap-1.5"
        >
          <Database className="w-3.5 h-3.5" />
          Datasets
        </Button>

        <Button
          variant="primary"
          size="sm"
          onClick={() => navigate('/analysis')}
          className="flex items-center gap-1.5"
        >
          <Plus className="w-4 h-4" />
          <span>New Analysis</span>
        </Button>

        <button className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors relative">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-indigo-500" />
        </button>
      </div>
    </header>
  );
};
