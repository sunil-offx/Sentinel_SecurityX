import React from 'react';
import { Calendar, DollarSign, Clock, FileText, Building, AlertTriangle, CheckCircle2, ShieldAlert, Cpu, Lock, FileCheck2, ArrowRight } from 'lucide-react';

export default function OverviewCard({ metadata, readiness, complianceResults = [], submittedBid }) {
  if (!metadata) return null;

  const totalReqs = complianceResults.length;
  const compliantCount = complianceResults.filter(r => r.status === 'Compliant').length;
  const needsCount = complianceResults.filter(r => r.status === 'Needs Verification').length;
  const nonCompliantCount = complianceResults.filter(r => r.status === 'Non-Compliant').length;

  const getVerdictStyle = (verdict) => {
    switch (verdict) {
      case 'PROCEED':
      case 'RECOMMENDED':
        return {
          badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
          gradient: 'from-emerald-500/20 to-teal-500/5',
          text: '🟢 PROCEED TO BID',
          icon: <CheckCircle2 className="w-5 h-5 text-emerald-400" />
        };
      case 'BORDERLINE':
        return {
          badge: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
          gradient: 'from-amber-500/20 to-orange-500/5',
          text: '🟡 BORDERLINE / REVIEW GAPS',
          icon: <AlertTriangle className="w-5 h-5 text-amber-400" />
        };
      case 'DO_NOT_BID':
      case 'NOT_RECOMMENDED':
      default:
        return {
          badge: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
          gradient: 'from-rose-500/20 to-red-500/5',
          text: '🔴 DO NOT BID (HIGH RISK)',
          icon: <ShieldAlert className="w-5 h-5 text-rose-400" />
        };
    }
  };

  const verdictConfig = getVerdictStyle(readiness?.verdict);

  return (
    <div className="glass-panel rounded-2xl p-6 mb-6 shadow-xl relative overflow-hidden border border-slate-800">
      {/* Background ambient gradient */}
      <div className={`absolute top-0 right-0 w-96 h-96 bg-gradient-to-br ${verdictConfig.gradient} rounded-full blur-3xl pointer-events-none -mr-20 -mt-20`} />

      <div className="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
        {/* Left column: Title & Metadata */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2.5 mb-2 flex-wrap">
            <span className="text-xs font-mono px-2.5 py-1 rounded bg-slate-800 text-blue-400 font-semibold border border-slate-700">
              {metadata.reference_number}
            </span>
            <span className="text-xs px-2.5 py-1 rounded bg-slate-800/80 text-slate-300 font-medium flex items-center gap-1.5 border border-slate-700/60">
              <Building className="w-3.5 h-3.5 text-slate-400" />
              {metadata.issuing_authority}
            </span>
            <span className="text-xs px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 font-bold border border-blue-500/20">
              {metadata.pages_count} Pages Analyzed
            </span>
            <span className="text-xs px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 font-medium border border-purple-500/20 flex items-center gap-1">
              <Lock className="w-3 h-3" />
              Two-Cover Separation
            </span>
          </div>

          <h1 className="text-xl lg:text-2xl font-black text-white tracking-tight leading-snug mb-1.5">
            {metadata.title}
          </h1>

          <p className="text-xs text-slate-300 line-clamp-2 max-w-3xl">
            {metadata.scope_summary}
          </p>

          {/* Evaluated Bidder Tag */}
          <div className="mt-3 flex items-center gap-2 text-xs text-slate-400">
            <span>Compared Against Bidder:</span>
            <span className="font-bold text-slate-200 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
              {submittedBid?.bidder_name || 'Apex Enterprise Systems'}
            </span>
          </div>
        </div>

        {/* Right column: 4-Pillar Readiness Score & Recommendation */}
        <div className="bg-slate-900/95 border border-slate-800 rounded-2xl p-5 shrink-0 w-full lg:w-auto min-w-[280px]">
          <div className="flex items-center justify-between gap-4 mb-3 border-b border-slate-800 pb-3">
            <div>
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                Overall Bid Readiness
              </div>
              <div className="text-sm font-extrabold text-white mt-0.5">
                {verdictConfig.text}
              </div>
            </div>
            <div className="text-3xl font-black text-emerald-400">
              {readiness?.overall_readiness || 88}%
            </div>
          </div>

          {/* 4 Pillars Mini-Bars */}
          <div className="space-y-1.5 text-[11px]">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Eligibility Readiness</span>
              <span className="font-bold text-blue-400">{readiness?.eligibility_score || 92}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Technical (TVC & Specs)</span>
              <span className="font-bold text-teal-400">{readiness?.technical_score || 87}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Document Checklist</span>
              <span className="font-bold text-amber-400">{readiness?.documents_score || 80}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Financial (EMD & Turnover)</span>
              <span className="font-bold text-purple-400">{readiness?.financial_score || 95}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6 pt-6 border-t border-slate-800/80">
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
          <div className="flex items-center gap-2 text-slate-400 text-xs font-medium mb-1">
            <DollarSign className="w-3.5 h-3.5 text-blue-400" />
            <span>Estimated Value</span>
          </div>
          <div className="text-sm lg:text-base font-bold text-slate-100 truncate">
            {metadata.estimated_value}
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
          <div className="flex items-center gap-2 text-slate-400 text-xs font-medium mb-1">
            <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
            <span>EMD Required (Page 142)</span>
          </div>
          <div className="text-sm lg:text-base font-bold text-amber-300 truncate">
            {metadata.emd_amount}
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
          <div className="flex items-center gap-2 text-slate-400 text-xs font-medium mb-1">
            <Clock className="w-3.5 h-3.5 text-rose-400" />
            <span>Submission Deadline</span>
          </div>
          <div className="text-sm lg:text-base font-bold text-rose-300 truncate">
            {metadata.submission_deadline}
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5">
          <div className="flex items-center gap-2 text-slate-400 text-xs font-medium mb-1">
            <FileText className="w-3.5 h-3.5 text-emerald-400" />
            <span>Compliance Breakdown</span>
          </div>
          <div className="text-xs font-bold flex items-center gap-1.5 mt-1">
            <span className="text-emerald-400">{compliantCount} Compliant</span>
            <span className="text-slate-600">&bull;</span>
            <span className="text-amber-400">{needsCount} Needs Review</span>
            <span className="text-slate-600">&bull;</span>
            <span className="text-rose-400">{nonCompliantCount} Non-Compliant</span>
          </div>
        </div>
      </div>
    </div>
  );
}
