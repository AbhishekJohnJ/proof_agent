import React from 'react';
import { Dataset } from '../../types';
import { Card } from '../common/Card';
import { Layers, Columns, AlertCircle, Copy, AlertTriangle } from 'lucide-react';

interface DatasetProfileProps {
  dataset: Dataset;
}

export const DatasetProfile: React.FC<DatasetProfileProps> = ({ dataset }) => {
  const profileItems = [
    { label: 'Rows', value: dataset.rows.toLocaleString(), icon: Layers, color: 'text-indigo-400' },
    { label: 'Columns', value: dataset.columns, icon: Columns, color: 'text-emerald-400' },
    { label: 'Missing values', value: `${dataset.missingValuesPct}%`, icon: AlertCircle, color: 'text-amber-400' },
    { label: 'Duplicate rows', value: dataset.duplicateRows, icon: Copy, color: 'text-sky-400' },
    { label: 'Warnings', value: dataset.warningCount, icon: AlertTriangle, color: 'text-amber-400' },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
      {profileItems.map((item, idx) => {
        const Icon = item.icon;
        return (
          <Card key={idx} className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{item.label}</span>
              <Icon className={`w-4 h-4 ${item.color}`} />
            </div>
            <p className="text-xl font-bold text-white mt-1.5 font-mono">{item.value}</p>
          </Card>
        );
      })}
    </div>
  );
};
