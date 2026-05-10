import anthropic
import json
import os
from config import MAX_ITEMS_PER_PILLAR, MAX_TOTAL_ITEMS, PILLARS

def _client():
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def compose(scored_items: list[dict], feedback_context: str = "") -> dict:
    by_pillar = {p: [] for p in PILLARS}
    for item in scored_items:
        pillar = item.get("pillar", "macro_capital")
        if pillar not in by_pillar:
            pillar = "macro_capital"
        item["pillar"] = pillar  # normalise in-place so downstream filters work
        by_pillar[pillar].append(item)

    all_sorted = sorted(scored_items, key=lambda x: x.get("total", 0), reverse=True)
    long_game = all_sorted[0] if all_sorted else None

    picks = []
    for pillar in PILLARS:
        if pillar in ("long_game", "stack"):
            continue
        for item in by_pillar.get(pillar, [])[:MAX_ITEMS_PER_PILLAR]:
            if item != long_game and len(picks) < MAX_TOTAL_ITEMS:
                picks.append(item)

    top_macro = [i for i in picks if i.get("pillar") == "macro_capital"][:3]
    macro_signal = generate_macro_signal(top_macro, feedback_context)

    return {
        "macro_signal": macro_signal,
        "picks": picks[:MAX_TOTAL_ITEMS],
        "long_game": long_game,
        "wealth_architecture": [i for i in picks if i.get("pillar") == "wealth_architecture"],
    }


def generate_macro_signal(top_items: list[dict], feedback_context: str) -> str:
    if not top_items:
        return ""
    titles = [i["raw_item"].get("title") for i in top_items]
    prompt = f"""
Based on these top macro/capital items this week: {titles}
Write a 2-paragraph macro signal — the dominant thesis or mechanism worth
understanding right now. Assume the reader is already tracking headlines.
Go to the structural level. No fluff. Return plain text only.
{f'Recent feedback context: {feedback_context}' if feedback_context else ''}
"""
    msg = _client().messages.create(
        model="claude-sonnet-4-5",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text
