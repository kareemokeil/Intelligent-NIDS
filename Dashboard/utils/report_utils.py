"""
utils/report_utils.py
-----------------------
Orchestrates: call your real report_generator.generate_report(...),
persist every generated report to reports/history.json + a .md file
on disk, and export a simple PDF version.
"""

from pathlib import Path
from datetime import datetime
import json
import uuid
import streamlit as st

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
HISTORY_FILE = REPORTS_DIR / "history.json"


def _ensure_dirs():
    REPORTS_DIR.mkdir(exist_ok=True)
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")


def new_report_id() -> str:
    return f"IR-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"


def call_report_pipeline(sample, predicted_class, confidence, shap_df, retrieved_docs):
    """
    Single integration point with your real pipeline. Import is done
    lazily so the rest of the dashboard still works even before
    report_generator.py is filled in with your Gemini + FAISS code.
    """
    try:
        from report_generator import generate_report
        return generate_report(sample, predicted_class, confidence, shap_df, retrieved_docs)
    except (ImportError, NotImplementedError) as e:
        st.error(
            "Report pipeline isn't wired up yet — see `report_generator.py`. "
            f"({e})"
        )
        return None


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


_UNICODE_REPLACEMENTS = {
    "\u2022": "-", "\u2013": "-", "\u2014": "-",   # •, –, —
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2192": "->", "\u2190": "<-", "\u2248": "~", "\u00b0": " deg",
}


def _sanitize_for_pdf(text: str) -> str:
    for src, dst in _UNICODE_REPLACEMENTS.items():
        text = text.replace(src, dst)
    # Anything else outside latin-1 (e.g. Arabic, emoji) becomes '?' rather than crashing
    return text.encode("latin-1", errors="replace").decode("latin-1")


def markdown_to_pdf_bytes(report_md: str) -> bytes:
    """Lightweight Markdown -> PDF export (headings + body text). For a
    pixel-perfect PDF you may prefer exporting the report as HTML and
    printing it, but this keeps the dependency footprint small.

    Raises ImportError if `fpdf2` isn't installed — the caller (Detection
    page) catches this and disables the Download PDF button gracefully
    instead of crashing the whole app.
    """
    from fpdf import FPDF  # lazy import: keeps fpdf2 an optional dependency

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    for raw_line in report_md.split("\n"):
        line = _sanitize_for_pdf(raw_line.rstrip())
        pdf.set_x(pdf.l_margin)  # guard against fpdf2's auto-page-break cursor edge case
        if line.startswith("### "):
            pdf.set_font("Helvetica", "B", 12)
            pdf.multi_cell(pdf.epw, 7, line[4:])
        elif line.startswith("## "):
            pdf.set_font("Helvetica", "B", 14)
            pdf.multi_cell(pdf.epw, 8, line[3:])
        elif line.startswith("# "):
            pdf.set_font("Helvetica", "B", 16)
            pdf.multi_cell(pdf.epw, 9, line[2:])
        elif line.startswith("- ") or line.startswith("* "):
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(pdf.epw, 6, f"  - {line[2:]}")
        elif line == "":
            pdf.ln(2)
        else:
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(pdf.epw, 6, line)

    return bytes(pdf.output(dest="S"))
