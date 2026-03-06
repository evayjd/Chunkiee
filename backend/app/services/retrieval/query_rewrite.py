import re
import requests
from typing import List


class QueryRewriter:
    def __init__(
        self,
        model: str = "qwen2.5:1.5b",
        url: str = "http://localhost:11434/api/generate"
    ):
        self.model = model
        self.url = url

        # 简单缓存
        self.cache = {}

    def _normalize(self, query: str) -> str:
        q = query.strip().lower()
        q = re.sub(r"\s+", " ", q)
        return q

    def _call_llm(self, query: str) -> List[str]:
        prompt = f"""
You are a search query expert.

Generate 3 alternative search queries that help retrieve relevant
documents from a vector database.

Also extract multilingual keywords in Chinese, English, and French.

Return STRICT JSON format:

{{
 "queries": ["query1","query2","query3"],
 "keywords": {{
    "zh": "...",
    "en": "...",
    "fr": "..."
 }}
}}

User Query:
{query}
"""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3}
        }

        try:

            r = requests.post(
                self.url,
                json=payload,
                timeout=10
            )

            res = r.json().get("response", "")

        except Exception:
            return []

        try:
            import json

            data = json.loads(res)

            queries = data.get("queries", [])
            keywords = data.get("keywords", {})

            keyword_str = " ".join(keywords.values())

            # keyword expansion
            queries = [
                f"{q} {keyword_str}".strip()
                for q in queries
            ]

            return queries

        except Exception:
            return []

    def rewrite(self, query: str) -> List[str]:
        q = self._normalize(query)

        # cache
        if q in self.cache:
            return self.cache[q]

        queries = [q]

        llm_queries = self._call_llm(q)

        queries.extend(llm_queries)

        queries = self._dedupe_keep_order(queries)

        self.cache[q] = queries

        return queries

    def _dedupe_keep_order(self, items: List[str]) -> List[str]:
        seen = set()
        result = []

        for item in items:
            if item not in seen:
                seen.add(item)
                result.append(item)

        return result


# singleton
_rewriter = QueryRewriter()


def rewrite_query(query: str) -> List[str]:
    return _rewriter.rewrite(query)