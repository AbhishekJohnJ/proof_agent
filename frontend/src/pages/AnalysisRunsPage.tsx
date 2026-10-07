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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b theme-border pb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Analysis Runs</h1>
          <p className="text-sm theme-text-muted mt-1">
            Historical audit log of all completed, warning, and refused analytical calculations.
          </p>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 theme-text-muted absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by question or dataset..."
            className="w-full theme-input border theme-border rounded-lg pl-9 pr-4 py-2 text-sm focus:outline-none focus:border-[#E64A32]"
          />
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 border-b theme-border pb-3 overflow-x-auto">
        <Filter className="w-4 h-4 theme-text-muted shrink-0 mr-1" />
        {filterTabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setFilterStatus(tab.id as any)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              filterStatus === tab.id
                ? 'bg-[#E64A32]/15 text-[#E64A32] border border-[#E64A32]/30'
                : 'theme-text-muted hover:bg-[#3C3B39]/40'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Runs Table */}
      <div className="theme-card border theme-border rounded-xl overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="theme-input text-xs uppercase font-medium border-b theme-border">
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
            <tbody className="divide-y theme-border">
              {filteredAnalyses.map((item) => (
                <tr
                  key={item.id}
                  className="hover:bg-[#3C3B39]/30 transition-colors cursor-pointer"
                  onClick={() => navigate(`/analysis/${item.id}`)}
                >
                  <td className="px-5 py-3.5 font-semibold max-w-xs truncate">
                    {item.question}
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="inline-flex items-center gap-1.5 text-xs font-mono theme-input px-2 py-1 rounded border theme-border">
                      <Database className="w-3 h-3 text-[#E64A32]" />
                      {item.datasetName}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 max-w-xs truncate font-mono text-xs theme-text-muted">
                    {item.answer || item.refusalDetails?.reason || '—'}
                  </td>
                  <td className="px-5 py-3.5">
                    <StatusBadge status={item.status} size="sm" />
                  </td>
                  <td className="px-5 py-3.5">
                    <ConfidenceBadge confidence={item.confidence} size="sm" />
                  </td>
                  <td className="px-5 py-3.5 text-xs theme-text-muted font-mono">
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
