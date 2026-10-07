import React, { useEffect, useState } from 'react';
import { IndexedDocument } from '../types';
import { getDocuments, searchEvidence } from '../services/evidence';
import { Search, FileText, CheckCircle2, ExternalLink, Layers } from 'lucide-react';
import { Modal } from '../components/common/Modal';
import { Button } from '../components/common/Button';

export const EvidencePage: React.FC = () => {
  const [documents, setDocuments] = useState<IndexedDocument[]>([]);
  const [search, setSearch] = useState('');
  const [selectedDoc, setSelectedDoc] = useState<IndexedDocument | null>(null);

  useEffect(() => {
    getDocuments().then(setDocuments);
  }, []);

  const handleSearch = async (val: string) => {
    setSearch(val);
    const results = await searchEvidence(val);
    setDocuments(results);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Evidence Library</h1>
          <p className="text-sm text-slate-400 mt-1">
            Browse and search indexed document sources supporting numerical verifications.
          </p>
        </div>

        {/* Search Input */}
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="Search evidence chunks..."
            className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      {/* Documents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {documents.map((doc) => (
          <div
            key={doc.id}
            className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4 hover:border-slate-700 transition-all shadow-xs"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-indigo-950/60 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                  <FileText className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white font-mono">{doc.filename}</h3>
                  <p className="text-xs text-slate-400 font-mono mt-0.5">
                    {doc.pages} pages · {doc.indexedChunks} indexed chunks
                  </p>
                </div>
              </div>

              <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-500/30 flex items-center gap-1 font-mono">
                <CheckCircle2 className="w-3.5 h-3.5" /> {doc.status}
              </span>
            </div>

            <div className="space-y-2 border-t border-slate-800/80 pt-3">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                Indexed Sections
              </span>
              <div className="space-y-2">
                {doc.sections.map((sec, idx) => (
                  <div
                    key={idx}
                    className="bg-slate-950/60 border border-slate-800 rounded-lg p-3 text-xs space-y-1 font-mono"
                  >
                    <div className="flex justify-between text-slate-300 font-sans font-semibold">
                      <span>{sec.title}</span>
                      <span className="text-slate-400 font-mono text-[11px]">Page {sec.page}</span>
                    </div>
                    <p className="text-slate-400 italic text-[11px] truncate">"{sec.snippet}"</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <Button variant="outline" size="sm" onClick={() => setSelectedDoc(doc)}>
                <ExternalLink className="w-3.5 h-3.5" /> Open Document View
              </Button>
            </div>
          </div>
        ))}
      </div>

      {/* Document Detail Modal */}
      {selectedDoc && (
        <Modal
          isOpen={!!selectedDoc}
          onClose={() => setSelectedDoc(null)}
          title={selectedDoc.filename}
          subtitle={`${selectedDoc.pages} pages · ${selectedDoc.indexedChunks} indexed vector chunks`}
          maxWidth="xl"
        >
          <div className="space-y-4 font-mono text-xs">
            <h4 className="font-semibold text-slate-200 uppercase font-sans tracking-wider">
              All Indexed Chunks & Text Snippets
            </h4>
            {selectedDoc.sections.map((sec, i) => (
              <div key={i} className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-2">
                <div className="flex justify-between font-sans font-bold text-indigo-300">
                  <span>{sec.title}</span>
                  <span className="text-slate-400 font-mono">Page {sec.page}</span>
                </div>
                <p className="text-slate-300 font-sans leading-relaxed text-sm">"{sec.snippet}"</p>
              </div>
            ))}
          </div>
        </Modal>
      )}
    </div>
  );
};
