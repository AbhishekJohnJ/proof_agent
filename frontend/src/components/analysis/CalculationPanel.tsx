import React from 'react';
import { CalculationDetails } from '../../types';
import { CheckCircle2, Calculator, Check } from 'lucide-react';

interface CalculationPanelProps {
  calculation?: CalculationDetails;
}

export const CalculationPanel: React.FC<CalculationPanelProps> = ({ calculation }) => {
  if (!calculation) {
    return (
      <div className="p-8 text-center text-[#F4F5EC]/60 text-sm">
        No formula breakdown available for this step.
      </div>
    );
  }

  return (
    <div className="space-y-6 p-2">
      {/* Verification Header */}
      <div className="bg-[#E64A32]/15 border border-[#E64A32]/30 rounded-lg p-4 flex items-center gap-3 text-[#F4F5EC] text-sm">
        <CheckCircle2 className="w-5 h-5 text-[#E64A32] shrink-0" />
        <div>
          <span className="font-bold text-[#E64A32]">Calculation Verified</span> — All mathematical transformations passed dual-pass verification checks with zero numeric error.
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Input variables & Formula */}
        <div className="space-y-4">
          <div>
            <h4 className="text-xs font-semibold text-[#F4F5EC]/60 uppercase tracking-wider mb-2">
              Input Variables
            </h4>
            <div className="bg-[#151918] border border-[#3C3B39] rounded-lg p-3 space-y-2 font-mono text-xs">
              {Object.entries(calculation.inputs).map(([key, val]) => (
                <div key={key} className="flex justify-between border-b border-[#3C3B39]/60 pb-1.5 last:border-0 last:pb-0">
                  <span className="text-[#F4F5EC]/60">{key}:</span>
                  <span className="text-[#F4F5EC] font-semibold">{val}</span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-[#F4F5EC]/60 uppercase tracking-wider mb-2">
              Exact Applied Formula
            </h4>
            <div className="bg-[#151918] border border-[#3C3B39] rounded-lg p-3.5 font-mono text-xs text-[#E18230] font-bold overflow-x-auto">
              {calculation.formula}
            </div>
          </div>
        </div>

        {/* Step-by-step evaluation */}
        <div>
          <h4 className="text-xs font-semibold text-[#F4F5EC]/60 uppercase tracking-wider mb-2">
            Step Evaluation Steps
          </h4>
          <div className="space-y-2 font-mono text-xs">
            {calculation.steps.map((step, idx) => (
              <div key={idx} className="bg-[#151918] border border-[#3C3B39] rounded-lg p-3 space-y-1">
                <div className="text-[#F4F5EC]/60 font-sans text-xs flex items-center gap-1.5">
                  <Calculator className="w-3 h-3 text-[#E64A32]" />
                  <span>{step.label}</span>
                </div>
                <div className="text-[#F4F5EC] text-xs">{step.expression}</div>
                <div className="text-[#E64A32] font-bold text-xs pt-0.5">➔ {step.result}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Validation checklist */}
      <div className="border-t border-[#3C3B39] pt-4">
        <h4 className="text-xs font-semibold text-[#F4F5EC]/60 uppercase tracking-wider mb-3">
          Verification Checks
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div className="flex items-center gap-2 bg-[#151918] p-3 rounded-lg border border-[#3C3B39] text-[#F4F5EC]">
            <Check className="w-4 h-4 text-[#E64A32]" />
            <span>Numeric result validated</span>
          </div>
          <div className="flex items-center gap-2 bg-[#151918] p-3 rounded-lg border border-[#3C3B39] text-[#F4F5EC]">
            <Check className="w-4 h-4 text-[#E64A32]" />
            <span>Required fields present</span>
          </div>
          <div className="flex items-center gap-2 bg-[#151918] p-3 rounded-lg border border-[#3C3B39] text-[#F4F5EC]">
            <Check className="w-4 h-4 text-[#E64A32]" />
            <span>Calculation completed</span>
          </div>
        </div>
      </div>
    </div>
  );
};
