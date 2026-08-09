"""
pages/2_Model_Performance.py
==============================
Full model evaluation computed live from the loaded model + test set:
Accuracy / Precision / Recall / F1 / MCC, confusion matrix, one-vs-rest
ROC curves, classification report table, feature importance.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.metrics import (
    classification_report, confusion_matrix, matthews_corrcoef,
    accuracy_score, precision_recall_fscore_support, roc_curve, auc,
)
from sklearn.preprocessing import label_binarize

from utils.theme import apply_theme, render_sidebar, metric_card
from utils.artifacts_loader import require_artifacts_or_stop
from utils.predictor import predict_test_set, predict_proba_test_set

st.set_page_config(page_title="Model Performance — NIDS", page_icon="📊", layout="wide")
apply_theme()
render_sidebar(active="Model Performance")

st.title("📊 Model Performance")

art = require_artifacts_or_stop()

cache_key = f"{art.X_test_z.shape}-{art.X_test_z.index[0]}-{art.X_test_z.index[-1]}"

try:
    with st.spinner("Scoring the full test set (cached after first run)..."):
        y_pred_encoded = predict_test_set(art.model, art.label_encoder, art.X_test_z.values, cache_key)
        y_score = predict_proba_test_set(art.model, art.X_test_z.values, cache_key)
except RuntimeError as e:
    st.error(f"⚠️ {e}")
    st.stop()

y_pred_labels = art.label_encoder.inverse_transform(y_pred_encoded)
y_true_labels = art.y_test

acc = accuracy_score(y_true_labels, y_pred_labels)
precision, recall, f1, _ = precision_recall_fscore_support(
    y_true_labels, y_pred_labels, average="macro", zero_division=0
)
mcc = matthews_corrcoef(art.y_test_encoded, y_pred_encoded)

st.subheader("Headline Metrics")
c1, c2, c3, c4, c5 = st.columns(5)
with c1: metric_card("✅", "Accuracy", f"{acc*100:.2f}%", "Overall test set")
with c2: metric_card("🎯", "Precision (macro)", f"{precision*100:.2f}%", "Averaged across 8 classes")
with c3: metric_card("🔁", "Recall (macro)", f"{recall*100:.2f}%", "Averaged across 8 classes")
with c4: metric_card("⚖️", "F1 Score (macro)", f"{f1*100:.2f}%", "Averaged across 8 classes")
with c5: metric_card("📐", "MCC", f"{mcc:.4f}", "Matthews Correlation Coefficient")

st.divider()
col_cm, col_roc = st.columns(2)

with col_cm:
    st.subheader("Confusion Matrix")
    cm = confusion_matrix(y_true_labels, y_pred_labels, labels=art.class_names_ordered)
    fig_cm = px.imshow(
        cm, x=art.class_names_ordered, y=art.class_names_ordered,
        color_continuous_scale="Blues", text_auto=True, aspect="auto",
        labels=dict(x="Predicted", y="True", color="Count"),
    )
    fig_cm.update_layout(template="plotly_dark", height=460,
                         paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_cm, width='stretch')

with col_roc:
    st.subheader("ROC Curves (One-vs-Rest)")
    y_true_bin = label_binarize(art.y_test_encoded, classes=art.model.classes_)

    fig_roc = go.Figure()
    fig_roc.add_shape(type="line", x0=0, y0=0, x1=1, y1=1,
                      line=dict(dash="dash", color="#4B5563"))
    for i, cls_name in enumerate(art.class_names_ordered):
        if y_true_bin[:, i].sum() == 0:
            continue  # class absent from this test split
        fpr, tpr, _ = roc_curve(y_true_bin[:, i], y_score[:, i])
        roc_auc = auc(fpr, tpr)
        fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines",
                                     name=f"{cls_name} (AUC={roc_auc:.3f})"))
    fig_roc.update_layout(
        template="plotly_dark", height=460,
        xaxis_title="False Positive Rate", yaxis_title="True Positive Rate",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(size=10)),
    )
    st.plotly_chart(fig_roc, width='stretch')

st.divider()
col_report, col_importance = st.columns([1.2, 1])

with col_report:
    st.subheader("Classification Report")
    report_dict = classification_report(y_true_labels, y_pred_labels, output_dict=True, zero_division=0)
    report_df = pd.DataFrame(report_dict).transpose().round(4)
    st.dataframe(report_df, width='stretch', height=400)

with col_importance:
    st.subheader("Feature Importance")
    importances = pd.Series(art.model.feature_importances_, index=art.feature_names)
    importances = importances.sort_values(ascending=True)
    fig_imp = go.Figure(go.Bar(x=importances.values, y=importances.index, orientation="h",
                               marker=dict(color="#22D3EE")))
    fig_imp.update_layout(template="plotly_dark", height=400, margin=dict(l=10, r=10, t=10, b=10),
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_imp, width='stretch')
