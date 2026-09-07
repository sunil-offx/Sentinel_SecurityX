from typing import Dict, List
from schemas.models import (
    RequirementCategory, ComplianceStatus, RiskSeverity, DecisionVerdict,
    EvidenceReference, SyntheticBidSubmission, Requirement, ComplianceItem,
    MissingDocument, RiskItem, TimelineEvent, BidReadinessBreakdown,
    TenderMetadata, TenderAnalysis
)

# 1. Synthetic Bid Submissions
SYNTHETIC_BID_APEX = SyntheticBidSubmission(
    bidder_name="Apex Enterprise Systems India Pvt Ltd",
    bidder_type="Primary System Integrator (SI)",
    incorporation_year=2017,
    experience_years=9,
    annual_turnover_inr_cr=45.0,
    net_worth_inr_cr=18.5,
    emd_submitted_amount="INR 2,00,000 (Bank Guarantee Attached)",
    emd_status="Submitted (Valid BG Attached)",
    technical_responses={
        "processor": "Dual Intel Xeon Gold 6430 (24 Cores, 2.1 GHz Base)",
        "ram": "128 GB DDR5 ECC Registered Memory",
        "storage": "2x 960 GB NVMe SSD (OS) + 4x 3.84 TB Enterprise SAS SSD",
        "warranty": "5 Years Comprehensive 24x7 4-Hour Call-to-Repair Onsite Support",
        "tvc_certificate": "OEM Lab Technical Verification Certificate (TVC) Attached",
        "maf_form": "Server OEM Authorization Letter Submitted (Tender Specific)",
        "os_compatibility": "Red Hat Enterprise Linux 9.x / Windows Server 2022 Certified"
    },
    certifications=[
        "ISO 9001:2015",
        "ISO 27001:2022",
        "ISO 20000-1:2018",
        "CMMI Level 3 (Services)"
    ],
    available_documents=[
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
    blacklisted=False
)

SYNTHETIC_BID_NOVATECH = SyntheticBidSubmission(
    bidder_name="NovaTech Solutions LLP",
    bidder_type="Authorized Partner / Bidder",
    incorporation_year=2021,
    experience_years=4,
    annual_turnover_inr_cr=16.0,
    net_worth_inr_cr=4.5,
    emd_submitted_amount="INR 2,00,000 (Online NEFT Transfer)",
    emd_status="Submitted (Receipt Enclosed)",
    technical_responses={
        "processor": "Dual Intel Xeon Silver 4410Y (12 Cores, 2.0 GHz)",  # Mismatch (requires 24 Cores)
        "ram": "128 GB DDR5 Memory",
        "storage": "1 TB SATA HDD Array",  # Mismatch (requires Enterprise NVMe/SAS SSD)
        "warranty": "3 Years Standard Warranty + 2 Years Extended",  # Needs verification
        "tvc_certificate": "Under Process from OEM Lab",  # Missing TVC
        "maf_form": "General Partner Authorization (Not Tender Specific)"
    },
    certifications=[
        "ISO 9001:2015"
    ],
    available_documents=[
        "Certificate of Incorporation",
        "GST Registration Certificate",
        "PAN Card Copy",
        "Audited Balance Sheets (2 Years)",
        "EMD Payment Receipt (Rs. 2,00,000)",
        "Power of Attorney"
    ],
    blacklisted=False
)

SYNTHETIC_BID_INELIGIBLE = SyntheticBidSubmission(
    bidder_name="Zenith Infraventures Pvt Ltd",
    bidder_type="Trader / Reseller",
    incorporation_year=2024,
    experience_years=1,
    annual_turnover_inr_cr=2.5,
    net_worth_inr_cr=-0.5,
    emd_submitted_amount="None (Claiming MSME Exemption without valid certificate)",
    emd_status="Missing / Exemption Claim Disputed",
    technical_responses={
        "processor": "Single 8-Core Desktop Processor",
        "ram": "32 GB RAM",
        "storage": "512 GB SSD",
        "warranty": "1 Year Return to Bench",
        "tvc_certificate": "Not Available",
        "maf_form": "Not Available"
    },
    certifications=[],
    available_documents=[
        "Certificate of Incorporation",
        "PAN Card Copy"
    ],
    blacklisted=True
)

SYNTHETIC_BIDS: Dict[str, SyntheticBidSubmission] = {
    "bid_apex_compliant": SYNTHETIC_BID_APEX,
    "bid_novatech_borderline": SYNTHETIC_BID_NOVATECH,
    "bid_zenith_ineligible": SYNTHETIC_BID_INELIGIBLE
}

# 2. Real ELCOT 152-Page Tender Page Excerpts
ELCOT_TENDER_PAGES = {
    1: """
ELECTRONICS CORPORATION OF TAMIL NADU LIMITED (ELCOT)
(A Government of Tamil Nadu Undertaking)
MHU Complex, 692, Anna Salai, Nandanam, Chennai - 600 035.
Tender Ref No: ELCOT/PROC/OT/33364/2026-27
Date of RFP Release: 05-March-2026

TENDER DOCUMENT (152 PAGES)
FOR RATE CONTRACT FOR SUPPLY, INSTALLATION, COMMISSIONING AND 5 YEARS ON-SITE COMPREHENSIVE WARRANTY MAINTENANCE OF ENTERPRISE RACK SERVERS, SAN STORAGE, TOP-OF-RACK SWITCHES AND VIRTUALIZATION INFRASTRUCTURE ACROSS TAMIL NADU STATE DATA CENTER (TNSDC).

Total Document Size: 152 Pages
Tender Fee: INR 10,000 (Non-refundable)
Earnest Money Deposit (EMD): INR 2,00,000 (Rupees Two Lakhs only)
Bid Validity: 180 Days from Technical Bid Opening
Two Cover System: Cover A - Technical Bid & Eligibility Credentials, Cover B - Price Bid
Submission Portal: https://tntenders.gov.in (Online e-Submission only)
Submission Deadline: 10-April-2026, 15:00 Hrs IST
    """,
    109: """
SECTION 3: BIDDER ELIGIBILITY CRITERIA (PAGES 109-114)
The Bidder must strictly satisfy all conditions on the date of submission with documentary evidence. Failure to provide required proof will result in summary rejection of the technical bid.

Clause 3.1: Legal Constitution & Minimum Experience (Page 109)
The Bidder must be a registered legal entity under Companies Act 1956/2013 or LLP, operating in India for at least three (3) completed financial years as on 31-March-2025.
Documentary Evidence Required: Certificate of Incorporation and Memorandum & Articles of Association.

Clause 3.2: Statutory Tax Registrations (Page 109)
The Bidder must have active GST Registration in Tamil Nadu/India and a valid PAN card.
Documentary Evidence Required: Copy of GST Registration Certificate & PAN Card.

Clause 3.3: Average Annual Turnover (Page 109)
The average annual sales turnover of the Bidder in the last three financial years (FY 2022-23, FY 2023-24, FY 2024-25) must not be less than INR 25,00,00,000 (INR 25.00 Crores).
Documentary Evidence Required: Turnover Certificate certified by Chartered Accountant with UDIN and Audited Balance Sheets.
    """,
    110: """
SECTION 3: BIDDER ELIGIBILITY CRITERIA (CONTINUED - PAGE 110)

Clause 3.4: Quality & Security Certifications (Page 110)
The Bidder must hold valid ISO 9001:2015 (Quality Management) and ISO 27001:2013 or ISO 27001:2022 (Information Security) certificates as on the bid release date.
Documentary Evidence Required: Valid ISO certificates with verifiable QR/URL.

Clause 3.5: Non-Blacklisting Declaration (Page 110)
The Bidder must not have been debarred or blacklisted by ELCOT, Government of Tamil Nadu, Government of India, or any State/Central PSU.
Documentary Evidence Required: Undertaking on Rs. 100 Non-Judicial Stamp Paper attested by Notary Public.

Clause 3.6: OEM Authorization & Standing (Page 110)
The Bidder must be an OEM or Authorized System Integrator of the proposed server hardware with tender-specific Manufacturer Authorization Form (MAF) signed by OEM Country Head.
Documentary Evidence Required: OEM MAF in prescribed Form F-4.
    """,
    124: """
SECTION 4: TECHNICAL SPECIFICATIONS & TECHNICAL VERIFICATION CERTIFICATE (TVC) (PAGE 124)

Clause 4.1: Enterprise 2U Dual-Socket Rack Server Specifications (Page 124)
- Processor: 2x Intel Xeon Gold Scalable Processor (Minimum 24 Cores per CPU, 2.1 GHz Base Frequency, 45MB L3 Cache or higher).
- Memory: 128 GB DDR5 4800MHz ECC Registered Memory, expandable to 2TB across 32 DIMM slots.
- Storage Configuration: 2x 960 GB NVMe SSD (M.2/U.3 for OS in Hardware RAID-1) PLUS minimum 4x 3.84 TB Enterprise SAS 12Gbps Mixed-Use SSDs.
- Network Interface: 4x 10/25GbE SFP28 Ports + 2x 1GbE Base-T Ports + Dedicated IPMI 2.0 Management Port.
- Power Supply: Dual Redundant (1+1) 80-Plus Platinum Hot-Plug Power Supplies (>= 1100W).

Clause 4.2: Technical Verification Certificate (TVC) (Page 124)
All proposed server models and subsystems must carry a formal Technical Verification Certificate (TVC) issued by the OEM central engineering lab or MeitY/STQC accredited laboratory certifying full compliance with all parameters in Clause 4.1.

Clause 4.3: Warranty & SLA (Page 124)
5 Years Comprehensive On-site 24x7 4-Hour Call-to-Repair Support directly backed by the OEM with all spare parts included.
    """,
    142: """
SECTION 5: COMMERCIAL TERMS & EMD (PAGE 142)

Clause 5.1: Earnest Money Deposit (EMD) (Page 142)
The Bidder must submit an EMD of INR 2,00,000 (Rupees Two Lakhs only) through Electronic Bank Guarantee (e-BG) or online transfer before the bid closing time. MSME exemptions shall be considered only upon submission of valid Tamil Nadu NSIC / Udyam registration matching the exact NIC code.

Clause 5.2: Strict Separation of Technical and Price Bids (Page 142)
The financial quotes, unit prices, or total bid price MUST NOT be revealed anywhere in Cover A (Technical Bid). Any inclusion of pricing in the Technical Bid will result in immediate disqualification without evaluation.

Clause 5.3: Performance Security (Page 142)
5% of total contract value within 15 days of Letter of Acceptance, valid for 63 months.
    """,
    148: """
SECTION 6: MANDATORY DOCUMENTS CHECKLIST (PAGE 148)
1. EMD proof (Bank Guarantee of Rs. 2 Lakhs) [Page 142, Clause 5.1]
2. Tender fee receipt of Rs. 10,000 [Page 1]
3. Certificate of Incorporation & MoA/AoA [Page 109, Clause 3.1]
4. GST Registration & PAN Card [Page 109, Clause 3.2]
5. CA Certified 3-Year Turnover Statement with UDIN [Page 109, Clause 3.3]
6. Audited Balance Sheet & P&L Statements [Page 109, Clause 3.3]
7. ISO 9001:2015 & ISO 27001:2022 Certificates [Page 110, Clause 3.4]
8. Notarized Non-Blacklisting Affidavit [Page 110, Clause 3.5]
9. Manufacturer Authorization Form (MAF) in Form F-4 [Page 110, Clause 3.6]
10. OEM Technical Verification Certificate (TVC) [Page 124, Clause 4.2]
11. Technical Compliance Statement with Datasheets [Page 124, Clause 4.1]
12. Power of Attorney / Board Resolution [Page 109]
    """
}

def generate_elcot_analysis(bid: SyntheticBidSubmission) -> TenderAnalysis:
    metadata = TenderMetadata(
        id="tender_elcot_servers",
        title="Procurement & 5-Yr Maintenance of Enterprise Servers & Storage for TNSDC",
        reference_number="ELCOT/PROC/OT/33364/2026-27",
        issuing_authority="Electronics Corporation of Tamil Nadu Limited (ELCOT)",
        tender_type="Open E-Tender (Two Cover System: Technical & Price)",
        estimated_value="INR 32.50 Crores (~$3.9M USD)",
        emd_amount="INR 2,00,000 (Rupees Two Lakhs only)",
        tender_fee="INR 10,000 (Non-refundable)",
        submission_deadline="10-April-2026 at 15:00 Hrs IST",
        bid_validity_period="180 Days from Technical Bid Opening",
        pages_count=152,
        scope_summary="Supply, installation, technical verification certificate (TVC) validation, and 5-year comprehensive 24x7 maintenance of 2U enterprise dual-socket servers, storage arrays, and network switches."
    )

    requirements = [
        Requirement(
            id="REQ-E01",
            category=RequirementCategory.ELIGIBILITY,
            title="Company Existence & Legal Registration",
            description="Bidder must be registered under Companies Act or LLP, operating in India for at least 3 completed financial years.",
            source_page=109,
            section_name="Section 3: Bidder Eligibility Criteria",
            mandatory=True,
            threshold_value=">= 3 Years in India",
            evidence=EvidenceReference(
                page=109,
                section_name="Bidder Eligibility Criteria",
                clause_ref="Clause 3.1",
                exact_text_excerpt="The Bidder must be a registered legal entity under Companies Act 1956/2013 or LLP, operating in India for at least three (3) completed financial years as on 31-March-2025."
            )
        ),
        Requirement(
            id="REQ-E02",
            category=RequirementCategory.ELIGIBILITY,
            title="GST Registration & PAN Card",
            description="Active GST registration in India and valid PAN card copy must be furnished.",
            source_page=109,
            section_name="Section 3: Bidder Eligibility Criteria",
            mandatory=True,
            threshold_value="Active GST & PAN",
            evidence=EvidenceReference(
                page=109,
                section_name="Bidder Eligibility Criteria",
                clause_ref="Clause 3.2",
                exact_text_excerpt="The Bidder must have active GST Registration in Tamil Nadu/India and a valid PAN card. Documentary Evidence Required: Copy of GST Registration Certificate & PAN Card."
            )
        ),
        Requirement(
            id="REQ-E03",
            category=RequirementCategory.ELIGIBILITY,
            title="Quality & Security Certifications (ISO 9001 & 27001)",
            description="Valid ISO 9001:2015 and ISO 27001:2013/2022 certificates on bid release date.",
            source_page=110,
            section_name="Section 3: Bidder Eligibility Criteria",
            mandatory=True,
            threshold_value="ISO 9001:2015 + ISO 27001",
            evidence=EvidenceReference(
                page=110,
                section_name="Bidder Eligibility Criteria",
                clause_ref="Clause 3.4",
                exact_text_excerpt="The Bidder must hold valid ISO 9001:2015 and ISO 27001:2013 or ISO 27001:2022 certificates as on the bid release date."
            )
        ),
        Requirement(
            id="REQ-E04",
            category=RequirementCategory.ELIGIBILITY,
            title="Non-Blacklisting Declaration",
            description="Undertaking on Rs. 100 Stamp Paper confirming no debarment by ELCOT, Tamil Nadu Govt or Govt of India.",
            source_page=110,
            section_name="Section 3: Bidder Eligibility Criteria",
            mandatory=True,
            threshold_value="Notarized Undertaking",
            evidence=EvidenceReference(
                page=110,
                section_name="Bidder Eligibility Criteria",
                clause_ref="Clause 3.5",
                exact_text_excerpt="The Bidder must not have been debarred or blacklisted by ELCOT, Government of Tamil Nadu, Government of India, or any State/Central PSU."
            )
        ),
        Requirement(
            id="REQ-T01",
            category=RequirementCategory.TECHNICAL,
            title="Processor: Dual Intel Xeon Gold (Minimum 24 Cores)",
            description="2x Intel Xeon Gold Scalable CPU, minimum 24 Cores per CPU, 2.1 GHz Base Frequency, 45MB L3 Cache.",
            source_page=124,
            section_name="Section 4: Technical Specifications",
            mandatory=True,
            threshold_value="Dual Xeon >= 24 Cores/CPU",
            evidence=EvidenceReference(
                page=124,
                section_name="Technical Specifications",
                clause_ref="Clause 4.1",
                exact_text_excerpt="Processor: 2x Intel Xeon Gold Scalable Processor (Minimum 24 Cores per CPU, 2.1 GHz Base Frequency, 45MB L3 Cache or higher)."
            )
        ),
        Requirement(
            id="REQ-T02",
            category=RequirementCategory.TECHNICAL,
            title="Memory: 128 GB DDR5 ECC Registered",
            description="128 GB DDR5 4800MHz ECC Registered Memory, expandable to 2TB.",
            source_page=124,
            section_name="Section 4: Technical Specifications",
            mandatory=True,
            threshold_value=">= 128 GB DDR5 ECC",
            evidence=EvidenceReference(
                page=124,
                section_name="Technical Specifications",
                clause_ref="Clause 4.1",
                exact_text_excerpt="Memory: 128 GB DDR5 4800MHz ECC Registered Memory, expandable to 2TB across 32 DIMM slots."
            )
        ),
        Requirement(
            id="REQ-T03",
            category=RequirementCategory.TECHNICAL,
            title="Storage Configuration: NVMe OS RAID-1 + SAS SSDs",
            description="2x 960 GB NVMe SSD for OS in RAID-1 plus minimum 4x 3.84 TB Enterprise SAS Mixed-Use SSDs.",
            source_page=124,
            section_name="Section 4: Technical Specifications",
            mandatory=True,
            threshold_value="2x 960GB NVMe + 4x 3.84TB SAS SSD",
            evidence=EvidenceReference(
                page=124,
                section_name="Technical Specifications",
                clause_ref="Clause 4.1",
                exact_text_excerpt="Storage Configuration: 2x 960 GB NVMe SSD (M.2/U.3 for OS in Hardware RAID-1) PLUS minimum 4x 3.84 TB Enterprise SAS 12Gbps Mixed-Use SSDs."
            )
        ),
        Requirement(
            id="REQ-T04",
            category=RequirementCategory.TECHNICAL,
            title="Technical Verification Certificate (TVC)",
            description="Technical Verification Certificate (TVC) issued by OEM central engineering lab or MeitY/STQC lab.",
            source_page=124,
            section_name="Section 4: Technical Specifications",
            mandatory=True,
            threshold_value="Mandatory OEM Lab TVC",
            evidence=EvidenceReference(
                page=124,
                section_name="Technical Specifications",
                clause_ref="Clause 4.2",
                exact_text_excerpt="Clause 4.2: Technical Verification Certificate (TVC) - All proposed server models and subsystems must carry a formal Technical Verification Certificate (TVC) issued by the OEM central engineering lab or MeitY/STQC accredited laboratory certifying full compliance.",
                tvc_required=True
            )
        ),
        Requirement(
            id="REQ-T05",
            category=RequirementCategory.TECHNICAL,
            title="5 Years 24x7 4-Hour Response Onsite Warranty",
            description="5 Years Comprehensive On-site 24x7 4-Hour Call-to-Repair Support directly backed by OEM.",
            source_page=124,
            section_name="Section 4: Technical Specifications",
            mandatory=True,
            threshold_value="5 Yrs 24x7 4-Hr Call-to-Repair",
            evidence=EvidenceReference(
                page=124,
                section_name="Technical Specifications",
                clause_ref="Clause 4.3",
                exact_text_excerpt="5 Years Comprehensive On-site 24x7 4-Hour Call-to-Repair Support directly backed by the OEM with all spare parts included."
            )
        ),
        Requirement(
            id="REQ-F01",
            category=RequirementCategory.FINANCIAL,
            title="Average Annual Turnover (>= INR 25.00 Crores)",
            description="Average annual turnover in last 3 financial years must not be less than INR 25.00 Crores with UDIN certificate.",
            source_page=109,
            section_name="Section 3: Bidder Eligibility Criteria",
            mandatory=True,
            threshold_value=">= INR 25.00 Cr",
            evidence=EvidenceReference(
                page=109,
                section_name="Bidder Eligibility Criteria",
                clause_ref="Clause 3.3",
                exact_text_excerpt="The average annual sales turnover of the Bidder in the last three financial years (FY 2022-23, FY 2023-24, FY 2024-25) must not be less than INR 25,00,00,000 (INR 25.00 Crores)."
            )
        ),
        Requirement(
            id="REQ-F02",
            category=RequirementCategory.FINANCIAL,
            title="Earnest Money Deposit (EMD) (INR 2,00,000)",
            description="EMD of INR 2,00,000 submitted through Electronic Bank Guarantee (e-BG) or online transfer.",
            source_page=142,
            section_name="Section 5: Commercial Terms & EMD",
            mandatory=True,
            threshold_value="INR 2,00,000 EMD",
            evidence=EvidenceReference(
                page=142,
                section_name="Commercial Terms & EMD",
                clause_ref="Clause 5.1",
                exact_text_excerpt="The Bidder must submit an EMD of INR 2,00,000 (Rupees Two Lakhs only) through Electronic Bank Guarantee (e-BG) or online transfer before the bid closing time."
            )
        )
    ]

    # Evaluate dynamic compliance vs submitted bid
    compliance_results = []

    # 1. Experience
    exp_ok = bid.experience_years >= 3
    compliance_results.append(ComplianceItem(
        requirement_id="REQ-E01",
        requirement_title="Company Existence & Legal Registration",
        category=RequirementCategory.ELIGIBILITY,
        status=ComplianceStatus.COMPLIANT if exp_ok else ComplianceStatus.NON_COMPLIANT,
        source_page=109,
        section_name="Section 3: Bidder Eligibility Criteria",
        mandatory=True,
        tender_requirement_summary="At least 3 completed financial years in India (Clause 3.1)",
        bidder_submitted_response=f"Incorporated in {bid.incorporation_year} ({bid.experience_years} completed operating years)",
        reasoning=f"Bidder has {bid.experience_years} years operating track record, fulfilling the 3-year threshold required on Page 109." if exp_ok else f"Bidder only has {bid.experience_years} year(s) operating experience, failing the mandatory 3-year minimum (Page 109).",
        evidence_excerpt="Clause 3.1 (Page 109): Bidder must be operating in India for at least three (3) completed financial years as on 31-March-2025.",
        suggested_remediation=None if exp_ok else "Ineligible to bid as primary contractor under Clause 3.1."
    ))

    # 2. GST / PAN
    has_gst = any("GST" in d for d in bid.available_documents) and any("PAN" in d for d in bid.available_documents)
    compliance_results.append(ComplianceItem(
        requirement_id="REQ-E02",
        requirement_title="GST Registration & PAN Card",
        category=RequirementCategory.ELIGIBILITY,
        status=ComplianceStatus.COMPLIANT if has_gst else ComplianceStatus.NON_COMPLIANT,
        source_page=109,
        section_name="Section 3: Bidder Eligibility Criteria",
        mandatory=True,
        tender_requirement_summary="Active GST registration & PAN card copy (Clause 3.2)",
        bidder_submitted_response="GST Certificate and PAN Card copies attached in credential pack" if has_gst else "Missing GST/PAN copies",
        reasoning="Both statutory registrations are on record and verified." if has_gst else "Mandatory statutory tax registration copies missing (Page 109).",
        evidence_excerpt="Clause 3.2 (Page 109): The Bidder must have active GST Registration in Tamil Nadu/India and a valid PAN card."
    ))

    # 3. Certifications
    has_iso9001 = any("9001" in c for c in bid.certifications)
    has_iso27001 = any("27001" in c for c in bid.certifications)
    iso_status = ComplianceStatus.COMPLIANT if (has_iso9001 and has_iso27001) else (ComplianceStatus.NEEDS_VERIFICATION if has_iso9001 else ComplianceStatus.NON_COMPLIANT)
    compliance_results.append(ComplianceItem(
        requirement_id="REQ-E03",
        requirement_title="Quality & Security Certifications (ISO 9001 & 27001)",
        category=RequirementCategory.ELIGIBILITY,
        status=iso_status,
        source_page=110,
        section_name="Section 3: Bidder Eligibility Criteria",
        mandatory=True,
        tender_requirement_summary="Valid ISO 9001:2015 and ISO 27001:2013/2022 (Clause 3.4)",
        bidder_submitted_response=f"Current Certs: {', '.join(bid.certifications) or 'None'}",
        reasoning="Both ISO 9001 and ISO 27001 are valid with active accreditation (Page 110)." if iso_status == ComplianceStatus.COMPLIANT else "Missing mandatory ISO 27001 security certification required under Clause 3.4 (Page 110).",
        evidence_excerpt="Clause 3.4 (Page 110): The Bidder must hold valid ISO 9001:2015 and ISO 27001:2013 or ISO 27001:2022 certificates as on the bid release date.",
        suggested_remediation=None if iso_status == ComplianceStatus.COMPLIANT else "Acquire fast-track ISO 27001 audit or form qualifying consortium."
    ))

    # 4. Non-blacklisting
    compliance_results.append(ComplianceItem(
        requirement_id="REQ-E04",
        requirement_title="Non-Blacklisting Declaration",
        category=RequirementCategory.ELIGIBILITY,
        status=ComplianceStatus.NON_COMPLIANT if bid.blacklisted else ComplianceStatus.COMPLIANT,
        source_page=110,
        section_name="Section 3: Bidder Eligibility Criteria",
        mandatory=True,
        tender_requirement_summary="Notarized non-blacklisting undertaking on Rs. 100 Stamp Paper (Clause 3.5)",
        bidder_submitted_response=f"Blacklisted Flag: {'YES' if bid.blacklisted else 'NO (Spotless record, affidavit enclosed)'}",
        reasoning="Affidavit on non-judicial stamp paper enclosed, confirming clean compliance history (Page 110)." if not bid.blacklisted else "CRITICAL: Entity is blacklisted/debarred by authorities, causing immediate disqualification.",
        evidence_excerpt="Clause 3.5 (Page 110): The Bidder must not have been debarred or blacklisted by ELCOT, Government of Tamil Nadu, Government of India, or any State/Central PSU."
    ))

    # 5. Processor
    proc_resp = bid.technical_responses.get("processor", "")
    proc_ok = "24 Core" in proc_resp or "24 Cores" in proc_resp or "Gold 6430" in proc_resp
    compliance_results.append(ComplianceItem(
        requirement_id="REQ-T01",
        requirement_title="Processor: Dual Intel Xeon Gold (Minimum 24 Cores)",
        category=RequirementCategory.TECHNICAL,
        status=ComplianceStatus.COMPLIANT if proc_ok else ComplianceStatus.NON_COMPLIANT,
        source_page=124,
        section_name="Section 4: Technical Specifications",
        mandatory=True,
        tender_requirement_summary="Dual Intel Xeon Gold (>= 24 Cores/CPU, 2.1 GHz) (Clause 4.1)",
        bidder_submitted_response=proc_resp or "No response specified",
        reasoning=f"Proposed processor ({proc_resp}) meets or exceeds 24-core requirement (Page 124)." if proc_ok else f"Offered processor ({proc_resp}) falls short of mandatory 24-core specification (Page 124).",
        evidence_excerpt="Clause 4.1 (Page 124): Processor: 2x Intel Xeon Gold Scalable Processor (Minimum 24 Cores per CPU, 2.1 GHz Base Frequency, 45MB L3 Cache or higher)."
    ))

    # 6. RAM
    ram_resp = bid.technical_responses.get("ram", "")
    ram_ok = "128" in ram_resp and "DDR5" in ram_resp
    compliance_results.append(ComplianceItem(
        requirement_id="REQ-T02",
        requirement_title="Memory: 128 GB DDR5 ECC Registered",
        category=RequirementCategory.TECHNICAL,
        status=ComplianceStatus.COMPLIANT if ram_ok else ComplianceStatus.NEEDS_VERIFICATION,
        source_page=124,
        section_name="Section 4: Technical Specifications",
        mandatory=True,
        tender_requirement_summary="128 GB DDR5 4800MHz ECC Registered Memory (Clause 4.1)",
        bidder_submitted_response=ram_resp or "128 GB DDR5",
        reasoning="Proposed memory capacity and speed comply with Clause 4.1 specifications (Page 124).",
        evidence_excerpt="Clause 4.1 (Page 124): Memory: 128 GB DDR5 4800MHz ECC Registered Memory, expandable to 2TB across 32 DIMM slots."
    ))

    # 7. Storage
    storage_resp = bid.technical_responses.get("storage", "")
    storage_ok = ("NVMe" in storage_resp or "SSD" in storage_resp) and ("3.84" in storage_resp or "SAS" in storage_resp)
    compliance_results.append(ComplianceItem(
        requirement_id="REQ-T03",
        requirement_title="Storage Configuration: NVMe OS RAID-1 + SAS SSDs",
        category=RequirementCategory.TECHNICAL,
        status=ComplianceStatus.COMPLIANT if storage_ok else ComplianceStatus.NON_COMPLIANT,
        source_page=124,
        section_name="Section 4: Technical Specifications",
        mandatory=True,
        tender_requirement_summary="2x 960GB NVMe OS RAID-1 + 4x 3.84TB SAS SSD (Clause 4.1)",
        bidder_submitted_response=storage_resp or "Not specified",
        reasoning="Storage configuration includes both mirrored NVMe OS drives and 4x SAS enterprise SSDs (Page 124)." if storage_ok else f"Storage response ({storage_resp}) does not meet the specified dual NVMe + 4x SAS SSD matrix (Page 124).",
        evidence_excerpt="Clause 4.1 (Page 124): Storage Configuration: 2x 960 GB NVMe SSD (M.2/U.3 for OS in Hardware RAID-1) PLUS minimum 4x 3.84 TB Enterprise SAS 12Gbps Mixed-Use SSDs."
    ))

    # 8. TVC Certificate
    tvc_resp = bid.technical_responses.get("tvc_certificate", "")
    tvc_ok = "Attached" in tvc_resp or any("TVC" in d or "Technical Verification" in d for d in bid.available_documents)
    compliance_results.append(ComplianceItem(
        requirement_id="REQ-T04",
        requirement_title="Technical Verification Certificate (TVC)",
        category=RequirementCategory.TECHNICAL,
        status=ComplianceStatus.COMPLIANT if tvc_ok else ComplianceStatus.NON_COMPLIANT,
        source_page=124,
        section_name="Section 4: Technical Specifications",
        mandatory=True,
        tender_requirement_summary="OEM Lab / STQC Technical Verification Certificate (TVC) (Clause 4.2)",
        bidder_submitted_response=tvc_resp or "TVC Pending",
        reasoning="OEM central engineering lab Technical Verification Certificate (TVC) attached to technical bid (Page 124)." if tvc_ok else "CRITICAL: Missing mandatory TVC certificate. ELCOT tender explicitly mandates TVC; omission causes technical rejection (Page 124).",
        evidence_excerpt="Clause 4.2 (Page 124): Technical Verification Certificate (TVC) - All proposed server models and subsystems must carry a formal Technical Verification Certificate (TVC) issued by the OEM central engineering lab.",
        suggested_remediation=None if tvc_ok else "Request urgent TVC letter from Server OEM Lab before bid submission."
    ))

    # 9. Warranty
    warr_resp = bid.technical_responses.get("warranty", "")
    warr_ok = "5 Year" in warr_resp or "5 Years" in warr_resp
    compliance_results.append(ComplianceItem(
        requirement_id="REQ-T05",
        requirement_title="5 Years 24x7 4-Hour Response Onsite Warranty",
        category=RequirementCategory.TECHNICAL,
        status=ComplianceStatus.COMPLIANT if warr_ok else ComplianceStatus.NEEDS_VERIFICATION,
        source_page=124,
        section_name="Section 4: Technical Specifications",
        mandatory=True,
        tender_requirement_summary="5 Years 24x7 4-Hour Call-to-Repair Direct OEM Support (Clause 4.3)",
        bidder_submitted_response=warr_resp or "5 Years 24x7 OEM Support",
        reasoning="Direct OEM 5-year 24x7 4-hour SLA confirmed in authorization paperwork (Page 124)." if warr_ok else "Offered warranty duration requires formal OEM commitment letter for 5 full years (Page 124).",
        evidence_excerpt="Clause 4.3 (Page 124): 5 Years Comprehensive On-site 24x7 4-Hour Call-to-Repair Support directly backed by the OEM with all spare parts included."
    ))

    # 10. Turnover
    turnover_ok = bid.annual_turnover_inr_cr >= 25.0
    compliance_results.append(ComplianceItem(
        requirement_id="REQ-F01",
        requirement_title="Average Annual Turnover (>= INR 25.00 Crores)",
        category=RequirementCategory.FINANCIAL,
        status=ComplianceStatus.COMPLIANT if turnover_ok else ComplianceStatus.NON_COMPLIANT,
        source_page=109,
        section_name="Section 3: Bidder Eligibility Criteria",
        mandatory=True,
        tender_requirement_summary="Average 3-year turnover >= INR 25.00 Crores (Clause 3.3)",
        bidder_submitted_response=f"Annual Turnover: INR {bid.annual_turnover_inr_cr:.1f} Crores",
        reasoning=f"Reported turnover of INR {bid.annual_turnover_inr_cr:.1f} Cr satisfies the INR 25.00 Cr requirement (Page 109)." if turnover_ok else f"Reported turnover of INR {bid.annual_turnover_inr_cr:.1f} Cr is below the mandatory INR 25.00 Cr threshold (Page 109).",
        evidence_excerpt="Clause 3.3 (Page 109): The average annual sales turnover of the Bidder in the last three financial years must not be less than INR 25,00,00,000 (INR 25.00 Crores)."
    ))

    # 11. EMD
    emd_ok = "2,00,000" in bid.emd_submitted_amount or "200000" in bid.emd_submitted_amount or "Submitted" in bid.emd_status
    compliance_results.append(ComplianceItem(
        requirement_id="REQ-F02",
        requirement_title="Earnest Money Deposit (EMD) (INR 2,00,000)",
        category=RequirementCategory.FINANCIAL,
        status=ComplianceStatus.COMPLIANT if emd_ok else ComplianceStatus.NON_COMPLIANT,
        source_page=142,
        section_name="Section 5: Commercial Terms & EMD",
        mandatory=True,
        tender_requirement_summary="INR 2,00,000 via Bank Guarantee or online payment (Clause 5.1)",
        bidder_submitted_response=f"{bid.emd_submitted_amount} - Status: {bid.emd_status}",
        reasoning="EMD Bank Guarantee of Rs. 2,00,000 verified in accordance with Clause 5.1 (Page 142)." if emd_ok else "CRITICAL: EMD missing or exemption invalid. Technical bid will be rejected at opening (Page 142).",
        evidence_excerpt="Clause 5.1 (Page 142): The Bidder must submit an EMD of INR 2,00,000 (Rupees Two Lakhs only) through Electronic Bank Guarantee (e-BG) or online transfer."
    ))

    # Missing documents
    required_doc_checklist = [
        ("EMD Bank Guarantee (Rs. 2,00,000)", True, 142, "Clause 5.1", "Rejection at bid opening"),
        ("Tender Fee Payment Receipt (Rs. 10,000)", True, 1, "Clause 1.2", "Administrative rejection"),
        ("Certificate of Incorporation & MoA/AoA", True, 109, "Clause 3.1", "Eligibility disqualification"),
        ("GST Registration Certificate & PAN Card", True, 109, "Clause 3.2", "Statutory non-compliance"),
        ("CA Certified Turnover Statement with UDIN", True, 109, "Clause 3.3", "Financial disqualification"),
        ("ISO 9001:2015 Certificate", True, 110, "Clause 3.4", "Technical bid rejection"),
        ("ISO 27001:2022 Certificate", True, 110, "Clause 3.4", "Technical bid rejection"),
        ("Notarized Non-Blacklisting Affidavit", True, 110, "Clause 3.5", "Statutory rejection"),
        ("OEM Authorization Form (MAF) in Form F-4", True, 110, "Clause 3.6", "Technical disqualification"),
        ("OEM Technical Verification Certificate (TVC)", True, 124, "Clause 4.2", "Technical compliance rejection"),
        ("Power of Attorney for Authorized Signatory", True, 109, "Clause 3.1", "Bid deemed invalid")
    ]

    missing_docs = []
    for dname, mand, pg, clause, impact in required_doc_checklist:
        present = any(dname.lower() in d.lower() or d.lower() in dname.lower() for d in bid.available_documents)
        if not present:
            missing_docs.append(MissingDocument(
                doc_name=dname,
                mandatory=mand,
                source_page=pg,
                section_name=f"Page {pg}",
                clause_ref=clause,
                status="Missing",
                impact=impact
            ))

    # Risks
    risks = [
        RiskItem(
            id="RISK-01",
            category="Technical Verification Certificate (TVC)",
            severity=RiskSeverity.HIGH,
            clause_title="Strict TVC Requirement (Clause 4.2 - Page 124)",
            clause_text="Clause 4.2: All proposed server models must carry a formal Technical Verification Certificate (TVC) issued by the OEM central engineering lab.",
            source_page=124,
            section_name="Section 4: Technical Specifications",
            plain_language_reason="Failure to provide the exact TVC format from the OEM central lab will lead to immediate disqualification without grace period.",
            mitigation_suggestion="Obtain pre-signed TVC directly from OEM Country Technology Office with tender reference ELCOT/PROC/OT/33364."
        ),
        RiskItem(
            id="RISK-02",
            category="Two-Cover Separation & Price Leakage",
            severity=RiskSeverity.HIGH,
            clause_title="Zero Financial Exposure in Technical Bid (Clause 5.2 - Page 142)",
            clause_text="Clause 5.2: Any inclusion of pricing, commercial quotes, or BOQ values in Cover A (Technical Bid) will result in immediate disqualification.",
            source_page=142,
            section_name="Section 5: Commercial Terms",
            plain_language_reason="Accidental inclusion of price figures in datasheets or MAF attachments causes fatal rejection.",
            mitigation_suggestion="Double-audit all Cover A PDF uploads to ensure no rate or price mentions are visible."
        ),
        RiskItem(
            id="RISK-03",
            category="24x7 4-Hour Call-to-Repair SLA",
            severity=RiskSeverity.MEDIUM,
            clause_title="Stringent 4-Hour Call-to-Repair Penalty (Clause 4.3 - Page 124)",
            clause_text="Clause 4.3: 5 Years on-site 24x7 4-hour call-to-repair SLA with standby server spares in Chennai.",
            source_page=124,
            section_name="Section 4: Technical Specifications",
            plain_language_reason="Downtime exceeding 4 hours triggers hourly penalties deducted from quarterly CAMC payments.",
            mitigation_suggestion="Ensure OEM maintains dedicated hot-spare stock at Chennai depot."
        )
    ]

    # Timeline
    timeline = [
        TimelineEvent(event_name="RFP Release Date", date_str="05-Mar-2026", source_page=1, critical=False),
        TimelineEvent(event_name="Pre-Bid Clarification Meeting (Chennai)", date_str="18-Mar-2026 11:30 IST", source_page=1, critical=True, notes="Clarify TVC submission format and storage NVMe tiers"),
        TimelineEvent(event_name="Issue of Corrigendum & Clarifications", date_str="25-Mar-2026", source_page=1, critical=False),
        TimelineEvent(event_name="Final Bid Submission Deadline", date_str="10-Apr-2026 15:00 IST", source_page=1, critical=True, notes="Must upload signed TVC & EMD e-BG on tntenders.gov.in"),
        TimelineEvent(event_name="Technical Bid Opening (Cover A)", date_str="11-Apr-2026 15:30 IST", source_page=1, critical=False),
        TimelineEvent(event_name="Price Bid Opening (Cover B)", date_str="24-Apr-2026", source_page=142, critical=False)
    ]

    # Calculate 4-Pillar Readiness Breakdown
    elig_items = [c for c in compliance_results if c.category == RequirementCategory.ELIGIBILITY]
    tech_items = [c for c in compliance_results if c.category == RequirementCategory.TECHNICAL]
    fin_items = [c for c in compliance_results if c.category == RequirementCategory.FINANCIAL]

    def score_group(items):
        if not items: return 100
        pts = sum(100 if c.status == ComplianceStatus.COMPLIANT else (50 if c.status == ComplianceStatus.NEEDS_VERIFICATION else 0) for c in items)
        return int(pts / len(items))

    elig_score = score_group(elig_items)
    tech_score = score_group(tech_items)
    fin_score = score_group(fin_items)
    doc_score = max(0, int(((len(required_doc_checklist) - len(missing_docs)) / len(required_doc_checklist)) * 100))

    overall = int((elig_score * 0.30) + (tech_score * 0.35) + (fin_score * 0.20) + (doc_score * 0.15))

    critical_issues = []
    if bid.blacklisted:
        critical_issues.append("Bidder is blacklisted/debarred by government authorities (Clause 3.5).")
    for c in compliance_results:
        if c.status == ComplianceStatus.NON_COMPLIANT and c.mandatory:
            critical_issues.append(f"Non-compliant on: {c.requirement_title} (Page {c.source_page}).")
    for m in missing_docs:
        critical_issues.append(f"Missing mandatory document: {m.doc_name} (Page {m.source_page}).")

    if bid.blacklisted or len(critical_issues) >= 3 or overall < 60:
        verdict = DecisionVerdict.DO_NOT_BID
        verdict_reason = f"High probability of technical/administrative disqualification ({len(critical_issues)} critical gaps). Do not bid independently."
    elif len(critical_issues) >= 1 or overall < 85:
        verdict = DecisionVerdict.BORDERLINE
        verdict_reason = f"Conditionally viable bid ({overall}% readiness), but requires closing {len(critical_issues)} mandatory document/specification gap(s) prior to submission."
    else:
        verdict = DecisionVerdict.PROCEED
        verdict_reason = f"Strong competitive fit ({overall}% overall readiness). All mandatory eligibility, technical TVC, and financial EMD parameters satisfied."

    readiness = BidReadinessBreakdown(
        eligibility_score=elig_score,
        technical_score=tech_score,
        documents_score=doc_score,
        financial_score=fin_score,
        overall_readiness=overall,
        verdict=verdict,
        verdict_rationale=verdict_reason,
        critical_issues=critical_issues[:4],
        key_strengths=[
            f"Financial turnover (INR {bid.annual_turnover_inr_cr} Cr) exceeds INR 25 Cr threshold",
            "Dual Xeon 24-core processor satisfies high-performance compute requirement",
            "OEM Technical Verification Certificate (TVC) available and validated",
            "ISO 9001 and ISO 27001 active certifications in place"
        ] if overall >= 75 else ["Corporate legal registration in order"],
        action_roadmap=[
            "Verify that OEM MAF (Form F-4) has the exact tender ref ELCOT/PROC/OT/33364.",
            "Confirm Technical Verification Certificate (TVC) covers both server chassis & power supplies.",
            "Verify that Cover A PDF contains ZERO pricing mentions as required by Clause 5.2.",
            "Upload notarized non-blacklisting affidavit on Rs. 100 stamp paper."
        ]
    )

    return TenderAnalysis(
        metadata=metadata,
        requirements=requirements,
        compliance_results=compliance_results,
        missing_documents=missing_docs,
        risks=risks,
        timeline=timeline,
        readiness=readiness,
        submitted_bid=bid,
        extracted_text_by_page=ELCOT_TENDER_PAGES
    )

# Sample Q&A Grounded Knowledge Base for ELCOT
ELCOT_QNA_KNOWLEDGE = [
    {
        "keywords": ["tvc", "technical verification", "certificate", "stqc"],
        "answer": "Under Clause 4.2 (Page 124), all proposed server models and subsystems must carry a formal Technical Verification Certificate (TVC) issued by the OEM central engineering lab or MeitY/STQC accredited laboratory certifying compliance with all hardware specifications.",
        "citations": [{"page": 124, "section": "Section 4: Technical Specifications", "text_snippet": "Clause 4.2: Technical Verification Certificate (TVC) - All proposed server models and subsystems must carry a formal Technical Verification Certificate (TVC) issued by the OEM central engineering lab or MeitY/STQC accredited laboratory", "relevance_score": 0.99}]
    },
    {
        "keywords": ["emd", "earnest money", "deposit", "fee", "cost"],
        "answer": "The Earnest Money Deposit (EMD) is INR 2,00,000 (Rupees Two Lakhs only) submitted via Electronic Bank Guarantee (e-BG) or online transfer before bid closing. The non-refundable tender fee is INR 10,000.",
        "citations": [{"page": 142, "section": "Section 5: Commercial Terms", "text_snippet": "Clause 5.1: The Bidder must submit an EMD of INR 2,00,000 (Rupees Two Lakhs only) through Electronic Bank Guarantee (e-BG) or online transfer before the bid closing time. Tender Fee: INR 10,000.", "relevance_score": 0.98}]
    },
    {
        "keywords": ["eligibility", "years", "experience", "age", "existence"],
        "answer": "Under Clause 3.1 (Page 109), the Bidder must be a registered legal entity under Companies Act or LLP operating in India for at least three (3) completed financial years as on 31-March-2025. Documentary proof: Certificate of Incorporation and MoA/AoA.",
        "citations": [{"page": 109, "section": "Section 3: Bidder Eligibility Criteria", "text_snippet": "Clause 3.1: The Bidder must be a registered legal entity under Companies Act 1956/2013 or LLP, operating in India for at least three (3) completed financial years as on 31-March-2025.", "relevance_score": 0.99}]
    },
    {
        "keywords": ["turnover", "financial", "revenue", "sales"],
        "answer": "Under Clause 3.3 (Page 109), the average annual sales turnover in the last 3 financial years (FY 2022-23, FY 2023-24, FY 2024-25) must not be less than INR 25,00,00,000 (INR 25.00 Crores), certified by a CA with UDIN.",
        "citations": [{"page": 109, "section": "Section 3: Bidder Eligibility Criteria", "text_snippet": "Clause 3.3: Average annual sales turnover of the Bidder in the last three financial years must not be less than INR 25,00,00,000 (INR 25.00 Crores).", "relevance_score": 0.98}]
    },
    {
        "keywords": ["processor", "cpu", "cores", "xeon"],
        "answer": "Under Clause 4.1 (Page 124), the server must be equipped with 2x Intel Xeon Gold Scalable Processors with a minimum of 24 Cores per CPU, 2.1 GHz Base Frequency, and 45MB L3 Cache or higher.",
        "citations": [{"page": 124, "section": "Section 4: Technical Specifications", "text_snippet": "Clause 4.1: Processor: 2x Intel Xeon Gold Scalable Processor (Minimum 24 Cores per CPU, 2.1 GHz Base Frequency, 45MB L3 Cache or higher).", "relevance_score": 0.99}]
    },
    {
        "keywords": ["price", "cover", "separate", "leak", "commercial"],
        "answer": "Under Clause 5.2 (Page 142), there is a strict separation between Cover A (Technical Bid) and Cover B (Price Bid). Financial quotes or unit rates MUST NOT be revealed inside Cover A. Any inclusion of pricing in the technical bid results in immediate disqualification.",
        "citations": [{"page": 142, "section": "Section 5: Commercial Terms", "text_snippet": "Clause 5.2: Strict Separation of Technical and Price Bids - The financial quotes, unit prices, or total bid price MUST NOT be revealed anywhere in Cover A (Technical Bid).", "relevance_score": 0.99}]
    }
]
