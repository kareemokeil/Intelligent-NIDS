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

import os
from pathlib import Path
from dataclasses import dataclass
import joblib
import pandas as pd
import streamlit as st
from huggingface_hub import hf_hub_download

ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "artifacts"
MODEL_REPO = os.getenv("HF_MODEL_REPO", "KareemOkeil/nids-artifacts")

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


def ensure_artifacts():
    """Auto-downloads missing required artifacts from Hugging Face Model Hub if missing locally."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    missing = [f for f in REQUIRED_FILES if not (ARTIFACTS_DIR / f).exists()]
    if missing:
        with st.spinner("Downloading model artifacts from Hugging Face Hub... Please wait..."):
            for fname in missing:
                try:
                    hf_hub_download(repo_id=MODEL_REPO, filename=fname, local_dir=str(ARTIFACTS_DIR))
                except Exception as e:
                    st.error(f"Failed to download {fname} from Hugging Face ({MODEL_REPO}): {e}")


def missing_files() -> list:
    ensure_artifacts()
    return [f for f in REQUIRED_FILES if not (ARTIFACTS_DIR / f).exists()]



def get_feature_count():
    """Lightweight way to read the selected-feature count without loading
    the full model — used by UI copy (sidebar, About page, upload hints)
    so displayed numbers never drift from the real artifacts.
    Returns None if feature_names.pkl isn't present yet."""
    path = ARTIFACTS_DIR / "feature_names.pkl"
    if not path.exists():
        try:
            ensure_artifacts()
        except Exception:
            return None
    try:
        return len(joblib.load(path))
    except Exception:
        return None


@st.cache_resource
def load_artifacts() -> Artifacts:
    ensure_artifacts()
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
    """Call at the top of any page that needs the model. Auto-downloads from HF if missing."""
    ensure_artifacts()
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

