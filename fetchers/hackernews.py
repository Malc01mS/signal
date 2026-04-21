import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Keywords that match Malcolm's pillars — title-level filter before scoring
SIGNAL_KEYWORDS = [
    "macro", "economy", "economic", "monetary", "fiscal", "inflation",
    "deflation", "debt", "deficit", "fed", "treasury", "dollar",
    "interest rate", "yield", "bond",
    "geopolit", "china", "trade", "tariff", "sanction", "military",
    "nato", "war", "ukraine", "taiwan",
    "semiconductor", "chip", "nvidia", "tsmc", "intel",
    "ai ", "a.i.", "artificial intelligence", "llm", "openai",
    "energy", "oil", "gas", "commodity", "gold", "bitcoin", "crypto",
    "startup", "venture", "equity", "ipo", "valuation", "fundrais",
    "tax", "wealth", "capital gains", "real estate", "housing",
    "manufacturing", "industrial", "supply chain", "reshoring",
    "labour", "labor", "employment", "wage",
]


def _fetch_item(story_id: int) -> dict | None:
    try:
        resp = requests.get(
            f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
            timeout=6,
        )
        if resp.status_code != 200:
            return None
        item = resp.json()
        if not item or item.get("type") != "story" or not item.get("title"):
            return None
        title_lower = item["title"].lower()
        if not any(kw in title_lower for kw in SIGNAL_KEYWORDS):
            return None
        return {
            "source_type": "discussion",
            "title": item["title"],
            "url": item.get("url") or f"https://news.ycombinator.com/item?id={story_id}",
            "summary": (
                f"HackerNews: {item.get('score', 0)} points, "
                f"{item.get('descendants', 0)} comments."
                + (f" {item.get('text', '')[:400]}" if item.get("text") else "")
            ),
            "source_name": "Hacker News",
            "keyword_match": "hackernews",
        }
    except Exception:
        return None


def fetch_hackernews(limit=15) -> list[dict]:
    try:
        resp = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=10,
        )
        if resp.status_code != 200:
            print(f"  HackerNews top stories: HTTP {resp.status_code}", flush=True)
            return []

        story_ids = resp.json()[:80]
        results = []

        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = {pool.submit(_fetch_item, sid): sid for sid in story_ids}
            for future in as_completed(futures):
                item = future.result()
                if item:
                    results.append(item)
                if len(results) >= limit:
                    break

        return results[:limit]
    except Exception as e:
        print(f"  HackerNews fetch error: {e}", flush=True)
        return []
