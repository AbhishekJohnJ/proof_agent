import React from 'react';
import { HelpCircle, AlertCircle, RefreshCw } from 'lucide-react';

interface SuggestedQuestionsProps {
  onSelect: (q: string) => void;
}

export const SuggestedQuestions: React.FC<SuggestedQuestionsProps> = ({ onSelect }) => {
  const suggestions = [
    { text: 'What is the total revenue?', type: 'standard' },
    { text: 'Which region generated the highest revenue?', type: 'standard' },
    { text: 'What was the revenue growth between Q3 and Q4?', type: 'highlight' },
    { text: 'Which product had the highest profit margin?', type: 'standard' },
    { text: 'Are there duplicate records?', type: 'standard' },
    { text: 'Are there unusual values?', type: 'standard' },
    { text: 'What is customer satisfaction by region?', type: 'refusal' },
    { text: 'Compare Q4 revenue between financial report and sales dataset', type: 'conflict' },
  ];

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
        <span className="flex items-center gap-1.5 uppercase tracking-wider text-[11px]">
          <HelpCircle className="w-3.5 h-3.5 text-indigo-400" /> Suggested Questions
        </span>
        <span className="text-[11px] text-slate-400">Click any question to load</span>
      </div>

      <div className="flex flex-wrap gap-2">
        {suggestions.map((item, idx) => {
          const isRefusal = item.type === 'refusal';
          const isConflict = item.type === 'conflict';
          const isHighlight = item.type === 'highlight';

          return (
            <button
              key={idx}
              onClick={() => onSelect(item.text)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all text-left flex items-center gap-1.5 cursor-pointer ${
                isRefusal
                  ? 'bg-rose-950/40 text-rose-300 border-rose-500/30 hover:bg-rose-950/70 hover:border-rose-500/50'
                  : isConflict
                  ? 'bg-amber-950/40 text-amber-300 border-amber-500/30 hover:bg-amber-950/70 hover:border-amber-500/50'
                  : isHighlight
                  ? 'bg-indigo-950/60 text-indigo-200 border-indigo-500/40 hover:bg-indigo-900/80 hover:border-indigo-500'
                  : 'bg-slate-900 text-slate-300 border-slate-800 hover:bg-slate-800 hover:text-white'
              }`}
            >
              {isRefusal && <AlertCircle className="w-3 h-3 text-rose-400" />}
              {isConflict && <RefreshCw className="w-3 h-3 text-amber-400" />}
              <span>{item.text}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
