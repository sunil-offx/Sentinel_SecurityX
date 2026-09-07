from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class RequirementCategory(str, Enum):
    ELIGIBILITY = "eligibility"
    TECHNICAL = "technical"
    FINANCIAL = "financial"

class ComplianceStatus(str, Enum):
    COMPLIANT = "Compliant"
    NEEDS_VERIFICATION = "Needs Verification"
    NON_COMPLIANT = "Non-Compliant"

class RiskSeverity(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class DecisionVerdict(str, Enum):
    PROCEED = "PROCEED"
    BORDERLINE = "BORDERLINE"
    DO_NOT_BID = "DO_NOT_BID"

class EvidenceReference(BaseModel):
    page: int
    section_name: str
    clause_ref: str
    exact_text_excerpt: str
    tvc_required: bool = False  # Technical Verification Certificate provision

class SyntheticBidSubmission(BaseModel):
    bidder_name: str = "Apex Enterprise Systems India Pvt Ltd"
    bidder_type: str = "Primary System Integrator (SI)"
    incorporation_year: int = 2017
    experience_years: int = 9
    annual_turnover_inr_cr: float = 45.0
    net_worth_inr_cr: float = 18.5
    emd_submitted_amount: str = "INR 2,00,000 (Bank Guarantee)"
    emd_status: str = "Submitted (Valid BG Attached)"
    technical_responses: Dict[str, str] = {
        "processor": "Dual Intel Xeon Gold 6430 (24 Cores, 2.1 GHz Base)",
        "ram": "128 GB DDR5 ECC Registered Memory",
        "storage": "2x 960 GB NVMe SSD (RAID-1 OS) + 4x 3.84 TB SAS SSD",
        "warranty": "5 Years Comprehensive 24x7 4-Hour Call-to-Repair Support",
        "tvc_certificate": "OEM Lab Technical Verification Certificate (TVC) Attached",
        "maf_form": "Original Equipment Manufacturer (OEM) Authorization Submitted"
    }
    certifications: List[str] = [
        "ISO 9001:2015",
        "ISO 27001:2022",
        "ISO 20000-1:2018",
        "CMMI Level 3 (Services)"
    ]
    available_documents: List[str] = [
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
    ]
    blacklisted: bool = False

class Requirement(BaseModel):
    id: str
    category: RequirementCategory
    title: str
    description: str
    source_page: int
    section_name: str = "General"
    mandatory: bool = True
    threshold_value: Optional[str] = None
    evidence: EvidenceReference

class ComplianceItem(BaseModel):
    requirement_id: str
    requirement_title: str
    category: RequirementCategory
    status: ComplianceStatus
    source_page: int
    section_name: str
    mandatory: bool
    tender_requirement_summary: str
    bidder_submitted_response: str
    reasoning: str
    evidence_excerpt: str
    confidence_score: float = Field(default=0.96, ge=0.0, le=1.0)
    suggested_remediation: Optional[str] = None

class MissingDocument(BaseModel):
    doc_name: str
    mandatory: bool
    source_page: int
    section_name: str
    clause_ref: str
    status: str = "Missing"  # "Missing" | "Available" | "Needs Verification"
    impact: str

class RiskItem(BaseModel):
    id: str
    category: str
    severity: RiskSeverity
    clause_title: str
    clause_text: str
    source_page: int
    section_name: str
    plain_language_reason: str
    mitigation_suggestion: str

class TimelineEvent(BaseModel):
    event_name: str
    date_str: str
    source_page: int
    critical: bool = False
    notes: Optional[str] = None

class BidReadinessBreakdown(BaseModel):
    eligibility_score: int = 92
    technical_score: int = 87
    documents_score: int = 80
    financial_score: int = 95
    overall_readiness: int = 88
    verdict: DecisionVerdict = DecisionVerdict.PROCEED
    verdict_rationale: str
    critical_issues: List[str] = []
    key_strengths: List[str] = []
    action_roadmap: List[str] = []

class QnACitation(BaseModel):
    page: int
    section: str
    text_snippet: str
    relevance_score: float = 0.95

class QnARequest(BaseModel):
    tender_id: str
    question: str

class QnAResponse(BaseModel):
    question: str
    answer: str
    citations: List[QnACitation] = []
    is_grounded: bool = True
    grounding_note: Optional[str] = None

class TenderMetadata(BaseModel):
    id: str
    title: str
    reference_number: str
    issuing_authority: str
    tender_type: str = "Open E-Tender (Two Cover System)"
    estimated_value: str
    emd_amount: str
    tender_fee: str
    submission_deadline: str
    bid_validity_period: str
    pages_count: int
    scope_summary: str

class TenderAnalysis(BaseModel):
    metadata: TenderMetadata
    requirements: List[Requirement]
    compliance_results: List[ComplianceItem]
    missing_documents: List[MissingDocument]
    risks: List[RiskItem]
    timeline: List[TimelineEvent]
    readiness: BidReadinessBreakdown
    submitted_bid: SyntheticBidSubmission
    extracted_text_by_page: Dict[int, str] = {}
