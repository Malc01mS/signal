import json
from pathlib import Path
from datetime import datetime

LOG_PATH = Path("data/feedback_log.json")


def append_feedback(text: str, issue_date: str = None):
    log = []
    if LOG_PATH.exists():
        log = json.loads(LOG_PATH.read_text())
    log.append({
        "date": issue_date or datetime.now().strftime("%Y-%m-%d"),
        "feedback": text.strip(),
    })
    LOG_PATH.parent.mkdir(exist_ok=True)
    LOG_PATH.write_text(json.dumps(log, indent=2))


def get_recent_feedback(n: int = 3) -> str:
    if not LOG_PATH.exists():
        return ""
    log = json.loads(LOG_PATH.read_text())
    recent = log[-n:]
    return "\n".join(f"[{e['date']}] {e['feedback']}" for e in recent)
