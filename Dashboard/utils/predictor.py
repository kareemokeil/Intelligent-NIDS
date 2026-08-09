"""
utils/predictor.py
--------------------
Single source of truth for turning model output into human-readable
predictions. Nothing in pages/*.py should call `model.predict_proba`,
`label_encoder.inverse_transform`, or `np.argmax` directly — everything
goes through this module.
"""

from dataclasses import dataclass
import numpy as np
import pandas as pd
import streamlit as st


@dataclass
class Prediction:
    label: str
    confidence: float                 # 0..1
    probabilities: pd.Series          # index = class name, values = probability


def predict(model, label_encoder, class_names_ordered, sample_z: pd.Series) -> Prediction:
    """Predict a single sample. `sample_z` must already be scaled
    (same transform used during training)."""
    try:
        proba = model.predict_proba(sample_z.values.reshape(1, -1))[0]
    except Exception as e:
        raise RuntimeError(f"Model prediction failed: {e}") from e

    pred_idx = int(np.argmax(proba))
    label = class_names_ordered[pred_idx]
    confidence = float(proba[pred_idx])
    probabilities = pd.Series(proba, index=class_names_ordered)
    return Prediction(label=label, confidence=confidence, probabilities=probabilities)


@st.cache_data(show_spinner=False)
def predict_test_set(_model, _label_encoder, X_test_z_values: np.ndarray, index_key: str) -> np.ndarray:
    """
    Predicts the ENTIRE test set once and caches the result — used by the
    Model Performance and Analytics pages so the full-dataset prediction
    only ever runs once per session instead of on every rerun.

    `index_key` is a cheap cache-busting fingerprint (e.g. str(X_test.shape))
    since numpy arrays aren't hashable inputs for st.cache_data on their own
    when passed as leading args prefixed with "_" (which skips hashing).
    """
    try:
        return _model.predict(X_test_z_values)
    except Exception as e:
        raise RuntimeError(f"Batch prediction on the test set failed: {e}") from e


@st.cache_data(show_spinner=False)
def predict_proba_test_set(_model, X_test_z_values: np.ndarray, index_key: str) -> np.ndarray:
    """Same idea as predict_test_set, but returns class probabilities
    (needed for ROC curves and confidence-distribution analytics)."""
    try:
        return _model.predict_proba(X_test_z_values)
    except Exception as e:
        raise RuntimeError(f"Batch probability prediction failed: {e}") from e


def decode_labels(label_encoder, encoded: np.ndarray) -> np.ndarray:
    return label_encoder.inverse_transform(encoded)
