import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Analysis } from '../../types';
import { XCircle, ShieldAlert, Check, X, ArrowLeft } from 'lucide-react';
import { Button } from '../common/Button';

interface RefusalCardProps {
  analysis: Analysis;
}

export const RefusalCard: React.FC<RefusalCardProps> = ({ analysis }) => {
  const navigate = useNavigate();
  const details = analysis.refusalDetails;

  return (
    <div className="bg-slate-900 border border-rose-500/30 rounded-2xl p-6 md:p-8 space-y-6 shadow-xl relative overflow-hidden bg-gradient-to-b from-slate-900 via-rose-950/10 to-slate-950">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-rose-500/20 pb-5">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-rose-950/80 border border-rose-500/40 flex items-center justify-center text-rose-400">
            <XCircle className="w-7 h-7" />
          </div>
          <div>
            <span className="px-2.5 py-0.5 rounded text-xs font-semibold uppercase tracking-wider bg-rose-950 text-rose-400 border border-rose-500/30">
              ✕ Refused
            </span>
            <h2 className="text-2xl font-bold text-white mt-1">Unable to verify this answer</h2>
          </div>
        </div>
        <span className="text-xs font-mono text-slate-400">Audit Code: ERR_MISSING_SCHEMA</span>
      </div>

      {/* Main explanation */}
      <p className="text-sm text-slate-300 leading-relaxed font-mono bg-slate-950/80 p-4 rounded-xl border border-slate-800">
        ProofAI cannot calculate customer satisfaction by region because the uploaded dataset (
        <span className="text-indigo-400 font-bold">{analysis.datasetName}</span>) does not contain a
        customer satisfaction field.
      </p>

      {/* Columns Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
        {/* Available Relevant Fields */}
        <div className="space-y-3 bg-slate-950/60 p-5 rounded-xl border border-slate-800">
          <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            Available Relevant Fields
          </h4>
          <div className="grid grid-cols-2 gap-2 text-xs font-mono">
            {details?.availableFields.map((f, i) => (
              <div key={i} className="flex items-center gap-1.5 text-slate-300 bg-slate-900 px-2.5 py-1.5 rounded border border-slate-800">
                <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span className="truncate">{f}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Missing Required Fields */}
        <div className="space-y-3 bg-rose-950/20 p-5 rounded-xl border border-rose-500/20">
          <h4 className="text-xs font-semibold text-rose-300 uppercase tracking-wider flex items-center gap-2">
            Missing Required Fields
          </h4>
          <div className="space-y-2 text-xs font-mono">
            {details?.missingFields.map((f, i) => (
              <div key={i} className="flex items-center gap-1.5 text-rose-200 bg-rose-950/60 px-2.5 py-1.5 rounded border border-rose-500/30">
                <X className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                <span className="font-bold">{f}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Why We Stopped */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-2">
        <h4 className="text-xs font-semibold text-amber-400 uppercase tracking-wider flex items-center gap-2">
          <ShieldAlert className="w-4 h-4" /> Why we stopped
        </h4>
        <p className="text-xs text-slate-300 leading-relaxed font-mono">
          {details?.whyStopped}
        </p>
      </div>

      {/* Action */}
      <div className="pt-4 border-t border-slate-800 flex justify-end">
        <Button variant="primary" onClick={() => navigate('/analysis')}>
          <ArrowLeft className="w-4 h-4" /> Ask another question
        </Button>
      </div>
    </div>
  );
};
