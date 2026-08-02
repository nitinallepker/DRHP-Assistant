import re
from typing import List

class Redactor:
    """
    Redactor provides utilities to search and mask sensitive personal 
    and financial information (PII) before regulatory document publishing.
    """
    
    def __init__(self):
        # Configure standard SEBI compliance PII matching patterns
        self.patterns = {
            "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "PAN": r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
            "AADHAAR": r"\b\d{4}[ -]\d{4}[ -]\d{4}\b|\b\d{12}\b",
            "PHONE": r"\+91[ -]?[6-9]\d{9}\b|\b[6-9]\d{9}\b",
            "BANK_ACCOUNT": r"\b\d{9,18}\b"  # Standard Indian bank accounts are between 9 and 18 digits
        }

    def redact(self, text: str, rules: List[str] = None) -> str:
        """
        Scrubs PII elements matching the active rule categories.
        If rules is None, applies all redaction patterns.
        """
        if not text:
            return ""
            
        active_rules = rules if rules else list(self.patterns.keys())
        redacted_text = text
        
        for rule in active_rules:
            pattern = self.patterns.get(rule)
            if not pattern:
                continue
                
            # Perform regex substitution with placeholder tags
            redacted_text = re.sub(
                pattern, 
                f"[REDACTED_{rule}]", 
                redacted_text, 
                flags=re.IGNORECASE if rule in ["EMAIL"] else 0
            )
            
        return redacted_text
