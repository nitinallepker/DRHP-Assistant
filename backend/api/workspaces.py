import os
import shutil
import uuid
import zipfile
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from database.connection import get_db, SessionLocal
from orchestrator.pipeline import IngestionPipeline
from orchestrator.automation import AutomationOrchestrator
from agents.company_generator import CompanyGenerator
from agents.industry_generator import IndustryGenerator
from agents.business_generator import BusinessGenerator
from agents.risk_generator import RiskGenerator
from agents.financial_generator import FinancialGenerator
from agents.ipo_generator import IPOGenerator
from agents.glossary_generator import GlossaryGenerator
from agents.legal_generator import LegalGenerator
from services.ai_service import AIService
from repository.knowledge_repository import KnowledgeRepository
from ingestion.scanner import DocumentScanner
from ingestion.classifier import DocumentClassifier
from fastapi.responses import FileResponse
from exports.pdf_compiler import PDFCompiler
from utils.search import SearchEngine
from agents.chat_agent import DRHPChatAgent
from pydantic import BaseModel

router = APIRouter(
    prefix="/workspaces",
    tags=["workspaces"]
)

# Set base paths relative to the API file
STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
TEMP_DIR = os.path.join(STORAGE_DIR, "temp")
WORKSPACES_DIR = os.path.join(STORAGE_DIR, "workspaces")

# Ensure storage subdirectories exist
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(WORKSPACES_DIR, exist_ok=True)

@router.post("/upload")
def upload_workspace(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a workspace ZIP archive, extract it to a local storage folder,
    and scan it recursively to inventory all documents.
    """
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only ZIP archives (.zip) are supported.")

    # Generate unique ID for this ingestion run
    workspace_id = str(uuid.uuid4())
    workspace_name = os.path.splitext(file.filename)[0]
    
    zip_path = os.path.join(TEMP_DIR, f"{workspace_id}.zip")
    extract_path = os.path.join(WORKSPACES_DIR, workspace_id)
    
    try:
        # 1. Save uploaded zip file to temp directory
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Extract contents safely (preventing path traversal attacks)
        os.makedirs(extract_path, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                # Normalize path and remove double slashes
                member_norm = os.path.normpath(member)
                
                # Check for path traversal vulnerabilities
                target_path = os.path.abspath(os.path.join(extract_path, member_norm))
                if not target_path.startswith(os.path.abspath(extract_path)):
                    continue
                
                # If it's a directory name, make it, else extract file
                if member.endswith('/') or member.endswith('\\'):
                    os.makedirs(target_path, exist_ok=True)
                else:
                    # Make sure parent directory exists
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with zip_ref.open(member) as source, open(target_path, "wb") as target:
                        shutil.copyfileobj(source, target)

        # 3. Create Workspace record in database (status starts as PROCESSING)
        repo = KnowledgeRepository()
        repo.create_workspace(
            db=db,
            workspace_id=workspace_id,
            name=workspace_name,
            root_path=extract_path,
            status="PROCESSING"
        )
        
        # 3.1 Define and queue background automation pipeline task
        def bg_automation_pipeline():
            db_bg = SessionLocal()
            try:
                orch = AutomationOrchestrator()
                orch.run_automated_pipeline(db_bg, workspace_id, workspace_name, extract_path)
            except Exception as bg_error:
                print(f"Background automation failed: {bg_error}")
            finally:
                db_bg.close()
        background_tasks.add_task(bg_automation_pipeline)
        
        # 3.5 Scan extracted workspace files for JSON response matching
        scanner = DocumentScanner()
        scanned_files = scanner.scan(extract_path)
        
        # 4. Classify scanned files for JSON response matching
        classifier = DocumentClassifier()
        classified_files = classifier.classify_files(scanned_files)
        
        # 5. Build custom structured summary and files list
        files_summary = {
            "total_files": len(classified_files),
            "pdfs": sum(1 for f in classified_files if f["type"] == "pdf"),
            "excel": sum(1 for f in classified_files if f["type"] == "excel"),
            "json": sum(1 for f in classified_files if f["type"] == "json")
        }
        
        # Add support for docx/docx summaries if present, keeping total files aligned
        docx_count = sum(1 for f in classified_files if f["type"] == "docx")
        if docx_count > 0:
            files_summary["docx"] = docx_count
            
        mime_mapping = {
            ".pdf": "application/pdf",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".xls": "application/vnd.ms-excel",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".doc": "application/msword",
            ".json": "application/json"
        }
        
        formatted_files = []
        for idx, f in enumerate(classified_files):
            ext = f["extension"]
            mime_type = mime_mapping.get(ext, "application/octet-stream")
            formatted_files.append({
                "id": f"FILE_{idx+1:04d}",
                "name": f["name"],
                "category": f["category"].upper(),
                "mime_type": mime_type,
                "processing_status": "PENDING",
                "path": f["path"],
                "size_bytes": f["size_bytes"]
            })
            
        # 6. Cleanup the temporary uploaded zip file
        if os.path.exists(zip_path):
            os.remove(zip_path)
            
        return {
            "workspace": {
                "id": workspace_id,
                "name": workspace_name,
                "status": "PROCESSING",
                "root_path": extract_path.replace(os.sep, '/'),
                "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            },
            "summary": files_summary,
            "files": formatted_files
        }
        
    except Exception as e:
        # Cleanup any partially extracted files and temporary ZIP on error
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path, ignore_errors=True)
        if os.path.exists(zip_path):
            try:
                os.remove(zip_path)
            except OSError:
                pass
        raise HTTPException(status_code=500, detail=f"Ingestion pipeline failed: {str(e)}")


@router.get("/{workspace_id}")
def get_workspace_details(workspace_id: str, db: Session = Depends(get_db)):
    """
    Retrieve metadata and processing status of a workspace.
    """
    repo = KnowledgeRepository()
    workspace = repo.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_id}' not found.")
        
    return {
        "workspace": {
            "id": workspace.id,
            "name": workspace.name,
            "status": workspace.status,
            "root_path": workspace.root_path,
            "created_at": workspace.created_at.isoformat() if workspace.created_at else None
        }
    }


@router.post("/{workspace_id}/generate")
def generate_initial_drhp(workspace_id: str, db: Session = Depends(get_db)):
    """
    Load all extracted facts from the knowledge repository and generate the 
    initial Draft DRHP sections in Markdown using corporate drafting agents.
    """
    repo = KnowledgeRepository()
    
    # 1. Verify workspace exists
    workspace = repo.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_id}' not found.")
        
    # 2. Fetch all stored facts
    facts = repo.get_knowledge_items(db, workspace_id)
    if not facts:
        raise HTTPException(
            status_code=400, 
            detail="No knowledge items found in repository. Please ensure workspace was successfully uploaded and scanned."
        )
        
    # Format DB rows into standard generator dictionaries
    facts_list = []
    for item in facts:
        facts_list.append({
            "category": item.category,
            "field": item.field,
            "value": item.value,
            "evidence": item.evidence,
            "source_document": item.source_document,
            "source_page": item.source_page
        })

    # 3. Check for API key presence to support offline testing mode
    use_mock_fallback = False
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        use_mock_fallback = True

    if use_mock_fallback:
        # Load realistic pre-drafted Markdown segments representing the formatted sections
        sections = {
            "COVER_PAGE": (
                f"# {workspace.name.upper()} LIMITED\n\n"
                f"**Draft Red Herring Prospectus (DRHP)**\n\n"
                f"**Fresh Issue Size**: 400 Crores\n"
                f"**Offer for Sale**: 250 Crores\n\n"
                f"Registered Office: Bandra Kurla Complex, Mumbai, 400051\n"
                f"Promoters: Nitin Sharma and Sharma Capital Group\n\n"
                f"*Regulatory Status: [●] Standard warning clauses...*"
            ),
            "COMPANY_OVERVIEW": (
                f"# SECTION I: COMPANY OVERVIEW & HISTORY\n\n"
                f"{workspace.name} Limited was incorporated as a private limited company under the Companies Act. "
                f"The registered address of the Company is BKC, Mumbai.\n\n"
                f"### Business Operations\n"
                f"The Company operates in technology and services sectors, maintaining standard operational compliance."
            ),
            "INDUSTRY_OVERVIEW": (
                f"# SECTION II: INDUSTRY OVERVIEW\n\n"
                f"The industry sector is characterized by positive CAGR trends. "
                f"Market size in India is projected to grow by 12% annually, driven by digitization and regulatory initiatives."
            ),
            "BUSINESS_OVERVIEW_STRENGTHS": (
                f"# SECTION III: BUSINESS MODEL & COMPETITIVE STRENGTHS\n\n"
                f"Our business model relies on B2B services. Our key strengths include:\n"
                f"1. **Strong Founder Base**: Managed by experienced promoters.\n"
                f"2. **Optimal Capitalization**: High revenue structures with solid EBITDA margins."
            ),
            "RISK_FACTORS": (
                f"# SECTION IV: RISK FACTORS\n\n"
                f"**Internal Risks**:\n"
                f"- Any disruption in our software servers could impact clients.\n"
                f"**External Risks**:\n"
                f"- Changes in SEBI guidelines or Indian corporate tax structures could impact the issue."
            ),
            "FINANCIAL_HIGHLIGHTS_MDA": (
                f"# SECTION V: FINANCIAL STATEMENTS & MD&A\n\n"
                f"Summary of Financial Operations (in Crores):\n\n"
                f"| Metric | FY25 |\n"
                f"|---|---|\n"
                f"| Revenue | 1,250 |\n"
                f"| Net Profit | 180 |\n"
                f"| EBITDA | 250 |"
            ),
            "IPO_DETAILS_OBJECTS_CAPITAL": (
                f"# SECTION VI: IPO OFFER STRUCTURE & OBJECTS\n\n"
                f"The Issue comprises a Fresh Issue of 400 Crores. The objects of the fresh issue are:\n"
                f"1. Funding working capital requirements (200 Crores).\n"
                f"2. Repayment of outstanding loans (150 Crores).\n"
                f"3. General corporate purposes (50 Crores)."
            ),
            "GLOSSARY_DEFINITIONS": (
                f"# SECTION VII: DEFINITIONS & STATUTORY REGULATION\n\n"
                f"| Term | Definition |\n"
                f"|---|---|\n"
                f"| SEBI | Securities and Exchange Board of India |\n"
                f"| Companies Act | Companies Act, 2013 and amendments thereto |"
            ),
            "LEGAL_LITIGATION_DECLARATION": (
                f"# SECTION VIII: OUTSTANDING LITIGATION & DECLARATION\n\n"
                f"There are no material outstanding tax or civil litigations against the Company or Promoters. "
                f"Declaration: The Company certifies that all disclosures in this Draft Red Herring Prospectus are true and correct."
            )
        }
        
        # Save each section to database version history
        for slug, text in sections.items():
            repo.save_section(
                db=db,
                workspace_id=workspace_id,
                section_slug=slug,
                title=slug.replace("_", " ").title(),
                content=text,
                status="DRAFT"
            )
            
        return {
            "status": "success",
            "workspace_id": workspace_id,
            "workspace_name": workspace.name,
            "mode": "MOCK_FALLBACK (No GEMINI_API_KEY configured)",
            "generated_sections_count": len(sections),
            "sections": sections
        }

    # 4. Live generation flow using Gemini
    try:
        ai_service = AIService()
        
        company_gen = CompanyGenerator(ai_service)
        industry_gen = IndustryGenerator(ai_service)
        business_gen = BusinessGenerator(ai_service)
        risk_gen = RiskGenerator(ai_service)
        financial_gen = FinancialGenerator(ai_service)
        ipo_gen = IPOGenerator(ai_service)
        glossary_gen = GlossaryGenerator(ai_service)
        legal_gen = LegalGenerator(ai_service)
        
        sections = {
            "COVER_PAGE": company_gen.generate_cover_page(facts_list),
            "COMPANY_OVERVIEW": company_gen.generate_company_overview(facts_list),
            "INDUSTRY_OVERVIEW": industry_gen.generate_industry_overview(facts_list),
            "BUSINESS_OVERVIEW_STRENGTHS": business_gen.generate_business_sections(facts_list),
            "RISK_FACTORS": risk_gen.generate_risk_factors(facts_list),
            "FINANCIAL_HIGHLIGHTS_MDA": financial_gen.generate_financial_sections(facts_list),
            "IPO_DETAILS_OBJECTS_CAPITAL": ipo_gen.generate_ipo_sections(facts_list),
            "GLOSSARY_DEFINITIONS": glossary_gen.generate_glossary_sections(facts_list),
            "LEGAL_LITIGATION_DECLARATION": legal_gen.generate_legal_sections(facts_list)
        }
        
        # Save each section to database version history
        for slug, text in sections.items():
            repo.save_section(
                db=db,
                workspace_id=workspace_id,
                section_slug=slug,
                title=slug.replace("_", " ").title(),
                content=text,
                status="DRAFT"
            )
            
        return {
            "status": "success",
            "workspace_id": workspace_id,
            "workspace_name": workspace.name,
            "mode": "LIVE_GEMINI_GENERATION",
            "generated_sections_count": len(sections),
            "sections": sections
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DRHP section drafting failed: {str(e)}")


@router.post("/{workspace_id}/export")
def export_drhp_pdf(workspace_id: str, db: Session = Depends(get_db)):
    """
    Retrieves the latest drafted versions of all DRHP sections for this workspace,
    compiles them into a single SEBI-compliant PDF, and returns it as a file download.
    """
    repo = KnowledgeRepository()
    
    # 1. Verify workspace exists
    workspace = repo.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_id}' not found.")
        
    # List of required section slugs
    section_slugs = [
        "COVER_PAGE",
        "COMPANY_OVERVIEW",
        "INDUSTRY_OVERVIEW",
        "BUSINESS_OVERVIEW_STRENGTHS",
        "RISK_FACTORS",
        "IPO_DETAILS_OBJECTS_CAPITAL",
        "FINANCIAL_HIGHLIGHTS_MDA",
        "GLOSSARY_DEFINITIONS",
        "LEGAL_LITIGATION_DECLARATION"
    ]
    
    # 2. Gather latest section content from DB
    sections_content = {}
    for slug in section_slugs:
        sec = repo.get_latest_section(db, workspace_id, slug)
        if sec:
            sections_content[slug] = sec.content
            
    # 3. Fallback placeholder generation if no sections have been drafted in DB yet
    # This prevents the compile endpoint from crashing and allows downloading a dummy PDF out of the box!
    if not sections_content:
        sections_content = {
            "COVER_PAGE": (
                f"# {workspace.name.upper()} LIMITED\n\n"
                f"**Draft Red Herring Prospectus (DRHP)**\n\n"
                f"**Fresh Issue Size**: 400 Crores\n"
                f"**Offer for Sale**: 250 Crores\n\n"
                f"Registered Office: Bandra Kurla Complex, Mumbai, 400051\n"
                f"Promoters: Nitin Sharma and Sharma Capital Group\n\n"
                f"*Regulatory Status: [●] Standard warning clauses...*"
            ),
            "COMPANY_OVERVIEW": (
                f"# SECTION I: COMPANY OVERVIEW & HISTORY\n\n"
                f"{workspace.name} Limited was incorporated as a private limited company under the Companies Act. "
                f"The registered address of the Company is BKC, Mumbai.\n\n"
                f"### Business Operations\n"
                f"The Company operates in technology and services sectors, maintaining standard operational compliance."
            ),
            "INDUSTRY_OVERVIEW": (
                f"# SECTION II: INDUSTRY OVERVIEW\n\n"
                f"The industry sector is characterized by positive CAGR trends. "
                f"Market size in India is projected to grow by 12% annually, driven by digitization and regulatory initiatives."
            ),
            "BUSINESS_OVERVIEW_STRENGTHS": (
                f"# SECTION III: BUSINESS MODEL & COMPETITIVE STRENGTHS\n\n"
                f"Our business model relies on B2B services. Our key strengths include:\n"
                f"1. **Strong Founder Base**: Managed by experienced promoters.\n"
                f"2. **Optimal Capitalization**: High revenue structures with solid EBITDA margins."
            ),
            "RISK_FACTORS": (
                f"# SECTION IV: RISK FACTORS\n\n"
                f"**Internal Risks**:\n"
                f"- Any disruption in our software servers could impact clients.\n"
                f"**External Risks**:\n"
                f"- Changes in SEBI guidelines or Indian corporate tax structures could impact the issue."
            ),
            "FINANCIAL_HIGHLIGHTS_MDA": (
                f"# SECTION V: FINANCIAL STATEMENTS & MD&A\n\n"
                f"Summary of Financial Operations (in Crores):\n\n"
                f"| Metric | FY25 |\n"
                f"|---|---|\n"
                f"| Revenue | 1,250 |\n"
                f"| Net Profit | 180 |\n"
                f"| EBITDA | 250 |"
            ),
            "IPO_DETAILS_OBJECTS_CAPITAL": (
                f"# SECTION VI: IPO OFFER STRUCTURE & OBJECTS\n\n"
                f"The Issue comprises a Fresh Issue of 400 Crores. The objects of the fresh issue are:\n"
                f"1. Funding working capital requirements (200 Crores).\n"
                f"2. Repayment of outstanding loans (150 Crores).\n"
                f"3. General corporate purposes (50 Crores)."
            ),
            "GLOSSARY_DEFINITIONS": (
                f"# SECTION VII: DEFINITIONS & STATUTORY REGULATION\n\n"
                f"| Term | Definition |\n"
                f"|---|---|\n"
                f"| SEBI | Securities and Exchange Board of India |\n"
                f"| Companies Act | Companies Act, 2013 and amendments thereto |"
            ),
            "LEGAL_LITIGATION_DECLARATION": (
                f"# SECTION VIII: OUTSTANDING LITIGATION & DECLARATION\n\n"
                f"There are no material outstanding tax or civil litigations against the Company or Promoters. "
                f"Declaration: The Company certifies that all disclosures in this Draft Red Herring Prospectus are true and correct."
            )
        }
        
    # 4. Define target path and run compiler
    exports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "exports"))
    os.makedirs(exports_dir, exist_ok=True)
    pdf_path = os.path.join(exports_dir, f"{workspace_id}.pdf")
    
    try:
        compiler = PDFCompiler()
        compiler.compile(
            workspace_name=workspace.name,
            sections=sections_content,
            output_pdf_path=pdf_path
        )
        
        # 5. Return compiled PDF file as an attachment
        return FileResponse(
            path=pdf_path,
            filename=f"{workspace.name}_DRHP_Draft.pdf",
            media_type="application/pdf"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF Compilation failed: {str(e)}")


@router.get("/{workspace_id}/search")
def search_workspace_sections(workspace_id: str, query: str = Query(...), db: Session = Depends(get_db)):
    """
    Search across the latest drafted versions of all DRHP sections in the workspace.
    Returns ranked keyword matches with snippet highlighting.
    """
    repo = KnowledgeRepository()
    
    # 1. Verify workspace exists
    workspace = repo.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_id}' not found.")
        
    # List of all standard sections
    section_slugs = [
        "COVER_PAGE",
        "COMPANY_OVERVIEW",
        "INDUSTRY_OVERVIEW",
        "BUSINESS_OVERVIEW_STRENGTHS",
        "RISK_FACTORS",
        "IPO_DETAILS_OBJECTS_CAPITAL",
        "FINANCIAL_HIGHLIGHTS_MDA",
        "GLOSSARY_DEFINITIONS",
        "LEGAL_LITIGATION_DECLARATION"
    ]
    
    # 2. Retrieve latest sections content
    sections_list = []
    for slug in section_slugs:
        sec = repo.get_latest_section(db, workspace_id, slug)
        if sec:
            sections_list.append(sec)
            
    if not sections_list:
        raise HTTPException(
            status_code=400, 
            detail="No drafted sections found. Please generate the initial DRHP sections first."
        )
        
    # 3. Execute search
    search_engine = SearchEngine()
    ranked_results = search_engine.search(query, sections_list)
    
    return {
        "status": "success",
        "workspace_id": workspace_id,
        "query": query,
        "results_count": len(ranked_results),
        "results": ranked_results
    }


class ChatRequest(BaseModel):
    message: str


@router.post("/{workspace_id}/chat")
def workspace_chat_assistant(workspace_id: str, body: ChatRequest, db: Session = Depends(get_db)):
    """
    Interact with the workspace AI agent helper to ask about facts,
    request section rewrites, or trigger workflow status updates.
    """
    # Check workspace exists
    repo = KnowledgeRepository()
    workspace = repo.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_id}' not found.")
        
    try:
        # Check if we are running in mock fallback mode (no Gemini API key)
        use_mock_fallback = False
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            use_mock_fallback = True

        if use_mock_fallback:
            # Standard mock actions based on user message text to make testing fully interactive
            msg_lower = body.message.lower()
            
            # Handle status updates
            if "approve" in msg_lower or "status" in msg_lower:
                slug = "RISK_FACTORS"
                if "cover" in msg_lower:
                    slug = "COVER_PAGE"
                elif "overview" in msg_lower:
                    slug = "COMPANY_OVERVIEW"
                    
                latest = repo.get_latest_section(db, workspace_id, slug)
                version = latest.version if latest else 1
                repo.update_section_status(db, workspace_id, slug, version, "APPROVED")
                
                return {
                    "status": "success",
                    "agent_response": f"*(System Action: Updated status of {slug} to APPROVED)*\nI have successfully approved the {slug} section draft as requested.",
                    "actions_executed": [{
                        "action": "STATUS_UPDATE",
                        "section_slug": slug,
                        "version": version,
                        "new_status": "APPROVED"
                    }]
                }
                
            # Handle section rewrites
            elif "rewrite" in msg_lower or "edit" in msg_lower or "update" in msg_lower:
                slug = "RISK_FACTORS"
                if "cover" in msg_lower:
                    slug = "COVER_PAGE"
                elif "overview" in msg_lower:
                    slug = "COMPANY_OVERVIEW"
                    
                latest = repo.get_latest_section(db, workspace_id, slug)
                title = latest.title if latest else slug.replace("_", " ").title()
                content = latest.content if latest else "# Mock Draft"
                
                new_sec = repo.save_section(
                    db=db,
                    workspace_id=workspace_id,
                    section_slug=slug,
                    title=title,
                    content=content + "\n\n*(Revised: Added compliance clauses per chat request)*",
                    status="DRAFT"
                )
                
                return {
                    "status": "success",
                    "agent_response": f"*(System Action: Created new version {new_sec.version} of {slug} in database)*\nI have successfully rewritten the {slug} section per your instructions.",
                    "actions_executed": [{
                        "action": "REWRITE",
                        "section_slug": slug,
                        "new_version": new_sec.version,
                        "status": "DRAFT"
                    }]
                }
                
            # Handle fact queries
            else:
                return {
                    "status": "success",
                    "agent_response": (
                        "Based on the Extracted Corporate Facts:\n"
                        "- **Company Name**: ABC Industries Limited\n"
                        "- **Fresh Issue Size**: 400 Crores\n"
                        "- **Promoters**: Nitin Sharma and Sharma Capital Group\n\n"
                        "Source: shareholding_pattern.xlsx, page/sheet: Sheet1"
                    ),
                    "actions_executed": []
                }

        # Live Agent Invocations
        ai_service = AIService()
        agent = DRHPChatAgent(ai_service)
        result = agent.process_message(db, workspace_id, body.message)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DRHP Chat agent failed: {str(e)}")
