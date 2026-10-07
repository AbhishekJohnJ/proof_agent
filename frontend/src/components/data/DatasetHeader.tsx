import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Dataset } from '../../types';
import { Database, Terminal, Eye, Trash2 } from 'lucide-react';
import { Button } from '../common/Button';

interface DatasetHeaderProps {
  dataset: Dataset;
  onRemove?: () => void;
  onPreview?: () => void;
}

export const DatasetHeader: React.FC<DatasetHeaderProps> = ({ dataset, onRemove, onPreview }) => {
  const navigate = useNavigate();

  return (
    <div className="theme-card border theme-border rounded-xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-sm">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-xl bg-[#E64A32]/15 border border-[#E64A32]/30 flex items-center justify-center text-[#E64A32] shrink-0">
          <Database className="w-6 h-6" />
        </div>
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold font-mono">{dataset.name}</h2>
            <span className="px-2.5 py-0.5 rounded text-xs font-semibold uppercase tracking-wider theme-input border theme-border font-mono">
              {dataset.type}
            </span>
          </div>
          <p className="text-xs theme-text-muted mt-1 flex flex-wrap items-center gap-3 font-mono">
            <span>{dataset.rows.toLocaleString()} rows</span>
            <span>•</span>
            <span>{dataset.columns} columns</span>
            <span>•</span>
            <span>Updated {dataset.updatedAt}</span>
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Button variant="secondary" size="sm" onClick={onPreview}>
          <Eye className="w-4 h-4" /> Preview
        </Button>
        <Button variant="primary" size="sm" onClick={() => navigate('/analysis')}>
          <Terminal className="w-4 h-4" /> Analyze
        </Button>
        {onRemove && (
          <Button variant="ghost" size="sm" onClick={onRemove} className="text-rose-500 hover:text-rose-400">
            <Trash2 className="w-4 h-4" />
          </Button>
        )}
      </div>
    </div>
  );
};
