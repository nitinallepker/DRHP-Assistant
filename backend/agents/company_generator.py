import os
from typing import List, Dict, Any
from services.ai_service import AIService

class CompanyGenerator:
    """
    CompanyGenerator manages drafting the first two key DRHP document sections:
    1. The DRHP Cover Page
    2. The Company Overview (Corporate History & Core Operations)
    """

    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.prompts_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "prompts")
        )

    def _load_template(self, filename: str) -> str:
        """
        Helper method to read prompt template contents.
        """
        path = os.path.join(self.prompts_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Prompt template file not found at '{path}'")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _format_facts_block(self, facts: List[Dict[str, Any]]) -> str:
        """
        Formats list of knowledge facts into a readable block for the LLM.
        """
        if not facts:
            return "No company facts available in the repository."
            
        formatted = []
        for fact in facts:
            source_info = ""
            if fact.get("source_document"):
                source_info = f" (Source: {fact.get('source_document')}, Page/Sheet: {fact.get('source_page')})"
                
            formatted.append(
                f"- Category: {fact.get('category')}\n"
                f"  Fact: {fact.get('field')}\n"
                f"  Value: {fact.get('value')}\n"
                f"  Evidence: \"{fact.get('evidence')}\"{source_info}"
            )
        return "\n".join(formatted)

    def generate_cover_page(self, facts: List[Dict[str, Any]]) -> str:
        """
        Generates the Cover Page section content.
        """
        template = self._load_template("cover_page_prompt.txt")
        facts_block = self._format_facts_block(facts)
        prompt = template.format(facts=facts_block)
        
        system_instruction = (
            "You are an expert SEBI compliance attorney. Generate a professional and legal DRHP "
            "Cover Page following standard formatting rules. Be concise and precise."
        )
        return self.ai_service.generate_text(
            prompt=prompt,
            system_instruction=system_instruction
        )

    def generate_company_overview(self, facts: List[Dict[str, Any]]) -> str:
        """
        Generates the Company Overview section content.
        """
        template = self._load_template("company_overview_prompt.txt")
        facts_block = self._format_facts_block(facts)
        prompt = template.format(facts=facts_block)
        
        system_instruction = (
            "You are a professional financial editor and legal writer. Generate a comprehensive "
            "Company Overview and Corporate History section. Keep it objective and facts-based."
        )
        return self.ai_service.generate_text(
            prompt=prompt,
            system_instruction=system_instruction
        )
