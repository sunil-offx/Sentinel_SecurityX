import React from 'react';
import { Award, CheckCircle, AlertTriangle, XCircle, ShieldAlert, Target, CheckCircle2, Lock } from 'lucide-react';

export default function DecisionSupport({ readiness, submittedBid }) {
  if (!readiness) return null;

  const getVerdictDetails = (verdict) => {
    switch (verdict) {
      case 'PROCEED':
      case 'RECOMMENDED':
        return {
          title: '🟢 PROCEED WITH BID SUBMISSION',
          subtitle: 'High probability of technical & financial qualification',
          bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
          badgeBg: 'bg-emerald-500 text-slate-950 font-black',
          scoreColor: 'text-emerald-400'
        };
      case 'BORDERLINE':
        return {
          title: '🟡 BORDERLINE / CONDITIONAL BID',
          subtitle: 'Viable proposal but requires closing critical technical/document gaps before submission',
          bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
          badgeBg: 'bg-amber-500 text-slate-950 font-black',
          scoreColor: 'text-amber-400'
        };
      case 'DO_NOT_BID':
      case 'NOT_RECOMMENDED':
      default:
        return {
          title: '🔴 DO NOT BID (CRITICAL DISQUALIFICATION RISK)',
          subtitle: 'Mandatory eligibility conditions or technical TVC parameters failed',
          bg: 'bg-rose-500/10 border-rose-500/30 text-rose-400',
          badgeBg: 'bg-rose-500 text-white font-black',
          scoreColor: 'text-rose-400'
        };
    }
  };

  const vInfo = getVerdictDetails(readiness.verdict);

  return (
    <div className="space-y-6">
      {/* Top Hero Verdict Card */}
      <div className={`glass-panel rounded-2xl p-6 lg:p-8 border ${vInfo.bg} shadow-2xl relative overflow-hidden`}>
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span className={`text-xs uppercase px-3 py-1 rounded-full ${vInfo.badgeBg} tracking-wider`}>
                AI Decision Agent
              </span>
              <span className="text-xs text-slate-400">Explainable Bid Readiness Model</span>
            </div>

            <h2 className="text-2xl lg:text-3xl font-extrabold text-white tracking-tight">
              {vInfo.title}
            </h2>

            <p className="text-slate-300 text-sm mt-1 mb-4 max-w-2xl leading-relaxed">
              {vInfo.subtitle}
            </p>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 text-xs text-slate-200 leading-relaxed font-medium">
              <span className="font-bold text-white">Explainable Rationale: </span>
              {readiness.verdict_rationale}
            </div>
          </div>

          {/* Fit Score Ring / Gauge */}
          <div className="flex flex-col items-center justify-center p-6 bg-slate-950/80 rounded-2xl border border-slate-800 shrink-0 w-full lg:w-48 text-center">
            <div className="text-xs uppercase font-bold text-slate-400 tracking-wider mb-1">
              Overall Readiness
            </div>
            <div className={`text-5xl font-black ${vInfo.scoreColor} tracking-tight`}>
              {readiness.overall_readiness}
              <span className="text-xl text-slate-500 font-normal">%</span>
            </div>
            <div className="text-[11px] text-slate-400 mt-2 font-medium">
              Bidder: <strong className="text-slate-200">{submittedBid?.bidder_name?.split(' ')[0]}</strong>
            </div>
          </div>
        </div>
      </div>

      {/* 4 Pillars Breakdown */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Eligibility */}
        <div className="glass-panel p-4 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-400 uppercase">1. Eligibility</span>
            <span className="text-base font-black text-blue-400">{readiness.eligibility_score}%</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 mb-2 overflow-hidden">
            <div className="bg-blue-500 h-full rounded-full transition-all duration-500" style={{ width: `${readiness.eligibility_score}%` }} />
          </div>
          <p className="text-[11px] text-slate-400">3-Year existence, GST, ISO 9001/27001, Non-blacklisting (Page 109).</p>
        </div>

        {/* Technical */}
        <div className="glass-panel p-4 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-400 uppercase">2. Technical & TVC</span>
            <span className="text-base font-black text-teal-400">{readiness.technical_score}%</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 mb-2 overflow-hidden">
            <div className="bg-teal-500 h-full rounded-full transition-all duration-500" style={{ width: `${readiness.technical_score}%` }} />
          </div>
          <p className="text-[11px] text-slate-400">Xeon 24-core, 128GB DDR5, NVMe RAID-1, OEM TVC certificate (Page 124).</p>
        </div>

        {/* Documents */}
        <div className="glass-panel p-4 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-400 uppercase">3. Documents</span>
            <span className="text-base font-black text-amber-400">{readiness.documents_score}%</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 mb-2 overflow-hidden">
            <div className="bg-amber-500 h-full rounded-full transition-all duration-500" style={{ width: `${readiness.documents_score}%` }} />
          </div>
          <p className="text-[11px] text-slate-400">Mandatory credentials checklist vs submitted attachments (Page 148).</p>
        </div>

        {/* Financial */}
        <div className="glass-panel p-4 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-400 uppercase">4. Financial</span>
            <span className="text-base font-black text-purple-400">{readiness.financial_score}%</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 mb-2 overflow-hidden">
            <div className="bg-purple-500 h-full rounded-full transition-all duration-500" style={{ width: `${readiness.financial_score}%` }} />
          </div>
          <p className="text-[11px] text-slate-400">₹25 Cr turnover & ₹2 Lakhs EMD guarantee with 2-cover separation (Page 142).</p>
        </div>
      </div>

      {/* Critical Issues & Action Roadmap */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Critical Issues */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <h4 className="text-sm font-bold text-rose-400 flex items-center gap-2 mb-3">
            <ShieldAlert className="w-4 h-4 text-rose-400" />
            Critical Issues & Disqualification Triggers
          </h4>
          {(readiness.critical_issues || []).length === 0 ? (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>No critical disqualification risks found in submitted bid.</span>
            </div>
          ) : (
            <ul className="space-y-2 text-xs text-slate-300">
              {readiness.critical_issues.map((iss, idx) => (
                <li key={idx} className="p-2.5 rounded-lg bg-rose-950/20 border border-rose-500/20 text-rose-200 flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-400 mt-1.5 shrink-0" />
                  <span>{iss}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Action Roadmap */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <h4 className="text-sm font-bold text-blue-400 flex items-center gap-2 mb-3">
            <Target className="w-4 h-4 text-blue-400" />
            Action Items & Roadmap to Win
          </h4>
          <div className="space-y-2.5">
            {(readiness.action_roadmap || []).map((item, idx) => (
              <div key={idx} className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-200 flex items-start gap-2.5">
                <span className="font-mono text-blue-400 font-bold bg-blue-500/10 w-5 h-5 rounded flex items-center justify-center shrink-0 text-[11px]">
                  {idx + 1}
                </span>
                <span className="leading-relaxed">{item}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
