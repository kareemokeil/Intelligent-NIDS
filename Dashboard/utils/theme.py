"""
utils/theme.py
---------------
Shared visual language for the whole dashboard: dark SOC-style CSS,
a custom sidebar (logo + navigation + project meta), and small
reusable HTML components (metric cards, status badges, bordered
containers) used across every page.

Call `apply_theme()` and `render_sidebar(active)` once at the top of
every page script (app.py and every file in pages/).
"""

import streamlit as st
from pathlib import Path

APP_VERSION = "1.0.0"
AUTHOR_NAME = "Kareem"  # TODO: change if you'd like a different display name

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

PAGES = [
    ("app.py", "🏠", "Home"),
    ("pages/1_Detection.py", "🔍", "Detection"),
    ("pages/2_Model_Performance.py", "📊", "Model Performance"),
    ("pages/3_Analytics.py", "📈", "Analytics"),
    ("pages/4_History.py", "🕒", "History"),
    ("pages/5_About.py", "ℹ️", "About"),
]

# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------
_CSS = """
<style>
/* Hide Streamlit's default auto-generated page nav — we render our own */
[data-testid="stSidebarNav"] { display: none; }
#MainMenu, footer, header[data-testid="stHeader"] { visibility: visible; }

html, body, [class*="css"] { font-family: 'Segoe UI', Inter, system-ui, sans-serif; }

.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1300px; }

/* ---- Metric / info cards ---- */
.soc-card {
    background: linear-gradient(180deg, #131826 0%, #0F1420 100%);
    border: 1px solid #232B3D;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.25);
}
.soc-card .icon { font-size: 22px; opacity: 0.9; }
.soc-card .label { color: #8B93A7; font-size: 12.5px; text-transform: uppercase;
                    letter-spacing: 0.06em; margin-top: 6px; }
.soc-card .value { font-size: 26px; font-weight: 700; color: #F1F5F9; margin-top: 2px; }
.soc-card .sub { color: #6B7488; font-size: 12.5px; margin-top: 4px; }

/* ---- Status badges ---- */
.badge { display:inline-block; padding: 3px 12px; border-radius: 999px;
         font-size: 12.5px; font-weight: 600; letter-spacing: 0.02em; }
.badge-critical { background: rgba(239,68,68,0.15); color: #F87171; border: 1px solid rgba(239,68,68,0.35); }
.badge-high     { background: rgba(249,115,22,0.15); color: #FB923C; border: 1px solid rgba(249,115,22,0.35); }
.badge-medium   { background: rgba(234,179,8,0.15); color: #FACC15; border: 1px solid rgba(234,179,8,0.35); }
.badge-low      { background: rgba(34,197,94,0.15); color: #4ADE80; border: 1px solid rgba(34,197,94,0.35); }
.badge-info     { background: rgba(59,130,246,0.15); color: #60A5FA; border: 1px solid rgba(59,130,246,0.35); }

/* ---- Bordered content container (report viewer, etc.) ---- */
.soc-panel {
    background: #0F1420; border: 1px solid #232B3D; border-radius: 14px;
    padding: 22px 26px; margin-top: 10px;
}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] { background: #0B0F19; border-right: 1px solid #1D2433; }
.sidebar-brand { display:flex; align-items:center; gap:10px; padding: 4px 2px 14px 2px;
                 border-bottom: 1px solid #1D2433; margin-bottom: 14px; }
.sidebar-brand .title { font-weight: 700; font-size: 15.5px; color: #F1F5F9; line-height: 1.15; }
.sidebar-brand .subtitle { font-size: 11px; color: #6B7488; }
.sidebar-section-label { color: #58607A; font-size: 11px; text-transform: uppercase;
                          letter-spacing: 0.08em; margin: 14px 0 6px 2px; }
.sidebar-meta-row { display:flex; justify-content: space-between; font-size: 12.5px;
                    color: #A7B0C4; padding: 3px 2px; }
.sidebar-meta-row span.k { color: #58607A; }
</style>
"""


def apply_theme():
    st.markdown(_CSS, unsafe_allow_html=True)


def render_sidebar(active: str):
    """Custom SOC-style sidebar: logo, nav links, project/model/RAG/LLM info."""
    logo_svg = (ASSETS_DIR / "logo.svg").read_text()

    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-brand">
                {logo_svg}
                <div>
                    <div class="title">Intelligent NIDS</div>
                    <div class="subtitle">SOC Detection Console</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-section-label">Navigation</div>', unsafe_allow_html=True)
        for path, icon, label in PAGES:
            st.page_link(path, label=label, icon=icon,
                         disabled=(label == active))

        from utils.artifacts_loader import get_feature_count
        feat_count = get_feature_count()

        st.markdown('<div class="sidebar-section-label">Dataset</div>', unsafe_allow_html=True)
        _meta_row("Source", "CIC-IDS2017")
        _meta_row("Classes", "8")
        _meta_row("Features", f"{feat_count} (selected)" if feat_count is not None else "— (selected)")

        st.markdown('<div class="sidebar-section-label">Model</div>', unsafe_allow_html=True)
        _meta_row("Algorithm", "Random Forest")
        _meta_row("Explainability", "SHAP")

        st.markdown('<div class="sidebar-section-label">Knowledge & LLM</div>', unsafe_allow_html=True)
        _meta_row("Retrieval", "FAISS RAG")
        _meta_row("LLM", "Gemini")

        st.markdown('<div class="sidebar-section-label">System</div>', unsafe_allow_html=True)
        _meta_row("Version", APP_VERSION)
        _meta_row("Author", AUTHOR_NAME)


def _meta_row(key: str, value: str):
    st.markdown(
        f'<div class="sidebar-meta-row"><span class="k">{key}</span><span>{value}</span></div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Reusable components
# ---------------------------------------------------------------------------
def metric_card(icon: str, label: str, value: str, sub: str = ""):
    st.markdown(
        f"""
        <div class="soc-card">
            <div class="icon">{icon}</div>
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            <div class="sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_badge(risk: str) -> str:
    risk = risk.lower()
    cls = {"critical": "badge-critical", "high": "badge-high",
           "medium": "badge-medium", "low": "badge-low"}.get(risk, "badge-info")
    return f'<span class="badge {cls}">{risk.upper()}</span>'


def risk_level_for(pred_class: str, confidence: float) -> str:
    """Simple, transparent risk heuristic — tune thresholds as needed."""
    if pred_class == "BENIGN":
        return "low"
    if confidence >= 0.9:
        return "critical"
    if confidence >= 0.7:
        return "high"
    return "medium"


def panel_start():
    st.markdown('<div class="soc-panel">', unsafe_allow_html=True)


def panel_end():
    st.markdown("</div>", unsafe_allow_html=True)
