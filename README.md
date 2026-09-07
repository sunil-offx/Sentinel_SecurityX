# TenderIQ — AI Tender Document Analyzer & Compliance Agent

> **Track:** Industries & MSME &middot; **Difficulty:** Medium (⭐⭐)  
> **Mission:** Transform complex, multi-page government and enterprise tender documents into actionable compliance matrices, risk assessments, bid/no-bid recommendations, grounded Q&A, and executive reports.

---

## 🚀 Features

- **Document Processing & Page Indexing**: Ingests PDF and DOCX documents with strict page-number preservation for 100% auditable citations.
- **Requirement Extraction & Classification**: Classifies tender clauses across **Eligibility**, **Technical**, and **Financial** categories.
- **Dynamic Compliance Agent**: Compares extracted requirements against company credentials to evaluate status (`Compliant`, `Needs Verification`, `Non-Compliant`) with grounded rationale.
- **Missing Document Detection**: Cross-references tender document checklists against corporate vaults to flag missing mandatory items before submission.
- **Risk Analysis Agent**: Flags liquidated damages, high EMD/PBG lockup, strict SLAs, and ambiguous penalties with plain-language reasons and mitigation blueprints.
- **Bid / No-Bid Decision Support**: Synthesizes a transparent Fit Score (0-100), 3-pillar breakdown (Eligibility, Technical, Financial), strengths, vulnerabilities, and roadmap to win.
- **Grounded Q&A (RAG Agent)**: Answers queries backed strictly by extracted tender pages, citing page numbers and enforcing a zero-hallucination guardrail ("Not specified in tender").
- **Executive Report Generation**: Single-click printable / PDF summary report.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn, Pydantic, PyMuPDF / pdfplumber / pypdf, python-docx
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide React
- **Multi-Agent Engine**: Modular pipeline supporting live LLMs (Anthropic Claude / OpenAI) with deterministic intelligent fallback for zero-latency offline demonstration.

---

## ⚡ Quickstart

### 1. Start the Backend API
```bash
# In project root
python backend/main.py
# Runs on http://127.0.0.1:8000
```
API Documentation available at: `http://127.0.0.1:8000/docs`

### 2. Start the Frontend Dashboard
```bash
# In frontend directory
cd frontend
npm run dev
# Runs on http://localhost:5173
```

---

## 🧪 Included Demonstration Scenarios

1. **Smart City CCTV & AI Video Analytics Tender (Pune Smart City - INR 48.5 Cr)**
   - Pre-loaded with realistic clauses across ANPR, NIST facial recognition, ISO/CMMI certifications, and liquidated damages.
2. **AIIMS Medical Imaging Suite RFP (INR 62 Cr)**
   - Illustrates non-compliant domain mismatch and strict biomedical equipment criteria.
3. **Live Company Profile Switching**:
   - **Apex Technologies**: Strong fit (INR 42.5 Cr turnover, CMMI L3, ISO 27001) &rarr; `RECOMMENDED` (94/100).
   - **NovaTech Systems**: Borderline (INR 18.2 Cr turnover, missing CMMI) &rarr; `BORDERLINE` (70/100).
   - **Zenith Infraventures**: Ineligible / Blacklisted &rarr; `NOT_RECOMMENDED` (35/100).
