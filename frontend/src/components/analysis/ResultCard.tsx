import React from 'react';
import { Analysis } from '../../types';
import { StatusBadge } from '../common/StatusBadge';
import { ConfidenceBadge } from '../common/ConfidenceBadge';
import { ShieldCheck, ArrowUpRight } from 'lucide-react';

interface ResultCardProps {
  analysis: Analysis;
}

export const ResultCard: React.FC<ResultCardProps> = ({ analysis }) => {
  return (
    <div className="bg-slate-900 border border-slate-700/80 rounded-2xl p-6 md:p-8 shadow-xl relative overflow-hidden bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950">
      <div className="absolute top-0 right-0 p-8 opacity-5 pointer-events-none text-indigo-400">
        <ShieldCheck className="w-64 h-64" />
      </div>

      <div className="relative z-10 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <StatusBadge status={analysis.status} size="lg" />
            <ConfidenceBadge confidence={analysis.confidence} size="lg" />
          </div>

          <span className="text-xs font-mono text-slate-400 bg-slate-800/80 px-2.5 py-1 rounded border border-slate-700">
            ID: {analysis.id}
          </span>
        </div>

        <div className="pt-2">
          <p className="text-xs uppercase font-semibold text-slate-400 tracking-wider">
            Verified Answer
          </p>
          <h1 className="text-3xl md:text-4xl font-extrabold text-white mt-1 tracking-tight leading-tight">
            {analysis.answer || 'Answer calculated and verified.'}
          </h1>
        </div>

        <div className="flex items-center gap-2 text-xs text-emerald-400 font-mono pt-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Proven via Sandboxed Python Computation & Dual Verification Pass</span>
        </div>
      </div>
    </div>
  );
};
