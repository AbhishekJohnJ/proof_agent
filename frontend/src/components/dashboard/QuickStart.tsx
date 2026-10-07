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
      accent: 'text-[#E64A32] bg-[#E64A32]/15 border-[#E64A32]/30',
    },
    {
      title: 'Ask a Question',
      description: 'Ask natural-language analytical questions. Code is computed and proven.',
      icon: MessageSquarePlus,
      action: () => navigate('/analysis'),
      cta: 'Ask Question',
      accent: 'text-[#E18230] bg-[#E18230]/15 border-[#E18230]/30',
    },
    {
      title: 'Inspect Evidence',
      description: 'Review formulas, execution trace, sandboxed code, and document source excerpts.',
      icon: FileSearch,
      action: () => navigate('/evidence'),
      cta: 'Browse Evidence',
      accent: 'text-[#F4F5EC] bg-[#3C3B39] border-[#3C3B39]',
    },
  ];

  return (
    <div className="space-y-3">
      <h3 className="text-xs font-semibold text-[#F4F5EC]/60 uppercase tracking-wider">
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
                <h4 className="text-base font-bold text-[#F4F5EC] group-hover:text-[#E64A32] transition-colors">
                  {card.title}
                </h4>
                <p className="text-xs text-[#F4F5EC]/70 mt-1 leading-relaxed">
                  {card.description}
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-[#3C3B39] flex items-center text-xs font-bold text-[#E64A32] group-hover:text-[#E64A32]">
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
