import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Analysis } from '../../types';
import { StatusBadge } from '../common/StatusBadge';
import { ConfidenceBadge } from '../common/ConfidenceBadge';
import { ArrowRight, Database } from 'lucide-react';
import { Button } from '../common/Button';

interface RecentAnalysesProps {
  analyses: Analysis[];
}

export const RecentAnalyses: React.FC<RecentAnalysesProps> = ({ analyses }) => {
  const navigate = useNavigate();

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-xs">
      <div className="p-5 border-b border-slate-800 flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold text-slate-100">Recent Analyses</h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Verified analytical runs and evidence checks
          </p>
        </div>
        <Button variant="ghost" size="sm" onClick={() => navigate('/runs')}>
          View all runs <ArrowRight className="w-3.5 h-3.5 ml-1" />
        </Button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-slate-950/60 text-slate-400 text-xs uppercase font-medium border-b border-slate-800">
            <tr>
              <th className="px-5 py-3">Analysis Question</th>
              <th className="px-5 py-3">Dataset</th>
              <th className="px-5 py-3">Status</th>
              <th className="px-5 py-3">Confidence</th>
              <th className="px-5 py-3">Date</th>
              <th className="px-5 py-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {analyses.map((item) => (
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
                <td className="px-5 py-3.5">
                  <StatusBadge status={item.status} size="sm" />
                </td>
                <td className="px-5 py-3.5">
                  <ConfidenceBadge confidence={item.confidence} size="sm" />
                </td>
                <td className="px-5 py-3.5 text-xs text-slate-400">{item.date}</td>
                <td className="px-5 py-3.5 text-right">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/analysis/${item.id}`);
                    }}
                  >
                    View Proof
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
