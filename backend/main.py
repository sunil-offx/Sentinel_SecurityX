import os
import uvicorn
from typing import Dict, List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse

from schemas.models import (
    SyntheticBidSubmission, Requirement, ComplianceItem, RiskItem,
    BidReadinessBreakdown, TenderAnalysis, QnARequest, QnAResponse
)
from services.document_parser import DocumentParser
from agents.pipeline import TenderIQPipeline
from sample_data import (
    SYNTHETIC_BID_APEX, SYNTHETIC_BID_NOVATECH, SYNTHETIC_BID_INELIGIBLE,
    SYNTHETIC_BIDS, generate_elcot_analysis, ELCOT_TENDER_PAGES
)

app = FastAPI(
    title="TenderIQ API — AI Tender Document Analyzer & Compliance Agent",
    description="Multi-agent compliance evaluation, technical verification (TVC) validation, risk analysis, and bid readiness scoring for real tenders like ELCOT.",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = TenderIQPipeline()

# In-memory storage for active session
active_tenders: Dict[str, TenderAnalysis] = {}
custom_bids: Dict[str, SyntheticBidSubmission] = dict(SYNTHETIC_BIDS)

# Initialize Real ELCOT 152-Page Tender with Apex Bid
active_tenders["tender_elcot_servers"] = generate_elcot_analysis(SYNTHETIC_BID_APEX)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "TenderIQ Engine v2.0 (ELCOT Specialized)", "version": "2.0.0"}

@app.get("/api/bids")
def get_synthetic_bids():
    return {
        "bids": list(custom_bids.values()),
        "default_bid_id": "bid_apex_compliant"
    }

@app.post("/api/bids")
def save_synthetic_bid(bid: SyntheticBidSubmission):
    custom_bids[bid.bidder_name] = bid
    return {"status": "success", "bid": bid}

@app.get("/api/tenders")
def list_tenders():
    summaries = []
    for tid, analysis in active_tenders.items():
        summaries.append({
            "id": tid,
            "title": analysis.metadata.title,
            "reference_number": analysis.metadata.reference_number,
            "issuing_authority": analysis.metadata.issuing_authority,
            "estimated_value": analysis.metadata.estimated_value,
            "submission_deadline": analysis.metadata.submission_deadline,
            "pages_count": analysis.metadata.pages_count,
            "verdict": analysis.readiness.verdict,
            "overall_readiness": analysis.readiness.overall_readiness
        })
    return {"tenders": summaries}

@app.get("/api/tenders/{tender_id}", response_model=TenderAnalysis)
def get_tender(tender_id: str, bid_id: Optional[str] = Query(None)):
    bid = custom_bids.get(bid_id, SYNTHETIC_BID_APEX)
    
    if tender_id == "tender_elcot_servers":
        analysis = generate_elcot_analysis(bid)
        active_tenders[tender_id] = analysis
        return analysis
        
    if tender_id in active_tenders:
        base = active_tenders[tender_id]
        if bid_id:
            re_evaluated = pipeline.analyze_tender_and_bid(
                tender_pages=base.extracted_text_by_page,
                tender_filename=base.metadata.title,
                submitted_bid=bid
            )
            re_evaluated.metadata = base.metadata
            active_tenders[tender_id] = re_evaluated
            return re_evaluated
        return base
        
    # Return default ELCOT
    analysis = generate_elcot_analysis(bid)
    active_tenders[tender_id] = analysis
    return analysis

@app.post("/api/tenders/upload", response_model=TenderAnalysis)
async def upload_tender(
    file: UploadFile = File(...),
    bid_id: Optional[str] = Form("bid_apex_compliant")
):
    try:
        content = await file.read()
        filename = file.filename or "uploaded_tender.pdf"
        
        if filename.lower().endswith(".docx"):
            pages_dict, total_pages = DocumentParser.parse_docx(content)
        else:
            pages_dict, total_pages = DocumentParser.parse_pdf(content)
            
        bid = custom_bids.get(bid_id, SYNTHETIC_BID_APEX)
        analysis = pipeline.analyze_tender_and_bid(pages_dict, filename, bid)
        
        tender_id = f"doc_{abs(hash(filename)) % 100000}"
        analysis.metadata.id = tender_id
        active_tenders[tender_id] = analysis
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@app.post("/api/tenders/{tender_id}/evaluate", response_model=TenderAnalysis)
def re_evaluate_tender(tender_id: str, bid: SyntheticBidSubmission):
    custom_bids[bid.bidder_name] = bid
    
    if tender_id == "tender_elcot_servers":
        analysis = generate_elcot_analysis(bid)
        active_tenders[tender_id] = analysis
        return analysis
        
    if tender_id in active_tenders:
        base = active_tenders[tender_id]
        analysis = pipeline.analyze_tender_and_bid(
            tender_pages=base.extracted_text_by_page,
            tender_filename=base.metadata.title,
            submitted_bid=bid
        )
        analysis.metadata = base.metadata
        active_tenders[tender_id] = analysis
        return analysis
        
    raise HTTPException(status_code=404, detail="Tender not found")

@app.post("/api/tenders/qna", response_model=QnAResponse)
def ask_question(request: QnARequest):
    tender = active_tenders.get(request.tender_id)
    pages = tender.extracted_text_by_page if tender else None
    return pipeline.answer_question(request.tender_id, request.question, pages)

# Mount frontend build if available for seamless single-port serving
frontend_dist_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist_path, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        file_path = os.path.join(frontend_dist_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist_path, "index.html"))

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
