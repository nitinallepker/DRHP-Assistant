import logging
from sqlalchemy.orm import Session
from services.ai_service import AIService
from repository.knowledge_repository import KnowledgeRepository
from review.reviewers import REVIEWER_REGISTRY

logger = logging.getLogger("review_engine")

class ReviewEngine:
    """
    ReviewEngine orchestrates the content auditing pipeline:
    1. Selects active reviewers registered in REVIEWER_REGISTRY.
    2. Packages reviewer-specific Knowledge Packs from extracted facts.
    3. Runs reviewer checks on eligible section drafts.
    4. Commits structured Suggestions to the SQLite Suggestion repository.
    """
    
    def __init__(self):
        self.repository = KnowledgeRepository()
        self.ai_service = AIService()

        # Define section slug relevancy rules for independent reviewers
        self.reviewer_relevance = {
            "LEGAL": ["LEGAL_LITIGATION_DECLARATION", "COMPANY_OVERVIEW", "GLOSSARY_DEFINITIONS"],
            "FINANCE": ["FINANCIAL_HIGHLIGHTS_MDA", "IPO_DETAILS_OBJECTS_CAPITAL"],
            "BUSINESS": ["COMPANY_OVERVIEW", "BUSINESS_OVERVIEW_STRENGTHS", "INDUSTRY_OVERVIEW"],
            "RISK": ["RISK_FACTORS"],
            "COMPLIANCE": ["GLOSSARY_DEFINITIONS", "COVER_PAGE", "LEGAL_LITIGATION_DECLARATION"],
            "LANGUAGE": [
                "COVER_PAGE", "COMPANY_OVERVIEW", "INDUSTRY_OVERVIEW", 
                "BUSINESS_OVERVIEW_STRENGTHS", "RISK_FACTORS", 
                "IPO_DETAILS_OBJECTS_CAPITAL", "FINANCIAL_HIGHLIGHTS_MDA", 
                "GLOSSARY_DEFINITIONS", "LEGAL_LITIGATION_DECLARATION"
            ]
            # CONSISTENCY is treated as a cross-section auditor, run once on all merged text
        }

    def _build_knowledge_pack(self, facts: list, reviewer_name: str) -> list:
        """
        Builds reviewer-specific Knowledge Packs by filtering facts category maps.
        """
        name = reviewer_name.upper()
        
        if name == "LEGAL":
            return [f for f in facts if f.category in ["LITIGATION", "GOVERNMENT_APPROVAL", "LEGAL_DOCUMENT"]]
        elif name == "FINANCE":
            return [f for f in facts if f.category in ["FINANCIAL_STATEMENTS", "IPO_DETAILS", "SHAREHOLDING"]]
        elif name == "BUSINESS":
            return [f for f in facts if f.category in ["COMPANY_PROFILE", "IPO_DETAILS", "SHAREHOLDING"]]
        elif name == "RISK":
            return [f for f in facts if f.category in ["LITIGATION", "IPO_DETAILS", "FINANCIAL_STATEMENTS"]]
        elif name == "COMPLIANCE":
            return [f for f in facts if f.category in ["IPO_DETAILS", "AUDITOR_REPORT", "LEGAL_DOCUMENT"]]
        elif name == "CONSISTENCY":
            return [f for f in facts if f.category in ["IPO_DETAILS", "FINANCIAL_STATEMENTS", "SHAREHOLDING"]]
            
        # Default fallback or LANGUAGE reviewer (gets all facts)
        return facts

    def run_workspace_review(self, db: Session, workspace_id: str) -> list:
        """
        Runs the full audit pipeline for the given workspace, executing
        independent reviewer agents on eligible drafts, and storing results in SQLite.
        """
        logger.info(f"Running review engine audit for workspace={workspace_id}")
        
        # 1. Gather all latest drafted versions of sections in DB
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
        
        active_sections = []
        for slug in section_slugs:
            sec = self.repository.get_latest_section(db, workspace_id, slug)
            if sec:
                active_sections.append(sec)
                
        if not active_sections:
            logger.warning(f"No drafted sections found to review for workspace={workspace_id}")
            return []
            
        # 2. Gather all extracted facts
        facts = self.repository.get_knowledge_items(db, workspace_id)
        
        suggestions_saved = []

        # 3. Iterate through reviewers from registered registry (extensible architecture)
        for name, reviewer_cls in REVIEWER_REGISTRY.items():
            reviewer_instance = reviewer_cls(self.ai_service)
            knowledge_pack = self._build_knowledge_pack(facts, name)

            # Special Case: Consistency Reviewer (cross-section audit)
            if name == "CONSISTENCY":
                # Combine all section content as context
                combined_content = "\n\n".join(
                    [f"=== SECTION: {s.section_slug} (v{s.version}) ===\n{s.content}" for s in active_sections]
                )
                
                # Execute Consistency reviewer once
                results = reviewer_instance.review(
                    section_slug="ALL_SECTIONS",
                    version=1,
                    content=combined_content,
                    facts=knowledge_pack
                )
                
                # Store suggestions (Consistency defaults to Cover Page or mapped target if possible)
                for res in results:
                    s = self.repository.add_review_suggestion(
                        db=db,
                        workspace_id=workspace_id,
                        section_slug="COVER_PAGE",  # Anchor consistency to cover page as standard
                        section_version=1,
                        reviewer=name,
                        severity=res.get("severity", "HIGH"),
                        confidence=float(res.get("confidence", 0.9)),
                        reason=res.get("reason", "Inconsistency discrepancy found."),
                        evidence=res.get("evidence", "Cross-section comparison."),
                        recommendation=res.get("recommendation", "Align numbers.")
                    )
                    suggestions_saved.append(s)
                continue

            # Standard Case: Legal, Finance, Business, Risk, Compliance, Language Reviewers
            relevant_slugs = self.reviewer_relevance.get(name, section_slugs)
            
            for sec in active_sections:
                if sec.section_slug not in relevant_slugs:
                    continue  # Skip sections not relevant to this reviewer
                    
                # Run independent reviewer
                results = reviewer_instance.review(
                    section_slug=sec.section_slug,
                    version=sec.version,
                    content=sec.content,
                    facts=knowledge_pack
                )
                
                # Save each suggestion returned to SQLite
                for res in results:
                    s = self.repository.add_review_suggestion(
                        db=db,
                        workspace_id=workspace_id,
                        section_slug=sec.section_slug,
                        section_version=sec.version,
                        reviewer=name,
                        severity=res.get("severity", "MEDIUM"),
                        confidence=float(res.get("confidence", 0.8)),
                        reason=res.get("reason", "Review suggestion flagged."),
                        evidence=res.get("evidence", "Filing detail check."),
                        recommendation=res.get("recommendation", "Update draft text.")
                    )
                    suggestions_saved.append(s)

        logger.info(f"Review engine execution complete. Generated {len(suggestions_saved)} suggestions.")
        return suggestions_saved
