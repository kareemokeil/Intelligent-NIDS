"""
utils/pdf_generator.py
-------------------------
Single responsibility: Markdown -> PDF export for incident reports.
Split out from history/report orchestration so PDF rendering concerns
never mix with persistence concerns.
"""

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

    Raises ImportError if `fpdf2` isn't installed — the caller catches
    this and disables the Download PDF button gracefully instead of
    crashing the whole app.
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
