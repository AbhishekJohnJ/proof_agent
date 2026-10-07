import React from 'react';
import { Card } from '../common/Card';
import { Calculator } from 'lucide-react';

interface ExplanationCardProps {
  explanation?: string;
}

export const ExplanationCard: React.FC<ExplanationCardProps> = ({ explanation }) => {
  if (!explanation) return null;

  return (
    <Card className="bg-slate-900 border-slate-800 p-6 space-y-3">
      <div className="flex items-center gap-2 text-xs font-semibold text-slate-300 uppercase tracking-wider border-b border-slate-800 pb-3">
        <Calculator className="w-4 h-4 text-indigo-400" />
        How we got this answer
      </div>
      <div className="text-sm text-slate-200 leading-relaxed font-mono whitespace-pre-line bg-slate-950/60 p-4 rounded-lg border border-slate-800/80">
        {explanation}
      </div>
    </Card>
  );
};
