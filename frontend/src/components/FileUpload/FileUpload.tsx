'use client';

import React, { useState } from 'react';
import { uploadFile } from '@/services/api';

interface FileUploadProps {
  onUploadSuccess: (data: any) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const data = await uploadFile(file);
      onUploadSuccess(data);
    } catch (err: any) {
      setError(err.message || 'File upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="border-2 border-dashed border-slate-700 bg-slate-900/50 rounded-xl p-6 text-center hover:border-indigo-500 transition-colors">
      <input
        type="file"
        id="file-upload-input"
        className="hidden"
        onChange={handleFileChange}
        accept=".csv,.xlsx,.xls,.json,.pdf,.txt,.docx"
      />
      <label htmlFor="file-upload-input" className="cursor-pointer block">
        <div className="text-3xl mb-2">📁</div>
        <p className="text-sm font-semibold text-slate-200">
          Upload Dataset or Document
        </p>
        <p className="text-xs text-slate-400 mt-1">
          Supports CSV, XLSX, JSON, PDF, TXT, DOCX
        </p>
      </label>

      {uploading && (
        <p className="text-xs text-indigo-400 mt-3 animate-pulse">Uploading and profiling dataset...</p>
      )}

      {error && (
        <p className="text-xs text-rose-400 mt-3 font-mono">{error}</p>
      )}
    </div>
  );
};
