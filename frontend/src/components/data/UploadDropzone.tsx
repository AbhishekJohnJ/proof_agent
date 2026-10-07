import React, { useState, useRef } from 'react';
import { UploadCloud, CheckCircle2, FileText, X } from 'lucide-react';
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
        <div className="bg-[#E64A32]/15 border border-[#E64A32]/40 rounded-xl p-5 flex items-center justify-between shadow-xs">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-[#E64A32]/20 border border-[#E64A32]/30 flex items-center justify-center text-[#E64A32]">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="text-base font-bold font-mono">{uploadedFile.name}</h4>
                <span className="px-2 py-0.5 text-xs font-semibold rounded bg-[#E64A32]/20 text-[#E64A32] border border-[#E64A32]/40 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Dataset loaded
                </span>
              </div>
              <p className="text-xs theme-text-muted mt-1 font-mono">
                {uploadedFile.size} · {uploadedFile.rows.toLocaleString()} rows · {uploadedFile.columns} columns
              </p>
            </div>
          </div>
          <button
            onClick={() => setUploadedFile(null)}
            className="p-1.5 rounded-lg theme-text-muted hover:text-[#E64A32] transition-colors"
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
          className={`border-2 border-dashed rounded-xl p-10 text-center transition-all cursor-pointer select-none flex flex-col items-center justify-center theme-card ${
            isDragging
              ? 'border-[#E64A32] bg-[#E64A32]/10'
              : 'theme-border hover:border-[#E64A32]/60'
          }`}
        >
          <div className="w-14 h-14 rounded-full theme-input border theme-border flex items-center justify-center text-[#E64A32] mb-4 shadow-sm">
            <UploadCloud className="w-7 h-7" />
          </div>

          <h3 className="text-base font-bold mb-1">
            Drop your dataset here
          </h3>
          <p className="text-xs theme-text-muted mb-4">
            or <span className="text-[#E64A32] underline font-bold">browse files</span> from your computer
          </p>

          <span className="px-3 py-1 rounded-full text-[11px] font-mono theme-text-muted theme-input border theme-border">
            Supported formats: CSV · XLSX · PDF
          </span>

          {uploading && (
            <div className="w-full max-w-xs mt-6 space-y-2">
              <div className="flex justify-between text-xs theme-text-muted font-mono">
                <span>Uploading dataset...</span>
                <span>{progress}%</span>
              </div>
              <div className="w-full theme-input h-2 rounded-full overflow-hidden border theme-border">
                <div
                  className="bg-[#E64A32] h-full transition-all duration-200"
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
