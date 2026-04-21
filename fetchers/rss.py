import feedparser
from config import RSS_SOURCES


def fetch_rss_items(limit_per_feed=5) -> list[dict]:
    results = []
    for url in RSS_SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:limit_per_feed]:
                results.append({
                    "source_type": "essay",
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "summary": entry.get("summary", "")[:800],
                    "published": entry.get("published", ""),
                    "source_name": feed.feed.get("title", url),
                    "keyword_match": "rss",
                })
        except Exception as e:
            print(f"RSS fetch error for {url}: {e}")
    return results
