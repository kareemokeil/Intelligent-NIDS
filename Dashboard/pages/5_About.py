"""
pages/5_About.py
===================
Static project documentation: description, dataset summary, pipeline
architecture, and a simple hand-built workflow diagram (SVG).
"""

import streamlit as st
from utils.theme import apply_theme, render_sidebar
from utils.artifacts_loader import get_feature_count

st.set_page_config(page_title="About — NIDS", page_icon="ℹ️", layout="wide")
apply_theme()
render_sidebar(active="About")

_feat_count = get_feature_count() or 17

st.title("ℹ️ About This Project")

st.markdown(
    """
    <div class="soc-panel">
    <h4>Project Description</h4>
    <p>The Intelligent Network Intrusion Detection System (NIDS) is a graduation project that
    classifies network traffic flows into benign or one of seven attack categories, then
    automatically produces a SOC-style incident report explaining <i>why</i> the model made
    that call and grounding the explanation in retrieved domain knowledge.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <div class="soc-panel">
        <h4>Dataset Summary</h4>
        <ul>
        <li><b>Source:</b> CIC-IDS2017 (~2.5M records, 79 raw features)</li>
        <li><b>Preprocessing:</b> infinity handling, ~11.69% duplicate removal,
            correlated-feature drop (&ge;0.99), zero-variance drop, log1p on skewed features</li>
        <li><b>Feature selection:</b> XGBoost-assisted &rarr; {_feat_count} final features</li>
        <li><b>Split:</b> 75 / 10 / 15 (Train / Val / Test), stratified</li>
        <li><b>Classes (8):</b> BENIGN, DoS, DDoS, PortScan, Brute Force, Web Attack, Bot, Rare Attack</li>
        <li><b>Imbalance handling:</b> custom class weights (SMOTE hit MemoryError)</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="soc-panel">
        <h4>Model & Explainability</h4>
        <ul>
        <li><b>Final model:</b> Random Forest (n_estimators=300, max_depth=30,
            min_samples_split=5, min_samples_leaf=2, max_features="sqrt")</li>
        <li><b>Comparison models:</b> XGBoost, LightGBM, Deep Neural Network</li>
        <li><b>Reported metrics:</b> Accuracy &approx; 0.9916, Macro F1 &approx; 0.8244,
            MCC &approx; 0.9724</li>
        <li><b>Known limitation:</b> weaker recall on Bot and Rare Attack classes</li>
        <li><b>Explainability:</b> SHAP (TreeExplainer)</li>
        <li><b>Knowledge grounding:</b> FAISS retrieval-augmented generation</li>
        <li><b>Report writer:</b> Gemini LLM</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()
st.subheader("System Workflow")

_WORKFLOW_SVG = """
<svg viewBox="0 0 1180 170" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:auto;">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L8,3 L0,6 Z" fill="#3B82F6"/>
    </marker>
  </defs>
  <style>
    .box { fill: #131826; stroke: #232B3D; stroke-width: 1.5; rx: 12; }
    .lbl { fill: #F1F5F9; font-size: 13px; font-family: sans-serif; font-weight: 600; }
    .sub { fill: #8B93A7; font-size: 10.5px; font-family: sans-serif; }
    .arrow { stroke: #3B82F6; stroke-width: 2; marker-end: url(#arrow); fill: none; }
  </style>

  <rect class="box" x="10"  y="55" width="150" height="70"/>
  <text class="lbl" x="30" y="85">Ingest</text>
  <text class="sub" x="30" y="103">CIC-IDS2017 flow</text>

  <rect class="box" x="195" y="55" width="150" height="70"/>
  <text class="lbl" x="215" y="85">Preprocess</text>
  <text class="sub" x="215" y="103">Scale, select 16 feats</text>

  <rect class="box" x="380" y="55" width="150" height="70"/>
  <text class="lbl" x="400" y="85">Classify</text>
  <text class="sub" x="400" y="103">Random Forest</text>

  <rect class="box" x="565" y="55" width="150" height="70"/>
  <text class="lbl" x="585" y="85">Explain</text>
  <text class="sub" x="585" y="103">SHAP attribution</text>

  <rect class="box" x="750" y="55" width="150" height="70"/>
  <text class="lbl" x="770" y="85">Retrieve</text>
  <text class="sub" x="770" y="103">FAISS knowledge base</text>

  <rect class="box" x="935" y="55" width="230" height="70"/>
  <text class="lbl" x="955" y="85">Report</text>
  <text class="sub" x="955" y="103">Gemini incident report</text>

  <path class="arrow" d="M160,90 L195,90"/>
  <path class="arrow" d="M345,90 L380,90"/>
  <path class="arrow" d="M530,90 L565,90"/>
  <path class="arrow" d="M715,90 L750,90"/>
  <path class="arrow" d="M900,90 L935,90"/>
</svg>
"""
_WORKFLOW_SVG = _WORKFLOW_SVG.replace("Scale, select 16 feats", f"Scale, select {_feat_count} feats")
st.markdown(_WORKFLOW_SVG, unsafe_allow_html=True)
