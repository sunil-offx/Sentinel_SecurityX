export const SYNTHETIC_BIDS = {
  bid_apex_compliant: {
    bidder_name: "Apex Enterprise Systems India Pvt Ltd",
    bidder_type: "Primary System Integrator (SI)",
    incorporation_year: 2017,
    experience_years: 9,
    annual_turnover_inr_cr: 45.0,
    net_worth_inr_cr: 18.5,
    emd_submitted_amount: "INR 2,00,000 (Bank Guarantee Attached)",
    emd_status: "Submitted (Valid BG Attached)",
    technical_responses: {
      processor: "Dual Intel Xeon Gold 6430 (24 Cores, 2.1 GHz Base)",
      ram: "128 GB DDR5 ECC Registered Memory",
      storage: "2x 960 GB NVMe SSD (OS) + 4x 3.84 TB Enterprise SAS SSD",
      warranty: "5 Years Comprehensive 24x7 4-Hour Call-to-Repair Onsite Support",
      tvc_certificate: "OEM Lab Technical Verification Certificate (TVC) Attached",
      maf_form: "Server OEM Authorization Letter Submitted (Tender Specific)"
    },
    certifications: [
      "ISO 9001:2015",
      "ISO 27001:2022",
      "ISO 20000-1:2018",
      "CMMI Level 3 (Services)"
    ],
    available_documents: [
      "Certificate of Incorporation",
      "GST Registration Certificate",
      "PAN Card Copy",
      "Audited Balance Sheets (FY 2022-23, 2023-24, 2024-25)",
      "Statutory Auditor Turnover Certificate with UDIN",
      "Bank Solvency Certificate (Rs. 10 Crores)",
      "EMD Bank Guarantee (Rs. 2,00,000)",
      "OEM Authorization Form (MAF) from Server OEM",
      "OEM Technical Verification Certificate (TVC)",
      "Past Performance Certificates (3 Govt/PSU Orders)",
      "Non-Blacklisting Undertaking Affidavit",
      "Power of Attorney for Authorized Signatory"
    ],
    blacklisted: false
  },
  bid_novatech_borderline: {
    bidder_name: "NovaTech Solutions LLP",
    bidder_type: "Authorized Partner / Bidder",
    incorporation_year: 2021,
    experience_years: 4,
    annual_turnover_inr_cr: 16.0,
    net_worth_inr_cr: 4.5,
    emd_submitted_amount: "INR 2,00,000 (Online NEFT Transfer)",
    emd_status: "Submitted (Receipt Enclosed)",
    technical_responses: {
      processor: "Dual Intel Xeon Silver 4410Y (12 Cores, 2.0 GHz)",
      ram: "128 GB DDR5 Memory",
      storage: "1 TB SATA HDD Array",
      warranty: "3 Years Standard Warranty + 2 Years Extended",
      tvc_certificate: "Under Process from OEM Lab (Missing)",
      maf_form: "General Partner Authorization (Not Tender Specific)"
    },
    certifications: [
      "ISO 9001:2015"
    ],
    available_documents: [
      "Certificate of Incorporation",
      "GST Registration Certificate",
      "PAN Card Copy",
      "Audited Balance Sheets (2 Years)",
      "EMD Payment Receipt (Rs. 2,00,000)",
      "Power of Attorney"
    ],
    blacklisted: false
  },
  bid_zenith_ineligible: {
    bidder_name: "Zenith Infraventures Pvt Ltd",
    bidder_type: "Trader / Reseller",
    incorporation_year: 2024,
    experience_years: 1,
    annual_turnover_inr_cr: 2.5,
    net_worth_inr_cr: -0.5,
    emd_submitted_amount: "None (Claiming MSME Exemption without valid certificate)",
    emd_status: "Missing / Exemption Disputed",
    technical_responses: {
      processor: "Single 8-Core Desktop Processor",
      ram: "32 GB RAM",
      storage: "512 GB SSD",
      warranty: "1 Year Return to Bench",
      tvc_certificate: "Not Available",
      maf_form: "Not Available"
    },
    certifications: [],
    available_documents: [
      "Certificate of Incorporation",
      "PAN Card Copy"
    ],
    blacklisted: true
  }
};

export const ELCOT_SAMPLE_ANALYSIS = {
  metadata: {
    id: "tender_elcot_servers",
    title: "Procurement & 5-Yr Maintenance of Enterprise Servers & Storage for TNSDC",
    reference_number: "ELCOT/PROC/OT/33364/2026-27",
    issuing_authority: "Electronics Corporation of Tamil Nadu Limited (ELCOT)",
    tender_type: "Open E-Tender (Two Cover System: Technical & Price)",
    estimated_value: "INR 32.50 Crores (~$3.9M USD)",
    emd_amount: "INR 2,00,000 (Rupees Two Lakhs only)",
    tender_fee: "INR 10,000 (Non-refundable)",
    submission_deadline: "10-April-2026 at 15:00 Hrs IST",
    bid_validity_period: "180 Days from Technical Bid Opening",
    pages_count: 152,
    scope_summary: "Supply, installation, technical verification certificate (TVC) validation, and 5-year comprehensive 24x7 maintenance of 2U enterprise dual-socket servers, storage arrays, and network switches."
  },
  requirements: [
    {
      id: "REQ-E01",
      category: "eligibility",
      title: "Company Existence & Legal Registration",
      description: "Bidder must be registered under Companies Act or LLP, operating in India for at least 3 completed financial years.",
      source_page: 109,
      section_name: "Section 3: Bidder Eligibility Criteria",
      mandatory: true,
      threshold_value: ">= 3 Years in India",
      evidence: {
        page: 109,
        section_name: "Bidder Eligibility Criteria",
        clause_ref: "Clause 3.1",
        exact_text_excerpt: "The Bidder must be a registered legal entity under Companies Act 1956/2013 or LLP, operating in India for at least three (3) completed financial years as on 31-March-2025."
      }
    },
    {
      id: "REQ-E02",
      category: "eligibility",
      title: "GST Registration & PAN Card",
      description: "Active GST registration in India and valid PAN card copy must be furnished.",
      source_page: 109,
      section_name: "Section 3: Bidder Eligibility Criteria",
      mandatory: true,
      threshold_value: "Active GST & PAN",
      evidence: {
        page: 109,
        section_name: "Bidder Eligibility Criteria",
        clause_ref: "Clause 3.2",
        exact_text_excerpt: "The Bidder must have active GST Registration in Tamil Nadu/India and a valid PAN card. Documentary Evidence Required: Copy of GST Registration Certificate & PAN Card."
      }
    },
    {
      id: "REQ-E03",
      category: "eligibility",
      title: "Quality & Security Certifications (ISO 9001 & 27001)",
      description: "Valid ISO 9001:2015 and ISO 27001:2013/2022 certificates on bid release date.",
      source_page: 110,
      section_name: "Section 3: Bidder Eligibility Criteria",
      mandatory: true,
      threshold_value: "ISO 9001:2015 + ISO 27001",
      evidence: {
        page: 110,
        section_name: "Bidder Eligibility Criteria",
        clause_ref: "Clause 3.4",
        exact_text_excerpt: "The Bidder must hold valid ISO 9001:2015 and ISO 27001:2013 or ISO 27001:2022 certificates as on the bid release date."
      }
    },
    {
      id: "REQ-E04",
      category: "eligibility",
      title: "Non-Blacklisting Declaration",
      description: "Undertaking on Rs. 100 Stamp Paper confirming no debarment by ELCOT, Tamil Nadu Govt or Govt of India.",
      source_page: 110,
      section_name: "Section 3: Bidder Eligibility Criteria",
      mandatory: true,
      threshold_value: "Notarized Undertaking",
      evidence: {
        page: 110,
        section_name: "Bidder Eligibility Criteria",
        clause_ref: "Clause 3.5",
        exact_text_excerpt: "The Bidder must not have been debarred or blacklisted by ELCOT, Government of Tamil Nadu, Government of India, or any State/Central PSU."
      }
    },
    {
      id: "REQ-T01",
      category: "technical",
      title: "Processor: Dual Intel Xeon Gold (Minimum 24 Cores)",
      description: "2x Intel Xeon Gold Scalable CPU, minimum 24 Cores per CPU, 2.1 GHz Base Frequency, 45MB L3 Cache.",
      source_page: 124,
      section_name: "Section 4: Technical Specifications",
      mandatory: true,
      threshold_value: "Dual Xeon >= 24 Cores/CPU",
      evidence: {
        page: 124,
        section_name: "Technical Specifications",
        clause_ref: "Clause 4.1",
        exact_text_excerpt: "Processor: 2x Intel Xeon Gold Scalable Processor (Minimum 24 Cores per CPU, 2.1 GHz Base Frequency, 45MB L3 Cache or higher)."
      }
    },
    {
      id: "REQ-T02",
      category: "technical",
      title: "Memory: 128 GB DDR5 ECC Registered",
      description: "128 GB DDR5 4800MHz ECC Registered Memory, expandable to 2TB.",
      source_page: 124,
      section_name: "Section 4: Technical Specifications",
      mandatory: true,
      threshold_value: ">= 128 GB DDR5 ECC",
      evidence: {
        page: 124,
        section_name: "Technical Specifications",
        clause_ref: "Clause 4.1",
        exact_text_excerpt: "Memory: 128 GB DDR5 4800MHz ECC Registered Memory, expandable to 2TB across 32 DIMM slots."
      }
    },
    {
      id: "REQ-T03",
      category: "technical",
      title: "Storage Configuration: NVMe OS RAID-1 + SAS SSDs",
      description: "2x 960 GB NVMe SSD for OS in RAID-1 plus minimum 4x 3.84 TB Enterprise SAS Mixed-Use SSDs.",
      source_page: 124,
      section_name: "Section 4: Technical Specifications",
      mandatory: true,
      threshold_value: "2x 960GB NVMe + 4x 3.84TB SAS SSD",
      evidence: {
        page: 124,
        section_name: "Technical Specifications",
        clause_ref: "Clause 4.1",
        exact_text_excerpt: "Storage Configuration: 2x 960 GB NVMe SSD (M.2/U.3 for OS in Hardware RAID-1) PLUS minimum 4x 3.84 TB Enterprise SAS 12Gbps Mixed-Use SSDs."
      }
    },
    {
      id: "REQ-T04",
      category: "technical",
      title: "Technical Verification Certificate (TVC)",
      description: "Technical Verification Certificate (TVC) issued by OEM central engineering lab or MeitY/STQC lab.",
      source_page: 124,
      section_name: "Section 4: Technical Specifications",
      mandatory: true,
      threshold_value: "Mandatory OEM Lab TVC",
      evidence: {
        page: 124,
        section_name: "Technical Specifications",
        clause_ref: "Clause 4.2",
        exact_text_excerpt: "Clause 4.2: Technical Verification Certificate (TVC) - All proposed server models and subsystems must carry a formal Technical Verification Certificate (TVC) issued by the OEM central engineering lab or MeitY/STQC accredited laboratory certifying full compliance."
      }
    },
    {
      id: "REQ-T05",
      category: "technical",
      title: "5 Years 24x7 4-Hour Response Onsite Warranty",
      description: "5 Years Comprehensive On-site 24x7 4-Hour Call-to-Repair Support directly backed by OEM.",
      source_page: 124,
      section_name: "Section 4: Technical Specifications",
      mandatory: true,
      threshold_value: "5 Yrs 24x7 4-Hr Call-to-Repair",
      evidence: {
        page: 124,
        section_name: "Technical Specifications",
        clause_ref: "Clause 4.3",
        exact_text_excerpt: "5 Years Comprehensive On-site 24x7 4-Hour Call-to-Repair Support directly backed by the OEM with all spare parts included."
      }
    },
    {
      id: "REQ-F01",
      category: "financial",
      title: "Average Annual Turnover (>= INR 25.00 Crores)",
      description: "Average annual turnover in last 3 financial years must not be less than INR 25.00 Crores with UDIN certificate.",
      source_page: 109,
      section_name: "Section 3: Bidder Eligibility Criteria",
      mandatory: true,
      threshold_value: ">= INR 25.00 Cr",
      evidence: {
        page: 109,
        section_name: "Bidder Eligibility Criteria",
        clause_ref: "Clause 3.3",
        exact_text_excerpt: "The average annual sales turnover of the Bidder in the last three financial years (FY 2022-23, FY 2023-24, FY 2024-25) must not be less than INR 25,00,00,000 (INR 25.00 Crores)."
      }
    },
    {
      id: "REQ-F02",
      category: "financial",
      title: "Earnest Money Deposit (EMD) (INR 2,00,000)",
      description: "EMD of INR 2,00,000 submitted through Electronic Bank Guarantee (e-BG) or online transfer.",
      source_page: 142,
      section_name: "Section 5: Commercial Terms & EMD",
      mandatory: true,
      threshold_value: "INR 2,00,000 EMD",
      evidence: {
        page: 142,
        section_name: "Commercial Terms & EMD",
        clause_ref: "Clause 5.1",
        exact_text_excerpt: "The Bidder must submit an EMD of INR 2,00,000 (Rupees Two Lakhs only) through Electronic Bank Guarantee (e-BG) or online transfer before the bid closing time."
      }
    }
  ],
  compliance_results: [
    {
      requirement_id: "REQ-E01",
      requirement_title: "Company Existence & Legal Registration",
      category: "eligibility",
      status: "Compliant",
      source_page: 109,
      section_name: "Section 3: Bidder Eligibility Criteria",
      mandatory: true,
      tender_requirement_summary: "At least 3 completed financial years in India (Clause 3.1)",
      bidder_submitted_response: "Incorporated in 2017 (9 completed operating years)",
      reasoning: "Bidder has 9 years operating track record, fulfilling the 3-year threshold required on Page 109.",
      evidence_excerpt: "Clause 3.1 (Page 109): Bidder must be operating in India for at least three (3) completed financial years as on 31-March-2025.",
      confidence_score: 0.99
    },
    {
      requirement_id: "REQ-E02",
      requirement_title: "GST Registration & PAN Card",
      category: "eligibility",
      status: "Compliant",
      source_page: 109,
      section_name: "Section 3: Bidder Eligibility Criteria",
      mandatory: true,
      tender_requirement_summary: "Active GST registration & PAN card copy (Clause 3.2)",
      bidder_submitted_response: "GST Certificate and PAN Card copies attached in credential pack",
      reasoning: "Both statutory registrations are on record and verified.",
      evidence_excerpt: "Clause 3.2 (Page 109): The Bidder must have active GST Registration in Tamil Nadu/India and a valid PAN card.",
      confidence_score: 1.0
    },
    {
      requirement_id: "REQ-E03",
      requirement_title: "Quality & Security Certifications (ISO 9001 & 27001)",
      category: "eligibility",
      status: "Compliant",
      source_page: 110,
      section_name: "Section 3: Bidder Eligibility Criteria",
      mandatory: true,
      tender_requirement_summary: "Valid ISO 9001:2015 and ISO 27001:2013/2022 (Clause 3.4)",
      bidder_submitted_response: "Holds ISO 9001:2015, ISO 27001:2022, CMMI Level 3",
      reasoning: "Both ISO 9001 and ISO 27001 are valid with active accreditation (Page 110).",
      evidence_excerpt: "Clause 3.4 (Page 110): The Bidder must hold valid ISO 9001:2015 and ISO 27001:2013 or ISO 27001:2022 certificates as on the bid release date.",
      confidence_score: 0.98
    },
    {
      requirement_id: "REQ-E04",
      requirement_title: "Non-Blacklisting Declaration",
      category: "eligibility",
      status: "Compliant",
      source_page: 110,
      section_name: "Section 3: Bidder Eligibility Criteria",
      mandatory: true,
      tender_requirement_summary: "Notarized non-blacklisting undertaking on Rs. 100 Stamp Paper (Clause 3.5)",
      bidder_submitted_response: "Blacklisted Flag: NO (Clean compliance history, affidavit enclosed)",
      reasoning: "Affidavit on non-judicial stamp paper enclosed, confirming clean compliance history (Page 110).",
      evidence_excerpt: "Clause 3.5 (Page 110): The Bidder must not have been debarred or blacklisted by ELCOT, Government of Tamil Nadu, Government of India, or any State/Central PSU.",
      confidence_score: 1.0
    },
    {
      requirement_id: "REQ-T01",
      requirement_title: "Processor: Dual Intel Xeon Gold (Minimum 24 Cores)",
      category: "technical",
      status: "Compliant",
      source_page: 124,
      section_name: "Section 4: Technical Specifications",
      mandatory: true,
      tender_requirement_summary: "Dual Intel Xeon Gold (>= 24 Cores/CPU, 2.1 GHz) (Clause 4.1)",
      bidder_submitted_response: "Dual Intel Xeon Gold 6430 (24 Cores, 2.1 GHz Base)",
      reasoning: "Proposed processor meets or exceeds 24-core requirement (Page 124).",
      evidence_excerpt: "Clause 4.1 (Page 124): Processor: 2x Intel Xeon Gold Scalable Processor (Minimum 24 Cores per CPU, 2.1 GHz Base Frequency, 45MB L3 Cache or higher).",
      confidence_score: 0.97
    },
    {
      requirement_id: "REQ-T02",
      requirement_title: "Memory: 128 GB DDR5 ECC Registered",
      category: "technical",
      status: "Compliant",
      source_page: 124,
      section_name: "Section 4: Technical Specifications",
      mandatory: true,
      tender_requirement_summary: "128 GB DDR5 4800MHz ECC Registered Memory (Clause 4.1)",
      bidder_submitted_response: "128 GB DDR5 ECC Registered Memory",
      reasoning: "Proposed memory capacity and speed comply with Clause 4.1 specifications (Page 124).",
      evidence_excerpt: "Clause 4.1 (Page 124): Memory: 128 GB DDR5 4800MHz ECC Registered Memory, expandable to 2TB across 32 DIMM slots.",
      confidence_score: 0.99
    },
    {
      requirement_id: "REQ-T03",
      requirement_title: "Storage Configuration: NVMe OS RAID-1 + SAS SSDs",
      category: "technical",
      status: "Compliant",
      source_page: 124,
      section_name: "Section 4: Technical Specifications",
      mandatory: true,
      tender_requirement_summary: "2x 960GB NVMe OS RAID-1 + 4x 3.84TB SAS SSD (Clause 4.1)",
      bidder_submitted_response: "2x 960 GB NVMe SSD (OS) + 4x 3.84 TB Enterprise SAS SSD",
      reasoning: "Storage configuration includes both mirrored NVMe OS drives and 4x SAS enterprise SSDs (Page 124).",
      evidence_excerpt: "Clause 4.1 (Page 124): Storage Configuration: 2x 960 GB NVMe SSD (M.2/U.3 for OS in Hardware RAID-1) PLUS minimum 4x 3.84 TB Enterprise SAS 12Gbps Mixed-Use SSDs.",
      confidence_score: 0.96
    },
    {
      requirement_id: "REQ-T04",
      requirement_title: "Technical Verification Certificate (TVC)",
      category: "technical",
      status: "Compliant",
      source_page: 124,
      section_name: "Section 4: Technical Specifications",
      mandatory: true,
      tender_requirement_summary: "OEM Lab / STQC Technical Verification Certificate (TVC) (Clause 4.2)",
      bidder_submitted_response: "OEM Lab Technical Verification Certificate (TVC) Attached",
      reasoning: "OEM central engineering lab Technical Verification Certificate (TVC) attached to technical bid (Page 124).",
      evidence_excerpt: "Clause 4.2 (Page 124): Technical Verification Certificate (TVC) - All proposed server models and subsystems must carry a formal Technical Verification Certificate (TVC) issued by the OEM central engineering lab.",
      confidence_score: 0.99
    },
    {
      requirement_id: "REQ-T05",
      requirement_title: "5 Years 24x7 4-Hour Response Onsite Warranty",
      category: "technical",
      status: "Compliant",
      source_page: 124,
      section_name: "Section 4: Technical Specifications",
      mandatory: true,
      tender_requirement_summary: "5 Years 24x7 4-Hour Call-to-Repair Direct OEM Support (Clause 4.3)",
      bidder_submitted_response: "5 Years Comprehensive 24x7 4-Hour Call-to-Repair Onsite Support",
      reasoning: "Direct OEM 5-year 24x7 4-hour SLA confirmed in authorization paperwork (Page 124).",
      evidence_excerpt: "Clause 4.3 (Page 124): 5 Years Comprehensive On-site 24x7 4-Hour Call-to-Repair Support directly backed by the OEM with all spare parts included.",
      confidence_score: 0.98
    },
    {
      requirement_id: "REQ-F01",
      requirement_title: "Average Annual Turnover (>= INR 25.00 Crores)",
      category: "financial",
      status: "Compliant",
      source_page: 109,
      section_name: "Section 3: Bidder Eligibility Criteria",
      mandatory: true,
      tender_requirement_summary: "Average 3-year turnover >= INR 25.00 Crores (Clause 3.3)",
      bidder_submitted_response: "Annual Turnover: INR 45.0 Crores",
      reasoning: "Reported turnover of INR 45.0 Cr satisfies the INR 25.00 Cr requirement (Page 109).",
      evidence_excerpt: "Clause 3.3 (Page 109): The average annual sales turnover of the Bidder in the last three financial years must not be less than INR 25,00,00,000 (INR 25.00 Crores).",
      confidence_score: 0.99
    },
    {
      requirement_id: "REQ-F02",
      requirement_title: "Earnest Money Deposit (EMD) (INR 2,00,000)",
      category: "financial",
      status: "Compliant",
      source_page: 142,
      section_name: "Section 5: Commercial Terms & EMD",
      mandatory: true,
      tender_requirement_summary: "INR 2,00,000 via Bank Guarantee or online payment (Clause 5.1)",
      bidder_submitted_response: "INR 2,00,000 (Bank Guarantee Attached)",
      reasoning: "EMD Bank Guarantee of Rs. 2,00,000 verified in accordance with Clause 5.1 (Page 142).",
      evidence_excerpt: "Clause 5.1 (Page 142): The Bidder must submit an EMD of INR 2,00,000 (Rupees Two Lakhs only) through Electronic Bank Guarantee (e-BG) or online transfer.",
      confidence_score: 1.0
    }
  ],
  missing_documents: [],
  risks: [
    {
      id: "RISK-01",
      category: "Technical Verification Certificate (TVC)",
      severity: "High",
      clause_title: "Strict TVC Requirement (Clause 4.2 - Page 124)",
      clause_text: "Clause 4.2: All proposed server models must carry a formal Technical Verification Certificate (TVC) issued by the OEM central engineering lab.",
      source_page: 124,
      section_name: "Section 4: Technical Specifications",
      plain_language_reason: "Failure to provide the exact TVC format from the OEM central lab will lead to immediate disqualification without grace period.",
      mitigation_suggestion: "Obtain pre-signed TVC directly from OEM Country Technology Office with tender reference ELCOT/PROC/OT/33364."
    },
    {
      id: "RISK-02",
      category: "Two-Cover Separation & Price Leakage",
      severity: "High",
      clause_title: "Zero Financial Exposure in Technical Bid (Clause 5.2 - Page 142)",
      clause_text: "Clause 5.2: Any inclusion of pricing, commercial quotes, or BOQ values in Cover A (Technical Bid) will result in immediate disqualification.",
      source_page: 142,
      section_name: "Section 5: Commercial Terms",
      plain_language_reason: "Accidental inclusion of price figures in datasheets or MAF attachments causes fatal rejection.",
      mitigation_suggestion: "Double-audit all Cover A PDF uploads to ensure no rate or price mentions are visible."
    },
    {
      id: "RISK-03",
      category: "24x7 4-Hour Call-to-Repair SLA",
      severity: "Medium",
      clause_title: "Stringent 4-Hour Call-to-Repair Penalty (Clause 4.3 - Page 124)",
      clause_text: "Clause 4.3: 5 Years on-site 24x7 4-hour call-to-repair SLA with standby server spares in Chennai.",
      source_page: 124,
      section_name: "Section 4: Technical Specifications",
      plain_language_reason: "Downtime exceeding 4 hours triggers hourly penalties deducted from quarterly CAMC payments.",
      mitigation_suggestion: "Ensure OEM maintains dedicated hot-spare stock at Chennai depot."
    }
  ],
  timeline: [
    { event_name: "RFP Release Date", date_str: "05-Mar-2026", source_page: 1, critical: false },
    { event_name: "Pre-Bid Clarification Meeting (Chennai)", date_str: "18-Mar-2026 11:30 IST", source_page: 1, critical: true, notes: "Clarify TVC submission format and storage NVMe tiers" },
    { event_name: "Issue of Corrigendum & Clarifications", date_str: "25-Mar-2026", source_page: 1, critical: false },
    { event_name: "Final Bid Submission Deadline", date_str: "10-Apr-2026 15:00 IST", source_page: 1, critical: true, notes: "Must upload signed TVC & EMD e-BG on tntenders.gov.in" },
    { event_name: "Technical Bid Opening (Cover A)", date_str: "11-Apr-2026 15:30 IST", source_page: 1, critical: false },
    { event_name: "Price Bid Opening (Cover B)", date_str: "24-Apr-2026", source_page: 142, critical: false }
  ],
  readiness: {
    eligibility_score: 95,
    technical_score: 92,
    documents_score: 90,
    financial_score: 98,
    overall_readiness: 94,
    verdict: "PROCEED",
    verdict_rationale: "Strong competitive fit (94% overall readiness). All mandatory eligibility, technical TVC, and financial EMD parameters satisfied.",
    critical_issues: [],
    key_strengths: [
      "Financial turnover (INR 45.0 Cr) exceeds INR 25 Cr threshold",
      "Dual Xeon 24-core processor satisfies high-performance compute requirement",
      "OEM Technical Verification Certificate (TVC) available and validated",
      "ISO 9001 and ISO 27001 active certifications in place"
    ],
    action_roadmap: [
      "Verify that OEM MAF (Form F-4) has the exact tender ref ELCOT/PROC/OT/33364.",
      "Confirm Technical Verification Certificate (TVC) covers both server chassis & power supplies.",
      "Verify that Cover A PDF contains ZERO pricing mentions as required by Clause 5.2.",
      "Upload notarized non-blacklisting affidavit on Rs. 100 stamp paper."
    ]
  },
  submitted_bid: SYNTHETIC_BIDS.bid_apex_compliant
};
