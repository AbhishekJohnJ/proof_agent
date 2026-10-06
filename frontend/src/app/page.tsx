'use client';

import React, { useState, useEffect } from 'react';
import { FileUpload } from '@/components/FileUpload/FileUpload';
import { DatasetProfileView } from '@/components/DatasetProfile/DatasetProfileView';
import { QueryInput } from '@/components/QueryInput/QueryInput';
import { AnalysisResultView } from '@/components/AnalysisResult/AnalysisResultView';
import { fetchDatasets, fetchDatasetProfile, submitQuery } from '@/services/api';
import { DatasetProfile, AnalysisResultData } from '@/types';

export default function Home() {
  const [datasets, setDatasets] = useState<any[]>([]);
  const [activeProfile, setActiveProfile] = useState<DatasetProfile | null>(null);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResultData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadDatasets = async () => {
    try {
      const dsList = await fetchDatasets();
      setDatasets(dsList);
      if (dsList.length > 0 && !selectedDatasetId) {
        setSelectedDatasetId(dsList[0].dataset_id);
        const profile = await fetchDatasetProfile(dsList[0].dataset_id);
        setActiveProfile(profile);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadDatasets();
  }, []);

  const handleUploadSuccess = async (uploadRes: any) => {
    if (uploadRes.type === 'dataset') {
      await loadDatasets();
      setSelectedDatasetId(uploadRes.id);
      setActiveProfile(uploadRes.profile);
    }
  };

  const handleQuerySubmit = async (question: string) => {
    setLoading(true);
    setError(null);
    try {
      const selectedDs = selectedDatasetId ? [selectedDatasetId] : datasets.map((d) => d.dataset_id);
      const res = await submitQuery(question, selectedDs, []);
      setAnalysisResult(res);
    } catch (err: any) {
      setError(err.message || 'Analysis request failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-10 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <header className="border-b border-slate-800 pb-6 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="bg-indigo-600 text-white font-black px-2.5 py-1 rounded text-sm tracking-wider">ProofAI</span>
              <span className="text-xs font-mono text-indigo-400">HNX26PSI08 — HackNex 2026</span>
            </div>
            <h1 className="text-2xl font-bold text-white mt-2">Proof-Carrying Data Analyst</h1>
            <p className="text-sm text-slate-400 mt-1">
              &quot;An AI Data Analyst That Proves Its Answers.&quot; — LLM proposes → Code computes → Verifier proves
            </p>
          </div>
        </header>

        {/* Upload & Workspace Grid */}
        <div className="grid md:grid-cols-3 gap-6">
          <div className="md:col-span-1 space-y-4">
            <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">Data Ingestion</h2>
            <FileUpload onUploadSuccess={handleUploadSuccess} />

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Uploaded Datasets</h3>
              {datasets.length === 0 ? (
                <p className="text-xs text-slate-500 italic">No datasets uploaded yet.</p>
              ) : (
                <ul className="space-y-1 font-mono text-xs">
                  {datasets.map((ds) => (
                    <li
                      key={ds.dataset_id}
                      onClick={async () => {
                        setSelectedDatasetId(ds.dataset_id);
                        const prof = await fetchDatasetProfile(ds.dataset_id);
                        setActiveProfile(prof);
                      }}
                      className={`p-2 rounded cursor-pointer transition-colors ${
                        selectedDatasetId === ds.dataset_id ? 'bg-indigo-900/50 text-indigo-300 font-semibold' : 'hover:bg-slate-800 text-slate-300'
                      }`}
                    >
                      📄 {ds.filename} ({ds.rows} rows)
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          <div className="md:col-span-2 space-y-6">
            <QueryInput onSubmit={handleQuerySubmit} loading={loading} />

            {error && (
              <div className="bg-rose-950/50 border border-rose-800 text-rose-300 p-4 rounded-xl text-xs font-mono">
                {error}
              </div>
            )}

            {analysisResult && <AnalysisResultView result={analysisResult} />}

            {activeProfile && <DatasetProfileView profile={activeProfile} />}
          </div>
        </div>
      </div>
    </main>
  );
}
