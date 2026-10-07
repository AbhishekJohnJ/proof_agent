import React from 'react';
import { Card } from '../common/Card';
import { Calculator } from 'lucide-react';

interface ExplanationCardProps {
  explanation?: string;
}

export const ExplanationCard: React.FC<ExplanationCardProps> = ({ explanation }) => {
  if (!explanation) return null;

  return (
    <Card className="bg-[#242726] border-[#3C3B39] p-6 space-y-3">
      <div className="flex items-center gap-2 text-xs font-bold text-[#F4F5EC] uppercase tracking-wider border-b border-[#3C3B39] pb-3">
        <Calculator className="w-4 h-4 text-[#E64A32]" />
        How we got this answer
      </div>
      <div className="text-sm text-[#F4F5EC] leading-relaxed font-mono whitespace-pre-line bg-[#151918] p-4 rounded-lg border border-[#3C3B39]">
        {explanation}
      </div>
    </Card>
  );
};
