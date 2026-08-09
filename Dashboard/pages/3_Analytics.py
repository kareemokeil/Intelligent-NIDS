"""
pages/3_Analytics.py
======================
Aggregate views over the test set and report history: attack
distribution, confidence distribution, prediction timeline, and
class frequency — all interactive Plotly charts.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.theme import apply_theme, render_sidebar
from utils.artifacts_loader import require_artifacts_or_stop
from utils.history import load_history
from utils.predictor import predict_test_set, predict_proba_test_set

st.set_page_config(page_title="Analytics — NIDS", page_icon="📈", layout="wide")
apply_theme()
render_sidebar(active="Analytics")

st.title("📈 Analytics")

art = require_artifacts_or_stop()

cache_key = f"{art.X_test_z.shape}-{art.X_test_z.index[0]}-{art.X_test_z.index[-1]}"

try:
    with st.spinner("Scoring the full test set (cached after first run)..."):
        y_pred_encoded = predict_test_set(art.model, art.label_encoder, art.X_test_z.values, cache_key)
        proba_all = predict_proba_test_set(art.model, art.X_test_z.values, cache_key)
except RuntimeError as e:
    st.error(f"⚠️ {e}")
    st.stop()

y_pred_labels = art.label_encoder.inverse_transform(y_pred_encoded)
confidences = proba_all.max(axis=1)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Attack Distribution (Test Set)")
    dist = pd.Series(art.y_test).value_counts().reset_index()
    dist.columns = ["class", "count"]
    fig_pie = px.pie(dist, names="class", values="count", hole=0.45,
                     color_discrete_sequence=px.colors.sequential.Blues_r)
    fig_pie.update_layout(template="plotly_dark", height=380,
                          paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_pie, width='stretch')

with col2:
    st.subheader("Confidence Distribution")
    fig_hist = px.histogram(x=confidences, nbins=30, color_discrete_sequence=["#3B82F6"])
    fig_hist.update_layout(template="plotly_dark", height=380,
                           xaxis_title="Prediction confidence", yaxis_title="Count",
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_hist, width='stretch')

col3, col4 = st.columns(2)

with col3:
    st.subheader("Class Frequency — True vs Predicted")
    true_counts = pd.Series(art.y_test).value_counts()
    pred_counts = pd.Series(y_pred_labels).value_counts()
    freq_df = pd.DataFrame({"True": true_counts, "Predicted": pred_counts}).fillna(0).reset_index()
    freq_df = freq_df.rename(columns={"index": "class"}).melt(id_vars="class", var_name="type", value_name="count")
    fig_bar = px.bar(freq_df, x="class", y="count", color="type", barmode="group",
                     color_discrete_map={"True": "#3B82F6", "Predicted": "#22D3EE"})
    fig_bar.update_layout(template="plotly_dark", height=380,
                         paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_bar, width='stretch')

with col4:
    st.subheader("Report Generation Timeline")
    history = load_history()
    if history:
        hist_df = pd.DataFrame(history)
        hist_df["timestamp"] = pd.to_datetime(hist_df["timestamp"])
        hist_df = hist_df.sort_values("timestamp")
        fig_timeline = px.scatter(hist_df, x="timestamp", y="attack", color="attack",
                                  size="confidence", hover_data=["id", "confidence"])
        fig_timeline.update_layout(template="plotly_dark", height=380,
                                   paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_timeline, width='stretch')
    else:
        st.info("No reports generated yet — the timeline will populate as you use the Detection page.")
