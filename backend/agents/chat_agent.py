import re
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from services.ai_service import AIService
from repository.knowledge_repository import KnowledgeRepository

logger = logging.getLogger("chat_agent")

class DRHPChatAgent:
    """
    DRHPChatAgent manages natural language interactions for the DRHP system:
    1. Answers questions about corporate facts.
    2. Modifies and rewrites sections, saving them as new versions in the DB.
    3. Changes section workflow statuses (e.g. approving drafts).
    """

    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.repository = KnowledgeRepository()

    def process_message(self, db: Session, workspace_id: str, user_message: str) -> Dict[str, Any]:
        """
        Processes a user message, queries database state, runs the AI agent,
        parses any action dispatch tags, and commits changes to SQLite.
        """
        # 1. Fetch facts context from DB
        facts = self.repository.get_knowledge_items(db, workspace_id)
        facts_block = []
        for f in facts:
            facts_block.append(f"- [{f.category}] {f.field}: {f.value} (Evidence: \"{f.evidence}\" | Doc: {f.source_document})")
        facts_context = "\n".join(facts_block) if facts_block else "No corporate facts found in database."

        # 2. Fetch latest sections context from DB
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
        sections_block = []
        for slug in section_slugs:
            sec = self.repository.get_latest_section(db, workspace_id, slug)
            if sec:
                sections_block.append(f"--- SECTION SLUG: {slug} (Version: {sec.version}, Status: {sec.status}) ---\n{sec.content}\n")
        sections_context = "\n".join(sections_block) if sections_block else "No drafted sections found in database."

        # 3. Compile Agent Prompt
        prompt = f"""You are an intelligent agentic AI editor and legal drafting assistant for the AI DRHP Operating System.
Your job is to help the user draft, edit, search, and manage a Draft Red Herring Prospectus (DRHP).

You have access to the current workspace database state:
=== EXTRACTED CORPORATE FACTS ===
{facts_context}
=================================

=== LATEST DRAFTED SECTIONS ===
{sections_context}
===============================

USER INSTRUCTION:
"{user_message}"

INSTRUCTIONS FOR YOUR RESPONSE:
1. If the user asks a question about the company, promoters, financials, or IPO structures, answer it directly using the Extracted Corporate Facts. Cites the source document names.
2. If the user asks to edit, revise, or rewrite a specific section:
   - Carefully write the new section text.
   - Wrap the completely updated section markdown in a XML-style tag:
     <REWRITE section_slug="SLUG">
     [Insert completely rewritten section markdown content here]
     </REWRITE>
   - Replace SLUG with the correct uppercase section slug (e.g., COVER_PAGE, RISK_FACTORS, COMPANY_OVERVIEW).
3. If the user wants to approve a section or update its workflow status (e.g. "Approve the cover page" or "Set status of RISK_FACTORS to APPROVED"):
   - Acknowledge the change.
   - Output the status update action tag:
     <STATUS section_slug="SLUG" status="STATUS_VALUE" />
   - Replace SLUG with the uppercase slug, and STATUS_VALUE with DRAFT, REVIEW_PENDING, or APPROVED.
4. For general chats, just respond in clean Markdown.
"""

        system_instruction = (
            "You are a professional investment banking compliance assistant. "
            "Help the user query facts, revise sections using rewrite tags, and change status using status tags."
        )

        # 4. Invoke AI Service
        try:
            ai_response = self.ai_service.generate_text(
                prompt=prompt,
                system_instruction=system_instruction
            )
        except Exception as e:
            logger.error(f"AI Service call failed: {e}")
            raise e

        # 5. Parse and Execute Actions
        actions_taken = []
        clean_response = ai_response

        # Parse <REWRITE section_slug="SLUG">...</REWRITE>
        rewrite_pattern = r"<REWRITE\s+section_slug=\"([^\"]+)\"\s*>(.*?)</REWRITE>"
        rewrites = re.findall(rewrite_pattern, ai_response, re.DOTALL)
        for slug, content in rewrites:
            slug_clean = slug.strip().upper()
            content_clean = content.strip()
            
            # Fetch latest to get title
            latest = self.repository.get_latest_section(db, workspace_id, slug_clean)
            title = latest.title if latest else slug_clean.replace("_", " ").title()
            
            # Save new version to SQLite DB
            new_sec = self.repository.save_section(
                db=db,
                workspace_id=workspace_id,
                section_slug=slug_clean,
                title=title,
                content=content_clean,
                status="DRAFT",
                metadata_json="{'action': 'agent_chat_revision'}"
            )
            actions_taken.append({
                "action": "REWRITE",
                "section_slug": slug_clean,
                "new_version": new_sec.version,
                "status": new_sec.status
            })
            
            # Clean rewrite tag from user-facing text
            clean_response = re.sub(rewrite_pattern, f"\n*(System Action: Created new version {new_sec.version} of {slug_clean} in database)*\n", clean_response, flags=re.DOTALL)

        # Parse <STATUS section_slug="SLUG" status="STATUS_VALUE" />
        status_pattern = r"<STATUS\s+section_slug=\"([^\"]+)\"\s+status=\"([^\"]+)\"\s*/>"
        status_changes = re.findall(status_pattern, ai_response)
        for slug, status in status_changes:
            slug_clean = slug.strip().upper()
            status_clean = status.strip().upper()
            
            # Find latest version to update
            latest = self.repository.get_latest_section(db, workspace_id, slug_clean)
            if latest:
                updated = self.repository.update_section_status(
                    db=db,
                    workspace_id=workspace_id,
                    section_slug=slug_clean,
                    version=latest.version,
                    status=status_clean
                )
                actions_taken.append({
                    "action": "STATUS_UPDATE",
                    "section_slug": slug_clean,
                    "version": latest.version,
                    "new_status": status_clean
                })
            
            # Clean status tag from user-facing text
            clean_response = re.sub(status_pattern, f"\n*(System Action: Updated status of {slug_clean} to {status_clean})*\n", clean_response)

        return {
            "status": "success",
            "agent_response": clean_response.strip(),
            "actions_executed": actions_taken
        }
