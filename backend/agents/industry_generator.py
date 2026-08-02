import os
from typing import List, Dict, Any
from services.ai_service import AIService

class IndustryGenerator:
    """
    IndustryGenerator drafts the Industry Overview section of the DRHP.
    """

    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.prompts_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "prompts")
        )

    def _load_template(self) -> str:
        path = os.path.join(self.prompts_dir, "industry_prompt.txt")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _format_facts(self, facts: List[Dict[str, Any]]) -> str:
        if not facts:
            return "No industry facts available."
        formatted = []
        for fact in facts:
            formatted.append(f"- Category: {fact.get('category')}\n  Fact: {fact.get('field')}\n  Value: {fact.get('value')}\n  Evidence: \"{fact.get('evidence')}\"")
        return "\n".join(formatted)

    def generate_industry_overview(self, facts: List[Dict[str, Any]]) -> str:
        template = self._load_template()
        facts_block = self._format_facts(facts)
        prompt = template.format(facts=facts_block)
        
        system_instruction = (
            "You are a professional industry research analyst and corporatelegal counsel. "
            "Write the Industry Overview section objectively using the provided facts and figures."
        )
        return self.ai_service.generate_text(
            prompt=prompt,
            system_instruction=system_instruction
        )
