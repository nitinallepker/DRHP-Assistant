import os
from typing import List, Dict, Any
from services.ai_service import AIService

class LegalGenerator:
    """
    LegalGenerator drafts the Board of Directors, Promoters & Management, Outstanding Litigation,
    Material Contracts, and Declaration sections of the DRHP.
    """

    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.prompts_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "prompts")
        )

    def _load_template(self) -> str:
        path = os.path.join(self.prompts_dir, "legal_prompt.txt")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _format_facts(self, facts: List[Dict[str, Any]]) -> str:
        if not facts:
            return "No legal facts available."
        formatted = []
        for fact in facts:
            formatted.append(f"- Category: {fact.get('category')}\n  Fact: {fact.get('field')}\n  Value: {fact.get('value')}\n  Evidence: \"{fact.get('evidence')}\"")
        return "\n".join(formatted)

    def generate_legal_sections(self, facts: List[Dict[str, Any]]) -> str:
        template = self._load_template()
        facts_block = self._format_facts(facts)
        prompt = template.format(facts=facts_block)
        
        system_instruction = (
            "You are a lead litigation attorney and corporate secretary. Generate legal tables, "
            "contracts details, board profile sections, and declarations in standard legal disclosure format."
        )
        return self.ai_service.generate_text(
            prompt=prompt,
            system_instruction=system_instruction
        )
