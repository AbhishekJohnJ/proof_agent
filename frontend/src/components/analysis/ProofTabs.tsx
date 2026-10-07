import React, { useState } from 'react';
import { Analysis } from '../../types';
import { CalculationPanel } from './CalculationPanel';
import { CodePanel } from './CodePanel';
import { EvidencePanel } from './EvidencePanel';
import { DataQualityTab } from './DataQualityTab';
import { AnalysisTrace } from './AnalysisTrace';
import { Calculator, Code2, FileCheck, ShieldCheck, Activity } from 'lucide-react';
import { cn } from '../../lib/utils';

interface ProofTabsProps {
  analysis: Analysis;
}

export const ProofTabs: React.FC<ProofTabsProps> = ({ analysis }) => {
  const [activeTab, setActiveTab] = useState<'calculation' | 'code' | 'evidence' | 'quality' | 'trace'>(
    'calculation'
  );

  const tabs = [
    { id: 'calculation', label: 'Calculation', icon: Calculator },
    { id: 'code', label: 'Code', icon: Code2 },
    { id: 'evidence', label: 'Evidence', icon: FileCheck },
    { id: 'quality', label: 'Data Quality', icon: ShieldCheck },
    { id: 'trace', label: 'Analysis Trace', icon: Activity },
  ] as const;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-md">
      {/* Tabs Header */}
      <div className="flex items-center gap-1 bg-slate-950/80 p-2 border-b border-slate-800 overflow-x-auto no-scrollbar">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all whitespace-nowrap cursor-pointer',
                isActive
                  ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/40 shadow-xs'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              )}
            >
              <Icon className={cn('w-4 h-4', isActive ? 'text-indigo-400' : 'text-slate-400')} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Body */}
      <div className="p-6 bg-slate-900/90">
        {activeTab === 'calculation' && <CalculationPanel calculation={analysis.calculation} />}
        {activeTab === 'code' && <CodePanel codeDetails={analysis.codeDetails} />}
        {activeTab === 'evidence' && <EvidencePanel evidence={analysis.evidence} />}
        {activeTab === 'quality' && <DataQualityTab dataQuality={analysis.dataQuality} />}
        {activeTab === 'trace' && <AnalysisTrace trace={analysis.trace} />}
      </div>
    </div>
  );
};
