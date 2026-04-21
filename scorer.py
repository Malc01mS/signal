import json
import os
import re
import sys
import anthropic
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import PROFILE, PILLARS, SCORING_THRESHOLDS


def _extract_json(text: str) -> str:
    """Strip markdown code fences if Claude wraps its response."""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    return text.strip()

def _client():
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

STAGE1_SYSTEM = f"""
You are a content filter for Signal, a weekly intelligence brief.

User profile:
{PROFILE}

For each item provided, return ONLY a JSON array. Each element:
{{
  "index": <int>,
  "pass": <bool>,
  "pillar": "<string>",
  "quick_reason": "<10 words max>"
}}

Be aggressive in cutting. Only pass items that have genuine mechanistic depth
or position value for this specific reader. Reject anything likely already
covered by his podcast/X ecosystem.
"""

STAGE2_SYSTEM = f"""
You are the editorial intelligence behind Signal, a weekly brief for Malcolm.

{PROFILE}

Score this item across five dimensions (1–10 each):

RELEVANCE — Hits one of his core pillars meaningfully
MECHANISTIC_DEPTH — Explains WHY something happens structurally, not just WHAT
POSITION_VALUE — Could sharpen, challenge, or build a view he holds (intellectual or financial)
WHY_NOW — A specific editorial reason it belongs THIS week (new, citation-spiking, illuminates current events)
NOVELTY — Unlikely to have already reached him via podcasts/X. Penalize heavily if it's been through All In, Dwarkesh, Lex, Acquired, or macro Twitter canon.

Return ONLY valid JSON:
{{
  "scores": {{
    "relevance": <int>,
    "mechanistic_depth": <int>,
    "position_value": <int>,
    "why_now": <int>,
    "novelty": <int>
  }},
  "total": <int>,
  "tier": "high_alpha | include | cut",
  "pillar": "<pillar_name>",
  "why_now_editorial": "<One sentence. Why does this appear this week specifically.>",
  "summary": "<3-4 sentences. What it says and why it matters to Malcolm specifically. Dense, no fluff.>",
  "directional_indicator": "<Specific: if this thesis holds, [X] follows. Watch [Y] as the counterfactual.>"
}}
"""


def stage1_filter(items: list[dict]) -> list[dict]:
    batch = json.dumps([
        {
            "index": i,
            "title": item.get("title"),
            "abstract": item.get("abstract") or item.get("summary"),
            "source": item.get("source_name", ""),
        }
        for i, item in enumerate(items)
    ])
    msg = _client().messages.create(
        model="claude-sonnet-4-5",
        max_tokens=8000,
        system=STAGE1_SYSTEM,
        messages=[{"role": "user", "content": f"Filter this batch:\n{batch}"}],
    )
    try:
        results = json.loads(_extract_json(msg.content[0].text))
        shortlist = []
        for r in results:
            if r.get("pass") and r["index"] < len(items):
                items[r["index"]]["pillar_hint"] = r.get("pillar")
                shortlist.append(items[r["index"]])
        return shortlist
    except Exception as e:
        print(f"Stage 1 parse error: {e}")
        return items[:25]


def stage2_score(item: dict) -> dict | None:
    content = json.dumps({
        "title": item.get("title"),
        "authors": item.get("authors"),
        "year": item.get("year"),
        "abstract": item.get("abstract") or item.get("summary"),
        "source": item.get("source_name", ""),
        "url": item.get("url"),
        "citation_count": item.get("citation_count"),
        "pillar_hint": item.get("pillar_hint"),
    })
    try:
        msg = _client().messages.create(
            model="claude-sonnet-4-5",
            max_tokens=600,
            system=STAGE2_SYSTEM,
            messages=[{"role": "user", "content": content}],
        )
        scored = json.loads(_extract_json(msg.content[0].text))
        scored["raw_item"] = item
        return scored
    except Exception as e:
        print(f"Stage 2 score error for '{item.get('title')}': {e}")
        return None


def score_all(items: list[dict]) -> list[dict]:
    print(f"Stage 1: filtering {len(items)} candidates...", flush=True)
    shortlist = stage1_filter(items)
    print(f"Stage 1: {len(shortlist)} passed to Stage 2", flush=True)

    scored = []
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(stage2_score, item): item for item in shortlist}
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            print(f"  Stage 2: scored {i}/{len(shortlist)}", flush=True)
            if result and result.get("total", 0) >= SCORING_THRESHOLDS["include"]:
                scored.append(result)

    scored.sort(key=lambda x: x.get("total", 0), reverse=True)
    print(f"Stage 2: {len(scored)} items scored above threshold", flush=True)
    return scored
