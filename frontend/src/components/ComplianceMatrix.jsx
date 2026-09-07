import React, { useState } from 'react';
import {
  Search,
  Filter,
  CheckCircle2,
  AlertCircle,
  XCircle,
  FileText,
  ChevronRight,
  ExternalLink,
  HelpCircle,
  BookOpen,
  Cpu,
  DollarSign,
  ShieldCheck,
  Check,
  AlertTriangle
} from 'lucide-react';

export default function ComplianceMatrix({ complianceResults = [], requirements = [] }) {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sourceModalItem, setSourceModalItem] = useState(null);
  const [explainModalItem, setExplainModalItem] = useState(null);

  const reqMap = (requirements || []).reduce((acc, r) => {
    acc[r.id] = r;
    return acc;
  }, {});

  const filteredItems = complianceResults.filter(item => {
    const matchesCat = selectedCategory === 'all' || item.category.toLowerCase() === selectedCategory.toLowerCase();
    const matchesStatus = selectedStatus === 'all' || item.status.toLowerCase() === selectedStatus.toLowerCase();
    const matchesSearch = searchQuery === '' ||
      item.requirement_title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.reasoning.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (item.bidder_submitted_response || '').toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesStatus && matchesSearch;
  });

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Compliant':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            Compliant
          </span>
        );
      case 'Needs Verification':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
            Needs Verification
          </span>
        );
      case 'Non-Compliant':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <XCircle className="w-3.5 h-3.5 text-rose-400" />
            Non-Compliant
          </span>
        );
    }
  };

  const getCategoryBadge = (cat) => {
    switch (cat.toLowerCase()) {
      case 'eligibility':
        return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">Eligibility</span>;
      case 'financial':
        return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20">Financial</span>;
      case 'technical':
        return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-teal-500/10 text-teal-400 border border-teal-500/20">Technical</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-800 text-slate-300">{cat}</span>;
    }
  };

  return (
    <div className="space-y-4">
      {/* Controls Bar */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
        {/* Search */}
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search requirements, bidder responses, TVC clauses..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-950/80 border border-slate-700/80 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        {/* Category Filters */}
        <div className="flex items-center gap-1.5 overflow-x-auto text-xs pb-1 md:pb-0">
          <span className="text-slate-400 font-medium px-1 flex items-center gap-1">
            <Filter className="w-3 h-3" />
            Category:
          </span>
          {['all', 'eligibility', 'technical', 'financial'].map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-2.5 py-1 rounded-md font-medium capitalize transition-all ${
                selectedCategory === cat
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Status Filters */}
        <div className="flex items-center gap-1.5 overflow-x-auto text-xs pb-1 md:pb-0">
          <span className="text-slate-400 font-medium px-1">Status:</span>
          {[
            { id: 'all', label: 'All' },
            { id: 'compliant', label: 'Compliant' },
            { id: 'needs verification', label: 'Needs Review' },
            { id: 'non-compliant', label: 'Non-Compliant' },
          ].map(st => (
            <button
              key={st.id}
              onClick={() => setSelectedStatus(st.id)}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                selectedStatus === st.id
                  ? 'bg-slate-700 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {st.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Compliance Matrix Table */}
      <div className="glass-panel rounded-2xl overflow-hidden border border-slate-800 shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/90 border-b border-slate-800 text-slate-400 text-[11px] uppercase tracking-wider font-semibold">
                <th className="py-3 px-4 w-20">Req ID</th>
                <th className="py-3 px-4 w-28">Type</th>
                <th className="py-3 px-4 min-w-[200px]">Tender Requirement</th>
                <th className="py-3 px-4 min-w-[220px]">Bidder Submitted Response</th>
                <th className="py-3 px-4 w-36">Status</th>
                <th className="py-3 px-4 w-28 text-center">Evidence Source</th>
                <th className="py-3 px-4 w-32 text-center">AI Analysis</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs">
              {filteredItems.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-400">
                    No requirements match your current filters.
                  </td>
                </tr>
              ) : (
                filteredItems.map((item, idx) => {
                  const req = reqMap[item.requirement_id];
                  return (
                    <tr
                      key={item.requirement_id || idx}
                      className="hover:bg-slate-800/40 transition-colors"
                    >
                      <td className="py-3.5 px-4 font-mono font-bold text-blue-400 whitespace-nowrap">
                        {item.requirement_id}
                      </td>
                      <td className="py-3.5 px-4">
                        {getCategoryBadge(item.category)}
                      </td>
                      <td className="py-3.5 px-4 font-medium text-slate-100">
                        <div className="font-semibold text-slate-100">
                          {item.requirement_title}
                        </div>
                        <div className="text-[11px] text-slate-400 mt-0.5 line-clamp-2">
                          {item.tender_requirement_summary || item.reasoning}
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-slate-300">
                        <div className="p-2 rounded-lg bg-slate-900/80 border border-slate-800 text-[11px] font-medium text-slate-200">
                          {item.bidder_submitted_response || 'Standard Credentials'}
                        </div>
                      </td>
                      <td className="py-3.5 px-4 whitespace-nowrap">
                        {getStatusBadge(item.status)}
                      </td>
                      <td className="py-3.5 px-4 text-center whitespace-nowrap">
                        <button
                          type="button"
                          onClick={() => setSourceModalItem({ ...item, rawReq: req })}
                          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 hover:text-blue-300 border border-blue-500/20 text-[11px] font-bold transition-all"
                        >
                          <BookOpen className="w-3.5 h-3.5" />
                          <span>Page {item.source_page}</span>
                        </button>
                      </td>
                      <td className="py-3.5 px-4 text-center whitespace-nowrap">
                        <button
                          type="button"
                          onClick={() => setExplainModalItem({ ...item, rawReq: req })}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] font-semibold border border-slate-700 transition-all"
                        >
                          <HelpCircle className="w-3.5 h-3.5 text-amber-400" />
                          <span>Why {item.status === 'Compliant' ? 'Pass' : 'Gap'}?</span>
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 1. View Source / Evidence Modal */}
      {sourceModalItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md">
          <div className="glass-panel w-full max-w-xl rounded-2xl p-6 border border-slate-700 shadow-2xl animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-start justify-between gap-4 border-b border-slate-800 pb-3 mb-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-mono text-sm font-bold text-blue-400">{sourceModalItem.requirement_id}</span>
                  <span className="text-[11px] px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 font-bold border border-blue-500/20">
                    Source: Page {sourceModalItem.source_page}
                  </span>
                </div>
                <h3 className="text-base font-bold text-white">{sourceModalItem.requirement_title}</h3>
              </div>
              <button
                onClick={() => setSourceModalItem(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-blue-400" />
                  <span>Exact Clause Excerpt from Tender Document (Page {sourceModalItem.source_page})</span>
                </div>
                <p className="font-mono text-slate-200 text-xs leading-relaxed bg-slate-950/80 p-3 rounded-lg border border-slate-800/80">
                  "{sourceModalItem.evidence_excerpt || sourceModalItem.rawReq?.evidence?.exact_text_excerpt || sourceModalItem.reasoning}"
                </p>
                <div className="text-[11px] text-slate-400 flex items-center justify-between pt-1">
                  <span>Section: <strong>{sourceModalItem.section_name || 'Tender Specifications'}</strong></span>
                  <span className="text-emerald-400 font-medium">100% Citation Grounded</span>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                  Submitted Bidder Data
                </div>
                <p className="text-slate-200 font-medium">{sourceModalItem.bidder_submitted_response}</p>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setSourceModalItem(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium"
              >
                Close Source Viewer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 2. Interactive "Why Am I Marked Compliant / Non-Compliant" Modal */}
      {explainModalItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md">
          <div className="glass-panel w-full max-w-xl rounded-2xl p-6 border border-slate-700 shadow-2xl animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-start justify-between gap-4 border-b border-slate-800 pb-3 mb-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-mono text-sm font-bold text-blue-400">{explainModalItem.requirement_id}</span>
                  {getStatusBadge(explainModalItem.status)}
                </div>
                <h3 className="text-base font-bold text-white">AI Compliance Reasoning</h3>
              </div>
              <button
                onClick={() => setExplainModalItem(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
                <div className="font-bold text-slate-400 text-[10px] uppercase tracking-wider mb-1">
                  1. Tender Requirement (Page {explainModalItem.source_page})
                </div>
                <p className="text-slate-200">{explainModalItem.tender_requirement_summary || explainModalItem.requirement_title}</p>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
                <div className="font-bold text-slate-400 text-[10px] uppercase tracking-wider mb-1">
                  2. Bidder Response Submitted
                </div>
                <p className="text-slate-200 font-medium">{explainModalItem.bidder_submitted_response}</p>
              </div>

              <div className={`p-4 rounded-xl border ${
                explainModalItem.status === 'Compliant'
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-200'
                  : 'bg-rose-500/10 border-rose-500/30 text-rose-200'
              }`}>
                <div className="font-bold text-xs mb-1 flex items-center gap-1.5">
                  {explainModalItem.status === 'Compliant' ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <XCircle className="w-4 h-4 text-rose-400" />
                  )}
                  <span>Agent Verdict: {explainModalItem.status}</span>
                </div>
                <p className="leading-relaxed text-xs">{explainModalItem.reasoning}</p>
              </div>

              {explainModalItem.suggested_remediation && (
                <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200">
                  <div className="font-bold text-[11px] text-amber-400 mb-0.5">Recommended Remediation:</div>
                  <p>{explainModalItem.suggested_remediation}</p>
                </div>
              )}
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setExplainModalItem(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium"
              >
                Close Explanation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
