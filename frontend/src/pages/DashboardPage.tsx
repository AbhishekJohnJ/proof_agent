import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Analysis } from '../types';
import { getAnalyses } from '../services/analysis';
import { StatCard } from '../components/dashboard/StatCard';
import { RecentAnalyses } from '../components/dashboard/RecentAnalyses';
import { QuickStart } from '../components/dashboard/QuickStart';
import { Button } from '../components/common/Button';
import { CheckCircle2, ShieldCheck, Database, Activity, Plus, UploadCloud } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState<Analysis[]>([]);

  useEffect(() => {
    getAnalyses().then(setAnalyses);
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b theme-border pb-6">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
            Good morning
          </h1>
          <p className="text-sm theme-text-muted mt-1">
            Analyze your data with answers you can verify.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={() => navigate('/data')}>
            <UploadCloud className="w-4 h-4" /> Upload Dataset
          </Button>
          <Button variant="primary" onClick={() => navigate('/analysis')}>
            <Plus className="w-4 h-4" /> New Analysis
          </Button>
        </div>
      </div>

      {/* KPI Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Analyses completed"
          value="128"
          subtext="Executed in Python sandbox"
          icon={Activity}
          trend="+14% this week"
          accentColor="red"
        />
        <StatCard
          label="Verified answers"
          value="116"
          subtext="100% mathematical audit"
          icon={CheckCircle2}
          trend="90.6% success"
          accentColor="red"
        />
        <StatCard
          label="Datasets"
          value="8"
          subtext="45.2 MB indexed data"
          icon={Database}
          accentColor="slate"
        />
        <StatCard
          label="Verification rate"
          value="90.6%"
          subtext="Strictly audited rules"
          icon={ShieldCheck}
          trend="High confidence"
          accentColor="red"
        />
      </div>

      {/* Quick Start Cards */}
      <QuickStart />

      {/* Recent Analysis Table */}
      <RecentAnalyses analyses={analyses.slice(0, 5)} />
    </div>
  );
};
