import json
import hashlib
from pathlib import Path

STORE_PATH = Path(__file__).parent.parent / "data" / "seen_items.json"


def load_seen() -> set:
    if STORE_PATH.exists():
        return set(json.loads(STORE_PATH.read_text()))
    return set()


def save_seen(seen: set):
    STORE_PATH.parent.mkdir(exist_ok=True)
    STORE_PATH.write_text(json.dumps(list(seen)))


def item_hash(item: dict) -> str:
    key = (item.get("title", "") + item.get("url", "")).lower()
    return hashlib.md5(key.encode()).hexdigest()


def filter_new(items: list[dict]) -> tuple[list[dict], set]:
    """Return (new_items, hashes_to_commit).
    Caller must call commit_seen() after a successful publish to persist."""
    seen = load_seen()
    new_items = [i for i in items if item_hash(i) not in seen]
    pending = {item_hash(i) for i in new_items}
    return new_items, pending


def commit_seen(pending: set):
    """Persist new item hashes only after a successful run."""
    seen = load_seen()
    seen.update(pending)
    save_seen(seen)
