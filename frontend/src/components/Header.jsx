import React from 'react';
import { ShieldCheck, Building2, UploadCloud, FileSpreadsheet, ArrowLeft, RefreshCw } from 'lucide-react';

export default function Header({
  activeProfile,
  onOpenProfileModal,
  onNewUpload,
  isAnalysisMode,
  activeTenderTitle,
  onExportReport
}) {
  return (
    <header className="sticky top-0 z-30 bg-[#0b0f19]/90 backdrop-blur-md border-b border-slate-800/80 px-4 lg:px-8 py-3.5">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
        {/* Logo & Subtitle */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={onNewUpload}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-500 to-emerald-400 p-0.5 shadow-lg shadow-blue-500/20 flex items-center justify-center">
            <div className="w-full h-full bg-[#0f172a] rounded-[10px] flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-blue-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                Tender<span className="text-blue-500">IQ</span>
              </span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                AI Compliance Agent
              </span>
            </div>
            <p className="text-xs text-slate-400">Government & Enterprise Tender Intelligence</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* If in Analysis Mode, show New Upload / Change Tender */}
          {isAnalysisMode ? (
            <button
              onClick={onNewUpload}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all shadow-sm"
            >
              <UploadCloud className="w-3.5 h-3.5 text-blue-400" />
              <span>Upload Another Tender</span>
            </button>
          ) : null}

          {/* Profile Manager Button */}
          <button
            onClick={onOpenProfileModal}
            className="flex items-center gap-2 px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-indigo-950/40 hover:bg-indigo-900/50 text-indigo-300 border border-indigo-500/30 transition-all"
          >
            <Building2 className="w-3.5 h-3.5 text-indigo-400" />
            <span className="max-w-[140px] truncate">{activeProfile?.company_name?.split(' ')[0] || 'Company Profile'}</span>
          </button>

          {/* Export Report (only in analysis mode) */}
          {isAnalysisMode && (
            <button
              onClick={onExportReport}
              className="flex items-center gap-2 px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-md shadow-emerald-900/20 transition-all"
            >
              <FileSpreadsheet className="w-3.5 h-3.5" />
              <span>Export Report</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
