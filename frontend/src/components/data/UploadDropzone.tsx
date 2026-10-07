import React, { useState, useRef } from 'react';
import { UploadCloud, CheckCircle2, FileText, X } from 'lucide-react';
import { Button } from '../common/Button';
import { Dataset } from '../../types';
import { uploadDataset } from '../../services/datasets';

interface UploadDropzoneProps {
  onUploaded?: (dataset: Dataset) => void;
}

export const UploadDropzone: React.FC<UploadDropzoneProps> = ({ onUploaded }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [uploadedFile, setUploadedFile] = useState<Dataset | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];

    setUploading(true);
    setProgress(15);

    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) {
          clearInterval(interval);
          return 90;
        }
        return prev + 25;
      });
    }, 200);

    try {
      const dataset = await uploadDataset(file);
      clearInterval(interval);
      setProgress(100);
      setTimeout(() => {
        setUploading(false);
        setUploadedFile(dataset);
        if (onUploaded) onUploaded(dataset);
      }, 400);
    } catch (err) {
      clearInterval(interval);
      setUploading(false);
      alert('Upload failed. Please try again.');
    }
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = () => {
    setIsDragging(false);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  return (
    <div className="space-y-4">
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv,.xlsx,.xls,.pdf"
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />

      {uploadedFile ? (
        <div className="bg-emerald-950/30 border border-emerald-500/40 rounded-xl p-5 flex items-center justify-between shadow-xs">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-emerald-900/50 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="text-base font-semibold text-white font-mono">{uploadedFile.name}</h4>
                <span className="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-900/60 text-emerald-300 border border-emerald-500/40 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Dataset loaded
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1 font-mono">
                {uploadedFile.size} · {uploadedFile.rows.toLocaleString()} rows · {uploadedFile.columns} columns
              </p>
            </div>
          </div>
          <button
            onClick={() => setUploadedFile(null)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ) : (
        <div
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-10 text-center transition-all cursor-pointer select-none flex flex-col items-center justify-center ${
            isDragging
              ? 'border-indigo-500 bg-indigo-950/30'
              : 'border-slate-800 bg-slate-900/40 hover:border-slate-700 hover:bg-slate-900/80'
          }`}
        >
          <div className="w-14 h-14 rounded-full bg-slate-800/80 border border-slate-700 flex items-center justify-center text-indigo-400 mb-4 shadow-sm">
            <UploadCloud className="w-7 h-7" />
          </div>

          <h3 className="text-base font-semibold text-slate-200 mb-1">
            Drop your dataset here
          </h3>
          <p className="text-xs text-slate-400 mb-4">
            or <span className="text-indigo-400 underline font-medium">browse files</span> from your computer
          </p>

          <span className="px-3 py-1 rounded-full text-[11px] font-mono text-slate-400 bg-slate-800/80 border border-slate-700">
            Supported formats: CSV · XLSX · PDF
          </span>

          {uploading && (
            <div className="w-full max-w-xs mt-6 space-y-2">
              <div className="flex justify-between text-xs text-slate-400">
                <span>Uploading dataset...</span>
                <span>{progress}%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-indigo-500 h-full transition-all duration-200"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
