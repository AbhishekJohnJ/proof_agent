'use client';

import React, { useState, useEffect } from 'react';
import { FileUpload } from '@/components/FileUpload/FileUpload';
import { DatasetProfileView } from '@/components/DatasetProfile/DatasetProfileView';
import { QueryInput } from '@/components/QueryInput/QueryInput';
import { AnalysisResultView } from '@/components/AnalysisResult/AnalysisResultView';
import { fetchDatasets, fetchDatasetProfile, fetchDocuments, submitQuery } from '@/services/api';
import { DatasetProfile, DocumentMetadata, AnalysisResultData } from '@/types';

export default function Home() {
  const [datasets, setDatasets] = useState<any[]>([]);
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [selectedDatasetIds, setSelectedDatasetIds] = useState<string[]>([]);
  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>([]);
  
  const [activeProfile, setActiveProfile] = useState<DatasetProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResultData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadWorkspace = async () => {
    try {
      const dsList = await fetchDatasets();
      setDatasets(dsList);
      if (dsList.length > 0 && selectedDatasetIds.length === 0) {
        setSelectedDatasetIds([dsList[0].dataset_id]);
        const profile = await fetchDatasetProfile(dsList[0].dataset_id);
        setActiveProfile(profile);
      }

      const docList = await fetchDocuments();
      setDocuments(docList);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadWorkspace();
  }, []);

  const handleUploadSuccess = async (uploadRes: any) => {
    await loadWorkspace();
    if (uploadRes.type === 'dataset') {
      setSelectedDatasetIds((prev) => [...new Set([...prev, uploadRes.id])]);
      setActiveProfile(uploadRes.profile);
    } else if (uploadRes.type === 'document') {
      setSelectedDocumentIds((prev) => [...new Set([...prev, uploadRes.id])]);
    }
  };

  const toggleDatasetSelection = async (dsId: string) => {
    if (selectedDatasetIds.includes(dsId)) {
      setSelectedDatasetIds(selectedDatasetIds.filter((id) => id !== dsId));
    } else {
      setSelectedDatasetIds([...selectedDatasetIds, dsId]);
      const prof = await fetchDatasetProfile(dsId);
      setActiveProfile(prof);
    }
  };

  const toggleDocumentSelection = (docId: string) => {
    if (selectedDocumentIds.includes(docId)) {
      setSelectedDocumentIds(selectedDocumentIds.filter((id) => id !== docId));
    } else {
      setSelectedDocumentIds([...selectedDocumentIds, docId]);
    }
  };

  const handleQuerySubmit = async (question: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await submitQuery(question, selectedDatasetIds, selectedDocumentIds);
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

        {/* Workspace Grid */}
        <div className="grid md:grid-cols-3 gap-6">
          <div className="md:col-span-1 space-y-4">
            <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">Data & Document Ingestion</h2>
            <FileUpload onUploadSuccess={handleUploadSuccess} />

            {/* Datasets Multi-Select List */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Tabular Datasets</h3>
              {datasets.length === 0 ? (
                <p className="text-xs text-slate-500 italic">No datasets uploaded yet.</p>
              ) : (
                <ul className="space-y-1 font-mono text-xs">
                  {datasets.map((ds) => (
                    <li
                      key={ds.dataset_id}
                      className="flex items-center gap-2 p-2 rounded hover:bg-slate-800 text-slate-300"
                    >
                      <input
                        type="checkbox"
                        checked={selectedDatasetIds.includes(ds.dataset_id)}
                        onChange={() => toggleDatasetSelection(ds.dataset_id)}
                        className="rounded border-slate-700 bg-slate-950 text-indigo-600 focus:ring-0"
                      />
                      <span
                        onClick={async () => {
                          const prof = await fetchDatasetProfile(ds.dataset_id);
                          setActiveProfile(prof);
                        }}
                        className="cursor-pointer truncate flex-1 hover:text-indigo-300"
                      >
                        📄 {ds.filename} ({ds.rows} rows)
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Documents Multi-Select List */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Supporting Documents</h3>
              {documents.length === 0 ? (
                <p className="text-xs text-slate-500 italic">No documents uploaded yet.</p>
              ) : (
                <ul className="space-y-1 font-mono text-xs">
                  {documents.map((doc) => (
                    <li
                      key={doc.document_id}
                      className="flex items-center gap-2 p-2 rounded hover:bg-slate-800 text-slate-300"
                    >
                      <input
                        type="checkbox"
                        checked={selectedDocumentIds.includes(doc.document_id)}
                        onChange={() => toggleDocumentSelection(doc.document_id)}
                        className="rounded border-slate-700 bg-slate-950 text-indigo-600 focus:ring-0"
                      />
                      <span className="truncate flex-1">
                        📑 {doc.filename} ({doc.page_count} pg, {doc.chunk_count} chk)
                      </span>
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
