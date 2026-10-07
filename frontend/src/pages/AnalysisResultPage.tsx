import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Analysis } from '../types';
import { getAnalysisById } from '../services/analysis';
import { ResultCard } from '../components/analysis/ResultCard';
import { KPIGrid } from '../components/analysis/KPIGrid';
import { ExplanationCard } from '../components/analysis/ExplanationCard';
import { ProofTabs } from '../components/analysis/ProofTabs';
import { RefusalCard } from '../components/analysis/RefusalCard';
import { ConflictCard } from '../components/analysis/ConflictCard';
import { RevenueGrowthChart } from '../components/charts/RevenueGrowthChart';
import { RegionRevenueChart } from '../components/charts/RegionRevenueChart';
import { Button } from '../components/common/Button';
import { ArrowLeft, ShieldCheck, Check } from 'lucide-react';

export const AnalysisResultPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<Analysis | null>(null);

  useEffect(() => {
    if (id) {
      getAnalysisById(id).then((res) => setAnalysis(res || null));
    }
  }, [id]);

  if (!analysis) {
    return (
      <div className="p-12 text-center theme-text-muted font-mono">
        Loading verified analysis proof...
      </div>
    );
  }

  const isRefusal = analysis.status === 'refused';
  const isConflict = !!analysis.conflictDetails;

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Top Breadcrumb & Question */}
      <div className="space-y-3 border-b theme-border pb-6">
        <Button variant="ghost" size="sm" onClick={() => navigate('/analysis')} className="theme-text-muted">
          <ArrowLeft className="w-4 h-4" /> Back to Workspace
        </Button>

        <div>
          <span className="text-xs uppercase font-semibold theme-text-muted tracking-wider">
            Analysis Result & Verification Certificate
          </span>
          <h1 className="text-2xl md:text-3xl font-bold mt-1">{analysis.question}</h1>
        </div>
      </div>

      {/* Render Refusal State */}
      {isRefusal ? (
        <RefusalCard analysis={analysis} />
      ) : isConflict ? (
        /* Render Conflict State */
        <ConflictCard analysis={analysis} />
      ) : (
        /* Render Standard Verified Result */
        <>
          {/* Dominant Answer Card */}
          <ResultCard analysis={analysis} />

          {/* KPI Summary Row */}
          <KPIGrid kpis={analysis.kpis} />

          {/* Explanation Step-by-Step */}
          <ExplanationCard explanation={analysis.explanation} />

          {/* Proof Tabs */}
          <div className="space-y-3">
            <h3 className="text-xs font-semibold theme-text-muted uppercase tracking-wider">
              Verification Proof & Audit Tabs
            </h3>
            <ProofTabs analysis={analysis} />
          </div>

          {/* Confidence Indicator Section */}
          <div className="theme-card border theme-border rounded-xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b theme-border pb-3">
              <h3 className="text-base font-bold flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-[#E64A32]" /> Confidence Audit Assessment
              </h3>
              <span className="px-3 py-1 rounded-full text-xs font-bold uppercase bg-[#E64A32]/20 text-[#E64A32] border border-[#E64A32]/30">
                {analysis.confidence} Confidence
              </span>
            </div>

            <div className="space-y-2 text-xs font-mono">
              <div className="theme-text-muted uppercase font-sans font-semibold tracking-wider text-[11px] mb-2">
                Why was this confidence level assigned?
              </div>
              {analysis.verification?.confidenceReason.map((reason, idx) => (
                <div key={idx} className="flex items-center gap-2 theme-input p-2.5 rounded border theme-border">
                  <Check className="w-4 h-4 text-[#E64A32] shrink-0" />
                  <span>{reason}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Contextual Charts */}
          {analysis.charts && (
            <div className="space-y-3 pt-2">
              <h3 className="text-xs font-semibold theme-text-muted uppercase tracking-wider">
                Visual Proof Charts
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {analysis.charts.type === 'monthly_growth' && <RevenueGrowthChart />}
                <RegionRevenueChart />
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
