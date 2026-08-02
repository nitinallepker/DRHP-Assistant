import re
from typing import List, Dict, Any

class SearchEngine:
    """
    SearchEngine indexes drafted DRHP sections and provides ranked, 
    snippet-highlighted keyword search capabilities.
    """
    
    def search(self, query: str, sections: List[Any]) -> List[Dict[str, Any]]:
        """
        Executes a keyword search across the provided list of DRHPSection rows.
        Returns a list of ranked search results containing snippets.
        """
        if not query or not sections:
            return []
            
        query_lower = query.lower().strip()
        query_terms = [t for t in query_lower.split() if len(t) > 1]
        
        results = []
        for sec in sections:
            content = sec.content
            content_lower = content.lower()
            
            score = 0.0
            first_match_idx = -1
            
            # 1. Exact phrase match boost
            if query_lower in content_lower:
                score += 15.0
                first_match_idx = content_lower.find(query_lower)
                
            # 2. Term frequency matching
            term_matches = 0
            for term in query_terms:
                matches = list(re.finditer(re.escape(term), content_lower))
                if matches:
                    term_matches += len(matches)
                    if first_match_idx == -1:
                        first_match_idx = matches[0].start()
                        
            if term_matches == 0 and score == 0.0:
                continue
                
            # Compute tf-like overlap score
            words_count = len(content.split())
            if words_count > 0:
                score += (term_matches * 5.0) / words_count
                
            # 3. Extract highlighted context snippet (approx 160 chars)
            snippet = ""
            if first_match_idx != -1:
                start = max(0, first_match_idx - 40)
                end = min(len(content), first_match_idx + 120)
                prefix = "..." if start > 0 else ""
                suffix = "..." if end < len(content) else ""
                snippet = f"{prefix}{content[start:end].strip()}{suffix}"
                # Clean up any inner newline artifacts in snippets
                snippet = snippet.replace("\n", " ").replace("  ", " ")
                
            results.append({
                "section_id": sec.id,
                "section_slug": sec.section_slug,
                "title": sec.title,
                "version": sec.version,
                "status": sec.status,
                "score": round(score, 2),
                "snippet": snippet
            })
            
        # Sort results by score in descending order
        return sorted(results, key=lambda x: x["score"], reverse=True)
