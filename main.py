import json
import pathlib
from dotenv import load_dotenv
load_dotenv()

from fetchers.semantic_scholar import fetch_trending_papers
from fetchers.papers_with_code import fetch_trending as fetch_pwc
from fetchers.ssrn import fetch_top_papers
from fetchers.rss import fetch_rss_items
from fetchers.dedupe import filter_new
from scorer import score_all
from composer import compose
from renderer import render
from publisher import publish
from emailer import send
from feedback import get_recent_feedback

ISSUE_FILE = pathlib.Path("data/issue.json")


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
    print(f"\n=== Signal Issue #{issue} ===\n")

    print("Fetching sources...")
    candidates = (
        fetch_trending_papers() +
        fetch_pwc() +
        fetch_top_papers() +
        fetch_rss_items()
    )
    print(f"  Total candidates: {len(candidates)}")

    candidates = filter_new(candidates)
    print(f"  After dedupe: {len(candidates)}")

    feedback_ctx = get_recent_feedback(n=3)
    scored = score_all(candidates)

    brief = compose(scored, feedback_context=feedback_ctx)

    html_path = render(brief, issue_number=issue)
    print(f"  HTML rendered: {html_path}")

    public_url = publish(html_path)
    print(f"  Published: {public_url}")

    send(public_url, issue_number=issue)
    print(f"  Email sent.")

    increment_issue(issue)
    print(f"\n=== Done ===")


if __name__ == "__main__":
    run()
