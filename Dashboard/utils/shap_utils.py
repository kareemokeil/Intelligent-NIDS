"""
utils/shap_utils.py
---------------------
Everything SHAP-related lives here. Pages call ONE function — `explain()`
— and get back a ready-to-render DataFrame, a ready-to-render Plotly
figure, and a top-features list for the report prompt. No page should
ever touch `shap.TreeExplainer` or build a SHAP chart itself.

Matches Kareem's real pipeline (5_LLM_Integration.ipynb):
  - features ending in "_log" are displayed WITHOUT the suffix
  - their observed value is inverse-transformed with expm1 to show the
    true original-scale number (not the log1p-transformed one)
"""

from dataclasses import dataclass
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


@dataclass
class ShapExplanation:
    shap_dataframe: pd.DataFrame   # Rank | Feature | Observed Value | SHAP Value | Direction | Contribution (%) | Impact
    shap_plot: go.Figure
    top_features: list             # list[str] of the top feature display names


def _display_name(feature: str) -> str:
    return feature[:-4] if feature.endswith("_log") else feature


def _observed_value(feature: str, raw_value: float) -> float:
    return float(np.expm1(raw_value)) if feature.endswith("_log") else float(raw_value)


@st.cache_resource
def get_explainer(_model):
    import shap
    return shap.TreeExplainer(_model)


def _compute_shap_dataframe(explainer, sample_z: pd.Series, sample_raw: pd.Series, pred_idx: int) -> pd.DataFrame:
    shap_values = explainer.shap_values(sample_z.values.reshape(1, -1))

    # Handles both legacy (list-per-class) and modern (3D array) shap outputs
    if isinstance(shap_values, list):
        class_shap = np.asarray(shap_values[pred_idx][0])
    elif shap_values.ndim == 3:
        class_shap = shap_values[0, :, pred_idx]
    else:
        class_shap = shap_values[0]

    df = pd.DataFrame({
        "Feature": [_display_name(f) for f in sample_z.index],
        "Observed Value": [_observed_value(f, sample_raw[f]) for f in sample_z.index],
        "SHAP Value": class_shap,
    })

    df["Direction"] = np.where(df["SHAP Value"] >= 0, "Positive", "Negative")

    total_abs = df["SHAP Value"].abs().sum()
    df["Contribution (%)"] = (df["SHAP Value"].abs() / total_abs * 100).round(1) if total_abs > 0 else 0.0

    df = df.sort_values("Contribution (%)", ascending=False).reset_index(drop=True)
    df.insert(0, "Rank", df.index + 1)

    def impact_label(rank):
        if rank <= 2:
            return "High"
        if rank <= 4:
            return "Medium"
        return "Low"

    df["Impact"] = df["Rank"].apply(impact_label)
    return df


def _build_shap_plot(shap_df: pd.DataFrame, n: int = 10) -> go.Figure:
    top = shap_df.head(n)
    fig = go.Figure(go.Bar(
        x=top["SHAP Value"], y=top["Feature"], orientation="h",
        marker=dict(color=["#EF4444" if v > 0 else "#3B82F6" for v in top["SHAP Value"]]),
        text=[f"{v:+.3f}" for v in top["SHAP Value"]], textposition="outside",
    ))
    fig.update_layout(
        height=380, margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="SHAP value (red = increases risk, blue = decreases risk)",
        yaxis=dict(autorange="reversed"), template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def explain(model, sample_z: pd.Series, sample_raw: pd.Series, pred_idx: int, top_n: int = 10) -> ShapExplanation:
    """
    The single entry point pages should use.

    Raises RuntimeError with a clear message on failure (caught by the
    calling page and shown via st.error, per the error-handling policy).
    """
    try:
        explainer = get_explainer(model)
        shap_df = _compute_shap_dataframe(explainer, sample_z, sample_raw, pred_idx)
        shap_plot = _build_shap_plot(shap_df, n=top_n)
        top_features = shap_df.head(5)["Feature"].tolist()
        return ShapExplanation(shap_dataframe=shap_df, shap_plot=shap_plot, top_features=top_features)
    except Exception as e:
        raise RuntimeError(f"SHAP explanation failed: {e}") from e

