import React, { useState } from 'react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { ShieldCheck, Sliders, Check } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [saved, setSaved] = useState(false);

  const [settings, setSettings] = useState({
    theme: 'Dark Cyber (Default)',
    language: 'English (US)',
    dateFormat: 'YYYY-MM-DD',
    showGeneratedCode: true,
    showTrace: true,
    defaultConfidenceDisplay: 'Badge with Explanation',
    requireExecution: true,
    requireReproducibility: true,
    showQualityWarnings: true,
    showSourceConflicts: true,
  });

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300 max-w-4xl">
      {/* Header */}
      <div className="flex items-center justify-between border-b theme-border pb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">System Settings</h1>
          <p className="text-sm theme-text-muted mt-1">
            Configure default verification rules, audit trace levels, and UI preferences.
          </p>
        </div>

        <Button variant="primary" onClick={handleSave}>
          {saved ? (
            <>
              <Check className="w-4 h-4 text-[#F4F5EC]" /> Saved
            </>
          ) : (
            'Save Preferences'
          )}
        </Button>
      </div>

      <div className="space-y-6">
        {/* Verification Rules */}
        <Card className="space-y-4">
          <div className="flex items-center gap-2 text-sm font-bold border-b theme-border pb-3">
            <ShieldCheck className="w-4 h-4 text-[#E64A32]" /> Verification Engine Enforcement
          </div>

          <div className="space-y-3 text-xs">
            <label className="flex items-center justify-between p-3 rounded-lg theme-input border theme-border cursor-pointer">
              <div>
                <div className="font-semibold">Require successful code execution</div>
                <div className="theme-text-muted mt-0.5">Refuse answers if sandboxed Python process fails</div>
              </div>
              <input
                type="checkbox"
                checked={settings.requireExecution}
                onChange={(e) => setSettings({ ...settings, requireExecution: e.target.checked })}
                className="w-4 h-4 accent-[#E64A32] rounded"
              />
            </label>

            <label className="flex items-center justify-between p-3 rounded-lg theme-input border theme-border cursor-pointer">
              <div>
                <div className="font-semibold">Require reproducibility check</div>
                <div className="theme-text-muted mt-0.5">Verify result twice across dual mathematical engines</div>
              </div>
              <input
                type="checkbox"
                checked={settings.requireReproducibility}
                onChange={(e) => setSettings({ ...settings, requireReproducibility: e.target.checked })}
                className="w-4 h-4 accent-[#E64A32] rounded"
              />
            </label>

            <label className="flex items-center justify-between p-3 rounded-lg theme-input border theme-border cursor-pointer">
              <div>
                <div className="font-semibold">Show data-quality warnings</div>
                <div className="theme-text-muted mt-0.5">Flag missing values, duplicate rows, and date format ambiguities</div>
              </div>
              <input
                type="checkbox"
                checked={settings.showQualityWarnings}
                onChange={(e) => setSettings({ ...settings, showQualityWarnings: e.target.checked })}
                className="w-4 h-4 accent-[#E64A32] rounded"
              />
            </label>

            <label className="flex items-center justify-between p-3 rounded-lg theme-input border theme-border cursor-pointer">
              <div>
                <div className="font-semibold">Surface source conflicts</div>
                <div className="theme-text-muted mt-0.5">Refuse arbitrary choices when PDF and CSV figures disagree</div>
              </div>
              <input
                type="checkbox"
                checked={settings.showSourceConflicts}
                onChange={(e) => setSettings({ ...settings, showSourceConflicts: e.target.checked })}
                className="w-4 h-4 accent-[#E64A32] rounded"
              />
            </label>
          </div>
        </Card>

        {/* Analysis & Display */}
        <Card className="space-y-4">
          <div className="flex items-center gap-2 text-sm font-bold border-b theme-border pb-3">
            <Sliders className="w-4 h-4 text-[#E64A32]" /> Analysis & Display Preferences
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block theme-text-muted mb-1 font-medium">Date Format</label>
              <select
                value={settings.dateFormat}
                onChange={(e) => setSettings({ ...settings, dateFormat: e.target.value })}
                className="w-full theme-input border theme-border rounded-lg px-3 py-2 focus:outline-none focus:border-[#E64A32]"
              >
                <option>YYYY-MM-DD</option>
                <option>DD/MM/YYYY</option>
                <option>MM/DD/YYYY</option>
              </select>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
