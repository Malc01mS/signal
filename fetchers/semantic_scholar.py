import requests
import time
from config import SEMANTIC_SCHOLAR_KEYWORDS

BASE_URL = "https://api.semanticscholar.org/graph/v1"

# Limit to a few high-signal keywords to stay under rate limit (no API key)
TOP_KEYWORDS = SEMANTIC_SCHOLAR_KEYWORDS[:4]


def fetch_trending_papers(limit=20) -> list[dict]:
    results = []
    seen = set()

    for i, keyword in enumerate(TOP_KEYWORDS):
        if i > 0:
            time.sleep(2)  # avoid 429 without API key
        try:
            resp = requests.get(
                f"{BASE_URL}/paper/search",
                params={
                    "query": keyword,
                    "fields": "title,authors,year,citationCount,influentialCitationCount,abstract,url,paperId",
                    "limit": 8,
                    "sort": "citationCount",
                },
                timeout=10,
            )
            if resp.status_code == 429:
                print(f"  Semantic Scholar rate limited — stopping early", flush=True)
                break
            if resp.status_code != 200:
                print(f"  Semantic Scholar '{keyword}': HTTP {resp.status_code}", flush=True)
                continue

            for paper in resp.json().get("data", []):
                title = paper.get("title", "")
                if title in seen:
                    continue
                seen.add(title)
                if paper.get("abstract") and paper.get("citationCount", 0) > 10:
                    results.append({
                        "source_type": "paper",
                        "title": title,
                        "authors": [a["name"] for a in paper.get("authors", [])[:3]],
                        "year": paper.get("year"),
                        "citation_count": paper.get("citationCount", 0),
                        "influential_citations": paper.get("influentialCitationCount", 0),
                        "abstract": paper.get("abstract", "")[:1000],
                        "url": paper.get("url") or f"https://www.semanticscholar.org/paper/{paper.get('paperId', '')}",
                        "source_name": "Semantic Scholar",
                        "keyword_match": keyword,
                    })
        except Exception as e:
            print(f"  Semantic Scholar fetch error for '{keyword}': {e}", flush=True)

    return results[:limit]
