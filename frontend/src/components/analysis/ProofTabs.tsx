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
    <div className="bg-[#242726] border border-[#3C3B39] rounded-xl overflow-hidden shadow-md">
      {/* Tabs Header */}
      <div className="flex items-center gap-1 bg-[#151918] p-2 border-b border-[#3C3B39] overflow-x-auto no-scrollbar">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all whitespace-nowrap cursor-pointer',
                isActive
                  ? 'bg-[#E64A32]/20 text-[#E64A32] border border-[#E64A32]/40 shadow-xs'
                  : 'text-[#F4F5EC]/60 hover:text-[#F4F5EC] hover:bg-[#3C3B39]/50'
              )}
            >
              <Icon className={cn('w-4 h-4', isActive ? 'text-[#E64A32]' : 'text-[#F4F5EC]/50')} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Body */}
      <div className="p-6 bg-[#242726]">
        {activeTab === 'calculation' && <CalculationPanel calculation={analysis.calculation} />}
        {activeTab === 'code' && <CodePanel codeDetails={analysis.codeDetails} />}
        {activeTab === 'evidence' && <EvidencePanel evidence={analysis.evidence} />}
        {activeTab === 'quality' && <DataQualityTab dataQuality={analysis.dataQuality} />}
        {activeTab === 'trace' && <AnalysisTrace trace={analysis.trace} />}
      </div>
    </div>
  );
};
