import React from 'react';
import { Send, Sparkles } from 'lucide-react';
import { Button } from '../common/Button';

interface QuestionInputProps {
  question: string;
  onChange: (val: string) => void;
  onSubmit: () => void;
  loading?: boolean;
}

export const QuestionInput: React.FC<QuestionInputProps> = ({
  question,
  onChange,
  onSubmit,
  loading = false,
}) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim() && !loading) {
      onSubmit();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="relative rounded-xl border border-[#3C3B39] bg-[#242726] shadow-lg p-2 focus-within:border-[#E64A32] focus-within:ring-2 focus-within:ring-[#E64A32]/20 transition-all">
        <textarea
          rows={3}
          value={question}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Example: Which region generated the highest revenue in Q4?"
          className="w-full bg-transparent text-[#F4F5EC] placeholder-[#F4F5EC]/40 text-base p-3 focus:outline-none resize-none"
        />

        <div className="flex items-center justify-between px-3 pt-2 border-t border-[#3C3B39]">
          <div className="flex items-center gap-2 text-xs text-[#F4F5EC]/60">
            <Sparkles className="w-3.5 h-3.5 text-[#E64A32]" />
            <span>Ask natural language analytical questions. Code is calculated & verified.</span>
          </div>

          <Button
            type="submit"
            variant="primary"
            size="md"
            disabled={!question.trim() || loading}
            className="flex items-center gap-2 shadow-md"
          >
            <Send className="w-4 h-4" />
            <span>{loading ? 'Analyzing...' : 'Run Analysis'}</span>
          </Button>
        </div>
      </div>
    </form>
  );
};
