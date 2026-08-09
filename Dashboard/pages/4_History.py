"""
pages/4_History.py
=====================
Every report generated in the Detection page is persisted to
reports/history.json. This page shows them as a searchable, filterable,
downloadable table.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from utils.theme import apply_theme, render_sidebar
from utils.history import load_history

st.set_page_config(page_title="History — NIDS", page_icon="🕒", layout="wide")
apply_theme()
render_sidebar(active="History")

st.title("🕒 Report History")

history = load_history()

if not history:
    st.info("No reports generated yet. Go to **Detection** and click **Generate Report**.")
    st.stop()

df = pd.DataFrame(history)

col1, col2 = st.columns([2, 1])
with col1:
    search = st.text_input("Search by report ID or attack type", "")
with col2:
    attack_filter = st.multiselect("Filter by attack", sorted(df["attack"].unique().tolist()))

filtered = df.copy()
if search:
    filtered = filtered[
        filtered["id"].str.contains(search, case=False) |
        filtered["attack"].str.contains(search, case=False)
    ]
if attack_filter:
    filtered = filtered[filtered["attack"].isin(attack_filter)]

st.caption(f"{len(filtered)} of {len(df)} reports shown")
st.dataframe(
    filtered[["id", "attack", "confidence", "timestamp"]],
    width='stretch', height=420,
)

st.subheader("Download a report")
selected_id = st.selectbox("Select report", filtered["id"].tolist() if len(filtered) else [])
if selected_id:
    record = df[df["id"] == selected_id].iloc[0]
    md_path = Path(record["md_path"])
    if md_path.exists():
        st.download_button("⬇️ Download .md", data=md_path.read_text(encoding="utf-8"),
                            file_name=f"{selected_id}.md", mime="text/markdown")
        with st.expander("Preview"):
            st.markdown(md_path.read_text(encoding="utf-8"))
    else:
        st.warning("Report file not found on disk (may have been moved or deleted).")
