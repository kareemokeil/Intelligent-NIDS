"""
=====================================================================
 Intelligent Network Intrusion Detection System (NIDS) — Dashboard
 Graduation Project — CIC-IDS2017 / Random Forest / SHAP / RAG Reports
=====================================================================

HOW TO RUN
----------
    pip install -r requirements.txt
    streamlit run app.py

WHAT YOU NEED TO PLUG IN (search for "TODO" in this file)
-----------------------------------------------------------
1. artifacts/rf_model.pkl        -> your trained Random Forest model
2. artifacts/X_test.pkl          -> test-set features (DataFrame, 16 selected features)
3. artifacts/y_test.pkl          -> test-set true labels (Series/array, string class names)
4. artifacts/feature_names.pkl   -> list of the 16 final feature names (optional,
                                     inferred from X_test.columns if not provided)
5. report_generator.py           -> YOUR existing LLM + SHAP + RAG report pipeline.
                                     This file expects a function:

                                         generate_report(sample: pd.Series,
                                                          predicted_class: str,
                                                          confidence: float,
                                                          shap_contributions: dict) -> str

                                     that returns the final incident report as a
                                     Markdown string (same style as your
                                     IR-20260723-054821 example). Import it below.

Everything else (sample picker, prediction, SHAP plot, report rendering,
download button) is ready to go.
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import shap
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# TODO: uncomment this once report_generator.py (your real pipeline) is in the same folder
# from report_generator import generate_report

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Intelligent NIDS Dashboard",
    page_icon="🛡️",
    layout="wide",
)

ARTIFACTS_DIR = Path("artifacts")

CLASS_NAMES = [
    "BENIGN", "DoS", "DDoS", "PortScan",
    "Brute Force", "Web Attack", "Bot", "Rare Attack",
]

# ---------------------------------------------------------------------------
# Cached loaders — swap paths for your real files
# ---------------------------------------------------------------------------
@st.cache_resource
def load_model():
    # TODO: point to your actual saved Random Forest model
    return joblib.load(ARTIFACTS_DIR / "rf_model.pkl")


@st.cache_resource
def load_test_data():
    # TODO: point to your actual saved test set (post feature-selection, 16 features)
    X_test = joblib.load(ARTIFACTS_DIR / "X_test.pkl")
    y_test = joblib.load(ARTIFACTS_DIR / "y_test.pkl")
    return X_test, y_test


@st.cache_resource
def load_shap_explainer(_model):
    return shap.TreeExplainer(_model)


def safe_load():
    """Load artifacts and show a friendly setup message if they're missing."""
    try:
        model = load_model()
        X_test, y_test = load_test_data()
        explainer = load_shap_explainer(model)
        return model, X_test, y_test, explainer, None
    except FileNotFoundError as e:
        return None, None, None, None, str(e)


# ---------------------------------------------------------------------------
# Placeholder report generator (used ONLY until you wire in your real one)
# ---------------------------------------------------------------------------
def generate_report_placeholder(sample, predicted_class, confidence, shap_contributions):
    """
    TODO: DELETE this function once you import your real `generate_report`
    from report_generator.py above. This placeholder just formats SHAP values
    into a simple Markdown report so the dashboard is demo-able immediately.
    """
    top_features = sorted(shap_contributions.items(), key=lambda x: -abs(x[1]))[:5]
    report_id = f"IR-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    lines = [
        f"# Cybersecurity Incident Report: {report_id}",
        "",
        "## 1. Executive Summary",
        f"The Random Forest model classified this flow as **{predicted_class}** "
        f"with **{confidence*100:.2f}%** confidence.",
        "",
        "## 2. Attack Characteristics",
        f"- **Predicted Class:** {predicted_class}",
        f"- **Confidence:** {confidence*100:.2f}%",
        "- **Model:** Random Forest (CIC-IDS2017)",
        "",
        "## 3. Explainable AI Analysis (SHAP — Top Contributing Features)",
    ]
    for feat, val in top_features:
        lines.append(f"- **{feat}** (value: {sample[feat]:.4f}, SHAP: {val:+.4f})")

    lines += [
        "",
        "## 4. SOC Analyst Note",
        "⚠️ This is a placeholder report. Replace `generate_report_placeholder` "
        "with your real LLM + RAG pipeline in `report_generator.py`.",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🛡️ Intelligent Network Intrusion Detection System")
st.caption("CIC-IDS2017 · Random Forest · SHAP Explainability · AI-Generated Incident Reports")

model, X_test, y_test, explainer, load_error = safe_load()

if load_error:
    st.warning(
        "**Setup needed** — couldn't find your model/test artifacts.\n\n"
        f"Missing: `{load_error}`\n\n"
        "Create an `artifacts/` folder next to `app.py` containing:\n"
        "- `rf_model.pkl`\n- `X_test.pkl`\n- `y_test.pkl`\n\n"
        "The dashboard UI below is fully built — it will activate as soon as "
        "these files are present."
    )
    st.stop()

tab_detect, tab_perf, tab_about = st.tabs(["🔍 Detection", "📊 Model Performance", "ℹ️ About"])

# ---------------------------------------------------------------------------
# TAB 1 — Detection (pick a test-set sample, classify, explain, report)
# ---------------------------------------------------------------------------
with tab_detect:
    st.subheader("Select a network flow from the test set")

    col_filter, col_pick = st.columns([1, 1])
    with col_filter:
        label_filter = st.selectbox(
            "Filter by true label (optional)",
            options=["All"] + sorted(pd.Series(y_test).unique().tolist()),
        )
    with col_pick:
        if label_filter == "All":
            candidate_idx = X_test.index.tolist()
        else:
            candidate_idx = X_test.index[pd.Series(y_test, index=X_test.index) == label_filter].tolist()

        if len(candidate_idx) == 0:
            st.error("No samples match that filter.")
            st.stop()

        pick_mode = st.radio("Pick sample by", ["Index", "Random"], horizontal=True)
        if pick_mode == "Random":
            if st.button("🎲 Draw random sample"):
                st.session_state["sample_idx"] = np.random.choice(candidate_idx)
            sample_idx = st.session_state.get("sample_idx", candidate_idx[0])
        else:
            sample_idx = st.selectbox("Sample index", candidate_idx)
            st.session_state["sample_idx"] = sample_idx

    sample = X_test.loc[sample_idx]
    true_label = pd.Series(y_test, index=X_test.index).loc[sample_idx]

    st.divider()
    left, right = st.columns([1, 1])

    with left:
        st.markdown("**Flow features**")
        st.dataframe(sample.to_frame(name="value"), height=380)
        st.markdown(f"**True label (ground truth):** `{true_label}`")

    with right:
        st.markdown("**Prediction**")
        proba = model.predict_proba(sample.values.reshape(1, -1))[0]
        pred_idx = int(np.argmax(proba))
        pred_class = model.classes_[pred_idx]
        confidence = float(proba[pred_idx])

        badge_color = "green" if pred_class == "BENIGN" else "red"
        st.markdown(
            f"### :{badge_color}[{pred_class}] — {confidence*100:.2f}% confidence"
        )

        proba_df = pd.DataFrame({"class": model.classes_, "probability": proba}).sort_values(
            "probability", ascending=False
        )
        st.bar_chart(proba_df.set_index("class"))

        if pred_class != true_label:
            st.error(f"⚠️ Misclassified — true label is `{true_label}`")

    st.divider()
    st.markdown("**SHAP Explanation**")

    shap_values = explainer.shap_values(sample.values.reshape(1, -1))
    # shap_values shape handling for multi-class TreeExplainer
    if isinstance(shap_values, list):
        class_shap = shap_values[pred_idx][0]
    else:
        class_shap = shap_values[0, :, pred_idx] if shap_values.ndim == 3 else shap_values[0]

    shap_contributions = dict(zip(sample.index, class_shap))
    shap_sorted = sorted(shap_contributions.items(), key=lambda x: abs(x[1]), reverse=True)

    fig, ax = plt.subplots(figsize=(7, 4))
    feats, vals = zip(*shap_sorted[:8])
    colors = ["#d62728" if v > 0 else "#1f77b4" for v in vals]
    ax.barh(feats[::-1], vals[::-1], color=colors[::-1])
    ax.set_xlabel("SHAP value (impact on prediction)")
    ax.set_title(f"Top features driving '{pred_class}' classification")
    st.pyplot(fig)

    st.divider()
    st.markdown("**AI-Generated Incident Report**")

    if st.button("📝 Generate Incident Report", type="primary"):
        with st.spinner("Generating report..."):
            # TODO: swap this for your real pipeline:
            # report_md = generate_report(sample, pred_class, confidence, shap_contributions)
            report_md = generate_report_placeholder(sample, pred_class, confidence, shap_contributions)
        st.session_state["last_report"] = report_md

    if "last_report" in st.session_state:
        st.markdown(st.session_state["last_report"])
        st.download_button(
            "⬇️ Download report (.md)",
            data=st.session_state["last_report"],
            file_name=f"incident_report_{sample_idx}.md",
            mime="text/markdown",
        )

# ---------------------------------------------------------------------------
# TAB 2 — Model performance (confusion matrix + metrics)
# ---------------------------------------------------------------------------
with tab_perf:
    st.subheader("Model performance on the full test set")
    st.caption("Computed live from your loaded model and X_test / y_test.")

    from sklearn.metrics import classification_report, confusion_matrix, matthews_corrcoef

    y_pred_all = model.predict(X_test.values)
    report_dict = classification_report(y_test, y_pred_all, output_dict=True)
    report_df = pd.DataFrame(report_dict).transpose().round(4)
    st.dataframe(report_df, height=350)

    mcc = matthews_corrcoef(y_test, y_pred_all)
    st.metric("Matthews Correlation Coefficient (MCC)", f"{mcc:.4f}")

    cm = confusion_matrix(y_test, y_pred_all, labels=model.classes_)
    fig2, ax2 = plt.subplots(figsize=(7, 6))
    im = ax2.imshow(cm, cmap="Blues")
    ax2.set_xticks(range(len(model.classes_)))
    ax2.set_yticks(range(len(model.classes_)))
    ax2.set_xticklabels(model.classes_, rotation=45, ha="right")
    ax2.set_yticklabels(model.classes_)
    ax2.set_xlabel("Predicted")
    ax2.set_ylabel("True")
    for i in range(len(model.classes_)):
        for j in range(len(model.classes_)):
            ax2.text(j, i, cm[i, j], ha="center", va="center", fontsize=8)
    fig2.colorbar(im)
    st.pyplot(fig2)

# ---------------------------------------------------------------------------
# TAB 3 — About
# ---------------------------------------------------------------------------
with tab_about:
    st.markdown(
        """
        ### Project Summary
        - **Dataset:** CIC-IDS2017 (~2.5M records, 79 raw features, merged daily CSVs)
        - **Preprocessing:** infinity handling, ~11.69% duplicate removal, correlated
          feature drop (≥0.99), zero-variance column drop, log1p on skewed features
        - **Feature selection:** XGBoost-assisted → 16 final features
        - **Split:** 75 / 10 / 15 (Train / Val / Test), stratified
        - **Classes (8):** BENIGN, DoS, DDoS, PortScan, Brute Force, Web Attack, Bot, Rare Attack
        - **Imbalance handling:** custom class weights (SMOTE hit MemoryError)
        - **Final model:** Random Forest — Accuracy ≈ 0.9916, Macro F1 ≈ 0.8244, MCC ≈ 0.9724
        - **Known limitation:** weaker recall on Bot and Rare Attack classes
        - **Explainability:** SHAP
        - **Reporting:** LLM + FAISS RAG-based incident report generation
        """
    )