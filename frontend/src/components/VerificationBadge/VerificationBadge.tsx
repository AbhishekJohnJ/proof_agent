'use client';

import React from 'react';
import { VerificationResult } from '@/types';

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

  const isVerified = verification.status === 'verified';
  const isRefused = verification.status === 'refused';

  return (
    <div className="flex items-center gap-3">
      <span
        className={`px-3 py-1 text-xs font-bold rounded-full border ${
          isVerified
            ? 'bg-emerald-950 text-emerald-400 border-emerald-800'
            : isRefused
            ? 'bg-amber-950 text-amber-400 border-amber-800'
            : 'bg-rose-950 text-rose-400 border-rose-800'
        }`}
      >
        {isVerified ? '✓ PROVEN & VERIFIED' : isRefused ? '✋ REFUSED' : '❌ VERIFICATION FAILED'}
      </span>
      <span className="text-xs text-slate-400 font-mono">
        Confidence Score: <strong className="text-white">{(verification.confidence_score * 100).toFixed(0)}%</strong>
      </span>
    </div>
  );
};
