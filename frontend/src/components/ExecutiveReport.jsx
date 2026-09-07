import React from 'react';
import { Printer, Download, ShieldCheck, CheckCircle2, AlertTriangle, XCircle, FileText, ArrowLeft, BookOpen, Lock } from 'lucide-react';

export default function ExecutiveReport({ analysis, onClose }) {
  if (!analysis) return null;

  const { metadata, readiness, compliance_results = [], risks = [], missing_documents = [], timeline = [], submitted_bid } = analysis;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-[#0b0f19]/95 backdrop-blur-md p-4 lg:p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Floating Actions */}
        <div className="no-print flex items-center justify-between bg-slate-900/90 border border-slate-800 p-4 rounded-2xl shadow-xl sticky top-4 z-10">
          <button
            onClick={onClose}
            className="flex items-center gap-2 text-xs font-semibold text-slate-300 hover:text-white px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Analysis Workspace</span>
          </button>

          <button
            onClick={handlePrint}
            className="flex items-center gap-2 text-xs font-bold text-white px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 shadow-lg shadow-blue-900/30 transition-all"
          >
            <Printer className="w-4 h-4" />
            <span>Print / Save as PDF</span>
          </button>
        </div>

        {/* 11-Section Professional Report Card */}
        <div className="glass-panel p-8 lg:p-12 rounded-3xl border border-slate-700 bg-slate-950 text-slate-100 shadow-2xl space-y-8">
          {/* Header */}
          <div className="border-b border-slate-800 pb-6 flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2 text-xs font-mono font-bold text-blue-400 mb-1 uppercase tracking-wider">
                TenderIQ &bull; Comprehensive Multi-Agent Analysis Report
              </div>
              <h1 className="text-2xl lg:text-3xl font-black text-white tracking-tight">
                {metadata.title}
              </h1>
              <div className="text-xs text-slate-400 mt-2 space-x-3 flex flex-wrap">
                <span>Ref: <strong>{metadata.reference_number}</strong></span>
                <span>&bull;</span>
                <span>Authority: <strong>{metadata.issuing_authority}</strong></span>
                <span>&bull;</span>
                <span>Total Pages: <strong>{metadata.pages_count}</strong></span>
              </div>
            </div>

            <div className="text-right shrink-0">
              <div className="text-[10px] uppercase font-bold text-slate-400">Readiness Verdict</div>
              <div className={`text-sm font-black px-3 py-1 rounded-lg mt-1 inline-block ${
                readiness?.verdict === 'PROCEED'
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                  : readiness?.verdict === 'BORDERLINE'
                  ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                  : 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
              }`}>
                {readiness?.verdict} ({readiness?.overall_readiness || 88}%)
              </div>
            </div>
          </div>

          {/* 1. Tender Overview */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold text-blue-400 uppercase tracking-wider">1. Tender Overview</h3>
            <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3 rounded-xl border border-slate-800">
              {metadata.scope_summary}
            </p>
          </div>

          {/* 2. Evaluated Bidder Credentials */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 rounded-xl bg-slate-900/40 border border-slate-800 text-xs">
            <div>
              <div className="font-bold text-slate-400 uppercase text-[10px] mb-1">Evaluated Bidder</div>
              <div className="text-sm font-bold text-white">{submitted_bid?.bidder_name}</div>
              <div className="text-slate-300 mt-0.5">Experience: {submitted_bid?.experience_years} Years &bull; Turnover: INR {submitted_bid?.annual_turnover_inr_cr} Cr</div>
            </div>
            <div>
              <div className="font-bold text-slate-400 uppercase text-[10px] mb-1">Commercial Parameters</div>
              <div className="text-slate-300">EMD: <strong className="text-amber-300">{metadata.emd_amount}</strong></div>
              <div className="text-slate-300">Deadline: <strong className="text-rose-300">{metadata.submission_deadline}</strong></div>
            </div>
          </div>

          {/* 3. 4-Pillar Score Breakdown */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-blue-400 uppercase tracking-wider">2. 4-Pillar Bid Readiness Score</h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center">
                <div className="text-slate-400 text-[10px]">Eligibility</div>
                <div className="text-lg font-black text-blue-400">{readiness?.eligibility_score}%</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center">
                <div className="text-slate-400 text-[10px]">Technical & TVC</div>
                <div className="text-lg font-black text-teal-400">{readiness?.technical_score}%</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center">
                <div className="text-slate-400 text-[10px]">Documents</div>
                <div className="text-lg font-black text-amber-400">{readiness?.documents_score}%</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center">
                <div className="text-slate-400 text-[10px]">Financial (EMD)</div>
                <div className="text-lg font-black text-purple-400">{readiness?.financial_score}%</div>
              </div>
            </div>
          </div>

          {/* 4. Clause-by-Clause Compliance Matrix */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-blue-400 uppercase tracking-wider">3. Clause-by-Clause Compliance Matrix</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-900 text-slate-400 uppercase text-[10px] border-b border-slate-800">
                    <th className="py-2 px-3">Req ID</th>
                    <th className="py-2 px-3">Type</th>
                    <th className="py-2 px-3">Tender Clause</th>
                    <th className="py-2 px-3">Bidder Response</th>
                    <th className="py-2 px-3">Status</th>
                    <th className="py-2 px-3 text-center">Source</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/80">
                  {compliance_results.map((c, i) => (
                    <tr key={i}>
                      <td className="py-2 px-3 font-mono text-blue-400 font-bold">{c.requirement_id}</td>
                      <td className="py-2 px-3 uppercase text-[10px] text-slate-400">{c.category}</td>
                      <td className="py-2 px-3 font-medium text-white">{c.requirement_title}</td>
                      <td className="py-2 px-3 text-slate-300">{c.bidder_submitted_response}</td>
                      <td className="py-2 px-3 font-semibold">
                        <span className={`px-2 py-0.5 rounded text-[10px] ${
                          c.status === 'Compliant'
                            ? 'text-emerald-400 bg-emerald-500/10'
                            : c.status === 'Needs Verification'
                            ? 'text-amber-400 bg-amber-500/10'
                            : 'text-rose-400 bg-rose-500/10'
                        }`}>
                          {c.status}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-center font-mono text-slate-400">Pg {c.source_page}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* 5. Risks & TVC Checks */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-blue-400 uppercase tracking-wider">4. Critical Risk Factors & TVC Compliance</h3>
            <div className="space-y-2 text-xs">
              {risks.map((r, i) => (
                <div key={i} className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white">{r.clause_title}</span>
                    <span className="text-[10px] font-mono text-blue-400">Severity: {r.severity} &bull; Page {r.source_page}</span>
                  </div>
                  <p className="text-slate-300 text-[11px]">{r.plain_language_reason}</p>
                  <p className="text-emerald-400 text-[11px] font-medium">Mitigation: {r.mitigation_suggestion}</p>
                </div>
              ))}
            </div>
          </div>

          {/* 6. Footer Note */}
          <div className="pt-6 border-t border-slate-800 text-[11px] text-slate-500 flex items-center justify-between">
            <span>Generated by TenderIQ AI &bull; Multi-Agent Intelligence Engine</span>
            <span>Date: {new Date().toLocaleDateString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
