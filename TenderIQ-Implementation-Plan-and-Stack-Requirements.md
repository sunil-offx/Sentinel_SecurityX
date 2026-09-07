# TenderIQ — Implementation Plan & Technology Stack Requirements

**AI Tender Document Analyzer & Compliance Agent**
Track: Industries & MSME &middot; Difficulty: Medium (⭐⭐)

---

## 1. Purpose of this document

This document turns the TenderIQ project definition into a buildable plan: what gets built in what order, who builds it, and exactly which technologies satisfy each requirement in the original spec. It covers two horizons:

- **Hackathon build (24–36 hrs)** — the demo-able slice, matching the prototype already built.
- **Post-hackathon roadmap** — what a production version needs on top of that.

---

## 2. Scope recap

| Tier | Includes |
|---|---|
| **Must-have** | PDF/DOCX ingestion, eligibility/technical/financial extraction, source page references, company profile, compliance matrix, missing-document detection, grounded Q&A |
| **Advanced** | Risk analysis agent, bid/no-bid recommendation, multi-agent orchestration, report generation, deadline tracking |
| **Optional** | Multi-tender comparison, email notifications, collaboration, historical analytics |

The hackathon build targets **all of Must-have + Advanced** for one tender at a time, with Optional items explicitly deferred (Section 7).

---

## 3. Implementation plan

### Phase 0 — Setup (Hour 0–2)
- Repo scaffold, environment variables, API keys (Anthropic API key, cloud storage bucket if used)
- Agree on the JSON schema for extracted requirements, compliance results, and recommendations (this is the contract between extraction, compliance, and UI — lock it early so frontend and backend can build in parallel)
- Pick one real sample tender PDF (government e-tender portal is a good source) to test against throughout, in addition to the synthetic sample

### Phase 1 — Document ingestion (Hour 2–6)
- File upload endpoint (PDF/DOCX)
- Text + table extraction with page-number preservation
- OCR fallback path for scanned PDFs
- Output: a normalized `{page, text}[]` structure — this is what every downstream agent reads from, so get this right before extraction logic is written

### Phase 2 — Requirement extraction & classification (Hour 6–12)
- Requirement Extraction Agent: chunk the normalized text, prompt the LLM to pull out discrete requirement statements with page attribution
- Eligibility / Technical / Financial sub-classification (single prompt with a strict output schema is sufficient at this scale — three separate agents are a nice-to-have, not a requirement, for a first pass)
- Persist requirements to the database with `source_page`, `category`, `mandatory` flag

### Phase 3 — Company profile + Compliance Agent (Hour 12–18)
- Company profile CRUD (form-based, matches the fields in Section 7 of the spec)
- Compliance Agent: for each requirement, compare against the profile and classify as Compliant / Needs Verification / Non-Compliant, with a one-line grounded reason
- Missing Document Agent: cross-reference the "documents required" list extracted from the tender against what the profile implies is available

### Phase 4 — Risk Agent + Decision Support (Hour 18–24)
- Risk Agent: flag short deadlines, high EMD, strict specs, heavy penalties, ambiguous clauses, each with a plain-language reason
- Decision Support Agent: aggregate compliance %, critical gaps, and risk level into a RECOMMENDED / BORDERLINE / NOT_RECOMMENDED verdict with explicit reasons (never an unexplained score)
- Important-dates extraction feeding a timeline view

### Phase 5 — Q&A (RAG) + Reporting (Hour 24–30)
- Embed the tender text (chunked by section/page) into a vector store
- Q&A Agent: retrieve relevant chunks, answer grounded in retrieved text only, cite page number, and explicitly say "not specified" when the tender is silent
- Report Agent: compose the executive summary, requirement tables, compliance matrix, risk section, and recommendation into a single exportable report (PDF or formatted document)

### Phase 6 — Dashboard, polish, demo prep (Hour 30–36)
- Dashboard: tender list, status, high-risk flags, upcoming deadlines
- Tender detail page wiring all agent outputs together
- Auth (can be minimal — single demo account is acceptable for a hackathon)
- Error states, loading states, and a rehearsed demo script using one strong sample tender

### What was deferred to keep Phase 0–6 achievable
- True multi-tenant auth/roles beyond a basic login
- Multi-tender comparison and historical analytics
- Email notifications and real-time collaboration
- Full three-way agent split (separate Eligibility/Technical/Financial agents) — collapsed into one classification pass for time, with a clear upgrade path noted in Section 6

---

## 4. Team & role breakdown (4–5 person team)

| Role | Owns | Primary phases |
|---|---|---|
| Backend/AI engineer | Extraction, compliance, risk, decision-support prompts and orchestration | 2, 3, 4 |
| Backend engineer | Ingestion pipeline, database, API endpoints, auth | 1, 3, 6 |
| AI/RAG engineer | Embeddings, vector search, Q&A grounding, report generation | 1, 5 |
| Frontend engineer(s) | Upload flow, profile form, dashboard, compliance/risk/report views | 3, 6 |
| PM / demo owner | Schema sign-off, sample tender curation, demo script, judging criteria alignment | 0, 6 |

---

## 5. Technology stack requirements

### 5.1 Frontend
| Requirement (from spec §17) | Recommended choice | Notes |
|---|---|---|
| Modern web dashboard, responsive UI | React (Vite) + Tailwind CSS | Fast to scaffold, matches component-based tab/table UI already prototyped |
| Tender workspace, tables/charts | TanStack Table or plain styled tables; Recharts for any charts | Keep charting minimal — the matrix/status pills carry more signal than charts for this data |
| Search/filter | Client-side filter for hackathon scope; server-side filter/pagination once multiple tenders exist | |

### 5.2 Backend
| Requirement | Recommended choice | Notes |
|---|---|---|
| API layer | Node.js + Express, **or** Python + FastAPI | FastAPI is preferable if the team is already Python-heavy for the AI pieces — keeps extraction/orchestration code and API in one language |
| Authentication | JWT-based auth (Auth0/Clerk for hackathon speed, or hand-rolled JWT if avoiding third-party dependencies) | Role-based access (Applicant / Manager / Admin) can be a simple role field on the user record for v1 |
| Document processing | `pdfplumber` / `PyMuPDF` (text + layout + page numbers), `python-docx` for Word files, Tesseract or a hosted OCR API for scanned PDFs | Preserving page numbers during extraction is what makes every downstream citation possible — do not skip this |
| File storage | Local disk for hackathon demo; S3-compatible bucket (S3, Cloudflare R2, or Supabase Storage) for anything beyond demo day | |

### 5.3 AI / orchestration
| Requirement | Recommended choice | Notes |
|---|---|---|
| LLM | Claude (Anthropic API), model `claude-sonnet-4-6` | Used for extraction, classification, compliance comparison, risk analysis, recommendation synthesis, and Q&A |
| Structured extraction | Prompt-enforced JSON schema (as used in the prototype) | Simpler and more reliable at hackathon scale than a separate structured-output library; validate/parse defensively regardless |
| RAG / embeddings | Any Anthropic-compatible embeddings model, or OpenAI `text-embedding-3-small` if mixing providers is acceptable | Chunk by page/section, not by fixed token windows, so citations stay meaningful |
| Vector search | Chroma or pgvector (Postgres extension) | pgvector is the simpler choice if Postgres is already the primary datastore — avoids running a second database |
| Agent orchestration | Sequential function calls from the backend (extraction → compliance → risk → decision) rather than a heavyweight agent framework | The "multi-agent" architecture in the spec is achievable as a pipeline of scoped LLM calls; frameworks like LangGraph are optional, not required, at this scale |

### 5.4 Database
| Requirement | Recommended choice |
|---|---|
| Primary datastore | PostgreSQL |
| Entities to model | `users`, `companies` (profiles), `tenders`, `documents`, `requirements`, `compliance_results`, `missing_documents`, `risks`, `important_dates`, `recommendations`, `audit_log` |
| Vector data | pgvector extension on the same Postgres instance, or a separate Chroma instance if simpler to stand up quickly |

### 5.5 Security (spec §18)
| Requirement | Implementation approach |
|---|---|
| Authentication | JWT with short-lived access tokens |
| Role-based access | Applicant / Manager / Admin roles gating tender and document visibility |
| User-specific document access | Documents scoped to the uploading user/organization; enforced at the query layer, not just the UI |
| Secure file handling | Validate file type/size on upload; store outside the web root; signed URLs for retrieval |
| Input validation | Schema validation on every API boundary (e.g., Pydantic on FastAPI, Zod on Express) |
| Audit logs | Append-only `audit_log` table recording uploads, analysis runs, and profile edits |
| Secure API keys | Server-side only — the LLM API key must never reach the browser; all AI calls proxy through the backend |
| Session/token management | Refresh-token rotation; revoke on logout |

### 5.6 Deployment (hackathon-appropriate)
| Layer | Choice |
|---|---|
| Frontend hosting | Vercel or Netlify |
| Backend hosting | Render, Railway, or Fly.io |
| Database | Managed Postgres (Supabase, Neon, or Render Postgres) — Supabase also bundles auth and storage if the team wants fewer moving pieces |
| Secrets | Platform-native environment variable management (never committed to the repo) |

---

## 6. Architecture

```
                    Tender PDF / DOCX
                           │
                           ▼
                Document Processing Agent
        (text + tables + page numbers preserved)
                           │
                           ▼
                Requirement Extraction Agent
              (single classification pass:
             eligibility / technical / financial)
                           │
                           ▼
                  Compliance Agent
        (requirement × company profile → status)
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
         Missing Document Agent   Risk Agent
                 │                   │
                 └─────────┬─────────┘
                           ▼
                Decision Support Agent
             (compliance % + gaps + risk
                → RECOMMENDED / BORDERLINE /
                     NOT_RECOMMENDED)
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
          Q&A / RAG Agent        Report Agent
                │                     │
                └──────────┬──────────┘
                           ▼
                    User Dashboard
```

**Upgrade path:** the three sub-categories inside Requirement Extraction can be split into independent Eligibility/Technical/Financial agents post-hackathon if extraction quality on long or unusually structured tenders needs improvement — the schema is already designed to support that split without a rework.

---

## 7. Evaluation checklist (maps to spec §20)

| Criterion | How it's verified in the build |
|---|---|
| Document extraction accuracy | Manual spot-check against 3–5 real tenders of varying format quality (clean PDF, scanned, DOCX) |
| Requirement classification | Sample of 20+ extracted requirements manually labeled and compared against agent output |
| Compliance accuracy | Test with 2–3 company profiles per tender (strong fit, weak fit, borderline) — confirm status changes sensibly |
| Grounded Q&A | Ask 10 questions with known answers in the tender and 3 questions with no answer in the tender; confirm no hallucination on the latter |
| Missing-requirement detection | Deliberately omit a mandatory document from a test profile and confirm it's flagged |
| Recommendation quality | Confirm every recommendation includes explicit reasons, not just a score |
| Usability | A judge or teammate unfamiliar with the tender should be able to explain its key requirements after 2 minutes in the dashboard |

---

## 8. Immediate next steps

1. Lock the requirement/compliance/recommendation JSON schema (blocks Phases 2–6 from starting in parallel)
2. Source 2–3 real tender PDFs (a government e-procurement portal is the fastest source) to replace/supplement the synthetic sample
3. Stand up Postgres + pgvector and the file storage bucket
4. Assign phase owners from Section 4 and start Phase 0/1 in parallel
