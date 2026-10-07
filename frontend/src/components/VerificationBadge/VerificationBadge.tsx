'use client';

import React from 'react';
import { VerificationResult, CheckStatus } from '@/types';

interface VerificationBadgeProps {
  verification?: VerificationResult;
}

export const VerificationBadge: React.FC<VerificationBadgeProps> = ({ verification }) => {
  if (!verification) {
    return (
      <span className="px-3 py-1 bg-slate-800 text-slate-400 text-xs rounded-full font-semibold">
        UNVERIFIED
      </span>
    );
  }

  const isVerified = verification.status === 'VERIFIED';
  const isRefused = verification.status === 'REFUSED';
  const isModelPrediction = verification.status === 'MODEL_PREDICTION';
  const isDocumentSupported = verification.status === 'DOCUMENT_SUPPORTED';

  const renderCheckIcon = (status?: CheckStatus) => {
    if (status === 'PASS') return <span className="text-emerald-400 font-bold">✓ PASS</span>;
    if (status === 'FAIL') return <span className="text-rose-400 font-bold">✗ FAIL</span>;
    if (status === 'NOT_APPLICABLE') return <span className="text-slate-500">N/A</span>;
    return <span className="text-slate-500">NOT CHECKED</span>;
  };

  return (
    <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 space-y-3">
      <div className="flex items-center justify-between">
        <span
          className={`px-3 py-1 text-xs font-bold rounded-full border ${
            isVerified
              ? 'bg-emerald-950 text-emerald-400 border-emerald-800'
              : isRefused
              ? 'bg-amber-950 text-amber-400 border-amber-800'
              : isModelPrediction
              ? 'bg-purple-950 text-purple-400 border-purple-800'
              : isDocumentSupported
              ? 'bg-blue-950 text-blue-400 border-blue-800'
              : 'bg-rose-950 text-rose-400 border-rose-800'
          }`}
        >
          {isVerified
            ? '✓ PROVEN & VERIFIED'
            : isRefused
            ? '✋ REFUSED'
            : isModelPrediction
            ? '🤖 MODEL PREDICTION'
            : isDocumentSupported
            ? '📄 DOCUMENT SUPPORTED'
            : '❌ VERIFICATION FAILED'}
        </span>
        <span className="text-xs text-slate-400 font-mono">
          Confidence Score: <strong className="text-white">{(verification.confidence_score * 100).toFixed(0)}%</strong>
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs font-mono bg-slate-900/60 p-3 rounded-lg border border-slate-850">
        <div>Execution: {renderCheckIcon(verification.execution_success)}</div>
        <div>Output Valid: {renderCheckIcon(verification.output_valid)}</div>
        <div>Reproducible: {renderCheckIcon(verification.reproducible)}</div>
        <div>Datasets Used: {renderCheckIcon(verification.selected_datasets_used)}</div>
      </div>

      {verification.errors && verification.errors.length > 0 && (
        <div className="text-xs text-rose-400 bg-rose-950/40 border border-rose-900/60 p-2 rounded">
          {verification.errors.map((err, i) => (
            <p key={i}>• {err}</p>
          ))}
        </div>
      )}
    </div>
  );
};
