import os
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from services.ai_service import AIService
from repository.knowledge_repository import KnowledgeRepository
from database.models import ReviewSuggestion

logger = logging.getLogger("improvement_engine")

class ImprovementEngine:
    """
    ImprovementEngine processes accepted reviewer suggestions:
    1. Detects conflicting suggestions in the workspace (e.g. Legal redacting vs Finance auditing).
    2. Rewrites target draft sections incorporating accepted recommendations.
    3. Saves the modifications as new version drafts in SQLite.
    """
    
    def __init__(self):
        self.repository = KnowledgeRepository()
        self.ai_service = AIService()

    def detect_conflicts(self, suggestions: List[ReviewSuggestion]) -> List[Dict[str, Any]]:
        """
        Scans suggestions to detect conflicting recommendations.
        Heuristic: Flags suggestions targeting the same section slug from different reviewers
        that mention overlapping core context keywords (e.g. Noida, revenue, issue size).
        """
        conflicts = []
        conflict_counter = 1
        
        # Group suggestions by section
        by_section = {}
        for s in suggestions:
            by_section.setdefault(s.section_slug, []).append(s)
            
        keywords_to_check = ["noida", "revenue", "issue size", "promoter", "downtime"]
        
        for slug, sug_list in by_section.items():
            # Check pairs
            for i in range(len(sug_list)):
                for j in range(i + 1, len(sug_list)):
                    s1 = sug_list[i]
                    s2 = sug_list[j]
                    
                    # Only compare different reviewers
                    if s1.reviewer == s2.reviewer:
                        continue
                        
                    # Check for keyword overlap in reasons or recommendations
                    text1 = (s1.reason + " " + s1.recommendation).lower()
                    text2 = (s2.reason + " " + s2.recommendation).lower()
                    
                    for kw in keywords_to_check:
                        if kw in text1 and kw in text2:
                            # We found a potential conflict!
                            conflicts.append({
                                "conflict_id": f"CF-{conflict_counter:03d}",
                                "section_slug": slug,
                                "keyword": kw.upper(),
                                "suggestions": [
                                    {
                                        "suggestion_id": s1.suggestion_id,
                                        "reviewer": s1.reviewer,
                                        "severity": s1.severity,
                                        "recommendation": s1.recommendation
                                    },
                                    {
                                        "suggestion_id": s2.suggestion_id,
                                        "reviewer": s2.reviewer,
                                        "severity": s2.severity,
                                        "recommendation": s2.recommendation
                                    }
                                ],
                                "description": f"Potential drafting conflict detected on keyword '{kw.upper()}' between {s1.reviewer} and {s2.reviewer} reviewers."
                            })
                            conflict_counter += 1
                            break
                            
        return conflicts

    def apply_improvements(self, db: Session, workspace_id: str) -> List[Dict[str, Any]]:
        """
        Gathers all accepted suggestions for the workspace, groups them by section,
        rewrites the draft text to incorporate revisions, and saves them as new SQLite versions.
        """
        # Fetch accepted suggestions
        accepted_sugs = self.repository.get_review_suggestions(
            db=db,
            workspace_id=workspace_id,
            status="ACCEPTED"
        )
        
        if not accepted_sugs:
            logger.info(f"No accepted suggestions found to apply for workspace={workspace_id}")
            return []
            
        # Group by section slug
        grouped_sugs = {}
        for s in accepted_sugs:
            grouped_sugs.setdefault(s.section_slug, []).append(s)
            
        results = []
        api_key = os.getenv("GEMINI_API_KEY")
        use_mock = not api_key or api_key == "your_gemini_api_key_here"
        
        for slug, sugs in grouped_sugs.items():
            # Get latest section draft
            latest_sec = self.repository.get_latest_section(db, workspace_id, slug)
            if not latest_sec:
                logger.warning(f"Target section '{slug}' not found for improvement.")
                continue
                
            recs_lines = []
            for s in sugs:
                recs_lines.append(f"- [{s.reviewer}] (Confidence: {s.confidence}): {s.recommendation}")
            recommendations_text = "\n".join(recs_lines)
            
            # 1. Generate improved content
            improved_content = ""
            if use_mock:
                # Mock rewriting fallback: append applied revisions summary cleanly
                reviewers = ", ".join(list(set([s.reviewer for s in sugs])))
                improved_content = (
                    f"{latest_sec.content}\n\n"
                    f"*(AI Improvement Version - Applied recommendations from {reviewers} reviewers:)*\n"
                    f"{recommendations_text}"
                )
            else:
                prompt = f"""You are a professional investment banking compliance editor.
Rewrite the following section content to incorporate these accepted reviewer recommendations.
Do not make any other changes to the text. Ensure tone remains formal and SEBI-compliant.

=== ORIGINAL CONTENT ===
{latest_sec.content}
========================

=== ACCEPTED RECOMMENDATIONS ===
{recommendations_text}
================================
"""
                system_instruction = "You are a professional corporate editor. Rewrite content based on the provided list of recommendations."
                
                try:
                    improved_content = self.ai_service.generate_text(
                        prompt=prompt,
                        system_instruction=system_instruction
                    )
                except Exception as e:
                    logger.error(f"Live improvement generation failed for {slug}: {e}")
                    # Fallback to mock behavior on error
                    reviewers = ", ".join(list(set([s.reviewer for s in sugs])))
                    improved_content = (
                        f"{latest_sec.content}\n\n"
                        f"*(AI Improvement Version - Applied recommendations from {reviewers} reviewers:)*\n"
                        f"{recommendations_text}"
                    )
            
            # 2. Save improved text as new draft version in database
            suggestion_ids = [s.suggestion_id for s in sugs]
            new_sec = self.repository.save_section(
                db=db,
                workspace_id=workspace_id,
                section_slug=slug,
                title=latest_sec.title,
                content=improved_content.strip(),
                status="DRAFT",
                metadata_json=f"{{'action': 'apply_improvements', 'applied_suggestions': {suggestion_ids}}}"
            )
            
            # 3. Update applied suggestion status to a finished marker (e.g. keep status as ACCEPTED but record application)
            # Standard workflow leaves them as ACCEPTED to show they were approved, but they are now integrated.
            
            results.append({
                "section_slug": slug,
                "previous_version": latest_sec.version,
                "new_version": new_sec.version,
                "applied_suggestions_count": len(sugs)
            })
            
        logger.info(f"Applied improvements to {len(results)} sections successfully.")
        return results
