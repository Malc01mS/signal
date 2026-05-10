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

    # Collect all eligible picks (excluding long_game/stack), rank by score, cap at MAX_TOTAL_ITEMS
    candidates = []
    for pillar in PILLARS:
        if pillar in ("long_game", "stack"):
            continue
        for item in by_pillar.get(pillar, [])[:MAX_ITEMS_PER_PILLAR]:
            if item != long_game:
                candidates.append(item)
    candidates.sort(key=lambda x: x.get("total", 0), reverse=True)
    picks = candidates[:MAX_TOTAL_ITEMS]

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
These are this week's top macro/capital picks: {titles}

Write a macro signal of 100-150 words. Hard limit — do not exceed 150 words.

Framing: look for fragility in coordination infrastructure. Which of these picks
reveals a system that breaks or centralises under pressure? That is the thread.
Do not use reflexivity or abstract market-incompleteness framing.

Structure:
- Open with the structural mechanism (1-2 sentences, specific, no hedging)
- Connect the picks to that mechanism (1-2 sentences)
- Close with a concrete implication: one thing to watch or one position it
  sharpens. Must be actionable or directional — not a restatement of the thesis.

No academic connective tissue. No "this suggests that" or "it is worth noting".
Return plain text only, two short paragraphs.
{f'Recent feedback: {feedback_context}' if feedback_context else ''}
"""
    msg = _client().messages.create(
        model="claude-sonnet-4-5",
        max_tokens=250,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text
