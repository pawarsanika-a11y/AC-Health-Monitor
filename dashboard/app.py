"""
app.py - AI-AC-Health-Monitor Primary Application

Main Streamlit application interface providing:
1. Public Homepage: System purpose, architecture, features, and login/get started
2. Protected Dashboard Console: Real-time AC health monitoring, IoT sensor telemetry,
   temperature dynamic charts, and ML-ready diagnostic cards.
"""

import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Configure page layout and title
st.set_page_config(
    page_title="AI-AC Health Monitor | IoT & ML Diagnostics",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from dashboard.components.charts import (
    render_energy_and_delta_t_chart,
    render_temperature_chart,
)
from dashboard.components.metrics_cards import (
    render_hardware_status_banner,
    render_top_kpi_row,
)
from dashboard.components.fault_analysis_view import render_fault_analysis_view
from dashboard.components.climate_impact_view import render_climate_impact_view
from dashboard.components.homepage import render_homepage
from dashboard.utils.ml_inference import models_available, run_inference
from dashboard.components.sidebar import render_sidebar
from dashboard.utils.sample_data import (
    generate_recent_telemetry_events,
    generate_temperature_timeseries,
    get_current_system_state,
)
from dashboard.utils.theme import apply_custom_theme, get_current_theme, set_theme


def main():
    # Retrieve current theme ('dark' or 'light')
    current_theme = get_current_theme()
    apply_custom_theme(current_theme)

    # Initialize navigation and session state
    if "logged_in" not in st.session_state:
        # Check query params for deep-linking (e.g. ?page=dashboard)
        qp_page = st.query_params.get("page", None)
        if qp_page == "dashboard":
            st.session_state["logged_in"] = True
            st.session_state["current_page"] = "dashboard"
        else:
            st.session_state["logged_in"] = False
            st.session_state["current_page"] = "home"

    # ROUTE 1: PUBLIC HOMEPAGE (First page users see when visiting)
    if not st.session_state.get("logged_in", False) and st.session_state.get("current_page", "home") == "home":
        render_homepage()
        return

    # ROUTE 2: PROTECTED OPERATIONAL CONSOLE (Dashboard & Diagnostic Views)
    # Render navigation and sidebar controls (including the unchanged AC Units dropdown)
    selected_nav, scenario, esp32_online, unit_id = render_sidebar()

    # Acquire current state data (needed for all views)
    state = get_current_system_state(scenario_name=scenario, esp32_online=esp32_online)

    # Run ML inference (returns demo fallback if models not trained)
    ml_result = None
    if models_available():
        try:
            ml_result = run_inference(state)
        except Exception:
            ml_result = None

    # Route based on selected sidebar navigation
    if selected_nav == "Fault Analysis":
        render_fault_analysis_view(state, ml_result)
        return

    if selected_nav == "Energy & Climate Impact":
        render_climate_impact_view(state, ml_result)
        return

    # --- PRIMARY DASHBOARD VIEW ---
    # Header Section
    col_header_left, col_header_right = st.columns([2.5, 1.2])

    with col_header_left:
        st.markdown(f"""
        <div style="margin-bottom: 0.25rem;">
            <h1 style="font-size: 1.85rem; font-weight: 800; color: var(--text-primary); margin-bottom: 0.2rem; letter-spacing: -0.02em;">
                AC Health & Telemetry Dashboard
            </h1>
            <div class="header-subtitle">
                Monitoring Target: <strong style="color: var(--accent-blue);">{unit_id}</strong> &nbsp;•&nbsp; 
                Mode: <span style="color: var(--text-secondary);">{scenario}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_header_right:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f"""
        <div style="text-align: right; padding-top: 0.4rem;">
            <div style="font-size: 0.72rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">System Time</div>
            <div style="font-size: 0.88rem; color: var(--text-primary); font-family: 'JetBrains Mono', monospace; font-weight: 600;">{now_str}</div>
            <div style="font-size: 0.72rem; color: #10B981; margin-top: 0.2rem;">● Auto-sync: 1 Hz active</div>
        </div>
        """, unsafe_allow_html=True)

    # 1. Top KPI Row: AC Health Score, Operating Status, Anomaly Detection, Power Overview
    render_top_kpi_row(state)

    # 2. ESP32 Hardware Connection Banner
    render_hardware_status_banner(state)

    # 3. Temperature Monitoring Section
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem; margin-bottom: 0.75rem;">
        <div>
            <h3 style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary); margin: 0;">
                Temperature Dynamics & Thermal Gradients
            </h3>
            <p style="font-size: 0.78rem; color: var(--text-secondary); margin: 0;">
                Evaporator Supply vs Indoor Ambient vs Outdoor Diurnal Profile
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Time range selector & chart controls
    col_chart_filter, _ = st.columns([1.5, 3.5])
    with col_chart_filter:
        time_range = st.radio(
            "Time Range Filter",
            options=["Last 1 Hour", "Last 6 Hours", "Last 24 Hours"],
            index=1,
            horizontal=True,
            label_visibility="collapsed",
            key="time_range_radio"
        )

    # Calculate hours based on filter
    duration_map = {
        "Last 1 Hour": 1,
        "Last 6 Hours": 6,
        "Last 24 Hours": 24,
    }
    duration_hours = duration_map.get(time_range, 6)
    points_count = 60 if duration_hours == 1 else (120 if duration_hours == 6 else 240)

    # Generate realistic time series
    df_timeseries = generate_temperature_timeseries(
        duration_hours=duration_hours,
        scenario_name=scenario,
        points=points_count
    )

    # Render temperature and secondary energy/delta-t charts side-by-side
    chart_col1, chart_col2 = st.columns([1.55, 1.0])

    with chart_col1:
        st.markdown('<div class="iot-card" style="padding: 1rem 1rem 0.5rem 1rem;">', unsafe_allow_html=True)
        render_temperature_chart(df_timeseries, time_range, theme_mode=current_theme)
        st.markdown('</div>', unsafe_allow_html=True)

    with chart_col2:
        st.markdown('<div class="iot-card" style="padding: 1rem 1rem 0.5rem 1rem;">', unsafe_allow_html=True)
        render_energy_and_delta_t_chart(df_timeseries, theme_mode=current_theme)
        st.markdown('</div>', unsafe_allow_html=True)

    # 4. Recent Telemetry Events / Anomaly Log Section
    st.markdown("""
    <div style="margin-top: 1rem; margin-bottom: 0.65rem;">
        <h3 style="font-size: 1.05rem; font-weight: 700; color: var(--text-primary); margin: 0;">
            Live Telemetry & Anomaly Event Log
        </h3>
    </div>
    """, unsafe_allow_html=True)

    events = generate_recent_telemetry_events(scenario_name=scenario)
    if events:
        event_df = pd.DataFrame(events, columns=["time", "level", "source", "message"])
        event_df = event_df.rename(columns={"message": "event"})
        event_df = event_df[["time", "level", "source", "event"]]

        st.dataframe(
            event_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "time": st.column_config.TextColumn("Time", width="small"),
                "level": st.column_config.TextColumn("Level", width="small"),
                "source": st.column_config.TextColumn("Source", width="medium"),
                "event": st.column_config.TextColumn("Event"),
            },
        )
    else:
        st.info("No telemetry events available for the current scenario.")


if __name__ == "__main__":
    main()
