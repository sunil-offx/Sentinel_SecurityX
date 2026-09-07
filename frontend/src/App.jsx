import React, { useState } from 'react';
import {
  FileCheck2,
  AlertTriangle,
  Award,
  FileWarning,
  Calendar,
  MessageSquare,
  ArrowLeft
} from 'lucide-react';

import Header from './components/Header';
import UploadHeroWindow from './components/UploadHeroWindow';
import OverviewCard from './components/OverviewCard';
import ComplianceMatrix from './components/ComplianceMatrix';
import RiskDashboard from './components/RiskDashboard';
import DecisionSupport from './components/DecisionSupport';
import MissingDocuments from './components/MissingDocuments';
import TimelineView from './components/TimelineView';
import QnAAssistant from './components/QnAAssistant';
import CompanyProfileModal from './components/CompanyProfileModal';
import ExecutiveReport from './components/ExecutiveReport';

import { api } from './services/api';
import { SYNTHETIC_BIDS, ELCOT_SAMPLE_ANALYSIS } from './mock/sampleData';

export default function App() {
  const [viewMode, setViewMode] = useState('upload'); // 'upload' | 'analysis'
  const [activeTab, setActiveTab] = useState('compliance');
  const [activeTenderId, setActiveTenderId] = useState('tender_elcot_servers');
  const [activeBid, setActiveBid] = useState(SYNTHETIC_BIDS.bid_apex_compliant);
  const [analysisData, setAnalysisData] = useState(ELCOT_SAMPLE_ANALYSIS);
  const [loading, setLoading] = useState(false);

  // Modals
  const [isBidModalOpen, setIsBidModalOpen] = useState(false);
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);

  const handleAnalysisReady = (data, tenderId) => {
    setAnalysisData(data);
    setActiveTenderId(tenderId);
    if (data.submitted_bid) {
      setActiveBid(data.submitted_bid);
    }
    setViewMode('analysis');
    setActiveTab('compliance');
  };

  const handleBidUpdate = async (updatedBid) => {
    setActiveBid(updatedBid);
    if (analysisData && activeTenderId) {
      setLoading(true);
      try {
        const updatedAnalysis = await api.reEvaluateTender(activeTenderId, updatedBid);
        setAnalysisData(updatedAnalysis);
      } catch (err) {
        console.error('Error re-evaluating with bid:', err);
      } finally {
        setLoading(false);
      }
    }
  };

  const tabs = [
    { id: 'compliance', label: 'Compliance Matrix', icon: FileCheck2, badge: `${analysisData?.compliance_results?.length || 0}` },
    { id: 'decision', label: 'Bid / No-Bid Decision', icon: Award, badge: `${analysisData?.readiness?.overall_readiness || 88}%` },
    { id: 'risks', label: 'Risk Analysis', icon: AlertTriangle, badge: `${analysisData?.risks?.length || 0}` },
    { id: 'missing_docs', label: 'Missing Documents', icon: FileWarning, badge: `${analysisData?.missing_documents?.length || 0}`, alert: (analysisData?.missing_documents?.length || 0) > 0 },
    { id: 'timeline', label: 'Timeline & Dates', icon: Calendar, badge: `${analysisData?.timeline?.length || 0}` },
    { id: 'qna', label: 'Grounded Q&A (RAG)', icon: MessageSquare, badge: 'AI' }
  ];

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col selection:bg-blue-600 selection:text-white">
      {/* Top Navigation */}
      <Header
        activeProfile={activeBid}
        onOpenProfileModal={() => setIsBidModalOpen(true)}
        onNewUpload={() => setViewMode('upload')}
        isAnalysisMode={viewMode === 'analysis'}
        activeTenderTitle={analysisData?.metadata?.title}
        onExportReport={() => setIsReportModalOpen(true)}
      />

      {/* Main Workspace Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 lg:px-8 py-6">
        {viewMode === 'upload' ? (
          /* Upload & Initiation Window */
          <UploadHeroWindow
            activeBid={activeBid}
            onOpenBidModal={() => setIsBidModalOpen(true)}
            onAnalysisReady={handleAnalysisReady}
          />
        ) : (
          /* Analysis Window */
          <div className="animate-in fade-in duration-150">
            {/* Top Navigation Control */}
            <div className="mb-4 flex items-center justify-between">
              <button
                onClick={() => setViewMode('upload')}
                className="flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white px-3.5 py-1.5 rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-800 transition-all shadow-sm"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Upload / Compare Different Tender</span>
              </button>
            </div>

            {loading ? (
              <div className="flex flex-col items-center justify-center py-24 space-y-4">
                <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
                <div className="text-sm font-semibold text-slate-300">
                  Re-evaluating compliance against bidder response...
                </div>
              </div>
            ) : (
              <>
                {/* Overview Card with 4-Pillar Score */}
                <OverviewCard
                  metadata={analysisData?.metadata}
                  readiness={analysisData?.readiness}
                  complianceResults={analysisData?.compliance_results}
                  submittedBid={analysisData?.submitted_bid || activeBid}
                />

                {/* Tabs */}
                <div className="flex items-center gap-2 border-b border-slate-800 mb-6 overflow-x-auto pb-1 no-scrollbar">
                  {tabs.map((tab) => {
                    const Icon = tab.icon;
                    const isActive = activeTab === tab.id;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex items-center gap-2 px-4 py-3 text-xs font-bold rounded-t-xl transition-all whitespace-nowrap border-b-2 relative ${
                          isActive
                            ? 'border-blue-500 text-blue-400 bg-slate-900/60'
                            : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/30'
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                        <span>{tab.label}</span>
                        {tab.badge && (
                          <span
                            className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono font-bold ${
                              tab.alert
                                ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                                : isActive
                                ? 'bg-blue-500/20 text-blue-300'
                                : 'bg-slate-800 text-slate-400'
                            }`}
                          >
                            {tab.badge}
                          </span>
                        )}
                      </button>
                    );
                  })}
                </div>

                {/* Active Tab View */}
                <div>
                  {activeTab === 'compliance' && (
                    <ComplianceMatrix
                      complianceResults={analysisData?.compliance_results}
                      requirements={analysisData?.requirements}
                    />
                  )}

                  {activeTab === 'decision' && (
                    <DecisionSupport
                      readiness={analysisData?.readiness}
                      submittedBid={analysisData?.submitted_bid || activeBid}
                    />
                  )}

                  {activeTab === 'risks' && (
                    <RiskDashboard risks={analysisData?.risks} />
                  )}

                  {activeTab === 'missing_docs' && (
                    <MissingDocuments
                      missingDocuments={analysisData?.missing_documents}
                      availableDocuments={analysisData?.submitted_bid?.available_documents || activeBid?.available_documents}
                    />
                  )}

                  {activeTab === 'timeline' && (
                    <TimelineView timeline={analysisData?.timeline} />
                  )}

                  {activeTab === 'qna' && (
                    <QnAAssistant activeTenderId={activeTenderId} />
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="no-print mt-auto border-t border-slate-800/60 bg-slate-950/60 px-4 py-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>TenderIQ &mdash; AI Tender Document Analyzer & Compliance Agent</span>
          <span className="text-[11px] font-mono">ELCOT Specialized &bull; Industries & MSME Track</span>
        </div>
      </footer>

      {/* Modals */}
      <CompanyProfileModal
        isOpen={isBidModalOpen}
        onClose={() => setIsBidModalOpen(false)}
        currentBid={activeBid}
        onSaveBid={handleBidUpdate}
      />

      {isReportModalOpen && (
        <ExecutiveReport
          analysis={analysisData}
          onClose={() => setIsReportModalOpen(false)}
        />
      )}
    </div>
  );
}
