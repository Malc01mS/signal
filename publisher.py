from github import Github
from pathlib import Path
from datetime import datetime
import os


def publish(html_path: str) -> str:
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo(os.environ["GITHUB_REPO"])

    date_str = datetime.now().strftime("%Y-%m-%d")
    file_path = f"docs/{date_str}.html"
    content = Path(html_path).read_text(encoding="utf-8")

    try:
        existing = repo.get_contents(file_path)
        repo.update_file(file_path, f"Signal {date_str}", content, existing.sha)
    except Exception:
        repo.create_file(file_path, f"Signal {date_str}", content)

    base_url = os.environ["GITHUB_PAGES_URL"].rstrip("/")
    return f"{base_url}/{date_str}.html"
