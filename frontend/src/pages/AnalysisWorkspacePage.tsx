import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { QuestionInput } from '../components/analysis/QuestionInput';
import { SuggestedQuestions } from '../components/analysis/SuggestedQuestions';
import { AnalysisPipeline } from '../components/analysis/AnalysisPipeline';
import { createAnalysis } from '../services/analysis';
import { Database, FileCheck, Layers, Columns, ShieldCheck } from 'lucide-react';
import { Card } from '../components/common/Card';

export const AnalysisWorkspacePage: React.FC = () => {
  const navigate = useNavigate();
  const [question, setQuestion] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeDataset] = useState({
    name: 'sales_data.csv',
    rows: 10482,
    columns: 12,
  });

  const handleRun = async () => {
    if (!question.trim()) return;
    setIsProcessing(true);
  };

  const handlePipelineComplete = async () => {
    const analysis = await createAnalysis(question, 'ds-1', activeDataset.name);
    setIsProcessing(false);
    navigate(`/analysis/${analysis.id}`);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Page Title */}
      <div className="border-b theme-border pb-4">
        <h1 className="text-2xl font-bold tracking-tight">Analysis Workspace</h1>
        <p className="text-sm theme-text-muted mt-1">
          Formulate analytical queries. ProofAI computes code and verifies answers.
        </p>
      </div>

      {isProcessing ? (
        <AnalysisPipeline onComplete={handlePipelineComplete} />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
          {/* Left Panel: Data Context */}
          <div className="space-y-4">
            <h3 className="text-xs font-semibold theme-text-muted uppercase tracking-wider">
              Active Data Context
            </h3>

            <Card className="space-y-4">
              <div className="flex items-center gap-3 border-b theme-border pb-3">
                <div className="w-10 h-10 rounded-lg bg-[#E64A32]/15 border border-[#E64A32]/30 flex items-center justify-center text-[#E64A32]">
                  <Database className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold font-mono">{activeDataset.name}</h4>
                  <span className="text-[11px] font-mono text-[#E64A32] flex items-center gap-1 font-semibold">
                    <ShieldCheck className="w-3 h-3" /> Ready for verification
                  </span>
                </div>
              </div>

              <div className="space-y-2 text-xs font-mono">
                <div className="flex justify-between theme-text-muted py-1 border-b theme-border">
                  <span className="flex items-center gap-1.5 font-sans">
                    <Layers className="w-3.5 h-3.5" /> Total Rows
                  </span>
                  <span className="font-bold">{activeDataset.rows.toLocaleString()}</span>
                </div>
                <div className="flex justify-between theme-text-muted py-1 border-b theme-border">
                  <span className="flex items-center gap-1.5 font-sans">
                    <Columns className="w-3.5 h-3.5" /> Columns
                  </span>
                  <span className="font-bold">{activeDataset.columns}</span>
                </div>
                <div className="flex justify-between theme-text-muted py-1">
                  <span className="flex items-center gap-1.5 font-sans">
                    <FileCheck className="w-3.5 h-3.5" /> Evidence PDF
                  </span>
                  <span className="text-[#E64A32] font-semibold">Annual_Report_2025.pdf</span>
                </div>
              </div>
            </Card>

            <div className="theme-card border theme-border rounded-xl p-4 text-xs leading-relaxed space-y-2">
              <div className="font-bold uppercase tracking-wider text-[11px] text-[#E18230]">
                Deterministic Engine Rules
              </div>
              <p className="theme-text-muted">• LLM proposes analysis plan & pandas script</p>
              <p className="theme-text-muted">• Script executes in sandboxed Python 3.11</p>
              <p className="theme-text-muted">• Numerical result is independently double-verified</p>
              <p className="theme-text-muted">• If required dataset columns are missing, query is refused</p>
            </div>
          </div>

          {/* Right Panel: Ask ProofAI */}
          <div className="lg:col-span-2 space-y-6">
            <div className="space-y-2">
              <h3 className="text-xs font-semibold theme-text-muted uppercase tracking-wider">
                Ask ProofAI
              </h3>
              <QuestionInput
                question={question}
                onChange={setQuestion}
                onSubmit={handleRun}
                loading={isProcessing}
              />
            </div>

            <SuggestedQuestions onSelect={(q) => setQuestion(q)} />
          </div>
        </div>
      )}
    </div>
  );
};
