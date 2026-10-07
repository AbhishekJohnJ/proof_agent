import React from 'react';
import { TraceStep } from '../../types';
import { CheckCircle2, AlertTriangle, Clock } from 'lucide-react';

interface AnalysisTraceProps {
  trace?: TraceStep[];
}

export const AnalysisTrace: React.FC<AnalysisTraceProps> = ({ trace }) => {
  if (!trace || trace.length === 0) {
    return <div className="p-8 text-center text-slate-400">No trace log available.</div>;
  }

  return (
    <div className="space-y-4 p-2">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <Clock className="w-4 h-4 text-indigo-400" /> Audit Timeline & Execution Log
        </h4>
        <span className="text-xs text-slate-400 font-mono">{trace.length} events logged</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono text-slate-300">
          <thead className="bg-slate-950 text-slate-400 uppercase font-sans border-b border-slate-800">
            <tr>
              <th className="px-4 py-2.5">Time</th>
              <th className="px-4 py-2.5">Execution Event</th>
              <th className="px-4 py-2.5">Status</th>
              <th className="px-4 py-2.5">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 bg-slate-950/60">
            {trace.map((t, idx) => (
              <tr key={idx} className="hover:bg-slate-900/80 transition-colors">
                <td className="px-4 py-3 text-slate-400 font-semibold">{t.timestamp}</td>
                <td className="px-4 py-3 text-slate-100 font-sans font-medium">{t.step}</td>
                <td className="px-4 py-3">
                  {t.status === 'completed' ? (
                    <span className="text-emerald-400 flex items-center gap-1 font-semibold">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Done
                    </span>
                  ) : t.status === 'warning' ? (
                    <span className="text-amber-400 flex items-center gap-1 font-semibold">
                      <AlertTriangle className="w-3.5 h-3.5" /> Warning
                    </span>
                  ) : (
                    <span className="text-slate-400">{t.status}</span>
                  )}
                </td>
                <td className="px-4 py-3 text-slate-400">{t.details || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
