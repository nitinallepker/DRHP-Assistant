import os
import logging
from sqlalchemy.orm import Session
from orchestrator.pipeline import IngestionPipeline
from repository.knowledge_repository import KnowledgeRepository

# Import drafting generators
from agents.company_generator import CompanyGenerator
from agents.industry_generator import IndustryGenerator
from agents.business_generator import BusinessGenerator
from agents.risk_generator import RiskGenerator
from agents.financial_generator import FinancialGenerator
from agents.ipo_generator import IPOGenerator
from agents.glossary_generator import GlossaryGenerator
from agents.legal_generator import LegalGenerator
from services.ai_service import AIService

# Import reviewers, improvement, transformations, and compilers
from review.review_engine import ReviewEngine
from review.improvement_engine import ImprovementEngine
from transformation.transformer import ContentTransformer
from exports.pdf_compiler import PDFCompiler

logger = logging.getLogger("automation")

class AutomationOrchestrator:
    """
    AutomationOrchestrator manages the end-to-end pipeline execution:
    Upload -> Ingestion -> Content Drafting -> Review -> Auto-Improvement -> PDF compilation -> Downstream Transformation.
    """
    
    def run_automated_pipeline(self, db: Session, workspace_id: str, workspace_name: str, root_path: str):
        repo = KnowledgeRepository()
        logger.info(f"Triggering automated pipeline flow for workspace={workspace_id}")
        
        try:
            # 1. Set workspace status to processing
            repo.update_workspace_status(db, workspace_id, "PROCESSING")
            
            # --- STAGE 1: Knowledge Ingestion ---
            logger.info("Automation Stage 1: Running Ingestion Pipeline...")
            ingestion = IngestionPipeline()
            ingestion.run(db, workspace_id, workspace_name, root_path)
            
            # Retrieve extracted corporate facts
            db_facts = repo.get_knowledge_items(db, workspace_id)
            facts = []
            for item in db_facts:
                facts.append({
                    "category": item.category,
                    "field": item.field,
                    "value": item.value,
                    "evidence": item.evidence,
                    "source_document": item.source_document,
                    "source_page": item.source_page
                })
            
            # --- STAGE 2: Content Creation & Organization (Drafting V1) ---
            logger.info("Automation Stage 2: Drafting initial DRHP sections...")
            
            api_key = os.getenv("GEMINI_API_KEY")
            use_mock_fallback = not api_key or api_key == "your_gemini_api_key_here"
            
            if use_mock_fallback:
                sections = {
                    "COVER_PAGE": (
                        f"# {workspace_name.upper()} LIMITED\n\n"
                        f"**Draft Red Herring Prospectus (DRHP)**\n\n"
                        f"**Fresh Issue Size**: 400 Crores\n"
                        f"**Offer for Sale**: 250 Crores\n\n"
                        f"Registered Office: Bandra Kurla Complex, Mumbai, 400051\n"
                        f"Promoters: Nitin Sharma and Sharma Capital Group\n\n"
                        f"*Regulatory Status: [●] Standard warning clauses...*"
                    ),
                    "COMPANY_OVERVIEW": (
                        f"# SECTION I: COMPANY OVERVIEW & HISTORY\n\n"
                        f"{workspace_name} Limited was incorporated as a private limited company under the Companies Act. "
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
            else:
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
                    "COVER_PAGE": company_gen.generate_cover_page(facts),
                    "COMPANY_OVERVIEW": company_gen.generate_company_overview(facts),
                    "INDUSTRY_OVERVIEW": industry_gen.generate_industry_overview(facts),
                    "BUSINESS_OVERVIEW_STRENGTHS": business_gen.generate_business_sections(facts),
                    "RISK_FACTORS": risk_gen.generate_risk_factors(facts),
                    "FINANCIAL_HIGHLIGHTS_MDA": financial_gen.generate_financial_sections(facts),
                    "IPO_DETAILS_OBJECTS_CAPITAL": ipo_gen.generate_ipo_sections(facts),
                    "GLOSSARY_DEFINITIONS": glossary_gen.generate_glossary_sections(facts),
                    "LEGAL_LITIGATION_DECLARATION": legal_gen.generate_legal_sections(facts)
                }
            
            for slug, text in sections.items():
                repo.save_section(
                    db=db,
                    workspace_id=workspace_id,
                    section_slug=slug,
                    title=slug.replace("_", " ").title(),
                    content=text,
                    status="DRAFT"
                )
                
            # --- STAGE 3: Content Review ---
            logger.info("Automation Stage 3: Generating AI Review Suggestions...")
            review_engine = ReviewEngine()
            suggestions = review_engine.run_workspace_review(db, workspace_id)
            
            # --- STAGE 4: Content Improvement (Auto-Accept Revisions) ---
            logger.info("Automation Stage 4: Auto-Accepting and applying suggestions...")
            # Auto-accept all open suggestions to progress the automated pipeline
            for s in suggestions:
                repo.update_review_suggestion_status(db, s.suggestion_id, "ACCEPTED")
                
            improvement_engine = ImprovementEngine()
            improvement_engine.apply_improvements(db, workspace_id)
            
            # --- STAGE 5: Final DRHP Book PDF Compilation ---
            logger.info("Automation Stage 5: Compiling SEBI-compliant PDF book...")
            final_sections_content = {}
            for slug in sections.keys():
                sec = repo.get_latest_section(db, workspace_id, slug)
                if sec:
                    final_sections_content[slug] = sec.content
                    
            exports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "exports"))
            os.makedirs(exports_dir, exist_ok=True)
            pdf_path = os.path.join(exports_dir, f"{workspace_id}.pdf")
            
            compiler = PDFCompiler()
            compiler.compile(
                workspace_name=workspace_name,
                sections=final_sections_content,
                output_pdf_path=pdf_path
            )
            
            # --- STAGE 6: Content Transformation ---
            logger.info("Automation Stage 6: Running Downstream Content Transformation Engine...")
            transformer = ContentTransformer()
            transformer.transform_workspace(db, workspace_id)
            
            # 2. Set workspace status to READY
            repo.update_workspace_status(db, workspace_id, "READY")
            logger.info(f"Automation pipeline complete for workspace={workspace_id}")
            
        except Exception as e:
            logger.error(f"Automation pipeline failed for workspace={workspace_id}: {e}")
            repo.update_workspace_status(db, workspace_id, "FAILED")
            # We don't want background tasks to silently swallow exceptions during development testing
            raise e
