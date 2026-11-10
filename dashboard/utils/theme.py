"""
theme.py - Custom IoT SaaS Design System for AI-AC-Health-Monitor

Provides modern dark navy/charcoal styling with electric blue accents,
clean card typography, status badges, and responsive containers.
Supports dynamic switching between Dark Mode and Light Mode with persistent state.
"""

from typing import Dict, Any, Tuple
import streamlit as st


def get_current_theme() -> str:
    """Returns the current active theme ('dark' or 'light')."""
    # Check query params first for URL persistence, then session state
    if "theme_mode" not in st.session_state:
        # Check URL query param
        qp_theme = st.query_params.get("theme", None)
        if qp_theme in ["dark", "light"]:
            st.session_state["theme_mode"] = qp_theme
        else:
            st.session_state["theme_mode"] = "dark"
    return st.session_state["theme_mode"]


def set_theme(new_theme: str):
    """Updates active theme and syncs with query params."""
    if new_theme in ["dark", "light"]:
        st.session_state["theme_mode"] = new_theme
        st.query_params["theme"] = new_theme


def get_axis_colors(theme_mode: str = "dark") -> Dict[str, str]:
    """Returns axis styling colors for grid, line, text, and title for the active theme."""
    is_dark = (theme_mode == "dark")
    return dict(
        gridcolor="rgba(255, 255, 255, 0.05)" if is_dark else "rgba(15, 23, 42, 0.06)",
        linecolor="rgba(255, 255, 255, 0.1)" if is_dark else "rgba(15, 23, 42, 0.12)",
        text_color="#94A3B8" if is_dark else "#475569",
        title_color="#F8FAFC" if is_dark else "#0F172A",
    )


def get_plot_layout(theme_mode: str = "dark") -> Dict[str, Any]:
    """Returns a base Plotly layout dictionary adapted for the selected theme."""
    is_dark = (theme_mode == "dark")

    font_color = "#94A3B8" if is_dark else "#475569"
    legend_bg = "rgba(15, 23, 42, 0.85)" if is_dark else "rgba(255, 255, 255, 0.92)"
    legend_text = "#CBD5E1" if is_dark else "#1E293B"
    legend_border = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(15, 23, 42, 0.1)"
    hover_bg = "#1E293B" if is_dark else "#FFFFFF"
    hover_text = "#F8FAFC" if is_dark else "#0F172A"

    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.45)" if is_dark else "rgba(241, 245, 249, 0.7)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color=font_color, size=11),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color=legend_text),
            bgcolor=legend_bg,
            bordercolor=legend_border,
            borderwidth=1,
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=hover_bg,
            font_size=11,
            font_family="JetBrains Mono, monospace",
            font_color=hover_text,
            bordercolor="#3B82F6",
        ),
    )


def apply_custom_theme(theme_mode: str = None):
    """
    Injects high-end IoT/AI SaaS custom CSS for both Dark and Light themes.
    """
    if theme_mode is None:
        theme_mode = get_current_theme()

    is_dark = (theme_mode == "dark")

    # CSS Variables per theme
    if is_dark:
        bg_main = "#0B0F19"
        bg_secondary = "#0F172A"
        bg_card = "#111827"
        bg_card_alt = "linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(15, 23, 42, 0.85) 100%)"
        bg_card_highlight = "linear-gradient(135deg, rgba(20, 30, 52, 0.95) 0%, rgba(15, 23, 42, 0.9) 100%)"
        border_subtle = "rgba(255, 255, 255, 0.07)"
        border_accent = "rgba(59, 130, 246, 0.35)"
        accent_blue = "#3B82F6"
        accent_blue_glow = "rgba(59, 130, 246, 0.18)"
        text_primary = "#F8FAFC"
        text_secondary = "#94A3B8"
        text_muted = "#64748B"
        sidebar_bg = "#0A0E17"
        input_bg = "rgba(15, 23, 42, 0.75)"
        table_border = "rgba(255, 255, 255, 0.05)"
        table_th = "#64748B"
        hero_glow = "radial-gradient(ellipse 80% 50% at 50% -20%, rgba(59, 130, 246, 0.18), transparent)"
        nav_bg = "rgba(11, 15, 25, 0.88)"
        card_shadow = "0 8px 24px -4px rgba(0, 0, 0, 0.45)"
    else:
        bg_main = "#F8FAFC"
        bg_secondary = "#F1F5F9"
        bg_card = "#FFFFFF"
        bg_card_alt = "linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)"
        bg_card_highlight = "linear-gradient(135deg, #FFFFFF 0%, #EFF6FF 100%)"
        border_subtle = "rgba(15, 23, 42, 0.09)"
        border_accent = "rgba(37, 99, 235, 0.35)"
        accent_blue = "#2563EB"
        accent_blue_glow = "rgba(37, 99, 235, 0.12)"
        text_primary = "#0F172A"
        text_secondary = "#475569"
        text_muted = "#64748B"
        sidebar_bg = "#FFFFFF"
        input_bg = "#F1F5F9"
        table_border = "rgba(15, 23, 42, 0.08)"
        table_th = "#475569"
        hero_glow = "radial-gradient(ellipse 80% 50% at 50% -20%, rgba(37, 99, 235, 0.12), transparent)"
        nav_bg = "rgba(255, 255, 255, 0.92)"
        card_shadow = "0 6px 20px -2px rgba(15, 23, 42, 0.07)"

    st.markdown(f"""
    <style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {{
        --bg-main: {bg_main};
        --bg-secondary: {bg_secondary};
        --bg-card: {bg_card};
        --bg-card-alt: {bg_card_alt};
        --bg-card-highlight: {bg_card_highlight};
        --border-subtle: {border_subtle};
        --border-accent: {border_accent};
        --accent-blue: {accent_blue};
        --accent-blue-glow: {accent_blue_glow};
        --accent-teal: #06B6D4;
        --accent-green: #10B981;
        --accent-amber: #F59E0B;
        --accent-rose: #EF4444;
        --text-primary: {text_primary};
        --text-secondary: {text_secondary};
        --text-muted: {text_muted};
        --sidebar-bg: {sidebar_bg};
        --input-bg: {input_bg};
        --table-border: {table_border};
        --table-th: {table_th};
        --card-shadow: {card_shadow};
    }}

    /* Global Body & Container */
    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    .stApp {{
        background-color: var(--bg-main) !important;
        color: var(--text-primary) !important;
    }}

    code, pre {{
        font-family: 'JetBrains Mono', monospace !important;
    }}

    /* App container padding */
    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1380px !important;
    }}

    /* Streamlit Metric Overrides */
    div[data-testid="stMetric"] {{
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 12px !important;
        padding: 1.25rem 1.25rem !important;
        box-shadow: var(--card-shadow) !important;
        transition: transform 0.18s ease, border-color 0.18s ease !important;
    }}

    div[data-testid="stMetric"]:hover {{
        border-color: var(--border-accent) !important;
        transform: translateY(-1px) !important;
    }}

    div[data-testid="stMetricLabel"] {{
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
        color: var(--text-secondary) !important;
        margin-bottom: 0.35rem !important;
    }}

    div[data-testid="stMetricValue"] {{
        font-size: 1.85rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
    }}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }}

    section[data-testid="stSidebar"] div.block-container {{
        padding-top: 1.5rem !important;
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
    }}

    /* Custom IoT Card Component */
    .iot-card {{
        background: var(--bg-card-alt);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 1.35rem 1.45rem;
        margin-bottom: 1rem;
        box-shadow: var(--card-shadow);
        position: relative;
    }}

    .iot-card.highlight {{
        background: var(--bg-card-highlight);
        border-color: var(--border-accent);
        box-shadow: 0 6px 24px -2px var(--accent-blue-glow);
    }}

    .iot-card-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
        border-bottom: 1px solid var(--border-subtle);
        padding-bottom: 0.65rem;
    }}

    .iot-card-title {{
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--text-secondary);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}

    /* Badges */
    .badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        padding: 0.3rem 0.65rem;
        border-radius: 9999px;
        white-space: nowrap;
    }}

    .badge-dot {{
        width: 6px;
        height: 6px;
        border-radius: 50%;
        display: inline-block;
    }}

    .badge-success {{
        background: rgba(16, 185, 129, 0.12);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }}
    .badge-success .badge-dot {{ background: #10B981; box-shadow: 0 0 8px #10B981; }}

    .badge-warning {{
        background: rgba(245, 158, 11, 0.12);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }}
    .badge-warning .badge-dot {{ background: #F59E0B; box-shadow: 0 0 8px #F59E0B; }}

    .badge-danger {{
        background: rgba(239, 68, 68, 0.12);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }}
    .badge-danger .badge-dot {{ background: #EF4444; box-shadow: 0 0 8px #EF4444; }}

    .badge-blue {{
        background: rgba(59, 130, 246, 0.12);
        color: #3B82F6;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }}
    .badge-blue .badge-dot {{ background: #3B82F6; box-shadow: 0 0 8px #3B82F6; }}

    .badge-neutral {{
        background: rgba(148, 163, 184, 0.12);
        color: var(--text-secondary);
        border: 1px solid var(--border-subtle);
    }}
    .badge-neutral .badge-dot {{ background: var(--text-muted); }}

    /* Health Score Circle / Hero */
    .health-hero {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 0.25rem;
    }}

    .health-score-large {{
        font-size: 3.25rem;
        font-weight: 800;
        line-height: 1;
        letter-spacing: -0.03em;
    }}

    .health-score-desc {{
        color: var(--text-secondary);
        font-size: 0.82rem;
        margin-top: 0.35rem;
    }}

    /* Telemetry grid row */
    .telemetry-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.45rem 0;
        border-bottom: 1px solid var(--border-subtle);
        font-size: 0.82rem;
    }}

    .telemetry-row:last-child {{
        border-bottom: none;
    }}

    .telemetry-label {{
        color: var(--text-secondary);
        font-weight: 500;
    }}

    .telemetry-val {{
        color: var(--text-primary);
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }}

    /* Pulse animation */
    @keyframes pulse-subtle {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.55; }}
    }}

    .pulse {{
        animation: pulse-subtle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }}

    /* Custom Header Subtitle */
    .header-subtitle {{
        color: var(--text-secondary);
        font-size: 0.88rem;
        margin-top: -0.45rem;
        margin-bottom: 1.5rem;
    }}

    /* Streamlit radio pills style in sidebar */
    div[data-testid="stRadio"] > label {{
        display: none;
    }}

    div[data-testid="stRadio"] > div {{
        gap: 0.4rem;
    }}

    /* Clean divider */
    hr {{
        border: none;
        height: 1px;
        background: var(--border-subtle);
        margin: 1.25rem 0;
    }}

    /* Homepage Special Components */
    .hero-glow-bg {{
        background: {hero_glow};
        border-radius: 20px;
        padding: 3rem 2rem 2rem 2rem;
        border: 1px solid var(--border-subtle);
        margin-bottom: 2rem;
        position: relative;
    }}

    .nav-bar-container {{
        background: {nav_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 0.85rem 1.4rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.75rem;
        box-shadow: var(--card-shadow);
    }}

    .feature-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 1.5rem;
        height: 100%;
        box-shadow: var(--card-shadow);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }}

    .feature-card:hover {{
        border-color: var(--border-accent);
        transform: translateY(-2px);
    }}

    .step-number {{
        width: 32px;
        height: 32px;
        border-radius: 8px;
        background: rgba(59, 130, 246, 0.15);
        color: var(--accent-blue);
        font-weight: 800;
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'JetBrains Mono', monospace;
        margin-bottom: 0.75rem;
        border: 1px solid var(--border-accent);
    }}

    /* Buttons override for modern SaaS look */
    .stButton > button {{
        border-radius: 10px !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
        transition: all 0.2s ease !important;
    }}

    .stButton > button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px var(--accent-blue-glow) !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def get_health_color_and_badge(health_score: int) -> Tuple[str, str, str]:
    """
    Returns (color_hex, condition_label, badge_class) based on DESIGN.md:
    80–100: Healthy
    60–79: Moderate
    40–59: Needs inspection
    0–39: Poor condition
    """
    if health_score >= 80:
        return "#10B981", "Healthy", "badge-success"
    elif health_score >= 60:
        return "#F59E0B", "Moderate", "badge-warning"
    elif health_score >= 40:
        return "#FB923C", "Needs Inspection", "badge-warning"
    else:
        return "#EF4444", "Poor Condition", "badge-danger"


def get_anomaly_badge(anomaly_status: str) -> Tuple[str, str]:
    """Returns (badge_class, badge_label)."""
    if "Normal" in anomaly_status:
        return "badge-success", "Normal Operation"
    elif "Warning" in anomaly_status:
        return "badge-warning", "Anomaly Detected"
    else:
        return "badge-danger", "Critical Anomaly"
