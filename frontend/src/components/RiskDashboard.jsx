import React from 'react';
import { AlertOctagon, ShieldAlert, AlertTriangle, ShieldCheck, ArrowRight, Lightbulb, FileWarning } from 'lucide-react';

export default function RiskDashboard({ risks = [] }) {
  const highRisks = risks.filter(r => r.severity === 'High');
  const mediumRisks = risks.filter(r => r.severity === 'Medium');
  const lowRisks = risks.filter(r => r.severity === 'Low');

  const getSeverityBadge = (sev) => {
    switch (sev) {
      case 'High':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">
            <AlertOctagon className="w-3 h-3 text-rose-400" />
            HIGH RISK
          </span>
        );
      case 'Medium':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <AlertTriangle className="w-3 h-3 text-amber-400" />
            MEDIUM RISK
          </span>
        );
      case 'Low':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/30">
            <ShieldCheck className="w-3 h-3 text-blue-400" />
            LOW RISK
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Risk Summary Header Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass-panel p-4 rounded-xl border border-rose-500/20 bg-rose-950/10 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-rose-300/80 uppercase">Critical High Risks</div>
            <div className="text-2xl font-black text-rose-400 mt-0.5">{highRisks.length}</div>
            <div className="text-[11px] text-slate-400">Strict penalties & liquidated damages</div>
          </div>
          <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20">
            <AlertOctagon className="w-6 h-6 text-rose-400" />
          </div>
        </div>

        <div className="glass-panel p-4 rounded-xl border border-amber-500/20 bg-amber-950/10 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-amber-300/80 uppercase">Moderate Risks</div>
            <div className="text-2xl font-black text-amber-400 mt-0.5">{mediumRisks.length}</div>
            <div className="text-[11px] text-slate-400">Working capital & timeline risks</div>
          </div>
          <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20">
            <AlertTriangle className="w-6 h-6 text-amber-400" />
          </div>
        </div>

        <div className="glass-panel p-4 rounded-xl border border-blue-500/20 bg-blue-950/10 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-blue-300/80 uppercase">Low / Standard Terms</div>
            <div className="text-2xl font-black text-blue-400 mt-0.5">{lowRisks.length}</div>
            <div className="text-[11px] text-slate-400">Standard commercial clauses</div>
          </div>
          <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20">
            <ShieldCheck className="w-6 h-6 text-blue-400" />
          </div>
        </div>
      </div>

      {/* Risk Items List */}
      <div className="space-y-4">
        {risks.map((risk, index) => (
          <div
            key={risk.id || index}
            className="glass-panel rounded-2xl p-5 border border-slate-800 hover:border-slate-700 transition-all shadow-lg"
          >
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-3">
              <div className="flex items-center gap-2.5 flex-wrap">
                <span className="font-mono text-xs font-bold text-slate-400">{risk.id}</span>
                {getSeverityBadge(risk.severity)}
                <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-medium">
                  {risk.category}
                </span>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800/80 text-blue-400 border border-slate-700">
                  Page {risk.source_page}
                </span>
              </div>
            </div>

            <h4 className="text-base font-bold text-white mb-2">{risk.clause_title}</h4>

            {/* Quoted clause text */}
            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs font-mono text-slate-300 mb-3 leading-relaxed">
              "{risk.clause_text}"
            </div>

            {/* Impact & Mitigation */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              {/* Plain language impact */}
              <div className="p-3 rounded-xl bg-slate-900/40 border border-slate-800/80">
                <div className="flex items-center gap-1.5 font-bold text-slate-300 mb-1">
                  <FileWarning className="w-3.5 h-3.5 text-amber-400" />
                  <span>Why This Is a Risk</span>
                </div>
                <p className="text-slate-300 leading-relaxed">{risk.plain_language_reason}</p>
              </div>

              {/* Mitigation suggestion */}
              <div className="p-3 rounded-xl bg-emerald-500/5 border border-emerald-500/20">
                <div className="flex items-center gap-1.5 font-bold text-emerald-400 mb-1">
                  <Lightbulb className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Recommended Mitigation Strategy</span>
                </div>
                <p className="text-slate-200 leading-relaxed">{risk.mitigation_suggestion}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
