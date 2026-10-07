import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../common/Card';
import { UploadCloud, MessageSquarePlus, FileSearch, ArrowRight } from 'lucide-react';

export const QuickStart: React.FC = () => {
  const navigate = useNavigate();

  const cards = [
    {
      title: 'Analyze a Dataset',
      description: 'Upload CSV, Excel, or PDF files for automated schema profiling and validation.',
      icon: UploadCloud,
      action: () => navigate('/data'),
      cta: 'Upload Dataset',
      accent: 'text-indigo-400 bg-indigo-950/40 border-indigo-500/30',
    },
    {
      title: 'Ask a Question',
      description: 'Ask natural-language analytical questions. Code is computed and proven.',
      icon: MessageSquarePlus,
      action: () => navigate('/analysis'),
      cta: 'Ask Question',
      accent: 'text-emerald-400 bg-emerald-950/40 border-emerald-500/30',
    },
    {
      title: 'Inspect Evidence',
      description: 'Review formulas, execution trace, sandboxed code, and document source excerpts.',
      icon: FileSearch,
      action: () => navigate('/evidence'),
      cta: 'Browse Evidence',
      accent: 'text-sky-400 bg-sky-950/40 border-sky-500/30',
    },
  ];

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
        Quick Start
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {cards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <Card
              key={idx}
              hoverable
              onClick={card.action}
              className="flex flex-col justify-between group"
            >
              <div>
                <div
                  className={`w-10 h-10 rounded-lg border flex items-center justify-center mb-3 ${card.accent}`}
                >
                  <Icon className="w-5 h-5" />
                </div>
                <h4 className="text-base font-semibold text-white group-hover:text-indigo-300 transition-colors">
                  {card.title}
                </h4>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                  {card.description}
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center text-xs font-medium text-indigo-400 group-hover:text-indigo-300">
                {card.cta}
                <ArrowRight className="w-3.5 h-3.5 ml-1 transition-transform group-hover:translate-x-1" />
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
