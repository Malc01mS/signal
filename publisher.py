from github import Github
from pathlib import Path
from datetime import datetime
import os


def _build_index(issues: list[tuple[str, str]], base_url: str) -> str:
    """Generate an index.html listing all issues newest-first."""
    rows = ""
    for date_str, url in sorted(issues, reverse=True):
        try:
            label = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %-d, %Y")
        except Exception:
            label = date_str
        rows += f'      <li><a href="{url}">Signal — {label}</a></li>\n'

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


def publish(html_path: str) -> str:
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

    # Rebuild index.html from all docs/*.html files (excluding index itself)
    try:
        all_files = repo.get_contents("docs")
        issues = []
        for f in all_files:
            name = f.name
            if name == "index.html" or not name.endswith(".html"):
                continue
            stem = name[:-5]  # strip .html
            issues.append((stem, f"{base_url}/{name}"))

        index_html = _build_index(issues, base_url)
        try:
            existing_index = repo.get_contents("docs/index.html")
            repo.update_file("docs/index.html", "Update Signal index", index_html, existing_index.sha)
        except Exception:
            repo.create_file("docs/index.html", "Update Signal index", index_html)
    except Exception as e:
        print(f"  Warning: could not update index.html: {e}", flush=True)

    return f"{base_url}/{date_str}.html"
