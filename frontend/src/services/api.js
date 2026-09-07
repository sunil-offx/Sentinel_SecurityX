import { ELCOT_SAMPLE_ANALYSIS, SYNTHETIC_BIDS } from '../mock/sampleData';

const BASE_URL = '/api';

export const api = {
  async getTenders() {
    try {
      const res = await fetch(`${BASE_URL}/tenders`);
      if (!res.ok) throw new Error('API failed');
      return await res.json();
    } catch (e) {
      console.warn('Using mock tenders list:', e.message);
      return {
        tenders: [
          {
            id: "tender_elcot_servers",
            title: "Procurement & 5-Yr Maintenance of Enterprise Servers for TNSDC",
            reference_number: "ELCOT/PROC/OT/33364/2026-27",
            issuing_authority: "Electronics Corporation of Tamil Nadu Limited (ELCOT)",
            estimated_value: "INR 32.50 Crores",
            submission_deadline: "10-April-2026 at 15:00 IST",
            pages_count: 152,
            verdict: "PROCEED",
            overall_readiness: 94
          }
        ]
      };
    }
  },

  async getTender(tenderId = "tender_elcot_servers", bidId = "bid_apex_compliant") {
    try {
      const url = `${BASE_URL}/tenders/${tenderId}?bid_id=${bidId}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error('API failed');
      return await res.json();
    } catch (e) {
      console.warn('Using mock ELCOT tender analysis:', e.message);
      const selectedBid = SYNTHETIC_BIDS[bidId] || SYNTHETIC_BIDS.bid_apex_compliant;
      return {
        ...ELCOT_SAMPLE_ANALYSIS,
        submitted_bid: selectedBid
      };
    }
  },

  async uploadTender(file, bidId = "bid_apex_compliant") {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('bid_id', bidId);

    const res = await fetch(`${BASE_URL}/tenders/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to process tender');
    }
    return await res.json();
  },

  async reEvaluateTender(tenderId, bid) {
    try {
      const res = await fetch(`${BASE_URL}/tenders/${tenderId}/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bid),
      });
      if (!res.ok) throw new Error('API failed');
      return await res.json();
    } catch (e) {
      console.warn('Mock re-evaluation fallback:', e.message);
      return {
        ...ELCOT_SAMPLE_ANALYSIS,
        submitted_bid: bid
      };
    }
  },

  async askQuestion(tenderId, question) {
    try {
      const res = await fetch(`${BASE_URL}/tenders/qna`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tender_id: tenderId, question }),
      });
      if (!res.ok) throw new Error('API failed');
      return await res.json();
    } catch (e) {
      console.warn('Mock QnA fallback:', e.message);
      return {
        question,
        answer: "Under Clause 4.2 (Page 124), all proposed server models must carry a formal Technical Verification Certificate (TVC) issued by the OEM central engineering lab or MeitY/STQC accredited laboratory. EMD is INR 2,00,000 via e-BG (Page 142).",
        citations: [
          { page: 124, section: "Section 4: Technical Specifications", text_snippet: "Clause 4.2: Technical Verification Certificate (TVC) - All proposed server models must carry a formal TVC.", relevance_score: 0.99 }
        ],
        is_grounded: true
      };
    }
  },

  async getSyntheticBids() {
    try {
      const res = await fetch(`${BASE_URL}/bids`);
      if (!res.ok) throw new Error('API failed');
      return await res.json();
    } catch (e) {
      return {
        bids: Object.values(SYNTHETIC_BIDS),
        default_bid_id: "bid_apex_compliant"
      };
    }
  }
};
