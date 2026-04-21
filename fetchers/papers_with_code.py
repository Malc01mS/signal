import requests


def fetch_trending(limit=20) -> list[dict]:
    try:
        resp = requests.get(
            "https://paperswithcode.com/api/v1/papers/",
            params={"ordering": "-stars", "items_per_page": limit},
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (research aggregator)"},
        )
        if resp.status_code != 200:
            print(f"Papers With Code fetch error: HTTP {resp.status_code}", flush=True)
            return []
        try:
            data = resp.json()
        except Exception:
            print(f"Papers With Code fetch error: non-JSON response (likely blocked). Content-Type: {resp.headers.get('Content-Type')}", flush=True)
            return []
        results = []
        for p in data.get("results", []):
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
        print(f"Papers With Code fetch error: {e}", flush=True)
        return []
