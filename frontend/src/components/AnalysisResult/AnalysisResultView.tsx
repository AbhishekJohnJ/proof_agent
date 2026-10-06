'use client';

import React from 'react';
import { AnalysisResultData } from '@/types';
import { VerificationBadge } from '../VerificationBadge/VerificationBadge';
import { CodeViewer } from '../CodeViewer/CodeViewer';
import { EvidenceViewer } from '../EvidenceViewer/EvidenceViewer';

interface AnalysisResultViewProps {
  result: AnalysisResultData;
}

export const AnalysisResultView: React.FC<AnalysisResultViewProps> = ({ result }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <span className="text-xs text-indigo-400 font-semibold uppercase tracking-wider">Analysis Result</span>
          <h2 className="text-lg font-bold text-white mt-1">{result.question}</h2>
        </div>
        <VerificationBadge verification={result.verification} />
      </div>

      <div className="bg-slate-950/60 border border-slate-800 rounded-lg p-4">
        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Answer Output</h4>
        <p className="text-sm font-medium text-slate-100">{result.answer}</p>
        {result.refusal_reason && (
          <p className="mt-2 text-xs text-amber-400 font-mono">Refusal reason: {result.refusal_reason}</p>
        )}
      </div>

      {result.code && <CodeViewer code={result.code} />}

      <EvidenceViewer evidence={result.evidence} />
    </div>
  );
};
