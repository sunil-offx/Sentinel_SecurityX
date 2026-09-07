import React from 'react';
import { FileWarning, CheckCircle2, AlertOctagon, HelpCircle, FileCheck } from 'lucide-react';

export default function MissingDocuments({ missingDocuments = [], availableDocuments = [] }) {
  return (
    <div className="space-y-6">
      {/* Alert Banner if missing docs exist */}
      {missingDocuments.length > 0 ? (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-start gap-3">
          <AlertOctagon className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div className="text-xs">
            <span className="font-bold text-white">Critical Action Required: </span>
            The Missing Document Agent has detected <strong>{missingDocuments.length} mandatory documents</strong> referenced in the tender clauses that are absent from the active company repository. Failure to submit will result in administrative disqualification.
          </div>
        </div>
      ) : (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 flex items-center gap-3">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
          <div className="text-xs">
            <span className="font-bold text-white">All Core Documents Available: </span>
            The company document repository contains all statutory credentials and certificates required by this tender.
          </div>
        </div>
      )}

      {/* Grid: Missing vs Available */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Missing Required Documents */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-sm font-bold text-rose-400 flex items-center gap-2">
              <FileWarning className="w-4 h-4 text-rose-400" />
              Missing Mandatory Tender Documents ({missingDocuments.length})
            </h4>
            <span className="text-[11px] font-semibold text-slate-400">Clause Cross-Check</span>
          </div>

          {missingDocuments.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-400">
              <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2 opacity-80" />
              No missing documents found for this profile.
            </div>
          ) : (
            <div className="space-y-3">
              {missingDocuments.map((doc, idx) => (
                <div key={idx} className="p-3.5 rounded-xl bg-rose-950/20 border border-rose-500/20 text-xs">
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <span className="font-bold text-slate-100">{doc.doc_name}</span>
                    <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      Pg {doc.source_page}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-400 mb-2">
                    Clause Reference: <span className="text-blue-400 font-mono">{doc.clause_ref}</span>
                  </div>
                  <div className="text-[11px] font-medium text-rose-300/90 flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-400 shrink-0" />
                    Impact: {doc.impact}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Available Documents in Profile */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-sm font-bold text-emerald-400 flex items-center gap-2">
              <FileCheck className="w-4 h-4 text-emerald-400" />
              Available Documents on Record ({availableDocuments.length})
            </h4>
            <span className="text-[11px] font-semibold text-slate-400">Company Credentials</span>
          </div>

          <div className="space-y-2 max-h-[440px] overflow-y-auto pr-1">
            {availableDocuments.map((doc, idx) => (
              <div key={idx} className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80 text-xs text-slate-200 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span>{doc}</span>
                </div>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-medium">
                  Verified
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
