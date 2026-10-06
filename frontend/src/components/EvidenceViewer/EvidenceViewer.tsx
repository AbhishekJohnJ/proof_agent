'use client';

import React from 'react';
import { EvidenceItem } from '@/types';

interface EvidenceViewerProps {
  evidence: EvidenceItem[];
}

export const EvidenceViewer: React.FC<EvidenceViewerProps> = ({ evidence }) => {
  if (evidence.length === 0) return null;

  return (
    <div className="space-y-3">
      <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
        Evidence & Citation Chain
      </h4>
      <div className="grid gap-2">
        {evidence.map((item, idx) => (
          <div key={idx} className="bg-slate-900 border border-slate-800 rounded-lg p-3 text-xs">
            <div className="flex items-center justify-between font-mono mb-1">
              <span className="text-indigo-400 font-semibold uppercase">[{item.type}]</span>
              <span className="text-slate-400">{item.source}</span>
            </div>
            <p className="text-slate-200">{item.description}</p>
            {item.page_number && (
              <span className="inline-block mt-1 text-[11px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
                Page {item.page_number}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
