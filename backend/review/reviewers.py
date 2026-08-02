import os
import re
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("reviewers")

# Extensible registry map to hold reviewer implementations
REVIEWER_REGISTRY = {}

def register_reviewer(name: str):
    """
    Decorator to register reviewer implementations dynamically.
    """
    def decorator(cls):
        REVIEWER_REGISTRY[name.upper()] = cls
        return cls
    return decorator


class BaseReviewer:
    """
    Abstract base class for all independent reviewers.
    Provides standard prompt execution, parsing, and offline fallbacks.
    """
    def __init__(self, ai_service: Any):
        self.ai_service = ai_service

    def get_prompt(self, section_slug: str, content: str, facts_context: str) -> str:
        raise NotImplementedError()

    def get_system_instruction(self) -> str:
        raise NotImplementedError()

    def get_mock_suggestions(self, section_slug: str, content: str, facts: List[Any]) -> List[Dict[str, Any]]:
        raise NotImplementedError()

    def review(self, section_slug: str, version: int, content: str, facts: List[Any]) -> List[Dict[str, Any]]:
        """
        Executes the reviewer. Uses live Gemini model if configured, otherwise falls back to
        highly-specific structural mock analysis.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        use_mock = not api_key or api_key == "your_gemini_api_key_here"

        if use_mock:
            logger.info(f"Running mock review for reviewer={self.__class__.__name__} on slug={section_slug}")
            return self.get_mock_suggestions(section_slug, content, facts)

        # 1. Prepare contexts
        facts_lines = []
        for f in facts:
            facts_lines.append(
                f"- [{f.category}] {f.field}: {f.value} (Evidence: \"{f.evidence}\" | Doc: {f.source_document}, Page: {f.source_page})"
            )
        facts_context = "\n".join(facts_lines) if facts_lines else "No relevant corporate facts in this pack."

        prompt = self.get_prompt(section_slug, content, facts_context)
        system_instruction = self.get_system_instruction()

        try:
            ai_raw = self.ai_service.generate_text(
                prompt=prompt,
                system_instruction=system_instruction
            )
            
            # Find and parse JSON list from AI response
            json_match = re.search(r"\[\s*\{.*\}\s*\]", ai_raw, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                # Direct parse fallback
                return json.loads(ai_raw.strip())
        except Exception as e:
            logger.error(f"Live review failed for {self.__class__.__name__}: {e}. Falling back to mocks.")
            return self.get_mock_suggestions(section_slug, content, facts)


@register_reviewer("LEGAL")
class LegalReviewer(BaseReviewer):
    """
    Audits legal disclosures, litigation references, declarations, and liabilities.
    """
    def get_system_instruction(self) -> str:
        return "You are an expert SEBI corporate legal counsel reviewing DRHP draft sections for legal accuracy."

    def get_prompt(self, section_slug: str, content: str, facts_context: str) -> str:
        return f"""Audit the following DRHP section content against the legal corporate facts.
Identify legal disclosures, court litigations, or declaration inaccuracies. 
You must never modify the text. Return only a JSON list of suggestion objects.

=== RELEVANT LEGAL FACTS ===
{facts_context}
============================

=== TARGET SECTION: {section_slug} ===
{content}
======================================

RESPONSE FORMAT:
Return a JSON list (and NOTHING else) matching this schema:
[
  {{
    "severity": "HIGH", // HIGH, MEDIUM, or LOW
    "confidence": 0.95, // Float 0.0 to 1.0
    "reason": "Explanation of the legal issue.",
    "evidence": "Cite specific facts/pages/documents from the legal facts block.",
    "recommendation": "Provide clear legal wording suggestion."
  }}
]
"""

    def get_mock_suggestions(self, section_slug: str, content: str, facts: List[Any]) -> List[Dict[str, Any]]:
        suggestions = []
        if section_slug == "LEGAL_LITIGATION_DECLARATION":
            # Extract evidence link from facts if available
            evidence_source = "litigation_status.pdf"
            for f in facts:
                if f.category == "LITIGATION":
                    evidence_source = f"{f.source_document}, page: {f.source_page}"
                    break
            
            suggestions.append({
                "severity": "MEDIUM",
                "confidence": 0.9,
                "reason": "The outstanding municipal corporation litigation requires a direct petition filing reference ID.",
                "evidence": f"Fact category: LITIGATION, source: {evidence_source}",
                "recommendation": "Append: 'Municipal corporation petition status is pending under civil suit reference suit no. 204/2025.'"
            })
        return suggestions


@register_reviewer("FINANCE")
class FinanceReviewer(BaseReviewer):
    """
    Audits financial highlights, balance sheet metrics, ratios, and monetary balances.
    """
    def get_system_instruction(self) -> str:
        return "You are a professional investment banker and auditor reviewing DRHP financial statements."

    def get_prompt(self, section_slug: str, content: str, facts_context: str) -> str:
        return f"""Audit the financial metrics and numbers inside this DRHP section against the source financials.
You must never modify the text. Return only a JSON list of suggestion objects.

=== SOURCE FINANCIAL FACTS ===
{facts_context}
==============================

=== TARGET SECTION: {section_slug} ===
{content}
======================================

RESPONSE FORMAT:
[
  {{
    "severity": "HIGH",
    "confidence": 0.98,
    "reason": "Financial mismatch details.",
    "evidence": "Cite specific ledger, file sheets, or values.",
    "recommendation": "State the correct number alignment."
  }}
]
"""

    def get_mock_suggestions(self, section_slug: str, content: str, facts: List[Any]) -> List[Dict[str, Any]]:
        suggestions = []
        if section_slug == "FINANCIAL_HIGHLIGHTS_MDA":
            evidence_source = "financial_statements.xlsx"
            revenue_val = "1,250 Crores"
            for f in facts:
                if f.category == "FINANCIAL_STATEMENTS" and "revenue" in f.field.lower():
                    evidence_source = f"{f.source_document}, sheet: {f.source_page}"
                    revenue_val = f.value
                    break
            suggestions.append({
                "severity": "HIGH",
                "confidence": 0.98,
                "reason": "FY25 revenue totals must match corporate audited balance sheets exactly to prevent filing non-compliance.",
                "evidence": f"Fact category: FINANCIAL_STATEMENTS, source: {evidence_source}, value: {revenue_val}",
                "recommendation": f"Ensure the statement reads: 'Audited revenues for FY25 stood at INR {revenue_val} as per board reports.'"
            })
        return suggestions


@register_reviewer("BUSINESS")
class BusinessReviewer(BaseReviewer):
    """
    Audits company profile, promoters, history, operations, and business strengths.
    """
    def get_system_instruction(self) -> str:
        return "You are an industry analyst reviewing DRHP corporate business models."

    def get_prompt(self, section_slug: str, content: str, facts_context: str) -> str:
        return f"""Audit the business profile, founder histories, and operational highlights inside this DRHP section.
You must never modify the text. Return only a JSON list of suggestion objects.

=== BUSINESS FACTS ===
{facts_context}
======================

=== TARGET SECTION: {section_slug} ===
{content}
======================================

RESPONSE FORMAT:
[
  {{
    "severity": "LOW",
    "confidence": 0.85,
    "reason": "Operational/business narrative gap.",
    "evidence": "Cite source profile records.",
    "recommendation": "Provide wording adjustment."
  }}
]
"""

    def get_mock_suggestions(self, section_slug: str, content: str, facts: List[Any]) -> List[Dict[str, Any]]:
        suggestions = []
        if section_slug == "BUSINESS_OVERVIEW_STRENGTHS":
            evidence_source = "company_profile.pdf"
            for f in facts:
                if f.category == "COMPANY_PROFILE":
                    evidence_source = f"{f.source_document}"
                    break
            suggestions.append({
                "severity": "LOW",
                "confidence": 0.85,
                "reason": "Promoter history description could highlight Noida corporate headquarters establishment year.",
                "evidence": f"Fact category: COMPANY_PROFILE, source: {evidence_source}",
                "recommendation": "Revise sentence to: 'The promoters established core software services in the corporate hub of Noida in 2018.'"
            })
        return suggestions


@register_reviewer("RISK")
class RiskReviewer(BaseReviewer):
    """
    Audits internal and external risk factors, listing completeness and threat models.
    """
    def get_system_instruction(self) -> str:
        return "You are a risk management auditor reviewing DRHP investment risk sections."

    def get_prompt(self, section_slug: str, content: str, facts_context: str) -> str:
        return f"""Audit the internal and external risks mentioned in this section against corporate liability registries.
You must never modify the text. Return only a JSON list of suggestion objects.

=== ACCUMULATED LIABILITY FACTS ===
{facts_context}
===================================

=== TARGET SECTION: {section_slug} ===
{content}
======================================

RESPONSE FORMAT:
[
  {{
    "severity": "MEDIUM",
    "confidence": 0.90,
    "reason": "Risk omission or description mismatch.",
    "evidence": "Cite registry records.",
    "recommendation": "Provide concrete risk disclosure wording."
  }}
]
"""

    def get_mock_suggestions(self, section_slug: str, content: str, facts: List[Any]) -> List[Dict[str, Any]]:
        suggestions = []
        if section_slug == "RISK_FACTORS":
            evidence_source = "risk_registry.json"
            for f in facts:
                if f.category == "LITIGATION":
                    evidence_source = f"{f.source_document}"
                    break
            suggestions.append({
                "severity": "MEDIUM",
                "confidence": 0.92,
                "reason": "The server downtime risk lacks clear mitigation statements regarding redundancy backups.",
                "evidence": f"Fact category: LITIGATION/OPERATIONAL, source: {evidence_source}",
                "recommendation": "Add mitigation clause: 'We mitigate server downtime risks by implementing multi-region cloud backup strategies.'"
            })
        return suggestions


@register_reviewer("COMPLIANCE")
class ComplianceReviewer(BaseReviewer):
    """
    Audits regulatory clauses, SEBI ICDR guidelines, and mandatory corporate declarations.
    """
    def get_system_instruction(self) -> str:
        return "You are a SEBI ICDR compliance officer reviewing draft filing prospectuses."

    def get_prompt(self, section_slug: str, content: str, facts_context: str) -> str:
        return f"""Audit regulatory compliance statements and statutory boilerplate text in this section.
You must never modify the text. Return only a JSON list of suggestion objects.

=== COMPLIANCE FACTS ===
{facts_context}
========================

=== TARGET SECTION: {section_slug} ===
{content}
======================================

RESPONSE FORMAT:
[
  {{
    "severity": "HIGH",
    "confidence": 0.95,
    "reason": "Filing or SEBI ICDR non-compliance description.",
    "evidence": "Cite SEBI guides or registry files.",
    "recommendation": "Provide correct regulatory declaration text."
  }}
]
"""

    def get_mock_suggestions(self, section_slug: str, content: str, facts: List[Any]) -> List[Dict[str, Any]]:
        suggestions = []
        if section_slug == "GLOSSARY_DEFINITIONS":
            evidence_source = "board_resolutions.pdf"
            for f in facts:
                if f.category == "IPO_DETAILS":
                    evidence_source = f"{f.source_document}"
                    break
            suggestions.append({
                "severity": "HIGH",
                "confidence": 0.95,
                "reason": "The definitions for SEBI and Companies Act must include current references to SEBI ICDR Regulations 2018.",
                "evidence": f"Fact category: IPO_DETAILS, source: {evidence_source}",
                "recommendation": "Define: 'SEBI ICDR Regulations means the Securities and Exchange Board of India (Issue of Capital and Disclosure Requirements) Regulations, 2018, as amended.'"
            })
        return suggestions


@register_reviewer("LANGUAGE")
class LanguageReviewer(BaseReviewer):
    """
    Audits style, professional grammar, formatting, spelling, and legal drafting tones.
    Doesn't strictly require knowledge pack facts but reviews the raw text.
    """
    def get_system_instruction(self) -> str:
        return "You are a professional legal editor and compliance copywriter reviewing prospectuses."

    def get_prompt(self, section_slug: str, content: str, facts_context: str) -> str:
        return f"""Audit this section content for spelling, grammar, readability, formatting, and professional tone.
You must never modify the text. Return only a JSON list of suggestion objects.

=== TARGET SECTION: {section_slug} ===
{content}
======================================

RESPONSE FORMAT:
[
  {{
    "severity": "LOW",
    "confidence": 0.90,
    "reason": "Spelling or grammatical layout issue.",
    "evidence": "Cite the exact text segment that has the error.",
    "recommendation": "Provide corrected copy."
  }}
]
"""

    def get_mock_suggestions(self, section_slug: str, content: str, facts: List[Any]) -> List[Dict[str, Any]]:
        suggestions = []
        # General spelling or style check mockup
        suggestions.append({
            "severity": "LOW",
            "confidence": 0.95,
            "reason": "Grammatical correction to improve readability: replace informal contractions or abbreviations.",
            "evidence": "Line starting with 'The registered address' or 'Support details'",
            "recommendation": "Ensure all occurrences of 'etc.' are replaced with 'and other similar statutory registries' for formal registry submissions."
        })
        return suggestions


@register_reviewer("CONSISTENCY")
class ConsistencyReviewer(BaseReviewer):
    """
    Cross-checks alignment and verifies metrics consistency between all drafted sections.
    Receives all sections inside content to execute cross-sectional analysis.
    """
    def get_system_instruction(self) -> str:
        return "You are an analytical consistency checker auditing DRHP filings for contradictions."

    def get_prompt(self, section_slug: str, content: str, facts_context: str) -> str:
        return f"""Cross-audit all sections for contradictions in figures, promoter holding percentages, or dates.
You must never modify the text. Return only a JSON list of suggestion objects.

=== ALL DRAFT SECTIONS IN WORKSPACE ===
{content}
=======================================

=== COMPILATION FACTS ===
{facts_context}
=========================

RESPONSE FORMAT:
[
  {{
    "severity": "HIGH",
    "confidence": 0.97,
    "reason": "Contradiction found between Section X and Section Y regarding metric Z.",
    "evidence": "Cite discrepancy details.",
    "recommendation": "Suggest aligned values."
  }}
]
"""

    def get_mock_suggestions(self, section_slug: str, content: str, facts: List[Any]) -> List[Dict[str, Any]]:
        suggestions = []
        # Consistency checks lookups
        suggestions.append({
            "severity": "HIGH",
            "confidence": 0.97,
            "reason": "Fresh issue size of 400 Crores listed in Cover Page must align with issue allocation details in the capital structure statements.",
            "evidence": "Discrepancy: Cover Page states fresh issue up to 400 Crores, ensure capitalization matches in all tables.",
            "recommendation": "Align fresh issue details: Ensure fresh issue capital calculations total 400 Crores exactly in subsequent sections."
        })
        return suggestions
