"""
pages/1_Detection.py
======================
UI ONLY. No business logic lives here -- everything is delegated to:

    utils.predictor          -> predict(...)
    utils.shap_utils         -> explain(...)
    utils.rag                -> retrieve_context(...)
    utils.report_generator   -> generate_report(...)
    utils.history            -> save_report(...)
    utils.pdf_generator      -> markdown_to_pdf_bytes(...)

Pipeline (clean architecture): UI -> Predictor -> SHAP -> RAG -> Report Generator -> Gemini
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.theme import apply_theme, render_sidebar, metric_card, risk_badge, risk_level_for, panel_start, panel_end
from utils.artifacts_loader import require_artifacts_or_stop
from utils.predictor import predict
from utils.shap_utils import explain
from utils.rag import retrieve_context, rag_is_configured
from utils.report_generator import generate_report
from utils.history import save_report
from utils.pdf_generator import markdown_to_pdf_bytes

st.set_page_config(page_title="Detection — NIDS", page_icon="🔍", layout="wide")
apply_theme()
render_sidebar(active="Detection")

st.title("🔍 Detection")

art = require_artifacts_or_stop()

# ---------------------------------------------------------------------------
# 1. Input: test-set sample OR uploaded CSV
# ---------------------------------------------------------------------------
st.subheader("1 · Select Input")
mode = st.radio("Input source", ["Choose sample from Test Set", "Upload CSV"], horizontal=True)

sample_raw = None
sample_z = None
true_label = None

if mode == "Choose sample from Test Set":
    col1, col2 = st.columns(2)
    with col1:
        label_filter = st.selectbox("Filter by true label (optional)",
                                     ["All"] + sorted(pd.Series(art.y_test).unique().tolist()))
    candidate_idx = (art.X_test.index.tolist() if label_filter == "All"
                     else art.X_test.index[pd.Series(art.y_test, index=art.X_test.index) == label_filter].tolist())
    with col2:
        pick_mode = st.radio("Pick by", ["Index", "Random"], horizontal=True)

    if pick_mode == "Random":
        if st.button("🎲 Draw random sample"):
            st.session_state["sample_idx"] = np.random.choice(candidate_idx)
        sample_idx = st.session_state.get("sample_idx", candidate_idx[0])
    else:
        sample_idx = st.selectbox("Sample index", candidate_idx)
        st.session_state["sample_idx"] = sample_idx

    sample_raw = art.X_test.loc[sample_idx]
    sample_z = art.X_test_z.loc[sample_idx]
    true_label = pd.Series(art.y_test, index=art.X_test.index).loc[sample_idx]

else:
    uploaded = st.file_uploader(
        f"Upload a CSV with the {len(art.feature_names)} required feature columns", type=["csv"]
    )
    if uploaded is not None:
        df_upload = pd.read_csv(uploaded)
        missing_cols = [c for c in art.feature_names if c not in df_upload.columns]
        unexpected_cols = [c for c in df_upload.columns if c not in art.feature_names and c != "Label"]
        if missing_cols:
            msg = f"Model expects {len(art.feature_names)} features, but {len(missing_cols)} are missing from the CSV.\n\n**Missing:** {missing_cols}"
            if unexpected_cols:
                msg += f"\n\n**Unexpected columns found (ignored):** {unexpected_cols}"
            st.error(msg)
            st.stop()
        row_idx = st.number_input("Row to analyze", min_value=0, max_value=len(df_upload) - 1, value=0)
        sample_raw = df_upload.iloc[row_idx][art.feature_names]
        sample_z = pd.Series(
            art.scaler.transform(sample_raw.values.reshape(1, -1))[0],
            index=art.feature_names,
        )
        if "Label" in df_upload.columns:
            true_label = df_upload.iloc[row_idx]["Label"]
    else:
        st.info("Upload a CSV to continue, or switch to test-set mode above.")
        st.stop()

# ---------------------------------------------------------------------------
# Run the pipeline: Predictor -> SHAP  (RAG + Report happen later, on demand)
# ---------------------------------------------------------------------------
try:
    with st.spinner("Running Random Forest prediction..."):
        result = predict(art.model, art.label_encoder, art.class_names_ordered, sample_z)
except RuntimeError as e:
    st.error(f"⚠️ {e}")
    st.stop()

pred_class, confidence = result.label, result.confidence
risk = risk_level_for(pred_class, confidence)
pred_idx = art.class_names_ordered.index(pred_class)

try:
    with st.spinner("Computing SHAP explanation..."):
        shap_result = explain(art.model, sample_z, sample_raw, pred_idx)
except RuntimeError as e:
    st.error(f"⚠️ {e}")
    st.stop()

shap_df, shap_fig = shap_result.shap_dataframe, shap_result.shap_plot

# ---------------------------------------------------------------------------
# Tabs: Prediction | SHAP Explainability | Retrieved Knowledge | AI Report
# ---------------------------------------------------------------------------
tab_pred, tab_shap, tab_rag, tab_report = st.tabs(
    ["🎯 Prediction", "🧠 SHAP Explainability", "📚 Retrieved Knowledge", "📝 AI Incident Report"]
)

# --- Tab 1: Prediction -------------------------------------------------------
with tab_pred:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("🧾", "Ground Truth", str(true_label) if true_label is not None else "N/A",
                    "From dataset label" if true_label is not None else "Not provided in upload")
    with c2:
        metric_card("🎯", "Predicted Attack", pred_class, "Random Forest output")
    with c3:
        metric_card("📶", "Confidence", f"{confidence*100:.2f}%", "Softmax-style probability")
    with c4:
        st.markdown(
            f'<div class="soc-card"><div class="icon">⚠️</div><div class="label">Risk Level</div>'
            f'<div class="value">{risk_badge(risk)}</div><div class="sub">Class + confidence heuristic</div></div>',
            unsafe_allow_html=True,
        )

    if true_label is not None and pred_class != true_label:
        st.error(f"⚠️ Misclassified — true label is `{true_label}`")

    st.markdown("**Prediction Probability**")
    proba_df = result.probabilities.sort_values(ascending=False).reset_index()
    proba_df.columns = ["class", "probability"]
    fig_proba = go.Figure(go.Bar(
        x=proba_df["probability"], y=proba_df["class"], orientation="h",
        marker=dict(color=proba_df["probability"], colorscale="Blues"),
        text=[f"{p*100:.1f}%" for p in proba_df["probability"]], textposition="outside",
    ))
    fig_proba.update_layout(
        height=320, margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Probability", yaxis_title="", template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_proba, width="stretch")

# --- Tab 2: SHAP Explainability ---------------------------------------------
with tab_shap:
    st.plotly_chart(shap_fig, width="stretch")

    st.markdown("**Feature Contribution Table**")

    def _style_shap(val):
        if isinstance(val, (int, float)):
            color = "#F87171" if val > 0 else ("#60A5FA" if val < 0 else "#9CA3AF")
            return f"color: {color}; font-weight: 600;"
        return ""

    st.dataframe(shap_df.style.map(_style_shap, subset=["SHAP Value"]), width="stretch", height=380)

    with st.expander("🔎 Feature Explorer (searchable)", expanded=False):
        search = st.text_input("Search feature name", "")
        explorer_df = shap_df[["Feature", "Observed Value", "SHAP Value"]]
        if search:
            explorer_df = explorer_df[explorer_df["Feature"].str.contains(search, case=False)]
        st.dataframe(explorer_df, width="stretch", height=350)

# --- Tab 3: Retrieved Knowledge ----------------------------------------------
with tab_rag:
    if not rag_is_configured():
        st.info(
            "FAISS knowledge base not configured yet. Copy your `faiss_index/` folder "
            "into `artifacts/faiss_index/` — see `utils/rag.py` for the exact format."
        )
    else:
        try:
            with st.spinner("Retrieving supporting knowledge-base documents..."):
                retrieved_docs = retrieve_context(pred_class)
        except RuntimeError as e:
            st.error(f"⚠️ {e}")
            retrieved_docs = []

        if not retrieved_docs:
            st.info("No matching documents retrieved for this prediction.")
        for doc in retrieved_docs:
            with st.expander(f"📄 {doc['title']}  ·  similarity {doc['score']:.3f}"):
                st.write(doc["content"])

# --- Tab 4: AI Incident Report ------------------------------------------------
with tab_report:
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
    with btn_col1:
        generate_clicked = st.button("📝 Generate Report", type="primary", width="stretch")

    if generate_clicked:
        try:
            with st.spinner("Generating AI incident report (SHAP + RAG + Gemini)..."):
                report_md = generate_report(sample_raw, pred_class, confidence, shap_df)
            st.session_state["last_report"] = report_md
            st.session_state["last_report_meta"] = save_report(report_md, pred_class, confidence)
        except RuntimeError as e:
            st.error(f"⚠️ Report generation failed: {e}")

    if "last_report" in st.session_state:
        report_md = st.session_state["last_report"]

        with btn_col2:
            st.download_button("⬇️ Download .md", data=report_md,
                                file_name=f"{st.session_state['last_report_meta']['id']}.md",
                                mime="text/markdown", width="stretch")
        with btn_col3:
            try:
                pdf_bytes = markdown_to_pdf_bytes(report_md)
                st.download_button("⬇️ Download .pdf", data=pdf_bytes,
                                    file_name=f"{st.session_state['last_report_meta']['id']}.pdf",
                                    mime="application/pdf", width="stretch")
            except ImportError:
                st.button("⬇️ Download .pdf", disabled=True, width="stretch",
                          help="Install `fpdf2` to enable PDF export")
        with btn_col4:
            st.button("📋 Copy Report", width="stretch",
                      help="Select the text in the panel below and copy (Ctrl/Cmd+C)")

        panel_start()
        st.markdown(report_md)
        panel_end()
