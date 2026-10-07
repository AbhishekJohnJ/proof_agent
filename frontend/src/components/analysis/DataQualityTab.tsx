import React from 'react';
import { DataQualityReport } from '../../types';
import { CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';

interface DataQualityTabProps {
  dataQuality?: DataQualityReport;
}

export const DataQualityTab: React.FC<DataQualityTabProps> = ({ dataQuality }) => {
  if (!dataQuality) {
    return <div className="p-8 text-center text-slate-400">No data quality report attached.</div>;
  }

  const checks = [
    { label: 'Required columns present', status: dataQuality.requiredColumnsPresent },
    { label: 'Numeric fields valid', status: dataQuality.numericFieldsValid },
    { label: 'No relevant missing values', status: dataQuality.noRelevantMissingValues },
    { label: 'No currency mismatch detected', status: !dataQuality.currencyMismatch },
  ];

  return (
    <div className="space-y-6 p-2">
      <div>
        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
          Dataset Health Signals
        </h4>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 font-mono text-xs">
          {checks.map((c, idx) => (
            <div
              key={idx}
              className="bg-slate-950 p-3.5 rounded-lg border border-slate-800 flex items-center justify-between"
            >
              <span className="text-slate-200 font-sans">{c.label}</span>
              {c.status ? (
                <span className="text-emerald-400 flex items-center gap-1 font-semibold">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Passed
                </span>
              ) : (
                <span className="text-rose-400 flex items-center gap-1 font-semibold">
                  <AlertTriangle className="w-3.5 h-3.5" /> Failed
                </span>
              )}
            </div>
          ))}

          {/* Duplicates check */}
          <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800 flex items-center justify-between">
            <span className="text-slate-200 font-sans">Duplicate records status</span>
            <span className="text-amber-400 flex items-center gap-1 font-semibold">
              <AlertTriangle className="w-3.5 h-3.5" /> {dataQuality.duplicateRowsCount} duplicates detected
            </span>
          </div>
        </div>
      </div>

      {/* Impact on this answer */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-2">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-emerald-400" />
          <h4 className="text-sm font-bold text-white uppercase tracking-wider">
            Impact on this answer
          </h4>
          <span className="ml-auto px-2.5 py-0.5 rounded text-xs font-semibold uppercase bg-emerald-950 text-emerald-400 border border-emerald-500/30">
            {dataQuality.impactLevel} Impact
          </span>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed font-mono pt-1">
          {dataQuality.impactOnAnswer}
        </p>
      </div>
    </div>
  );
};
