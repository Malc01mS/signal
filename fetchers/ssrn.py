import requests
from bs4 import BeautifulSoup

SSRN_CATEGORIES = [
    "https://papers.ssrn.com/sol3/topten/topTenResults.cfm?groupingId=2&netorjrnl=net",
    "https://papers.ssrn.com/sol3/topten/topTenResults.cfm?groupingId=18&netorjrnl=net",
    "https://papers.ssrn.com/sol3/topten/topTenResults.cfm?groupingId=6&netorjrnl=net",
]


def fetch_top_papers(limit=10) -> list[dict]:
    results = []
    headers = {"User-Agent": "Mozilla/5.0 (research aggregator)"}
    for url in SSRN_CATEGORIES:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, "lxml")
            for row in soup.select("table.w-100 tr")[1:limit+1]:
                cells = row.find_all("td")
                if len(cells) >= 3:
                    link = cells[1].find("a")
                    if link:
                        href = link.get("href", "")
                        full_url = href if href.startswith("http") else "https://papers.ssrn.com" + href
                        results.append({
                            "source_type": "paper",
                            "title": link.text.strip(),
                            "url": full_url,
                            "downloads": cells[2].text.strip(),
                            "keyword_match": "SSRN top download",
                        })
        except Exception as e:
            print(f"SSRN fetch error: {e}")
    return results
