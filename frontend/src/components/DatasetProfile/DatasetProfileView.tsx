'use client';

import React from 'react';
import { DatasetProfile } from '@/types';
import { DataQualityReport } from '../DataQuality/DataQualityReport';

interface DatasetProfileProps {
  profile: DatasetProfile;
}

export const DatasetProfileView: React.FC<DatasetProfileProps> = ({ profile }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-5">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-base font-semibold text-white">{profile.filename}</h3>
          <p className="text-xs text-slate-400 font-mono">ID: {profile.dataset_id}</p>
        </div>
        <div className="flex gap-4 text-xs text-slate-300">
          <div><span className="font-semibold text-indigo-400">{profile.rows}</span> Rows</div>
          <div><span className="font-semibold text-indigo-400">{profile.columns}</span> Columns</div>
        </div>
      </div>

      <DataQualityReport status={profile.quality_status} warnings={profile.quality_warnings} />

      <div>
        <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
          Column Profiles
        </h4>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-800/60 text-slate-400 uppercase text-[10px]">
              <tr>
                <th className="p-2">Column Name</th>
                <th className="p-2">Type</th>
                <th className="p-2">Missing</th>
                <th className="p-2">Unique</th>
                <th className="p-2">Sample Values</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono">
              {profile.column_profiles.map((col, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40">
                  <td className="p-2 font-semibold text-slate-200">{col.name}</td>
                  <td className="p-2 text-indigo-400">{col.inferred_type}</td>
                  <td className="p-2">
                    {col.missing_count} ({col.missing_percentage}%)
                  </td>
                  <td className="p-2">{col.unique_count}</td>
                  <td className="p-2 text-slate-400 truncate max-w-[200px]">
                    {col.sample_values.join(', ')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
