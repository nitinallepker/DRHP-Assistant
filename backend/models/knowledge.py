from pydantic import BaseModel, Field
from typing import List

class KnowledgeItemSchema(BaseModel):
    """
    Schema for a single extracted fact/knowledge point.
    """
    category: str = Field(
        description="The business domain category of this fact. "
                    "Must be one of: company, business, industry, financials, ipo, promoters, management, legal, risk."
    )
    field: str = Field(
        description="The specific data field or metric name (e.g., registered_name, corporate_address, promoter_name, net_profit_fy25, litigation_amount, fresh_issue_crores)."
    )
    value: str = Field(
        description="The extracted value of this field (e.g., 'ABC Industries Limited', '100 Crores', 'Jane Doe'). Must be formatted as a string."
    )
    evidence: str = Field(
        description="The verbatim sentence, line, or table row from the source document that contains this fact."
    )
    source_page: str = Field(
        description="The page number (for PDFs/Word files) or sheet name (for Excel spreadsheets) where this fact resides."
    )
    confidence: float = Field(
        description="Estimated confidence score of the fact accuracy from 0.0 (low) to 1.0 (exact)."
    )

class KnowledgeExtractorResponse(BaseModel):
    """
    Wrapper schema to capture multiple facts from a single document.
    """
    items: List[KnowledgeItemSchema] = Field(
        description="A collection of extracted facts and structured data points from the document content."
    )
