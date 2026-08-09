"""
utils/artifacts_loader.py
--------------------------
Loads the trained model + supporting artifacts. File names match
Kareem's real exported files exactly:

    artifacts/rf_model.pkl
    artifacts/scaler.pkl
    artifacts/label_encoder.pkl
    artifacts/feature_names.pkl
    artifacts/X_test.pkl        (raw / human-readable features)
    artifacts/X_test_z.pkl      (scaled features — what the model predicts on)
    artifacts/y_test.pkl        (string labels)
    artifacts/y_test_encoded.pkl (encoded labels, match model raw output)
"""

from pathlib import Path
from dataclasses import dataclass
import joblib
import pandas as pd
import streamlit as st

ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "artifacts"

REQUIRED_FILES = [
    "rf_model.pkl", "scaler.pkl", "label_encoder.pkl", "feature_names.pkl",
    "X_test.pkl", "X_test_z.pkl", "y_test.pkl", "y_test_encoded.pkl",
]


@dataclass
class Artifacts:
    model: object
    scaler: object
    label_encoder: object
    feature_names: list
    X_test: pd.DataFrame
    X_test_z: pd.DataFrame
    y_test: object
    y_test_encoded: object
    class_names_ordered: list  # class names in model.classes_ order


def missing_files() -> list:
    return [f for f in REQUIRED_FILES if not (ARTIFACTS_DIR / f).exists()]


def get_feature_count():
    """Lightweight way to read the selected-feature count without loading
    the full model — used by UI copy (sidebar, About page, upload hints)
    so displayed numbers never drift from the real artifacts.
    Returns None if feature_names.pkl isn't present yet."""
    path = ARTIFACTS_DIR / "feature_names.pkl"
    if not path.exists():
        return None
    try:
        return len(joblib.load(path))
    except Exception:
        return None


@st.cache_resource
def load_artifacts() -> Artifacts:
    model = joblib.load(ARTIFACTS_DIR / "rf_model.pkl")
    scaler = joblib.load(ARTIFACTS_DIR / "scaler.pkl")
    label_encoder = joblib.load(ARTIFACTS_DIR / "label_encoder.pkl")
    feature_names = joblib.load(ARTIFACTS_DIR / "feature_names.pkl")
    X_test = joblib.load(ARTIFACTS_DIR / "X_test.pkl")
    X_test_z = joblib.load(ARTIFACTS_DIR / "X_test_z.pkl")
    y_test = joblib.load(ARTIFACTS_DIR / "y_test.pkl")
    y_test_encoded = joblib.load(ARTIFACTS_DIR / "y_test_encoded.pkl")
    class_names_ordered = list(label_encoder.inverse_transform(model.classes_))

    return Artifacts(model, scaler, label_encoder, feature_names,
                      X_test, X_test_z, y_test, y_test_encoded, class_names_ordered)


def require_artifacts_or_stop():
    """Call at the top of any page that needs the model. Shows a friendly
    setup message and halts the page if artifacts aren't present yet."""
    missing = missing_files()
    if missing:
        st.warning(
            "**Setup needed** — the following files are missing from `artifacts/`:\n\n"
            + "\n".join(f"- `{f}`" for f in missing)
            + "\n\nExport them from your training notebook (see README.md), "
              "then reload this page."
        )
        st.stop()
    return load_artifacts()
