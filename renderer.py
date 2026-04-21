from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"
OUTPUT_DIR = Path(__file__).parent / "output"


def render(brief: dict, issue_number: int = 1) -> str:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("signal.html")
    html = template.render(
        brief=brief,
        date=datetime.now().strftime("%B %d, %Y"),
        issue=issue_number,
    )
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / f"signal-{datetime.now().strftime('%Y-%m-%d')}.html"
    output_path.write_text(html, encoding="utf-8")
    return str(output_path)
