import json
import pathlib
from dotenv import load_dotenv
load_dotenv(dotenv_path=pathlib.Path(__file__).parent / ".env", override=True)

from fetchers.semantic_scholar import fetch_trending_papers
from fetchers.arxiv import fetch_arxiv
from fetchers.hackernews import fetch_hackernews
from fetchers.rss import fetch_rss_items
from fetchers.dedupe import filter_new, commit_seen
from scorer import score_all
from composer import compose
from renderer import render
from publisher import publish
from emailer import send
from feedback import get_recent_feedback

ISSUE_FILE = pathlib.Path(__file__).parent / "data" / "issue.json"


def get_issue_number() -> int:
    try:
        return json.loads(ISSUE_FILE.read_text())["number"]
    except Exception:
        return 1


def increment_issue(n: int):
    ISSUE_FILE.parent.mkdir(exist_ok=True)
    ISSUE_FILE.write_text(json.dumps({"number": n + 1}))


def run():
    issue = get_issue_number()
    print(f"\n=== Signal Issue #{issue} ===\n", flush=True)

    print("Fetching sources...", flush=True)
    candidates = (
        fetch_rss_items() +
        fetch_arxiv() +
        fetch_hackernews() +
        fetch_trending_papers()
    )
    print(f"  Total candidates: {len(candidates)}", flush=True)

    if not candidates:
        print("  No candidates fetched — check fetcher errors above. Aborting.", flush=True)
        return

    candidates, pending_seen = filter_new(candidates)
    print(f"  After dedupe: {len(candidates)}", flush=True)

    if not candidates:
        print("  All candidates already seen this week. Nothing new to score.", flush=True)
        return

    feedback_ctx = get_recent_feedback(n=3)
    scored = score_all(candidates)

    if not scored:
        print("  No items scored above threshold. Brief would be empty — aborting.", flush=True)
        return

    brief = compose(scored, feedback_context=feedback_ctx)

    html_path = render(brief, issue_number=issue)
    print(f"  HTML rendered: {html_path}", flush=True)

    public_url = publish(html_path)
    print(f"  Published: {public_url}", flush=True)

    commit_seen(pending_seen)  # persist after successful publish, before email
    increment_issue(issue)

    send(public_url, issue_number=issue)
    print(f"  Email sent.", flush=True)
    print(f"\n=== Done ===", flush=True)


if __name__ == "__main__":
    run()
