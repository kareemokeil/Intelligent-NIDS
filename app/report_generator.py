from pathlib import Path


def generate_report(summary: str, output_path: str | None = None) -> str:
    output = Path(output_path or "reports/incidents/report.txt")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(summary, encoding="utf-8")
    return str(output)
