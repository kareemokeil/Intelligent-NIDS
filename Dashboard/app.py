"""
app.py — Home
==============
Entry point of the Intelligent NIDS SOC dashboard. Shows a landing
overview with top-level metric cards summarizing the most recent
detection (or a neutral placeholder state if nothing has been run yet).

Run with:  streamlit run app.py
"""

import streamlit as st
from datetime import datetime

from utils.theme import apply_theme, render_sidebar, metric_card, risk_badge, risk_level_for
from utils.artifacts_loader import missing_files, get_feature_count
from utils.history import load_history

st.set_page_config(page_title="Intelligent NIDS — SOC Console", page_icon="🛡️", layout="wide")
apply_theme()
render_sidebar(active="Home")

st.title("🛡️ Intelligent Network Intrusion Detection System")
st.caption("CIC-IDS2017 · Random Forest · SHAP Explainability · FAISS RAG · Gemini-generated Incident Reports")

missing = missing_files()
if missing:
    st.warning(
        "**Model artifacts not detected yet.** The dashboard UI is fully built and will "
        "activate as soon as your trained model files are in `artifacts/`. "
        f"Missing: {', '.join('`'+m+'`' for m in missing)}. See `README.md` for the export snippet."
    )

history = load_history()
latest = history[0] if history else None

st.subheader("Latest Detection Summary")
cols = st.columns(5)

if latest:
    risk = risk_level_for(latest["attack"], latest["confidence"] / 100)
    with cols[0]:
        metric_card("🎯", "Predicted Attack", latest["attack"], "Most recent report")
    with cols[1]:
        metric_card("📶", "Confidence", f"{latest['confidence']:.1f}%", "Model certainty")
    with cols[2]:
        st.markdown(
            f'<div class="soc-card"><div class="icon">⚠️</div>'
            f'<div class="label">Risk Level</div>'
            f'<div class="value">{risk_badge(risk)}</div>'
            f'<div class="sub">Heuristic from class + confidence</div></div>',
            unsafe_allow_html=True,
        )
    with cols[3]:
        ts = datetime.fromisoformat(latest["timestamp"]).strftime("%H:%M:%S")
        metric_card("🕒", "Detection Time", ts, latest["timestamp"][:10])
    with cols[4]:
        metric_card("🧠", "Model", "Random Forest", "CIC-IDS2017")
else:
    with cols[0]:
        metric_card("🎯", "Predicted Attack", "—", "No detections yet")
    with cols[1]:
        metric_card("📶", "Confidence", "—", "Run a detection first")
    with cols[2]:
        metric_card("⚠️", "Risk Level", "—", "—")
    with cols[3]:
        metric_card("🕒", "Detection Time", "—", "—")
    with cols[4]:
        metric_card("🧠", "Model", "Random Forest", "CIC-IDS2017")

st.divider()

left, right = st.columns([1.3, 1])
with left:
    st.subheader("Quick Actions")
    st.page_link("pages/1_Detection.py", label="🔍  Run a new detection", icon="➡️")
    st.page_link("pages/2_Model_Performance.py", label="📊  Review model performance", icon="➡️")
    st.page_link("pages/3_Analytics.py", label="📈  Explore analytics", icon="➡️")
    st.page_link("pages/4_History.py", label="🕒  Browse report history", icon="➡️")

with right:
    st.subheader("Pipeline Overview")
    feat_count = get_feature_count()
    feat_label = f"{feat_count} selected features" if feat_count is not None else "selected features"
    st.markdown(
        f"""
        <div class="soc-panel" style="font-size:14px; line-height:1.9;">
        <b>1. Ingest</b> — CIC-IDS2017 flow features (test sample or uploaded CSV)<br>
        <b>2. Preprocess</b> — scaler transform → {feat_label}<br>
        <b>3. Classify</b> — Random Forest (8 classes)<br>
        <b>4. Explain</b> — SHAP per-feature attribution<br>
        <b>5. Retrieve</b> — FAISS lookup of relevant knowledge-base entries<br>
        <b>6. Report</b> — Gemini-generated SOC incident report
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()
if history:
    st.subheader("Recent Reports")
    for rec in history[:5]:
        risk = risk_level_for(rec["attack"], rec["confidence"] / 100)
        st.markdown(
            f'<div class="soc-card" style="margin-bottom:8px; display:flex; '
            f'justify-content:space-between; align-items:center;">'
            f'<div><b>{rec["id"]}</b> &nbsp; {rec["attack"]} &nbsp; {risk_badge(risk)}</div>'
            f'<div class="sub">{rec["timestamp"]} · {rec["confidence"]:.1f}% confidence</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
