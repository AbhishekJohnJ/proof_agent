import React, { useState } from 'react';
import { CodeExecutionDetails } from '../../types';
import { Copy, Check, Terminal, Play, Cpu, ShieldCheck } from 'lucide-react';
import { Button } from '../common/Button';

interface CodePanelProps {
  codeDetails?: CodeExecutionDetails;
}

export const CodePanel: React.FC<CodePanelProps> = ({ codeDetails }) => {
  const [copied, setCopied] = useState(false);

  if (!codeDetails) {
    return <div className="p-8 text-center text-slate-400">No generated code available.</div>;
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(codeDetails.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-4 p-2">
      {/* Code Header bar */}
      <div className="flex items-center justify-between bg-slate-950 px-4 py-2.5 rounded-t-lg border border-slate-800">
        <div className="flex items-center gap-2 text-xs font-mono text-slate-300">
          <Terminal className="w-4 h-4 text-indigo-400" />
          <span>analysis_script.py</span>
          <span className="text-slate-500">|</span>
          <span className="text-emerald-400 flex items-center gap-1">
            <Play className="w-3 h-3 fill-current" /> {codeDetails.environment}
          </span>
        </div>
        <Button variant="ghost" size="sm" onClick={handleCopy} className="text-xs">
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-400" /> Copied
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" /> Copy code
            </>
          )}
        </Button>
      </div>

      {/* Code Viewer */}
      <div className="bg-slate-950 border-x border-b border-slate-800 rounded-b-lg p-4 font-mono text-xs text-slate-200 overflow-x-auto leading-relaxed">
        <pre>{codeDetails.code}</pre>
      </div>

      {/* Execution Details Table */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 pt-2">
        <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs">
          <div className="text-slate-400 mb-0.5">Execution Status</div>
          <div className="font-semibold text-emerald-400 flex items-center gap-1">
            <Check className="w-3.5 h-3.5" /> {codeDetails.executionStatus}
          </div>
        </div>

        <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs font-mono">
          <div className="text-slate-400 mb-0.5">Execution Time</div>
          <div className="font-semibold text-slate-100">{codeDetails.executionTime}</div>
        </div>

        <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs">
          <div className="text-slate-400 mb-0.5">Environment</div>
          <div className="font-semibold text-indigo-300 truncate">{codeDetails.environment}</div>
        </div>

        <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs">
          <div className="text-slate-400 mb-0.5">Output Type</div>
          <div className="font-semibold text-slate-200">{codeDetails.outputType}</div>
        </div>

        <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs">
          <div className="text-slate-400 mb-0.5">Reproducible</div>
          <div className="font-semibold text-emerald-400 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5" /> Yes
          </div>
        </div>
      </div>
    </div>
  );
};
