"""
sidebar.py - Navigation and Hardware Control Sidebar

Provides clean, professional navigation between Dashboard, Fault Analysis,
and Energy & Climate Impact views, along with hardware device status and simulation controls.
"""

from typing import Tuple
import streamlit as st
from dashboard.utils.sample_data import PRESET_SCENARIOS


def render_sidebar() -> Tuple[str, str, bool, str]:
    """
    Renders the sidebar navigation and IoT device telemetry controls.

    Returns:
        selected_nav: "Dashboard" | "Fault Analysis" | "Energy & Climate Impact"
        scenario: Selected operating condition scenario
        esp32_online: Hardware connection state
        unit_id: Selected AC Unit
    """
    with st.sidebar:
        # System Branding
        st.markdown("""
        <div style="padding: 0.25rem 0 1rem 0;">
            <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.35rem;">
                <div style="width: 10px; height: 10px; border-radius: 50%; background: #3B82F6; box-shadow: 0 0 10px #3B82F6;"></div>
                <span style="font-size: 1.05rem; font-weight: 800; letter-spacing: 0.04em; color: #F8FAFC;">AI-AC MONITOR</span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <span style="font-size: 0.72rem; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">IoT & ML Diagnostics</span>
                <span class="badge badge-success" style="font-size: 0.65rem; padding: 0.15rem 0.45rem;">
                    <span class="badge-dot pulse"></span>LIVE
                </span>
            </div>
        </div>
        <hr style="margin: 0.5rem 0 1.25rem 0;"/>
        """, unsafe_allow_html=True)

        # Primary Navigation
        st.markdown('<p style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #94A3B8; margin-bottom: 0.5rem;">Navigation</p>', unsafe_allow_html=True)
        nav_options = [
            "Dashboard",
            "Fault Analysis",
            "Energy & Climate Impact"
        ]
        selected_nav = st.radio(
            "Navigation Menu",
            options=nav_options,
            index=0,
            key="main_navigation",
            label_visibility="collapsed"
        )

        st.markdown("<hr style='margin: 1.25rem 0 1rem 0;'/>", unsafe_allow_html=True)

        # Unit Selection
        st.markdown('<p style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #94A3B8; margin-bottom: 0.4rem;">Target AC Unit</p>', unsafe_allow_html=True)
        unit_id = st.selectbox(
            "AC Unit",
            options=[
                "Unit 01 — Lab Split AC (1.5 Ton)",
                "Unit 02 — Server Zone AC (2.0 Ton)",
                "Unit 03 — Office Inverter AC (1.0 Ton)"
            ],
            index=0,
            key="selected_unit",
            label_visibility="collapsed"
        )

        # Simulation & Diagnostic Presets (Functional tester)
        st.markdown('<p style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #94A3B8; margin-top: 1rem; margin-bottom: 0.4rem;">Simulation Preset</p>', unsafe_allow_html=True)
        scenario = st.selectbox(
            "Operating Scenario",
            options=list(PRESET_SCENARIOS.keys()),
            index=0,
            key="selected_scenario",
            help="Switch between realistic operational conditions to evaluate dashboard behavior.",
            label_visibility="collapsed"
        )

        st.markdown("<hr style='margin: 1.25rem 0 1rem 0;'/>", unsafe_allow_html=True)

        # ESP32 Sensor Telemetry Card
        st.markdown('<p style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #94A3B8; margin-bottom: 0.5rem;">ESP32 Node Status</p>', unsafe_allow_html=True)
        
        esp32_online = st.toggle("ESP32 Sensor Link", value=True, key="esp32_toggle")

        status_class = "badge-success" if esp32_online else "badge-neutral"
        status_text = "CONNECTED" if esp32_online else "SIMULATED / OFFLINE"
        port_text = "COM3 (USB 115200)" if esp32_online else "N/A"
        rssi_text = "-56 dBm (Strong)" if esp32_online else "Disconnected"

        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 10px; padding: 0.85rem; font-size: 0.76rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span style="color: #94A3B8; font-weight: 600;">Status</span>
                <span class="badge {status_class}" style="font-size: 0.65rem; padding: 0.15rem 0.45rem;">
                    <span class="badge-dot"></span>{status_text}
                </span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.35rem;">
                <span style="color: #64748B;">Device</span>
                <span style="color: #CBD5E1; font-family: 'JetBrains Mono', monospace;">ESP32-WROOM-32D</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.35rem;">
                <span style="color: #64748B;">Probe</span>
                <span style="color: #CBD5E1; font-family: 'JetBrains Mono', monospace;">DS18B20 (1-Wire)</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.35rem;">
                <span style="color: #64748B;">Port / Bus</span>
                <span style="color: #CBD5E1; font-family: 'JetBrains Mono', monospace;">{port_text}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #64748B;">Telemetry RSSI</span>
                <span style="color: #CBD5E1; font-family: 'JetBrains Mono', monospace;">{rssi_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

        # Refresh Action
        if st.button("Refresh Telemetry", use_container_width=True, type="secondary"):
            st.rerun()

        # Footer info
        st.markdown("""
        <div style="padding-top: 1rem; text-align: center; color: #475569; font-size: 0.68rem;">
            AI-AC-Health-Monitor • Phase 1<br/>
            NIST Dataset & IoT Prototype Ready
        </div>
        """, unsafe_allow_html=True)

    return selected_nav, scenario, esp32_online, unit_id

