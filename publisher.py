from github import Github
from pathlib import Path
from datetime import datetime
import json
import os


MANIFEST_PATH = "docs/manifest.json"


def _load_manifest(repo) -> dict:
    """Load {date_str: issue_number} manifest from the repo, or return empty dict."""
    try:
        f = repo.get_contents(MANIFEST_PATH)
        return json.loads(f.decoded_content.decode("utf-8"))
    except Exception:
        return {}


def _save_manifest(repo, manifest: dict) -> None:
    data = json.dumps(manifest, sort_keys=True, indent=2)
    try:
        existing = repo.get_contents(MANIFEST_PATH)
        repo.update_file(MANIFEST_PATH, "Update Signal manifest", data, existing.sha)
    except Exception:
        repo.create_file(MANIFEST_PATH, "Create Signal manifest", data)


def _build_index(manifest: dict, base_url: str) -> str:
    """Generate index.html from {date_str: issue_number} manifest, newest first."""
    rows = ""
    for date_str, issue_number in sorted(manifest.items(), reverse=True):
        try:
            label = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %-d, %Y")
        except Exception:
            label = date_str
        url = f"{base_url}/{date_str}.html"
        rows += f'      <li><a href="{url}">Issue #{issue_number} &mdash; {label}</a></li>\n'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Signal</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #0a0a0a; color: #d8d8d8;
      font-family: 'Space Grotesk', sans-serif;
      padding: 64px 24px;
    }}
    .container {{ max-width: 560px; margin: 0 auto; }}
    h1 {{
      font-size: 3rem; font-weight: 700; letter-spacing: 0.18em;
      text-transform: uppercase; color: #d8d8d8; margin-bottom: 8px;
    }}
    .rule {{ height: 1px; background: #c9a84c; margin-bottom: 40px; }}
    ul {{ list-style: none; }}
    li {{ border-bottom: 1px solid #1a1a1a; padding: 16px 0; }}
    a {{
      color: #c9a84c; text-decoration: none;
      font-size: 0.95rem; letter-spacing: 0.04em;
    }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
<div class="container">
  <h1>Signal</h1>
  <div class="rule"></div>
  <ul>
{rows}  </ul>
</div>
</body>
</html>"""


def publish(html_path: str, issue_number: int = None) -> str:
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo(os.environ["GITHUB_REPO"])
    base_url = os.environ["GITHUB_PAGES_URL"].rstrip("/")

    date_str = datetime.now().strftime("%Y-%m-%d")
    file_path = f"docs/{date_str}.html"
    content = Path(html_path).read_text(encoding="utf-8")

    # Push the issue HTML
    try:
        existing = repo.get_contents(file_path)
        repo.update_file(file_path, f"Signal {date_str}", content, existing.sha)
    except Exception:
        repo.create_file(file_path, f"Signal {date_str}", content)

    # Update manifest and rebuild index
    try:
        manifest = _load_manifest(repo)
        if issue_number is not None:
            manifest[date_str] = issue_number
        _save_manifest(repo, manifest)

        index_html = _build_index(manifest, base_url)
        try:
            existing_index = repo.get_contents("docs/index.html")
            repo.update_file("docs/index.html", "Update Signal index", index_html, existing_index.sha)
        except Exception:
            repo.create_file("docs/index.html", "Update Signal index", index_html)
    except Exception as e:
        print(f"  Warning: could not update index: {e}", flush=True)

    return f"{base_url}/{date_str}.html"
