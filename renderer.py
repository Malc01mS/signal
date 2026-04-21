from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from pathlib import Path


def render(brief: dict, issue_number: int = 1) -> str:
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("signal.html")
    html = template.render(
        brief=brief,
        date=datetime.now().strftime("%B %d, %Y"),
        issue=issue_number,
    )
    output_path = Path(f"output/signal-{datetime.now().strftime('%Y-%m-%d')}.html")
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return str(output_path)
