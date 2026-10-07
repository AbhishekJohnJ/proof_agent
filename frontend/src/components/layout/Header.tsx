import React from 'react';
import { useLocation } from 'react-router-dom';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

export const Header: React.FC = () => {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();

  const getPageTitle = () => {
    const path = location.pathname;
    if (path.startsWith('/dashboard')) return 'Dashboard Overview';
    if (path.startsWith('/data')) return 'Data Sources & Auditing';
    if (path.startsWith('/analysis/')) return 'Analysis Verification Result';
    if (path.startsWith('/analysis')) return 'Analysis Workspace';
    if (path.startsWith('/evidence')) return 'Document & Evidence Library';
    if (path.startsWith('/runs')) return 'Analysis Audit Runs';
    if (path.startsWith('/settings')) return 'System Settings';
    return 'Dashboard Overview';
  };

  return (
    <header className="h-16 border-b theme-border theme-main backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-20 transition-colors">
      <h2 className="text-base font-bold tracking-tight">{getPageTitle()}</h2>

      {/* Theme Toggle Option */}
      <button
        onClick={toggleTheme}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg border theme-border theme-card text-xs font-semibold hover:border-[#E64A32] transition-colors cursor-pointer"
        title="Toggle Theme (White / Dark)"
      >
        {theme === 'dark' ? (
          <>
            <Sun className="w-4 h-4 text-[#E18230]" />
            <span>Light Theme</span>
          </>
        ) : (
          <>
            <Moon className="w-4 h-4 text-[#E64A32]" />
            <span>Dark Theme</span>
          </>
        )}
      </button>
    </header>
  );
};
