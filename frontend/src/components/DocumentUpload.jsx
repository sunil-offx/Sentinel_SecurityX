import React, { useState } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, X, Loader2, Sparkles } from 'lucide-react';
import { api } from '../services/api';

export default function DocumentUpload({
  isOpen,
  onClose,
  activeProfileId,
  onUploadSuccess
}) {
  if (!isOpen) return null;

  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
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

  const handleProcess = async () => {
    if (!selectedFile || uploading) return;

    setUploading(true);
    setErrorMsg('');
    setProgressStep('Ingesting PDF and preserving page indexes...');

    try {
      setTimeout(() => setProgressStep('Running Requirement Extraction & Classification Agent...'), 600);
      setTimeout(() => setProgressStep('Executing Compliance Agent vs Company Profile...'), 1200);
      setTimeout(() => setProgressStep('Synthesizing Risk Matrix & Bid/No-Bid Decision...'), 1800);

      const result = await api.uploadTender(selectedFile, activeProfileId);
      onUploadSuccess(result);
      onClose();
    } catch (err) {
      setErrorMsg(err.message || 'Error processing tender document. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md">
      <div className="glass-panel w-full max-w-lg rounded-2xl p-6 border border-slate-700 shadow-2xl animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400">
              <UploadCloud className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Upload Tender Document</h3>
              <p className="text-xs text-slate-400">PDF, DOCX format &bull; Multi-page extraction with page preservation</p>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={uploading}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors disabled:opacity-50"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Dropzone */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all ${
            dragActive
              ? 'border-blue-500 bg-blue-500/10'
              : selectedFile
              ? 'border-emerald-500/50 bg-emerald-500/5'
              : 'border-slate-700 hover:border-slate-600 bg-slate-900/40'
          }`}
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
              <div className="text-xs text-slate-400">{(selectedFile.size / 1024).toFixed(1)} KB</div>
              <label
                htmlFor="tender-file-input"
                className="inline-block text-xs text-blue-400 hover:underline cursor-pointer pt-1"
              >
                Change document
              </label>
            </div>
          ) : (
            <div className="space-y-3">
              <UploadCloud className="w-10 h-10 text-slate-500 mx-auto" />
              <div>
                <p className="text-sm font-semibold text-slate-200">
                  Drag and drop tender PDF or DOCX here
                </p>
                <p className="text-xs text-slate-400 mt-0.5">Supports scanned and digital tender RFPs</p>
              </div>
              <label
                htmlFor="tender-file-input"
                className="inline-block px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg cursor-pointer transition-all border border-slate-700"
              >
                Browse Files
              </label>
            </div>
          )}
        </div>

        {/* Error message */}
        {errorMsg && (
          <div className="mt-3 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Progress State */}
        {uploading && (
          <div className="mt-4 p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold text-blue-400">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Multi-Agent Pipeline Executing:</span>
            </div>
            <p className="text-xs text-slate-300 animate-pulse-subtle font-medium">{progressStep}</p>
          </div>
        )}

        {/* Actions */}
        <div className="mt-6 flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
          <button
            onClick={onClose}
            disabled={uploading}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-medium disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleProcess}
            disabled={!selectedFile || uploading}
            className="px-5 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-lg text-xs font-bold flex items-center gap-2 shadow-lg shadow-blue-900/30 transition-all"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{uploading ? 'Processing Agents...' : 'Analyze Document'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
