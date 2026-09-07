import React, { useState } from 'react';
import { Building2, Check, RefreshCw, X, Shield, AlertTriangle, Cpu, HardDrive } from 'lucide-react';
import { SYNTHETIC_BIDS } from '../mock/sampleData';

export default function CompanyProfileModal({
  isOpen,
  onClose,
  currentBid,
  onSaveBid
}) {
  if (!isOpen) return null;

  const [formData, setFormData] = useState({
    bidder_name: currentBid?.bidder_name || 'Apex Enterprise Systems India Pvt Ltd',
    bidder_type: currentBid?.bidder_type || 'Primary System Integrator (SI)',
    incorporation_year: currentBid?.incorporation_year || 2017,
    experience_years: currentBid?.experience_years || 9,
    annual_turnover_inr_cr: currentBid?.annual_turnover_inr_cr || 45.0,
    net_worth_inr_cr: currentBid?.net_worth_inr_cr || 18.5,
    emd_submitted_amount: currentBid?.emd_submitted_amount || 'INR 2,00,000 (Bank Guarantee)',
    emd_status: currentBid?.emd_status || 'Submitted (Valid BG Attached)',
    technical_responses: currentBid?.technical_responses || {
      processor: 'Dual Intel Xeon Gold 6430 (24 Cores, 2.1 GHz Base)',
      ram: '128 GB DDR5 ECC Registered Memory',
      storage: '2x 960 GB NVMe SSD (OS) + 4x 3.84 TB Enterprise SAS SSD',
      warranty: '5 Years Comprehensive 24x7 4-Hour Call-to-Repair Support',
      tvc_certificate: 'OEM Lab Technical Verification Certificate (TVC) Attached'
    },
    certifications: currentBid?.certifications || ['ISO 9001:2015', 'ISO 27001:2022'],
    available_documents: currentBid?.available_documents || [],
    blacklisted: currentBid?.blacklisted || false
  });

  const handleSelectPreset = (presetKey) => {
    const preset = SYNTHETIC_BIDS[presetKey];
    if (preset) {
      setFormData({ ...preset });
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSaveBid(formData);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md">
      <div className="glass-panel w-full max-w-2xl rounded-2xl p-6 border border-slate-700 shadow-2xl animate-in fade-in zoom-in-95 duration-150 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Building2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Synthetic Bidder Submission Editor</h3>
              <p className="text-xs text-slate-400">Modify bidder credentials to test live ELCOT compliance matrix changes</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Presets */}
        <div className="mb-5 p-3 rounded-xl bg-slate-900/80 border border-slate-800">
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">
            Load Quick Preset:
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
            <button
              type="button"
              onClick={() => handleSelectPreset('bid_apex_compliant')}
              className="p-2.5 rounded-lg bg-slate-800/80 hover:bg-emerald-950/40 border border-slate-700 hover:border-emerald-500/40 text-left transition-all"
            >
              <div className="font-bold text-emerald-400">🟢 Apex Enterprise</div>
              <div className="text-[10px] text-slate-400">24-Core &bull; TVC Attached &bull; 9 Yrs</div>
            </button>

            <button
              type="button"
              onClick={() => handleSelectPreset('bid_novatech_borderline')}
              className="p-2.5 rounded-lg bg-slate-800/80 hover:bg-amber-950/40 border border-slate-700 hover:border-amber-500/40 text-left transition-all"
            >
              <div className="font-bold text-amber-400">🟡 NovaTech Solutions</div>
              <div className="text-[10px] text-slate-400">12-Core &bull; Missing TVC &bull; 4 Yrs</div>
            </button>

            <button
              type="button"
              onClick={() => handleSelectPreset('bid_zenith_ineligible')}
              className="p-2.5 rounded-lg bg-slate-800/80 hover:bg-rose-950/40 border border-slate-700 hover:border-rose-500/40 text-left transition-all"
            >
              <div className="font-bold text-rose-400">🔴 Zenith Infra</div>
              <div className="text-[10px] text-slate-400">1 Yr &bull; Blacklisted &bull; No EMD</div>
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-300 font-medium mb-1">Bidder Company Name</label>
              <input
                type="text"
                value={formData.bidder_name}
                onChange={(e) => setFormData({ ...formData, bidder_name: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:border-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-1">Completed Operating Experience (Years)</label>
              <input
                type="number"
                value={formData.experience_years}
                onChange={(e) => setFormData({ ...formData, experience_years: parseInt(e.target.value) || 0 })}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:border-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-1">Average Annual Turnover (INR Crores)</label>
              <input
                type="number"
                step="0.1"
                value={formData.annual_turnover_inr_cr}
                onChange={(e) => setFormData({ ...formData, annual_turnover_inr_cr: parseFloat(e.target.value) || 0 })}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:border-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-1">EMD Submitted (Page 142)</label>
              <input
                type="text"
                value={formData.emd_submitted_amount}
                onChange={(e) => setFormData({ ...formData, emd_submitted_amount: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          {/* Technical Specifications Submitted */}
          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3">
            <div className="font-bold text-white text-xs flex items-center gap-2">
              <Cpu className="w-4 h-4 text-teal-400" />
              <span>Submitted Technical Specifications (Page 124)</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-400 font-medium mb-1">Proposed Processor Model</label>
                <input
                  type="text"
                  value={formData.technical_responses?.processor || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    technical_responses: { ...formData.technical_responses, processor: e.target.value }
                  })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-100"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Technical Verification Certificate (TVC)</label>
                <input
                  type="text"
                  value={formData.technical_responses?.tvc_certificate || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    technical_responses: { ...formData.technical_responses, tvc_certificate: e.target.value }
                  })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-100"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-slate-400 font-medium mb-1">Storage Configuration</label>
                <input
                  type="text"
                  value={formData.technical_responses?.storage || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    technical_responses: { ...formData.technical_responses, storage: e.target.value }
                  })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-100"
                />
              </div>
            </div>
          </div>

          {/* Blacklisting Flag */}
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <AlertTriangle className={`w-4 h-4 ${formData.blacklisted ? 'text-rose-400' : 'text-slate-500'}`} />
              <div>
                <div className="font-bold text-slate-200">Blacklisted / Debarred Status (Clause 3.5)</div>
                <div className="text-[10px] text-slate-400">Toggle to simulate immediate rejection on Clause 3.5.</div>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={formData.blacklisted}
                onChange={(e) => setFormData({ ...formData, blacklisted: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-rose-600"></div>
            </label>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-bold flex items-center gap-2 shadow-lg shadow-blue-900/30"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Apply & Re-Evaluate Against ELCOT</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
