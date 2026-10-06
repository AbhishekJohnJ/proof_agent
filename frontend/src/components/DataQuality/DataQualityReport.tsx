'use client';

import React from 'react';
import { QualityWarning } from '@/types';

interface DataQualityReportProps {
  status: string;
  warnings: QualityWarning[];
}

export const DataQualityReport: React.FC<DataQualityReportProps> = ({ status, warnings }) => {
  const statusColors = {
    good: 'bg-emerald-950/40 text-emerald-400 border-emerald-800/50',
    medium: 'bg-amber-950/40 text-amber-400 border-amber-800/50',
    poor: 'bg-rose-950/40 text-rose-400 border-rose-800/50',
    unprocessable: 'bg-red-950/40 text-red-400 border-red-800/50',
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
          Data Quality Engine Report
        </h4>
        <span
          className={`px-2.5 py-0.5 text-xs font-semibold rounded-full border ${
            statusColors[status as keyof typeof statusColors] || statusColors.good
          }`}
        >
          {status.toUpperCase()}
        </span>
      </div>

      {warnings.length === 0 ? (
        <p className="text-xs text-slate-400 italic">No quality anomalies detected.</p>
      ) : (
        <div className="space-y-2">
          {warnings.map((w, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-lg border text-xs ${
                w.severity === 'critical'
                  ? 'bg-rose-950/30 border-rose-800/40 text-rose-200'
                  : 'bg-amber-950/30 border-amber-800/40 text-amber-200'
              }`}
            >
              <div className="font-semibold flex items-center justify-between">
                <span>⚠️ [{w.type.toUpperCase()}]</span>
                <span className="uppercase text-[10px] opacity-75">{w.severity}</span>
              </div>
              <p className="mt-1 opacity-90">{w.message}</p>
              {w.affected_columns.length > 0 && (
                <p className="mt-1 font-mono text-[11px] opacity-75">
                  Affected: {w.affected_columns.join(', ')}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
