"""
AIService: lightweight AI hooks (placeholder) for reranking and enrichment.
This can be replaced by a real LLM or vector reranker later.
"""
from __future__ import annotations

from typing import List, Dict, Any, Callable, Optional
import re


class AIService:
    def __init__(self):
        pass

    def _basic_score(self, query: str, text: str | None) -> float:
        if not text:
            return 0.0
        q = query.strip().lower()
        t = text.lower()
        if not q:
            return 0.0
        # Simple token overlap score
        q_tokens = [tok for tok in re.split(r"\W+", q) if tok]
        score = 0
        for tok in q_tokens:
            score += t.count(tok)
        return float(score)

    def rerank_search_results(self, query: str, results: List[Any], get_text: Callable[[Any], str | None]) -> List[Any]:
        """
        Rerank a list of results by a simple heuristic score based on token overlap.
        """
        return sorted(results, key=lambda r: self._basic_score(query, get_text(r)), reverse=True)

    def rerank_dicts(self, query: str, items: List[Dict[str, Any]], text_keys: List[str]) -> List[Dict[str, Any]]:
        def get_text(d: Dict[str, Any]) -> str | None:
            for k in text_keys:
                if k in d and d[k]:
                    return str(d[k])
            return None

        return self.rerank_search_results(query, items, get_text)

