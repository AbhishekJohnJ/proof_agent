'use client';

import React, { useState } from 'react';

interface QueryInputProps {
  onSubmit: (question: string) => void;
  loading: boolean;
}

export const QueryInput: React.FC<QueryInputProps> = ({ onSubmit, loading }) => {
  const [question, setQuestion] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    onSubmit(question);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a analytical numerical question (e.g., What is total revenue in sales.csv?)..."
          className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold text-sm px-6 py-3 rounded-xl transition-colors"
        >
          {loading ? 'Analyzing...' : 'Ask ProofAI'}
        </button>
      </div>
    </form>
  );
};
