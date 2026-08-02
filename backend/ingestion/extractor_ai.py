import os
from typing import Dict, Any, List
from services.ai_service import AIService
from models.knowledge import KnowledgeExtractorResponse

class AIKnowledgeExtractor:
    """
    AIKnowledgeExtractor takes raw document text or tabular data, injects it into the
    externalized prompt template, and invokes Gemini to extract structured corporate facts.
    """
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.prompt_template_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "prompts", "knowledge_extraction.txt")
        )

    def _load_prompt_template(self) -> str:
        """
        Reads the externalized extraction prompt template.
        """
        if not os.path.exists(self.prompt_template_path):
            raise FileNotFoundError(f"System Prompt template not found at '{self.prompt_template_path}'")
        with open(self.prompt_template_path, "r", encoding="utf-8") as f:
            return f.read()

    def extract_knowledge(self, filename: str, category: str, raw_extracted_data: Any) -> List[Dict[str, Any]]:
        """
        Converts raw text/sheets structure into a single context, populates the template,
        and requests structured extraction from Gemini.
        """
        # 1. Format the raw content based on document data structure
        formatted_content = ""
        if isinstance(raw_extracted_data, list):
            # Page-by-page layout (PDF)
            for page in raw_extracted_data:
                formatted_content += f"--- Page {page['page_number']} ---\n{page['text']}\n\n"
        elif isinstance(raw_extracted_data, dict):
            # Sheet-by-sheet tables (Excel)
            for sheet_name, table in raw_extracted_data.items():
                formatted_content += f"--- Sheet Table: {sheet_name} ---\n{table}\n\n"
        else:
            # Plain text, DOCX, or JSON
            formatted_content = str(raw_extracted_data)

        # Clean check: limit context length to safe margins (Gemini accommodates 2M tokens but keep it clean)
        if len(formatted_content) > 150000:
            formatted_content = formatted_content[:150000] + "\n\n[CONTENT TRUNCATED FOR CONTEXT LIMITS]"

        # 2. Retrieve template and inject parameters
        template = self._load_prompt_template()
        prompt = template.format(
            filename=filename,
            category=category,
            content=formatted_content
        )

        # 3. Request structured Pydantic extraction from AI service
        try:
            response: KnowledgeExtractorResponse = self.ai_service.generate_structured(
                prompt=prompt,
                response_schema=KnowledgeExtractorResponse
            )
            
            # 4. Map the structured models back into serializable dict structures adding document source
            extracted_facts = []
            for item in response.items:
                extracted_facts.append({
                    "category": item.category,
                    "field": item.field,
                    "value": item.value,
                    "evidence": item.evidence,
                    "source_document": filename,
                    "source_page": item.source_page,
                    "confidence": item.confidence
                })
            return extracted_facts
            
        except Exception as e:
            raise RuntimeError(f"AI Fact Ingestion failed for document '{filename}': {str(e)}")
