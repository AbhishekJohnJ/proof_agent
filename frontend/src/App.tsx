import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { Layout } from './components/layout/Layout';
import { DashboardPage } from './pages/DashboardPage';
import { DataSourcesPage } from './pages/DataSourcesPage';
import { AnalysisWorkspacePage } from './pages/AnalysisWorkspacePage';
import { AnalysisResultPage } from './pages/AnalysisResultPage';
import { EvidencePage } from './pages/EvidencePage';
import { AnalysisRunsPage } from './pages/AnalysisRunsPage';
import { SettingsPage } from './pages/SettingsPage';

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/data" element={<DataSourcesPage />} />
            <Route path="/analysis" element={<AnalysisWorkspacePage />} />
            <Route path="/analysis/:id" element={<AnalysisResultPage />} />
            <Route path="/evidence" element={<EvidencePage />} />
            <Route path="/runs" element={<AnalysisRunsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </ThemeProvider>
  );
};

export default App;
