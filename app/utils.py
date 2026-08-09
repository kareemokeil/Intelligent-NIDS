from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "Data"
MODELS_DIR = ROOT_DIR / "models"
REPORTS_DIR = ROOT_DIR / "reports"


def get_project_paths():
    return {
        "root": ROOT_DIR,
        "data": DATA_DIR,
        "models": MODELS_DIR,
        "reports": REPORTS_DIR,
    }
