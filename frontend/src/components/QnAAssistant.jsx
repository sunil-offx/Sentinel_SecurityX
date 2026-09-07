import React, { useState } from 'react';
import { Send, Bot, User, Sparkles, BookOpen, ShieldCheck, AlertCircle, HelpCircle } from 'lucide-react';
import { api } from '../services/api';

const QUICK_QUESTIONS = [
  "What is the EMD and tender fee amount?",
  "What are the liquidated damages and delay penalties?",
  "What ISO and CMMI certifications are mandatory?",
  "What are the camera hardware and ONVIF specifications?",
  "What is the minimum annual turnover required?",
  "What is the required uptime SLA?"
];

export default function QnAAssistant({ activeTenderId }) {
  const [messages, setMessages] = useState([
    {
      sender: 'agent',
      text: 'Hello! I am your Tender Grounded Q&A Agent. Ask any question about this tender document and I will extract precise answers with page citations. If the tender is silent, I will explicitly flag that the information is not specified.',
      citations: [],
      is_grounded: true
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (queryText) => {
    const q = queryText || inputQuery;
    if (!q.trim() || loading) return;

    // Add user message
    const userMsg = { sender: 'user', text: q };
    setMessages(prev => [...prev, userMsg]);
    setInputQuery('');
    setLoading(true);

    try {
      const resp = await api.askQuestion(activeTenderId, q);
      setMessages(prev => [
        ...prev,
        {
          sender: 'agent',
          text: resp.answer,
          citations: resp.citations || [],
          is_grounded: resp.is_grounded,
          grounding_note: resp.grounding_note
        }
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          sender: 'agent',
          text: 'Unable to connect to the Q&A pipeline. Please try again.',
          citations: [],
          is_grounded: false
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel rounded-2xl border border-slate-800 shadow-xl flex flex-col h-[650px] overflow-hidden">
      {/* Chat Header */}
      <div className="p-4 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
            <Bot className="w-4 h-4 text-blue-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-white">Grounded Q&A (RAG Agent)</h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
                <ShieldCheck className="w-3 h-3" />
                Zero Hallucination Guardrail
              </span>
            </div>
            <p className="text-[11px] text-slate-400">Strictly citations-backed tender answers</p>
          </div>
        </div>
      </div>

      {/* Suggested Quick Prompts */}
      <div className="px-4 py-2 bg-slate-950/40 border-b border-slate-800/80 flex items-center gap-2 overflow-x-auto text-[11px]">
        <span className="text-slate-400 shrink-0 font-medium flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-amber-400" /> Quick Ask:
        </span>
        {QUICK_QUESTIONS.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(prompt)}
            disabled={loading}
            className="px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white shrink-0 transition-colors disabled:opacity-50"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Message Stream */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.sender === 'agent' && (
              <div className="w-7 h-7 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0 mt-0.5">
                <Bot className="w-4 h-4 text-blue-400" />
              </div>
            )}

            <div
              className={`max-w-[85%] rounded-2xl p-4 text-xs leading-relaxed ${
                msg.sender === 'user'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'bg-slate-900/90 border border-slate-800 text-slate-200'
              }`}
            >
              <div className="whitespace-pre-wrap">{msg.text}</div>

              {/* Citations block */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-800 space-y-2">
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
                    <BookOpen className="w-3 h-3 text-blue-400" />
                    Verified Tender Citations
                  </div>
                  {msg.citations.map((cite, cIdx) => (
                    <div
                      key={cIdx}
                      className="p-2 rounded bg-slate-950/80 border border-slate-800 font-mono text-[11px] text-slate-300"
                    >
                      <div className="text-blue-400 font-semibold mb-1 flex items-center justify-between">
                        <span>Source: Page {cite.page}</span>
                        <span className="text-[10px] text-slate-400 font-sans">Confidence: {Math.round(cite.relevance_score * 100)}%</span>
                      </div>
                      <p className="font-sans italic text-slate-300">"{cite.text_snippet}"</p>
                    </div>
                  ))}
                </div>
              )}

              {/* Guardrail note */}
              {msg.grounding_note && (
                <div className="mt-2 text-[10px] text-amber-300/90 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  <span>{msg.grounding_note}</span>
                </div>
              )}
            </div>

            {msg.sender === 'user' && (
              <div className="w-7 h-7 rounded-lg bg-blue-700 flex items-center justify-center shrink-0 mt-0.5">
                <User className="w-4 h-4 text-white" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-xs text-slate-400 py-2">
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <span>Scanning tender text and retrieving page citations...</span>
          </div>
        )}
      </div>

      {/* Input Box */}
      <div className="p-3 bg-slate-900/90 border-t border-slate-800">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            placeholder="Ask a question (e.g., 'What is the required solvency amount?')..."
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            disabled={loading}
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            disabled={!inputQuery.trim() || loading}
            className="px-4 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all shadow-md shadow-blue-900/20"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Ask</span>
          </button>
        </form>
      </div>
    </div>
  );
}
