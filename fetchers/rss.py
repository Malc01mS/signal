import feedparser
import requests
from config import RSS_SOURCES


def fetch_rss_items(limit_per_feed=5) -> list[dict]:
    results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    }
    for url in RSS_SOURCES:
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                print(f"  RSS {url}: HTTP {resp.status_code}", flush=True)
                continue
            feed = feedparser.parse(resp.content)
            if feed.bozo and not feed.entries:
                print(f"  RSS {url}: parse error — {feed.bozo_exception}", flush=True)
                continue
            for entry in feed.entries[:limit_per_feed]:
                results.append({
                    "source_type": "essay",
                    "title": entry.get("title", "").strip(),
                    "url": entry.get("link", ""),
                    "summary": entry.get("summary", "")[:800],
                    "published": entry.get("published", ""),
                    "source_name": feed.feed.get("title", url),
                    "keyword_match": "rss",
                })
        except Exception as e:
            print(f"  RSS fetch error for {url}: {e}", flush=True)
    return results
