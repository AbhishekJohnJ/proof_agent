import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Analysis, AnalysisStatus } from '../types';
import { getAnalyses } from '../services/analysis';
import { StatusBadge } from '../components/common/StatusBadge';
import { ConfidenceBadge } from '../components/common/ConfidenceBadge';
import { Search, Database, ArrowRight, Filter } from 'lucide-react';
import { Button } from '../components/common/Button';

export const AnalysisRunsPage: React.FC = () => {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState<AnalysisStatus | 'all'>('all');

  useEffect(() => {
    getAnalyses().then(setAnalyses);
  }, []);

  const filteredAnalyses = analyses.filter((item) => {
    const matchesQuery =
      item.question.toLowerCase().includes(search.toLowerCase()) ||
      item.datasetName.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filterStatus === 'all' || item.status === filterStatus;
    return matchesQuery && matchesFilter;
  });

  const filterTabs = [
    { id: 'all', label: 'All Runs' },
    { id: 'verified', label: 'Verified' },
    { id: 'warning', label: 'Warning' },
    { id: 'refused', label: 'Refused' },
    { id: 'failed', label: 'Failed' },
  ] as const;

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Analysis Runs</h1>
          <p className="text-sm text-slate-400 mt-1">
            Historical audit log of all completed, warning, and refused analytical calculations.
          </p>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by question or dataset..."
            className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-3 overflow-x-auto">
        <Filter className="w-4 h-4 text-slate-400 shrink-0 mr-1" />
        {filterTabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setFilterStatus(tab.id as any)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              filterStatus === tab.id
                ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Runs Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950/80 text-slate-400 text-xs uppercase font-medium border-b border-slate-800">
              <tr>
                <th className="px-5 py-3">Question</th>
                <th className="px-5 py-3">Dataset</th>
                <th className="px-5 py-3">Result Preview</th>
                <th className="px-5 py-3">Verification</th>
                <th className="px-5 py-3">Confidence</th>
                <th className="px-5 py-3">Timestamp</th>
                <th className="px-5 py-3 text-right">View</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredAnalyses.map((item) => (
                <tr
                  key={item.id}
                  className="hover:bg-slate-800/40 transition-colors cursor-pointer"
                  onClick={() => navigate(`/analysis/${item.id}`)}
                >
                  <td className="px-5 py-3.5 font-medium text-slate-100 max-w-xs truncate">
                    {item.question}
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="inline-flex items-center gap-1.5 text-xs font-mono text-slate-400 bg-slate-800/60 px-2 py-1 rounded border border-slate-700/50">
                      <Database className="w-3 h-3 text-indigo-400" />
                      {item.datasetName}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 max-w-xs truncate font-mono text-xs text-slate-300">
                    {item.answer || item.refusalDetails?.reason || '—'}
                  </td>
                  <td className="px-5 py-3.5">
                    <StatusBadge status={item.status} size="sm" />
                  </td>
                  <td className="px-5 py-3.5">
                    <ConfidenceBadge confidence={item.confidence} size="sm" />
                  </td>
                  <td className="px-5 py-3.5 text-xs text-slate-400 font-mono">
                    {item.timestamp || item.date}
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/analysis/${item.id}`);
                      }}
                    >
                      Inspect <ArrowRight className="w-3 h-3 ml-1" />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
