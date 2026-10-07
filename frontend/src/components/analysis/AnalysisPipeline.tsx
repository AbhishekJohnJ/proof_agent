import React, { useEffect, useState } from 'react';
import { CheckCircle2, Loader2, Circle, ShieldCheck } from 'lucide-react';
import { Card } from '../common/Card';

interface PipelineStep {
  id: string;
  label: string;
  status: 'pending' | 'running' | 'completed';
  timestamp?: string;
  detail?: string;
}

interface AnalysisPipelineProps {
  onComplete?: () => void;
  fastMode?: boolean;
}

export const AnalysisPipeline: React.FC<AnalysisPipelineProps> = ({ onComplete, fastMode = false }) => {
  const [steps, setSteps] = useState<PipelineStep[]>([
    { id: '1', label: 'Understanding question & classifying intent', status: 'pending', detail: 'Parsing temporal & numeric requirements' },
    { id: '2', label: 'Selecting relevant dataset (sales_data.csv)', status: 'pending', detail: 'Validating column schemas' },
    { id: '3', label: 'Generating analysis plan', status: 'pending', detail: 'Formulating mathematical model' },
    { id: '4', label: 'Generating Python code', status: 'pending', detail: 'Writing pandas aggregation logic' },
    { id: '5', label: 'Executing calculation in sandboxed runtime', status: 'pending', detail: 'Running Python 3.11 engine' },
    { id: '6', label: 'Verifying result against independent parser', status: 'pending', detail: 'Numerical tolerance check' },
    { id: '7', label: 'Checking reproducibility', status: 'pending', detail: 'Second pass calculation check' },
    { id: '8', label: 'Retrieving supporting document evidence', status: 'pending', detail: 'Scanning Annual_Report_2025.pdf' },
    { id: '9', label: 'Building final verified answer', status: 'pending', detail: 'Generating proof certificate' },
  ]);

  const [currentIdx, setCurrentIdx] = useState<number>(0);

  useEffect(() => {
    const delay = fastMode ? 250 : 600;

    const timer = setInterval(() => {
      setCurrentIdx((prev) => {
        if (prev >= steps.length - 1) {
          clearInterval(timer);
          if (onComplete) {
            setTimeout(onComplete, fastMode ? 200 : 500);
          }
          return prev;
        }
        return prev + 1;
      });
    }, delay);

    return () => clearInterval(timer);
  }, [steps.length, fastMode, onComplete]);

  return (
    <Card className="max-w-xl mx-auto border-indigo-500/30 bg-slate-900/90 p-8 shadow-xl">
      <div className="flex items-center gap-3 mb-6 pb-4 border-b border-slate-800">
        <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
          <ShieldCheck className="w-6 h-6 animate-pulse" />
        </div>
        <div>
          <h3 className="text-base font-bold text-white tracking-tight">ProofAI Verification Pipeline</h3>
          <p className="text-xs text-slate-400">Executing deterministic calculation and verification trace</p>
        </div>
      </div>

      <div className="relative pl-6 space-y-5 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-800">
        {steps.map((step, idx) => {
          const isDone = idx < currentIdx || (idx === steps.length - 1 && currentIdx === steps.length - 1);
          const isRunning = idx === currentIdx && currentIdx < steps.length - 1;

          return (
            <div key={step.id} className="relative flex items-start gap-3.5 group">
              <div
                className={`absolute -left-6 top-0.5 w-5 h-5 rounded-full flex items-center justify-center transition-all ${
                  isDone
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500'
                    : isRunning
                    ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500 animate-pulse'
                    : 'bg-slate-900 text-slate-600 border border-slate-800'
                }`}
              >
                {isDone ? (
                  <CheckCircle2 className="w-3.5 h-3.5" />
                ) : isRunning ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Circle className="w-2 h-2 fill-current" />
                )}
              </div>

              <div className="flex-1">
                <div
                  className={`text-sm font-medium transition-colors ${
                    isDone
                      ? 'text-slate-200'
                      : isRunning
                      ? 'text-indigo-300 font-semibold'
                      : 'text-slate-500'
                  }`}
                >
                  {step.label}
                </div>
                {step.detail && (
                  <div
                    className={`text-xs font-mono mt-0.5 transition-colors ${
                      isDone
                        ? 'text-slate-400'
                        : isRunning
                        ? 'text-indigo-400/90'
                        : 'text-slate-600'
                    }`}
                  >
                    {step.detail}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
};
