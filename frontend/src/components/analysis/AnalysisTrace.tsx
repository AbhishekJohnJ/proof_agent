import React from 'react';
import { TraceStep } from '../../types';
import { CheckCircle2, AlertTriangle, Clock } from 'lucide-react';

interface AnalysisTraceProps {
  trace?: TraceStep[];
}

export const AnalysisTrace: React.FC<AnalysisTraceProps> = ({ trace }) => {
  if (!trace || trace.length === 0) {
    return <div className="p-8 text-center theme-text-muted">No trace log available.</div>;
  }

  return (
    <div className="space-y-4 p-2">
      <div className="flex items-center justify-between border-b theme-border pb-3">
        <h4 className="text-xs font-semibold uppercase tracking-wider flex items-center gap-2">
          <Clock className="w-4 h-4 text-[#E64A32]" /> Audit Timeline & Execution Log
        </h4>
        <span className="text-xs theme-text-muted font-mono">{trace.length} events logged</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead className="theme-input theme-text-muted uppercase font-sans border-b theme-border">
            <tr>
              <th className="px-4 py-2.5">Time</th>
              <th className="px-4 py-2.5">Execution Event</th>
              <th className="px-4 py-2.5">Status</th>
              <th className="px-4 py-2.5">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y theme-border theme-card">
            {trace.map((t, idx) => (
              <tr key={idx} className="hover:bg-[#3C3B39]/20 transition-colors">
                <td className="px-4 py-3 theme-text-muted font-semibold">{t.timestamp}</td>
                <td className="px-4 py-3 font-sans font-medium">{t.step}</td>
                <td className="px-4 py-3">
                  {t.status === 'completed' ? (
                    <span className="text-[#E64A32] flex items-center gap-1 font-semibold">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Done
                    </span>
                  ) : t.status === 'warning' ? (
                    <span className="text-[#E18230] flex items-center gap-1 font-semibold">
                      <AlertTriangle className="w-3.5 h-3.5" /> Warning
                    </span>
                  ) : (
                    <span className="theme-text-muted">{t.status}</span>
                  )}
                </td>
                <td className="px-4 py-3 theme-text-muted">{t.details || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
