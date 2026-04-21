import requests
from datetime import datetime, timedelta
from config import SEMANTIC_SCHOLAR_KEYWORDS

BASE_URL = "https://api.semanticscholar.org/graph/v1"


def fetch_trending_papers(days_back=90, limit=50) -> list[dict]:
    results = []

    for keyword in SEMANTIC_SCHOLAR_KEYWORDS[:10]:
        try:
            resp = requests.get(
                f"{BASE_URL}/paper/search",
                params={
                    "query": keyword,
                    "fields": "title,authors,year,citationCount,influentialCitationCount,abstract,externalIds,publicationDate,url",
                    "limit": 10,
                    "sort": "citationCount",
                },
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                for paper in data.get("data", []):
                    if paper.get("abstract") and paper.get("citationCount", 0) > 10:
                        results.append({
                            "source_type": "paper",
                            "title": paper.get("title"),
                            "authors": [a["name"] for a in paper.get("authors", [])[:3]],
                            "year": paper.get("year"),
                            "citation_count": paper.get("citationCount", 0),
                            "influential_citations": paper.get("influentialCitationCount", 0),
                            "abstract": paper.get("abstract", "")[:1000],
                            "url": paper.get("url") or f"https://www.semanticscholar.org/paper/{paper.get('paperId', '')}",
                            "keyword_match": keyword,
                        })
        except Exception as e:
            print(f"Semantic Scholar fetch error for '{keyword}': {e}")

    seen = set()
    unique = []
    for p in sorted(results, key=lambda x: x["influential_citations"], reverse=True):
        if p["title"] not in seen:
            seen.add(p["title"])
            unique.append(p)

    return unique[:limit]
