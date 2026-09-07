import React, { useState } from 'react';
import {
  UploadCloud,
  FileText,
  Building2,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Zap,
  Cpu,
  Layers,
  FileCheck2,
  Lock
} from 'lucide-react';
import { api } from '../services/api';
import { SYNTHETIC_BIDS } from '../mock/sampleData';

export default function UploadHeroWindow({
  activeBid,
  onOpenBidModal,
  onAnalysisReady
}) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedTenderPreset, setSelectedTenderPreset] = useState('tender_elcot_servers');
  const [selectedBidPreset, setSelectedBidPreset] = useState('bid_apex_compliant');
  const [uploading, setUploading] = useState(false);
  const [progressStep, setProgressStep] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (file) => {
    setErrorMsg('');
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx', 'doc', 'txt'].includes(ext)) {
      setErrorMsg('Please upload a valid PDF or Word (.docx) tender document.');
      return;
    }
    setSelectedFile(file);
  };

  const handleRunAnalysis = async () => {
    setUploading(true);
    setErrorMsg('');

    try {
      if (selectedFile) {
        setProgressStep('Ingesting large tender PDF & indexing page numbers...');
        setTimeout(() => setProgressStep('Requirement Extraction Agent: Classifying clauses & sections...'), 600);
        setTimeout(() => setProgressStep('Compliance Agent: Evaluating against submitted synthetic bid...'), 1200);
        setTimeout(() => setProgressStep('Technical Verification (TVC) & Readiness Analysis...'), 1800);

        const result = await api.uploadTender(selectedFile, selectedBidPreset);
        onAnalysisReady(result, result.metadata.id);
      } else {
        setProgressStep('Loading Real ELCOT 152-Page Tender & Page Excerpts...');
        setTimeout(() => setProgressStep('Extracting Eligibility (Pg 109), Technical TVC (Pg 124), EMD (Pg 142)...'), 600);
        setTimeout(() => setProgressStep('Matching Synthetic Bidder Response vs Tender Clauses...'), 1200);

        const result = await api.getTender(selectedTenderPreset, selectedBidPreset);
        onAnalysisReady(result, selectedTenderPreset);
      }
    } catch (err) {
      setErrorMsg(err.message || 'Error analyzing tender. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-6 px-4 animate-in fade-in duration-200">
      {/* Title */}
      <div className="text-center mb-8 space-y-2.5">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-bold tracking-wide">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Real Tender + Synthetic Bid Comparison Engine</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
          TenderIQ &mdash; <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-emerald-400 bg-clip-text text-transparent">Upload & Analysis Workspace</span>
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 max-w-2xl mx-auto">
          Built for complex, multi-page government tenders (e.g. 152-page ELCOT Server RFP). Extract eligibility conditions, technical TVC requirements, and compare them against submitted bidder credentials.
        </p>
      </div>

      {/* Main Card */}
      <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 shadow-2xl space-y-6 relative overflow-hidden">
        {/* Glow */}
        <div className="absolute top-0 right-0 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />

        {/* Step 1: Tender RFP Document */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-blue-600 text-white font-mono text-[11px] flex items-center justify-center">1</span>
              Tender Document (RFP)
            </span>
            <span className="text-[11px] text-blue-400 font-medium">Supports Large 150+ Page PDFs</span>
          </div>

          {/* Upload Dropzone */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-2xl p-6 sm:p-8 text-center transition-all cursor-pointer ${
              dragActive
                ? 'border-blue-500 bg-blue-500/10 shadow-lg'
                : selectedFile
                ? 'border-emerald-500/60 bg-emerald-500/5'
                : 'border-slate-700 hover:border-blue-500/50 bg-slate-900/50 hover:bg-slate-900/80'
            }`}
            onClick={() => document.getElementById('tender-file-input').click()}
          >
            <input
              type="file"
              id="tender-file-input"
              accept=".pdf,.docx,.doc,.txt"
              onChange={handleChange}
              className="hidden"
              disabled={uploading}
            />

            {selectedFile ? (
              <div className="space-y-2">
                <FileText className="w-10 h-10 text-emerald-400 mx-auto" />
                <div className="text-sm font-bold text-white">{selectedFile.name}</div>
                <div className="text-xs text-slate-400">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB &bull; Uploaded for multi-agent extraction
                </div>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedFile(null);
                  }}
                  className="text-xs text-rose-400 hover:underline font-semibold pt-1"
                >
                  Remove custom file
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                <UploadCloud className="w-10 h-10 text-slate-400 mx-auto" />
                <p className="text-sm font-bold text-slate-200">
                  Drop tender PDF here, or <span className="text-blue-400 hover:underline">browse files</span>
                </p>
                <p className="text-xs text-slate-400">
                  Or test with the pre-loaded 152-Page ELCOT Tender below
                </p>
              </div>
            )}
          </div>

          {/* Sample Preloaded Tender Card */}
          {!selectedFile && (
            <div
              onClick={() => setSelectedTenderPreset('tender_elcot_servers')}
              className="p-4 rounded-xl bg-blue-600/10 border border-blue-500/30 flex items-start justify-between gap-4 cursor-pointer hover:bg-blue-600/15 transition-all"
            >
              <div className="flex items-start gap-3">
                <div className="p-2 rounded-lg bg-blue-600 text-white font-bold text-xs shrink-0 mt-0.5">
                  152 Pg
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white text-xs sm:text-sm">
                      ELCOT &mdash; Enterprise Rack Servers & Storage Rate Contract RFP
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold border border-emerald-500/20">
                      Real Document
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-0.5">
                    Ref: <strong className="text-slate-300">ELCOT/PROC/OT/33364/2026-27</strong> &bull; EMD: <strong className="text-amber-400">₹2,00,000</strong> &bull; Value: <strong className="text-slate-300">₹32.50 Cr</strong>
                  </div>
                  <div className="text-[11px] text-blue-300 mt-1 flex items-center gap-2">
                    <span>Includes: Bidder Eligibility (Pg 109)</span>
                    <span>&bull;</span>
                    <span>Technical TVC (Pg 124)</span>
                    <span>&bull;</span>
                    <span>Two-Cover Separation (Pg 142)</span>
                  </div>
                </div>
              </div>
              <CheckCircle2 className="w-5 h-5 text-blue-400 shrink-0 mt-1" />
            </div>
          )}
        </div>

        {/* Step 2: Synthetic Bid / Filled Bidder Submission */}
        <div className="space-y-3 pt-4 border-t border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-indigo-600 text-white font-mono text-[11px] flex items-center justify-center">2</span>
              Synthetic Bidder Document / Response
            </span>
            <span className="text-[11px] text-indigo-400 font-medium">Select Bidder Profile to Compare</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <button
              type="button"
              onClick={() => setSelectedBidPreset('bid_apex_compliant')}
              className={`p-3.5 rounded-xl border text-left transition-all ${
                selectedBidPreset === 'bid_apex_compliant'
                  ? 'bg-emerald-500/15 border-emerald-500 shadow-md text-white'
                  : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold text-emerald-400">🟢 Apex Enterprise</span>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300">Compliant</span>
              </div>
              <div className="text-[11px] text-slate-300">Dual Xeon 24-Core &bull; TVC Attached &bull; 9 Yrs Exp &bull; EMD Paid</div>
            </button>

            <button
              type="button"
              onClick={() => setSelectedBidPreset('bid_novatech_borderline')}
              className={`p-3.5 rounded-xl border text-left transition-all ${
                selectedBidPreset === 'bid_novatech_borderline'
                  ? 'bg-amber-500/15 border-amber-500 shadow-md text-white'
                  : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold text-amber-400">🟡 NovaTech Solutions</span>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300">Borderline</span>
              </div>
              <div className="text-[11px] text-slate-300">12-Core CPU &bull; Missing TVC &bull; 4 Yrs Exp &bull; Storage Gap</div>
            </button>

            <button
              type="button"
              onClick={() => setSelectedBidPreset('bid_zenith_ineligible')}
              className={`p-3.5 rounded-xl border text-left transition-all ${
                selectedBidPreset === 'bid_zenith_ineligible'
                  ? 'bg-rose-500/15 border-rose-500 shadow-md text-white'
                  : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold text-rose-400">🔴 Zenith Infra</span>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300">Ineligible</span>
              </div>
              <div className="text-[11px] text-slate-300">1 Yr Exp &bull; Missing EMD &bull; Blacklisted Flag</div>
            </button>
          </div>
        </div>

        {/* Error message */}
        {errorMsg && (
          <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Loading Progress State */}
        {uploading && (
          <div className="p-5 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-center space-y-3">
            <div className="flex items-center justify-center gap-2 text-sm font-bold text-blue-400">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Executing Multi-Agent TenderIQ Pipeline...</span>
            </div>
            <p className="text-xs text-slate-300 animate-pulse-subtle font-medium">{progressStep}</p>
          </div>
        )}

        {/* CTA Button */}
        <button
          type="button"
          onClick={handleRunAnalysis}
          disabled={uploading}
          className="w-full py-4 px-6 rounded-2xl bg-gradient-to-r from-blue-600 via-indigo-600 to-emerald-600 hover:from-blue-500 hover:to-emerald-500 disabled:opacity-50 text-white font-extrabold text-sm shadow-xl shadow-blue-900/30 flex items-center justify-center gap-2 transition-all"
        >
          <Zap className="w-4 h-4" />
          <span>{uploading ? 'Processing Agents...' : 'Compare Tender vs Bid & Generate Compliance Matrix'}</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
