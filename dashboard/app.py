"""
app.py - AI-AC-Health-Monitor Primary Dashboard

Main Streamlit application interface providing real-time AC health monitoring,
IoT sensor telemetry, temperature dynamic charts, and ML-ready diagnostic cards.
"""

import sys
from pathlib import Path
from datetime import datetime
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
from dashboard.components.placeholder_views import (
    render_climate_impact_placeholder,
    render_fault_analysis_placeholder,
)
from dashboard.components.sidebar import render_sidebar
from dashboard.utils.sample_data import (
    generate_recent_telemetry_events,
    generate_temperature_timeseries,
    get_current_system_state,
)
from dashboard.utils.theme import apply_custom_theme


def main():
    # Inject dark navy/charcoal IoT theme CSS
    apply_custom_theme()

    # Render navigation and sidebar controls
    selected_nav, scenario, esp32_online, unit_id = render_sidebar()

    # Route based on selected sidebar navigation
    if selected_nav == "Fault Analysis":
        render_fault_analysis_placeholder()
        return

    if selected_nav == "Energy & Climate Impact":
        render_climate_impact_placeholder()
        return

    # --- PRIMARY DASHBOARD VIEW ---
    # Header Section
    col_header_left, col_header_right = st.columns([2.5, 1.0])

    with col_header_left:
        st.markdown(f"""
        <div style="margin-bottom: 0.25rem;">
            <h1 style="font-size: 1.85rem; font-weight: 800; color: #F8FAFC; margin-bottom: 0.2rem; letter-spacing: -0.02em;">
                AC Health & Telemetry Dashboard
            </h1>
            <div class="header-subtitle">
                Monitoring Target: <strong style="color: #60A5FA;">{unit_id}</strong> &nbsp;•&nbsp; 
                Mode: <span style="color: #CBD5E1;">{scenario}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_header_right:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f"""
        <div style="text-align: right; padding-top: 0.5rem;">
            <div style="font-size: 0.72rem; color: #64748B; font-weight: 600; text-transform: uppercase;">System Time</div>
            <div style="font-size: 0.88rem; color: #E2E8F0; font-family: 'JetBrains Mono', monospace; font-weight: 600;">{now_str}</div>
            <div style="font-size: 0.72rem; color: #10B981; margin-top: 0.2rem;">● Auto-sync: 1 Hz active</div>
        </div>
        """, unsafe_allow_html=True)

    # Acquire current state data
    state = get_current_system_state(scenario_name=scenario, esp32_online=esp32_online)

    # 1. Top KPI Row: AC Health Score, Operating Status, Anomaly Detection, Power Overview
    render_top_kpi_row(state)

    # 2. ESP32 Hardware Connection Banner
    render_hardware_status_banner(state)

    # 3. Temperature Monitoring Section
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem; margin-bottom: 0.75rem;">
        <div>
            <h3 style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC; margin: 0;">
                Temperature Dynamics & Thermal Gradients
            </h3>
            <p style="font-size: 0.78rem; color: #94A3B8; margin: 0;">
                Evaporator Supply vs Indoor Ambient vs Outdoor Diurnal Profile
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Time range selector & chart controls
    col_chart_filter, col_filler = st.columns([1.5, 3.5])
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

    # Render temperature and secondary energy/delta-t charts side-by-side or stacked
    chart_col1, chart_col2 = st.columns([1.55, 1.0])

    with chart_col1:
        st.markdown('<div class="iot-card" style="padding: 1rem 1rem 0.5rem 1rem;">', unsafe_allow_html=True)
        render_temperature_chart(df_timeseries, time_range)
        st.markdown('</div>', unsafe_allow_html=True)

    with chart_col2:
        st.markdown('<div class="iot-card" style="padding: 1rem 1rem 0.5rem 1rem;">', unsafe_allow_html=True)
        render_energy_and_delta_t_chart(df_timeseries)
        st.markdown('</div>', unsafe_allow_html=True)

    # 4. Recent Telemetry Events / Anomaly Log Section
    st.markdown("""
    <div style="margin-top: 1rem; margin-bottom: 0.65rem;">
        <h3 style="font-size: 1.05rem; font-weight: 700; color: #F8FAFC; margin: 0;">
            Live Telemetry & Anomaly Event Log
        </h3>
        <p style="font-size: 0.76rem; color: #94A3B8; margin: 0;">
            Real-time feed from ESP32 node and Isolation Forest anomaly surveillance
        </p>
    </div>
    """, unsafe_allow_html=True)

    events = generate_recent_telemetry_events(scenario_name=scenario)

    event_rows_html = ""
    for ev in events:
        badge_cls = {
            "INFO": "badge-neutral",
            "WARN": "badge-warning",
            "ALERT": "badge-warning",
            "CRITICAL": "badge-danger"
        }.get(ev["level"], "badge-neutral")

        event_rows_html += f"""
        <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.04); font-size: 0.8rem;">
            <td style="padding: 0.65rem 0.75rem; color: #64748B; font-family: 'JetBrains Mono', monospace;">{ev['time']}</td>
            <td style="padding: 0.65rem 0.75rem;">
                <span class="badge {badge_cls}" style="font-size: 0.65rem; padding: 0.15rem 0.5rem;">
                    {ev['level']}
                </span>
            </td>
            <td style="padding: 0.65rem 0.75rem; color: #94A3B8; font-weight: 600;">{ev['source']}</td>
            <td style="padding: 0.65rem 0.75rem; color: #F1F5F9;">{ev['message']}</td>
        </tr>
        """

    st.markdown(f"""
    <div class="iot-card" style="padding: 0.5rem 0.75rem;">
        <table style="width: 100%; border-collapse: collapse; text-align: left;">
            <thead>
                <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.08); font-size: 0.72rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">
                    <th style="padding: 0.6rem 0.75rem; width: 110px;">Time</th>
                    <th style="padding: 0.6rem 0.75rem; width: 100px;">Severity</th>
                    <th style="padding: 0.6rem 0.75rem; width: 120px;">Source</th>
                    <th style="padding: 0.6rem 0.75rem;">Event Detail</th>
                </tr>
            </thead>
            <tbody>
                {event_rows_html}
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
