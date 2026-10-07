import React from 'react';
import { DataQualityReport } from '../../types';
import { ShieldCheck, AlertTriangle, Info, CheckCircle2, ShieldAlert } from 'lucide-react';

interface DataQualityPanelProps {
  quality: DataQualityReport;
}

export const DataQualityPanel: React.FC<DataQualityPanelProps> = ({ quality }) => {
  return (
    <div className="bg-[#242726] border border-[#3C3B39] rounded-xl p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-[#3C3B39] pb-4">
        <div>
          <h3 className="text-base font-bold text-[#F4F5EC] flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-[#E64A32]" />
            Data Quality & Integrity Profiler
          </h3>
          <p className="text-xs text-[#F4F5EC]/60 mt-0.5">
            Automated evaluation of null rates, duplicate records, and schema anomalies
          </p>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-[#E64A32]/20 text-[#E64A32] border border-[#E64A32]/30 flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5" /> Audited
        </span>
      </div>

      {/* Critical Verification Trust Banner */}
      <div className="bg-[#E18230]/15 border border-[#E18230]/30 rounded-lg p-3.5 flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-[#E18230] shrink-0 mt-0.5" />
        <div className="text-xs text-[#F4F5EC] leading-relaxed">
          <span className="font-bold uppercase tracking-wider text-[#E18230]">
            Detected, not automatically modified.
          </span>{' '}
          ProofAI preserves raw data integrity. Identified nulls, duplicate rows, and date format ambiguities are audited and factored into verification calculations rather than mutated automatically.
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Missing Values breakdown */}
        <div className="space-y-3">
          <h4 className="text-xs font-semibold text-[#F4F5EC]/60 uppercase tracking-wider">
            Missing Values Breakdown
          </h4>
          <div className="bg-[#151918] border border-[#3C3B39] rounded-lg p-4 space-y-3 font-mono text-xs">
            {Object.entries(quality.missingValuesMap).map(([col, pct]) => (
              <div key={col} className="space-y-1">
                <div className="flex justify-between text-[#F4F5EC]">
                  <span>{col}</span>
                  <span className={pct > 0 ? 'text-[#E18230] font-semibold' : 'text-[#F4F5EC]/60'}>
                    {pct.toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-[#3C3B39] h-1.5 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${pct > 0 ? 'bg-[#E18230]' : 'bg-[#E64A32]'}`}
                    style={{ width: `${Math.max(pct, 2)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Duplicate & Warnings Breakdown */}
        <div className="space-y-3">
          <h4 className="text-xs font-semibold text-[#F4F5EC]/60 uppercase tracking-wider">
            Data Quality Warnings ({quality.warnings.length})
          </h4>
          <div className="space-y-2.5">
            <div className="bg-[#151918] border border-[#3C3B39] rounded-lg p-3 flex items-center justify-between text-xs font-mono">
              <span className="text-[#F4F5EC]">Duplicate Records</span>
              <span className="text-[#F4F5EC] bg-[#3C3B39] px-2 py-0.5 rounded border border-[#3C3B39]">
                {quality.duplicateRowsCount} records detected
              </span>
            </div>

            {quality.warnings.map((warn) => (
              <div
                key={warn.id}
                className="bg-[#151918] border border-[#3C3B39] rounded-lg p-3 flex items-start gap-2.5 text-xs"
              >
                {warn.severity === 'critical' ? (
                  <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                ) : warn.severity === 'warning' ? (
                  <AlertTriangle className="w-4 h-4 text-[#E18230] shrink-0 mt-0.5" />
                ) : (
                  <Info className="w-4 h-4 text-[#E64A32] shrink-0 mt-0.5" />
                )}
                <div>
                  <div className="font-semibold text-[#F4F5EC]">{warn.type}</div>
                  <div className="text-[#F4F5EC]/60 mt-0.5 leading-normal">{warn.message}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
