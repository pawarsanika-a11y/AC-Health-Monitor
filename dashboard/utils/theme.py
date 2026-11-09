"""
theme.py - Custom IoT SaaS Design System for AI-AC-Health-Monitor

Provides modern dark navy/charcoal styling with electric blue accents,
clean card typography, status badges, and responsive containers.
"""

import streamlit as st


def apply_custom_theme():
    """Injects high-end IoT/AI SaaS custom CSS."""
    st.markdown("""
    <style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --bg-main: #0B0F19;
        --bg-card: #111827;
        --bg-card-hover: #1A2234;
        --border-subtle: rgba(255, 255, 255, 0.07);
        --border-accent: rgba(59, 130, 246, 0.3);
        --accent-blue: #3B82F6;
        --accent-blue-glow: rgba(59, 130, 246, 0.15);
        --accent-teal: #06B6D4;
        --accent-green: #10B981;
        --accent-amber: #F59E0B;
        --accent-rose: #EF4444;
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;
    }

    /* Base Font Override */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* App container padding */
    .block-container {
        padding-top: 1.75rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1400px !important;
    }

    /* Streamlit Metric Overrides */
    div[data-testid="stMetric"] {
        background-color: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 1.25rem 1.25rem;
        box-shadow: 0 4px 16px -2px rgba(0, 0, 0, 0.35);
        transition: transform 0.18s ease, border-color 0.18s ease;
    }

    div[data-testid="stMetric"]:hover {
        border-color: var(--border-accent);
        transform: translateY(-1px);
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
        color: var(--text-secondary) !important;
        margin-bottom: 0.35rem !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.85rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0A0E17 !important;
        border-right: 1px solid var(--border-subtle) !important;
    }

    section[data-testid="stSidebar"] div.block-container {
        padding-top: 2rem !important;
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
    }

    /* Custom IoT Card Component */
    .iot-card {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 1.35rem 1.45rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.4);
        position: relative;
    }

    .iot-card.highlight {
        border-color: var(--border-accent);
        box-shadow: 0 4px 24px -2px var(--accent-blue-glow);
    }

    .iot-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding-bottom: 0.65rem;
    }

    .iot-card-title {
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--text-secondary);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Badges */
    .badge {
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
    }

    .badge-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        display: inline-block;
    }

    .badge-success {
        background: rgba(16, 185, 129, 0.12);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-success .badge-dot { background: #10B981; box-shadow: 0 0 8px #10B981; }

    .badge-warning {
        background: rgba(245, 158, 11, 0.12);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .badge-warning .badge-dot { background: #F59E0B; box-shadow: 0 0 8px #F59E0B; }

    .badge-danger {
        background: rgba(239, 68, 68, 0.12);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .badge-danger .badge-dot { background: #EF4444; box-shadow: 0 0 8px #EF4444; }

    .badge-blue {
        background: rgba(59, 130, 246, 0.12);
        color: #60A5FA;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    .badge-blue .badge-dot { background: #3B82F6; box-shadow: 0 0 8px #3B82F6; }

    .badge-neutral {
        background: rgba(148, 163, 184, 0.12);
        color: #CBD5E1;
        border: 1px solid rgba(148, 163, 184, 0.25);
    }
    .badge-neutral .badge-dot { background: #94A3B8; }

    /* Health Score Circle / Hero */
    .health-hero {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 0.25rem;
    }

    .health-score-large {
        font-size: 3.25rem;
        font-weight: 800;
        line-height: 1;
        letter-spacing: -0.03em;
    }

    .health-score-desc {
        color: var(--text-secondary);
        font-size: 0.82rem;
        margin-top: 0.35rem;
    }

    /* Telemetry grid row */
    .telemetry-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.45rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        font-size: 0.82rem;
    }

    .telemetry-row:last-child {
        border-bottom: none;
    }

    .telemetry-label {
        color: var(--text-secondary);
        font-weight: 500;
    }

    .telemetry-val {
        color: var(--text-primary);
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Pulse animation */
    @keyframes pulse-subtle {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.55; }
    }

    .pulse {
        animation: pulse-subtle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    /* Custom Header Subtitle */
    .header-subtitle {
        color: var(--text-secondary);
        font-size: 0.88rem;
        margin-top: -0.65rem;
        margin-bottom: 1.5rem;
    }

    /* Streamlit radio pills style in sidebar */
    div[data-testid="stRadio"] > label {
        display: none;
    }

    div[data-testid="stRadio"] > div {
        gap: 0.4rem;
    }

    /* Clean divider */
    hr {
        border: none;
        height: 1px;
        background: var(--border-subtle);
        margin: 1.25rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


def get_health_color_and_badge(health_score: int) -> tuple[str, str, str]:
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


def get_anomaly_badge(anomaly_status: str) -> tuple[str, str]:
    """Returns (badge_class, badge_label)."""
    if "Normal" in anomaly_status:
        return "badge-success", "Normal Operation"
    elif "Warning" in anomaly_status:
        return "badge-warning", "Anomaly Detected"
    else:
        return "badge-danger", "Critical Anomaly"

