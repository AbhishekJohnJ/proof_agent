import React, { useEffect, useState } from 'react';
import { IndexedDocument } from '../types';
import { getDocuments, searchEvidence } from '../services/evidence';
import { Search, FileText, CheckCircle2, ExternalLink } from 'lucide-react';
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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b theme-border pb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Evidence Library</h1>
          <p className="text-sm theme-text-muted mt-1">
            Browse and search indexed document sources supporting numerical verifications.
          </p>
        </div>

        {/* Search Input */}
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 theme-text-muted absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="Search evidence chunks..."
            className="w-full theme-input border theme-border rounded-lg pl-9 pr-4 py-2 text-sm focus:outline-none focus:border-[#E64A32]"
          />
        </div>
      </div>

      {/* Documents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {documents.map((doc) => (
          <div
            key={doc.id}
            className="theme-card border theme-border rounded-xl p-6 space-y-4 hover:border-[#E64A32]/60 transition-all shadow-xs"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-[#E64A32]/15 border border-[#E64A32]/30 flex items-center justify-center text-[#E64A32]">
                  <FileText className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-base font-bold font-mono">{doc.filename}</h3>
                  <p className="text-xs theme-text-muted font-mono mt-0.5">
                    {doc.pages} pages · {doc.indexedChunks} indexed chunks
                  </p>
                </div>
              </div>

              <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-[#E64A32]/15 text-[#E64A32] border border-[#E64A32]/30 flex items-center gap-1 font-mono">
                <CheckCircle2 className="w-3.5 h-3.5" /> {doc.status}
              </span>
            </div>

            <div className="space-y-2 border-t theme-border pt-3">
              <span className="text-xs font-semibold theme-text-muted uppercase tracking-wider block">
                Indexed Sections
              </span>
              <div className="space-y-2">
                {doc.sections.map((sec, idx) => (
                  <div
                    key={idx}
                    className="theme-input border theme-border rounded-lg p-3 text-xs space-y-1 font-mono"
                  >
                    <div className="flex justify-between font-sans font-semibold">
                      <span>{sec.title}</span>
                      <span className="theme-text-muted font-mono text-[11px]">Page {sec.page}</span>
                    </div>
                    <p className="theme-text-muted italic text-[11px] truncate">"{sec.snippet}"</p>
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
            <h4 className="font-semibold uppercase font-sans tracking-wider">
              All Indexed Chunks & Text Snippets
            </h4>
            {selectedDoc.sections.map((sec, i) => (
              <div key={i} className="theme-input p-4 rounded-lg border theme-border space-y-2">
                <div className="flex justify-between font-sans font-bold text-[#E64A32]">
                  <span>{sec.title}</span>
                  <span className="theme-text-muted font-mono">Page {sec.page}</span>
                </div>
                <p className="font-sans leading-relaxed text-sm">"{sec.snippet}"</p>
              </div>
            ))}
          </div>
        </Modal>
      )}
    </div>
  );
};
