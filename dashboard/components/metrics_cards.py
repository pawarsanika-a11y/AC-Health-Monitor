"""
metrics_cards.py - Metric Cards & KPI Indicators

Renders polished IoT SaaS cards for:
1. AC Health Score (0-100)
2. AC Operating Status
3. Anomaly Detection Status (Isolation Forest)
4. Energy Consumption Overview
5. ESP32 Sensor Hardware Status
"""

import streamlit as st
from dashboard.utils.sample_data import ACSystemState
from dashboard.utils.theme import get_health_color_and_badge, get_anomaly_badge


def render_top_kpi_row(state: ACSystemState):
    """
    Renders top KPI cards: Health Score, Operating Status, Anomaly Status, and Live Power.
    """
    col1, col2, col3, col4 = st.columns([1.2, 1.1, 1.1, 1.0])

    health_color, condition_label, badge_class = get_health_color_and_badge(state.health_score)
    anomaly_badge_class, anomaly_label = get_anomaly_badge(state.anomaly_status)

    with col1:
        st.markdown(f"""
        <div class="iot-card highlight">
            <div class="iot-card-header">
                <span class="iot-card-title">AC Health Score</span>
                <span class="badge {badge_class}">
                    <span class="badge-dot"></span>{condition_label}
                </span>
            </div>
            <div class="health-hero">
                <div>
                    <div class="health-score-large" style="color: {health_color};">
                        {state.health_score}<span style="font-size: 1.15rem; color: #64748B; font-weight: 500;">/100</span>
                    </div>
                    <div class="health-score-desc">Estimated Condition Index</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; font-weight: 600;">Status Range</div>
                    <div style="font-size: 0.85rem; color: #F1F5F9; font-weight: 600;">{condition_label}</div>
                    <div style="font-size: 0.72rem; color: #10B981; font-weight: 600; margin-top: 0.2rem;">● Stable cycle</div>
                </div>
            </div>
            <!-- Progress Bar -->
            <div style="background: rgba(255, 255, 255, 0.08); border-radius: 9999px; height: 6px; width: 100%; overflow: hidden; margin-top: 0.65rem;">
                <div style="background: {health_color}; width: {state.health_score}%; height: 100%; border-radius: 9999px; transition: width 0.4s ease;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="iot-card">
            <div class="iot-card-header">
                <span class="iot-card-title">Operating Status</span>
                <span class="badge badge-blue">
                    <span class="badge-dot"></span>Active
                </span>
            </div>
            <div style="margin-top: 0.25rem;">
                <div style="font-size: 1.12rem; font-weight: 700; color: #F8FAFC; margin-bottom: 0.35rem; line-height: 1.3;">
                    {state.operating_status}
                </div>
                <div class="telemetry-row">
                    <span class="telemetry-label">Indoor Setpoint</span>
                    <span class="telemetry-val">{state.setpoint_temp:.1f}°C</span>
                </div>
                <div class="telemetry-row">
                    <span class="telemetry-label">Return Ambient</span>
                    <span class="telemetry-val">{state.return_air_temp:.1f}°C</span>
                </div>
                <div class="telemetry-row">
                    <span class="telemetry-label">Run Duration</span>
                    <span class="telemetry-val">{state.cycle_runtime_hours:.1f} hrs</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="iot-card">
            <div class="iot-card-header">
                <span class="iot-card-title">Anomaly Detection</span>
                <span class="badge {anomaly_badge_class}">
                    <span class="badge-dot"></span>{anomaly_label}
                </span>
            </div>
            <div style="margin-top: 0.25rem;">
                <div class="telemetry-row">
                    <span class="telemetry-label">Model Target</span>
                    <span class="telemetry-val" style="color: #60A5FA;">Isolation Forest</span>
                </div>
                <div class="telemetry-row">
                    <span class="telemetry-label">Anomaly Index</span>
                    <span class="telemetry-val">{state.anomaly_confidence:.2f}</span>
                </div>
                <div class="telemetry-row">
                    <span class="telemetry-label">Diagnostic Signature</span>
                    <span class="telemetry-val" style="font-size: 0.72rem; max-width: 130px; text-align: right; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="{state.anomaly_feature_flag}">{state.anomaly_feature_flag}</span>
                </div>
                <div class="telemetry-row">
                    <span class="telemetry-label">Safety State</span>
                    <span class="telemetry-val" style="color: {'#10B981' if state.anomaly_status == 'Normal Operation' else '#EF4444'};">
                        {'Nominal' if state.anomaly_status == 'Normal Operation' else 'Action Advised'}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="iot-card">
            <div class="iot-card-header">
                <span class="iot-card-title">Power & Energy</span>
                <span class="badge badge-neutral">Estimated</span>
            </div>
            <div style="margin-top: 0.25rem;">
                <div style="font-size: 1.7rem; font-weight: 700; color: #F8FAFC; line-height: 1.1;">
                    {state.power_kw:.2f} <span style="font-size: 0.95rem; font-weight: 500; color: #94A3B8;">kW</span>
                </div>
                <div style="font-size: 0.72rem; color: #64748B; margin-top: 0.2rem; margin-bottom: 0.5rem;">Current Inverter Draw</div>
                <div class="telemetry-row">
                    <span class="telemetry-label">Today's Usage</span>
                    <span class="telemetry-val">{state.daily_energy_kwh:.2f} kWh</span>
                </div>
                <div class="telemetry-row">
                    <span class="telemetry-label">Efficiency (COP)</span>
                    <span class="telemetry-val" style="color: #34D399;">{state.estimated_cop:.2f}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_hardware_status_banner(state: ACSystemState):
    """
    Renders the ESP32 sensor hardware telemetry banner.
    """
    esp_status_badge = "badge-success" if state.esp32_connected else "badge-danger"
    esp_status_label = "ONLINE • TELEMETRY ACTIVE" if state.esp32_connected else "OFFLINE • RECONNECT PROBE"
    dot_pulse = "pulse" if state.esp32_connected else ""

    col_a, col_b = st.columns([2.2, 1.0])

    with col_a:
        st.markdown(f"""
        <div class="iot-card" style="margin-bottom: 1.25rem; padding: 1.1rem 1.4rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <div style="display: flex; align-items: center; gap: 0.65rem;">
                    <div style="background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; font-size: 1.05rem;">
                        ⚡
                    </div>
                    <div>
                        <div style="font-size: 0.92rem; font-weight: 700; color: #F8FAFC;">ESP32 Hardware Telemetry Subsystem</div>
                        <div style="font-size: 0.74rem; color: #94A3B8;">Direct Microcontroller Interface • NIST Pre-processing Ready</div>
                    </div>
                </div>
                <span class="badge {esp_status_badge}">
                    <span class="badge-dot {dot_pulse}"></span>{esp_status_label}
                </span>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.85rem; background: rgba(10, 15, 25, 0.6); padding: 0.75rem 1rem; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.05);">
                <div>
                    <div style="font-size: 0.68rem; color: #64748B; text-transform: uppercase; font-weight: 600;">Device Model</div>
                    <div style="font-size: 0.82rem; font-weight: 600; color: #E2E8F0; font-family: 'JetBrains Mono', monospace;">{state.esp32_device_id}</div>
                </div>
                <div>
                    <div style="font-size: 0.68rem; color: #64748B; text-transform: uppercase; font-weight: 600;">Temperature Sensor</div>
                    <div style="font-size: 0.82rem; font-weight: 600; color: #E2E8F0; font-family: 'JetBrains Mono', monospace;">{state.esp32_sensor_type}</div>
                </div>
                <div>
                    <div style="font-size: 0.68rem; color: #64748B; text-transform: uppercase; font-weight: 600;">Communication Port</div>
                    <div style="font-size: 0.82rem; font-weight: 600; color: #60A5FA; font-family: 'JetBrains Mono', monospace;">{state.esp32_port}</div>
                </div>
                <div>
                    <div style="font-size: 0.68rem; color: #64748B; text-transform: uppercase; font-weight: 600;">Last Packet Ping</div>
                    <div style="font-size: 0.82rem; font-weight: 600; color: {'#10B981' if state.esp32_connected else '#EF4444'}; font-family: 'JetBrains Mono', monospace;">
                        {state.esp32_last_seen_sec}s ago (0% loss)
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        # Live Probe Direct Reading
        probe_reading = f"{state.supply_air_temp:.1f}°C" if state.esp32_connected else "N/A"
        delta_color = "#10B981" if state.delta_t >= 8.0 else ("#F59E0B" if state.delta_t >= 5.0 else "#EF4444")

        st.markdown(f"""
        <div class="iot-card" style="margin-bottom: 1.25rem; padding: 1.1rem 1.4rem;">
            <div class="iot-card-header" style="margin-bottom: 0.5rem; padding-bottom: 0.4rem;">
                <span class="iot-card-title">Live Probe Reading</span>
                <span class="badge badge-blue">DS18B20</span>
            </div>
            <div style="display: flex; align-items: baseline; justify-content: space-between;">
                <div>
                    <div style="font-size: 1.95rem; font-weight: 800; color: #38BDF8; font-family: 'JetBrains Mono', monospace;">
                        {probe_reading}
                    </div>
                    <div style="font-size: 0.72rem; color: #94A3B8;">Vent Supply Temperature</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.72rem; color: #64748B; font-weight: 600;">THERMAL SPLIT (ΔT)</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: {delta_color}; font-family: 'JetBrains Mono', monospace;">
                        {state.delta_t:.1f}°C
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

