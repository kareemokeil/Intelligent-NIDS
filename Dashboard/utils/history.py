"""
utils/history.py
-------------------
Single responsibility: persist and retrieve generated incident reports.
Every report the dashboard generates is saved as a .md file in reports/
plus an entry in reports/history.json.
"""

from pathlib import Path
from datetime import datetime
import json
import uuid

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
HISTORY_FILE = REPORTS_DIR / "history.json"


def _ensure_dirs():
    REPORTS_DIR.mkdir(exist_ok=True)
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")


def new_report_id() -> str:
    return f"IR-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"


def save_report(report_md: str, predicted_class: str, confidence: float) -> dict:
    _ensure_dirs()
    report_id = new_report_id()
    md_path = REPORTS_DIR / f"{report_id}.md"
    md_path.write_text(report_md, encoding="utf-8")

    record = {
        "id": report_id,
        "attack": predicted_class,
        "confidence": round(confidence * 100, 2),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "md_path": str(md_path),
    }

    history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    history.insert(0, record)
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")
    return record


def load_history() -> list:
    _ensure_dirs()
    return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
