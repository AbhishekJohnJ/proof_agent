import React, { useState } from 'react';
import { Analysis } from '../../types';
import { AlertTriangle, RefreshCw, FileText, Database, ShieldCheck, Check } from 'lucide-react';
import { Button } from '../common/Button';

interface ConflictCardProps {
  analysis: Analysis;
}

export const ConflictCard: React.FC<ConflictCardProps> = ({ analysis }) => {
  const conflict = analysis.conflictDetails;
  const [chosenSource, setChosenSource] = useState<'A' | 'B' | null>(null);

  return (
    <div className="bg-slate-900 border border-amber-500/30 rounded-2xl p-6 md:p-8 space-y-6 shadow-xl bg-gradient-to-b from-slate-900 via-amber-950/10 to-slate-950">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-amber-500/20 pb-5">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-amber-950/80 border border-amber-500/40 flex items-center justify-center text-amber-400">
            <AlertTriangle className="w-7 h-7" />
          </div>
          <div>
            <span className="px-2.5 py-0.5 rounded text-xs font-semibold uppercase tracking-wider bg-amber-950 text-amber-400 border border-amber-500/30">
              ⚠ Source Conflict Detected
            </span>
            <h2 className="text-2xl font-bold text-white mt-1">Conflicting values found across evidence sources</h2>
          </div>
        </div>
      </div>

      <p className="text-sm text-slate-300 leading-relaxed font-mono bg-slate-950/80 p-4 rounded-xl border border-slate-800">
        ProofAI will not arbitrarily choose between conflicting data sources without user authorization.
      </p>

      {/* Side by side comparison */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Source A */}
        <div
          onClick={() => setChosenSource('A')}
          className={`p-5 rounded-xl border transition-all cursor-pointer space-y-3 ${
            chosenSource === 'A'
              ? 'bg-indigo-950/50 border-indigo-500 shadow-md ring-1 ring-indigo-500'
              : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-2 text-xs font-mono text-slate-300">
              <FileText className="w-4 h-4 text-indigo-400" />
              {conflict?.sourceA.name}
            </span>
            {chosenSource === 'A' && (
              <span className="text-xs text-indigo-400 font-bold flex items-center gap-1">
                <Check className="w-3.5 h-3.5" /> Selected Authoritative
              </span>
            )}
          </div>
          <div className="text-2xl font-bold text-white font-mono">{conflict?.sourceA.val}</div>
          <p className="text-xs text-slate-400">Audited financial disclosure document</p>
        </div>

        {/* Source B */}
        <div
          onClick={() => setChosenSource('B')}
          className={`p-5 rounded-xl border transition-all cursor-pointer space-y-3 ${
            chosenSource === 'B'
              ? 'bg-indigo-950/50 border-indigo-500 shadow-md ring-1 ring-indigo-500'
              : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-2 text-xs font-mono text-slate-300">
              <Database className="w-4 h-4 text-emerald-400" />
              {conflict?.sourceB.name}
            </span>
            {chosenSource === 'B' && (
              <span className="text-xs text-indigo-400 font-bold flex items-center gap-1">
                <Check className="w-3.5 h-3.5" /> Selected Authoritative
              </span>
            )}
          </div>
          <div className="text-2xl font-bold text-white font-mono">{conflict?.sourceB.val}</div>
          <p className="text-xs text-slate-400">Raw unadjusted CSV transaction aggregation</p>
        </div>
      </div>

      {/* Explanation */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-2">
        <h4 className="text-xs font-semibold text-amber-400 uppercase tracking-wider flex items-center gap-2">
          <RefreshCw className="w-4 h-4" /> Root Cause Variance Analysis
        </h4>
        <p className="text-xs text-slate-300 leading-relaxed font-mono">
          {conflict?.explanation}
        </p>
      </div>

      {/* Action choices */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-slate-800">
        <span className="text-xs text-slate-400">
          Select an authoritative source above to proceed with calculation
        </span>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm">
            View Evidence Trace
          </Button>
          <Button variant="primary" size="sm" disabled={!chosenSource}>
            <ShieldCheck className="w-4 h-4" /> Confirm & Re-verify
          </Button>
        </div>
      </div>
    </div>
  );
};
