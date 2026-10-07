import React, { useState } from 'react';
import { EvidenceItem } from '../../types';
import { FileText, ExternalLink, ShieldCheck, Info } from 'lucide-react';
import { Button } from '../common/Button';
import { Modal } from '../common/Modal';

interface EvidencePanelProps {
  evidence?: EvidenceItem[];
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({ evidence }) => {
  const [selectedDoc, setSelectedDoc] = useState<EvidenceItem | null>(null);

  if (!evidence || evidence.length === 0) {
    return (
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-8 text-center space-y-3 my-2">
        <div className="w-12 h-12 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-indigo-400 mx-auto">
          <Info className="w-6 h-6" />
        </div>
        <h4 className="text-base font-semibold text-slate-200">No supporting documents were used.</h4>
        <p className="text-xs text-slate-400 max-w-md mx-auto">
          This answer was verified using structured dataset computation directly from raw transactional logs.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4 p-2">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          Supporting Document Evidence ({evidence.length})
        </h4>
        <span className="text-xs text-slate-400">Indexed document excerpts</span>
      </div>

      <div className="space-y-3">
        {evidence.map((item) => (
          <div
            key={item.id}
            className="bg-slate-950 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-all space-y-3"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-indigo-950/60 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-mono text-xs">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <h5 className="text-sm font-bold text-white font-mono">{item.document}</h5>
                  <p className="text-xs text-slate-400 font-mono">
                    Page {item.page || 1} · {item.section || 'General Section'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-emerald-950 text-emerald-300 border border-emerald-500/30">
                  {(item.relevance * 100).toFixed(0)}% Match
                </span>
                <Button variant="outline" size="sm" onClick={() => setSelectedDoc(item)}>
                  <ExternalLink className="w-3.5 h-3.5" /> View source
                </Button>
              </div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-3 text-xs text-slate-300 italic font-serif leading-relaxed">
              "{item.excerpt}"
            </div>
          </div>
        ))}
      </div>

      {/* Document View Modal */}
      {selectedDoc && (
        <Modal
          isOpen={!!selectedDoc}
          onClose={() => setSelectedDoc(null)}
          title={selectedDoc.document}
          subtitle={`Page ${selectedDoc.page || 1} — ${selectedDoc.section}`}
        >
          <div className="space-y-4 font-mono text-xs">
            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 text-slate-200 leading-relaxed font-sans text-sm">
              <span className="font-bold text-indigo-400 block mb-2 font-mono">EXTRACTED EXCERPT:</span>
              "{selectedDoc.excerpt}"
            </div>
            <div className="flex justify-between text-slate-400 pt-2 border-t border-slate-800">
              <span>Status: Verified & Indexed</span>
              <span>Relevance Score: {(selectedDoc.relevance * 100).toFixed(1)}%</span>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
