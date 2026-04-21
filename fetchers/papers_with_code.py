import requests


def fetch_trending(limit=20) -> list[dict]:
    try:
        resp = requests.get(
            "https://paperswithcode.com/api/v1/papers/",
            params={"ordering": "-stars", "items_per_page": limit},
            timeout=10,
        )
        results = []
        for p in resp.json().get("results", []):
            results.append({
                "source_type": "paper",
                "title": p.get("title"),
                "authors": p.get("authors", []),
                "abstract": p.get("abstract", "")[:1000],
                "url": p.get("url_abs") or p.get("paper_url"),
                "stars": p.get("stars", 0),
                "keyword_match": "AI/ML trending",
            })
        return results
    except Exception as e:
        print(f"Papers With Code fetch error: {e}")
        return []
