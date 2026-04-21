import requests
import urllib.parse
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed

NS = {"atom": "http://www.w3.org/2005/Atom"}

# Category-restricted queries — econ/q-fin/cs.CY keeps out physics/biology noise
# arXiv category prefixes: econ.GN, econ.PE, q-fin.GN, q-fin.MF, cs.CY (Computers & Society)
ARXIV_QUERIES = [
    ("macro_capital",       "cat:econ.GN AND all:monetary policy fiscal dominance debt"),
    ("macro_capital",       "cat:econ.PE AND all:dollar hegemony reserve currency multipolar"),
    ("macro_capital",       "cat:q-fin.GN AND all:inflation interest rate central bank"),
    ("geopolitics_power",   "cat:econ.GN AND all:trade policy tariffs industrial policy"),
    ("geopolitics_power",   "cat:econ.PE AND all:geopolitics national security economic"),
    ("tech_industry",       "cat:cs.CY AND all:artificial intelligence regulation labor"),
    ("wealth_architecture", "cat:econ.PE AND all:wealth inequality tax redistribution"),
    ("long_game",           "cat:econ.GN AND all:long run growth institutions history"),
]


def _fetch_query(pillar: str, query: str, max_results: int = 8) -> list[dict]:
    try:
        # Build URL manually — requests encodes ':' which breaks arXiv cat: syntax
        encoded = urllib.parse.quote_plus(query, safe=":()")
        url = (
            f"https://export.arxiv.org/api/query"
            f"?search_query={encoded}"
            f"&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
        )
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0 (research aggregator)"})
        if resp.status_code != 200:
            print(f"  arXiv '{query[:40]}': HTTP {resp.status_code}", flush=True)
            return []

        root = ET.fromstring(resp.text)
        results = []
        for entry in root.findall("atom:entry", NS):
            title_el = entry.find("atom:title", NS)
            summary_el = entry.find("atom:summary", NS)
            published_el = entry.find("atom:published", NS)
            authors = entry.findall("atom:author", NS)

            title = title_el.text.strip().replace("\n", " ") if title_el is not None else ""
            if not title:
                continue

            abs_url = ""
            for link in entry.findall("atom:link", NS):
                if link.get("rel") == "alternate":
                    abs_url = link.get("href", "")
                    break

            author_names = []
            for a in authors[:3]:
                name_el = a.find("atom:name", NS)
                if name_el is not None:
                    author_names.append(name_el.text)

            results.append({
                "source_type": "paper",
                "title": title,
                "authors": author_names,
                "year": published_el.text[:4] if published_el is not None else "",
                "abstract": summary_el.text.strip()[:1000] if summary_el is not None else "",
                "url": abs_url,
                "source_name": "arXiv",
                "pillar_hint": pillar,
                "keyword_match": query,
            })
        return results
    except Exception as e:
        print(f"  arXiv fetch error for '{query[:40]}': {e}", flush=True)
        return []


def fetch_arxiv(limit=40) -> list[dict]:
    all_results = []
    seen_titles = set()

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(_fetch_query, pillar, query): query
                   for pillar, query in ARXIV_QUERIES}
        for future in as_completed(futures):
            for item in future.result():
                if item["title"] not in seen_titles:
                    seen_titles.add(item["title"])
                    all_results.append(item)

    return all_results[:limit]
