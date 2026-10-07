import React, { useEffect, useState } from 'react';
import { Dataset } from '../types';
import { getDatasets, deleteDataset } from '../services/datasets';
import { UploadDropzone } from '../components/data/UploadDropzone';
import { DatasetHeader } from '../components/data/DatasetHeader';
import { DatasetProfile } from '../components/data/DatasetProfile';
import { DataQualityPanel } from '../components/data/DataQualityPanel';
import { SAMPLE_QUALITY_REPORT } from '../data/mockData';
import { Modal } from '../components/common/Modal';
import { Button } from '../components/common/Button';
import { Plus, Database, Table } from 'lucide-react';

export const DataSourcesPage: React.FC = () => {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [previewOpen, setPreviewOpen] = useState(false);

  useEffect(() => {
    getDatasets().then((data) => {
      setDatasets(data);
      if (data.length > 0) setSelectedDataset(data[0]);
    });
  }, []);

  const handleRemove = async (id: string) => {
    await deleteDataset(id);
    const updated = datasets.filter((d) => d.id !== id);
    setDatasets(updated);
    if (selectedDataset?.id === id) {
      setSelectedDataset(updated.length > 0 ? updated[0] : null);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Data Sources</h1>
          <p className="text-sm text-slate-400 mt-1">
            Upload and inspect the data used by your analyses.
          </p>
        </div>

        <Button variant="primary" onClick={() => window.scrollTo({ top: 300, behavior: 'smooth' })}>
          <Plus className="w-4 h-4" /> Upload Dataset
        </Button>
      </div>

      {/* Upload Dropzone */}
      <div className="space-y-2">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Upload New Dataset
        </h3>
        <UploadDropzone
          onUploaded={(newDs) => {
            setDatasets((prev) => [newDs, ...prev]);
            setSelectedDataset(newDs);
          }}
        />
      </div>

      {/* Datasets Selection List */}
      <div className="space-y-3">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Available Datasets ({datasets.length})
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {datasets.map((ds) => (
            <div
              key={ds.id}
              onClick={() => setSelectedDataset(ds)}
              className={`p-4 rounded-xl border transition-all cursor-pointer flex items-center gap-3 ${
                selectedDataset?.id === ds.id
                  ? 'bg-indigo-950/40 border-indigo-500/80 shadow-sm ring-1 ring-indigo-500/30'
                  : 'bg-slate-900 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center text-indigo-400 font-mono text-xs border border-slate-700">
                <Database className="w-5 h-5" />
              </div>
              <div className="min-w-0 flex-1">
                <h4 className="text-sm font-semibold text-slate-100 truncate font-mono">{ds.name}</h4>
                <p className="text-xs text-slate-400 font-mono mt-0.5">
                  {ds.size} · {ds.rows.toLocaleString()} rows
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Selected Dataset Inspection */}
      {selectedDataset && (
        <div className="space-y-6 pt-4 border-t border-slate-800">
          <DatasetHeader
            dataset={selectedDataset}
            onPreview={() => setPreviewOpen(true)}
            onRemove={() => handleRemove(selectedDataset.id)}
          />

          <DatasetProfile dataset={selectedDataset} />

          <DataQualityPanel quality={SAMPLE_QUALITY_REPORT} />
        </div>
      )}

      {/* Data Preview Modal */}
      {selectedDataset && (
        <Modal
          isOpen={previewOpen}
          onClose={() => setPreviewOpen(false)}
          title={`Preview: ${selectedDataset.name}`}
          subtitle={`${selectedDataset.rows.toLocaleString()} rows · ${selectedDataset.columns} columns`}
          maxWidth="2xl"
        >
          <div className="space-y-4 font-mono text-xs">
            <div className="flex items-center gap-2 text-slate-400 text-xs font-sans pb-2 border-b border-slate-800">
              <Table className="w-4 h-4 text-indigo-400" />
              <span>Showing first 5 sample rows of parsed dataset</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-950 border-b border-slate-800 text-slate-300">
                    <th className="p-2 border-r border-slate-800">Order_ID</th>
                    <th className="p-2 border-r border-slate-800">Order_Date</th>
                    <th className="p-2 border-r border-slate-800">Region</th>
                    <th className="p-2 border-r border-slate-800">Revenue</th>
                    <th className="p-2">Salesperson</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 bg-slate-900/60 text-slate-200">
                  <tr>
                    <td className="p-2 border-r border-slate-800">ORD-9021</td>
                    <td className="p-2 border-r border-slate-800">2025-10-14</td>
                    <td className="p-2 border-r border-slate-800">North</td>
                    <td className="p-2 border-r border-slate-800 text-emerald-400">₹45,000</td>
                    <td className="p-2">R. Sharma</td>
                  </tr>
                  <tr>
                    <td className="p-2 border-r border-slate-800">ORD-9022</td>
                    <td className="p-2 border-r border-slate-800">2025-10-15</td>
                    <td className="p-2 border-r border-slate-800">West</td>
                    <td className="p-2 border-r border-slate-800 text-emerald-400">₹1,20,000</td>
                    <td className="p-2">A. Patel</td>
                  </tr>
                  <tr>
                    <td className="p-2 border-r border-slate-800">ORD-9023</td>
                    <td className="p-2 border-r border-slate-800">2025-10-18</td>
                    <td className="p-2 border-r border-slate-800">South</td>
                    <td className="p-2 border-r border-slate-800 text-emerald-400">₹78,500</td>
                    <td className="p-2">M. Nair</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
