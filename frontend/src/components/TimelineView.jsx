import React from 'react';
import { Calendar, Clock, AlertCircle, CheckCircle, Flag } from 'lucide-react';

export default function TimelineView({ timeline = [] }) {
  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 shadow-xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Calendar className="w-5 h-5 text-blue-400" />
            Tender Timeline & Critical Milestones
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Key dates extracted by the Document Analysis Agent with page source citations.
          </p>
        </div>
        <span className="text-xs font-mono px-2.5 py-1 rounded bg-slate-800 text-blue-400 border border-slate-700">
          {timeline.length} Milestones
        </span>
      </div>

      <div className="relative pl-6 border-l-2 border-slate-800 space-y-6">
        {timeline.map((event, idx) => (
          <div key={idx} className="relative group">
            {/* Timeline node icon */}
            <div
              className={`absolute -left-[31px] top-0.5 w-6 h-6 rounded-full flex items-center justify-center border-2 ${
                event.critical
                  ? 'bg-rose-950 border-rose-500 text-rose-400'
                  : 'bg-slate-900 border-blue-500 text-blue-400'
              }`}
            >
              {event.critical ? (
                <AlertCircle className="w-3.5 h-3.5" />
              ) : (
                <Clock className="w-3.5 h-3.5" />
              )}
            </div>

            {/* Event Card */}
            <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800/80 hover:border-slate-700 transition-all text-xs">
              <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-slate-100 text-sm">{event.event_name}</span>
                  {event.critical && (
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                      CRITICAL DEADLINE
                    </span>
                  )}
                </div>
                <span className="font-mono text-blue-400 font-semibold bg-slate-950 px-2 py-1 rounded border border-slate-800">
                  {event.date_str}
                </span>
              </div>

              {event.notes && (
                <p className="text-slate-300 mt-1.5 leading-relaxed font-medium">
                  {event.notes}
                </p>
              )}

              <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-800/60 pt-1.5">
                <span>Extracted from Tender Schedule</span>
                <span className="font-mono text-slate-300">Page {event.source_page}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
