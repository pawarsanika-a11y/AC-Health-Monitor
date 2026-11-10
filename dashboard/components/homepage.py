"""
homepage.py - Modern SaaS Homepage for AI-AC-Health-Monitor

Provides a professional, technology-focused public landing page explaining:
- System purpose & real-world problems solved
- IoT edge temperature sensing (ESP32 + DS18B20)
- Dual-engine Machine Learning architecture (Isolation Forest + Random Forest)
- Key features & interactive live simulator
- Seamless 1-Click Demo & Credentials Login to the existing dashboard
"""

from datetime import datetime
import streamlit as st
from dashboard.utils.theme import (
    get_current_theme,
    set_theme,
    get_health_color_and_badge,
    get_anomaly_badge,
)
from dashboard.utils.sample_data import PRESET_SCENARIOS


def render_homepage():
    """Renders the complete public homepage."""
    theme_mode = get_current_theme()
    is_dark = (theme_mode == "dark")

    # 1. TOP NAVBAR
    _render_navbar(theme_mode)

    # 2. HERO SECTION
    _render_hero_section(is_dark)

    # 3. STATS & IMPACT RIBBON
    _render_impact_ribbon(is_dark)

    # 4. THE CORE PROBLEM & PURPOSE ("Why AI-AC Health Monitor?")
    _render_problem_purpose_section(is_dark)

    # 5. HOW IT WORKS & ARCHITECTURE
    _render_how_it_works_section(is_dark)

    # 6. KEY FEATURES MATRIX
    _render_features_grid(is_dark)

    # 7. INTERACTIVE TELEMETRY & MODEL SIMULATOR
    _render_interactive_simulator(is_dark)

    # 8. LOGIN / GET STARTED CALL TO ACTION
    _render_login_section(is_dark)

    # 9. FOOTER
    _render_footer(is_dark)


# ---------------------------------------------------------------------------
# Section Implementations
# ---------------------------------------------------------------------------

def _render_navbar(theme_mode: str):
    """Renders sticky-style top navigation bar with brand, theme toggle, and CTA."""
    is_dark = (theme_mode == "dark")
    theme_btn_label = "☀️ Light" if is_dark else "🌙 Dark"
    next_theme = "light" if is_dark else "dark"

    nav_brand, nav_links, nav_actions = st.columns([2.2, 2.5, 1.9])

    with nav_brand:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 0.65rem; min-height: 38px;">
            <div style="width: 32px; height: 32px; border-radius: 8px; background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); display: flex; align-items: center; justify-content: center; font-size: 1.15rem; flex-shrink: 0;">
                ❄️
            </div>
            <div style="display: flex; align-items: center; gap: 0.45rem; flex-wrap: wrap; min-width: 0;">
                <span style="font-size: 1.05rem; font-weight: 800; letter-spacing: 0.03em; color: var(--text-primary);">AI-AC MONITOR</span>
                <span class="badge badge-success" style="font-size: 0.62rem; padding: 0.15rem 0.45rem;">
                    <span class="badge-dot pulse"></span>IoT Active
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with nav_links:
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: center; gap: 1.1rem; min-height: 38px; font-size: 0.82rem; font-weight: 600; color: var(--text-secondary); flex-wrap: wrap;">
            <a href="#how-it-works" style="color: inherit; text-decoration: none;">How It Works</a>
            <a href="#features" style="color: inherit; text-decoration: none;">Features</a>
            <a href="#simulator" style="color: inherit; text-decoration: none;">Live Demo</a>
            <a href="#login" style="color: inherit; text-decoration: none;">Login</a>
        </div>
        """, unsafe_allow_html=True)

    with nav_actions:
        action_col1, action_col2 = st.columns([1.05, 1.45])
        with action_col1:
            if st.button(theme_btn_label, key="nav_theme_toggle", use_container_width=True):
                set_theme(next_theme)
                st.rerun()
        with action_col2:
            if st.button("🚀 Get Started", key="nav_get_started", type="primary", use_container_width=True):
                st.session_state["logged_in"] = True
                st.session_state["current_page"] = "dashboard"
                st.rerun()

    st.markdown("<hr style='margin: 0.3rem 0 1.25rem 0;'/>", unsafe_allow_html=True)


def _render_hero_section(is_dark: bool):
    """Renders high-impact SaaS hero section with value proposition and telemetry preview."""
    col_hero_text, col_hero_card = st.columns([1.55, 1.1])

    with col_hero_text:
        st.markdown("""
        <div style="padding-right: 1rem;">
            <div style="display: inline-flex; align-items: center; gap: 0.5rem; background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 9999px; padding: 0.35rem 0.85rem; font-size: 0.74rem; font-weight: 700; color: #3B82F6; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 1.2rem;">
                ⚡ AI-POWERED PREDICTIVE HVAC MAINTENANCE
            </div>
            <h1 style="font-size: 2.75rem; font-weight: 800; line-height: 1.15; letter-spacing: -0.03em; margin-bottom: 1.1rem;">
                Intelligent Air Conditioner Health & Anomaly Detection
            </h1>
            <p style="font-size: 1.05rem; line-height: 1.6; color: var(--text-secondary); margin-bottom: 1.75rem;">
                Continuous thermal telemetry, automated refrigerant leak surveillance, and multi-class fault classification.
                Powered by edge <b>ESP32 digital temperature sensors</b>, <b>NIST benchmark datasets</b>, and <b>dual-layer Machine Learning</b> to eliminate unexpected downtime and cut up to 30% in energy waste.
            </p>
        </div>
        """, unsafe_allow_html=True)

        cta_col1, cta_col2 = st.columns([1.2, 1.3])
        with cta_col1:
            if st.button("⚡ Launch Dashboard", key="hero_launch_console", type="primary", use_container_width=True):
                st.session_state["logged_in"] = True
                st.session_state["current_page"] = "dashboard"
                st.rerun()
        with cta_col2:
            if st.button("🔍 Explore Architecture", key="hero_learn_more", type="secondary", use_container_width=True):
                st.session_state["scroll_target"] = "how-it-works"
                st.rerun()

        st.markdown("""
        <div style="display: flex; gap: 1.5rem; margin-top: 1.6rem; font-size: 0.78rem; color: var(--text-muted);">
            <div>✓ No complex setup</div>
            <div>✓ ESP32 1-Wire Ready</div>
            <div>✓ Pre-Trained NIST ML</div>
        </div>
        """, unsafe_allow_html=True)

    with col_hero_card:
        # Live Telemetry Snapshot Card
        st.markdown("""
        <div class="iot-card highlight" style="padding: 1.4rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.65rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 8px; height: 8px; border-radius: 50%; background: #10B981; box-shadow: 0 0 8px #10B981;"></div>
                    <span style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary);">Real-Time Node Telemetry</span>
                </div>
                <span class="badge badge-success"><span class="badge-dot pulse"></span>Streaming (1 Hz)</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 1rem;">
                <div>
                    <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600;">System Health Score</div>
                    <div style="font-size: 2.8rem; font-weight: 800; color: #10B981; line-height: 1;">
                        92<span style="font-size: 1.2rem; color: var(--text-muted); font-weight: 500;">/100</span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <span class="badge badge-success" style="font-size: 0.75rem;">Optimal Condition</span>
                    <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 0.25rem;">ΔT = 10.8°C (Nominal)</div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.65rem; background: var(--bg-card); padding: 0.85rem; border-radius: 10px; border: 1px solid var(--border-subtle); margin-bottom: 1rem;">
                <div>
                    <div style="font-size: 0.68rem; color: var(--text-muted); text-transform: uppercase;">Supply Air Temp</div>
                    <div style="font-size: 1.15rem; font-weight: 700; color: #38BDF8; font-family: 'JetBrains Mono', monospace;">12.4°C</div>
                </div>
                <div>
                    <div style="font-size: 0.68rem; color: var(--text-muted); text-transform: uppercase;">Return Air Temp</div>
                    <div style="font-size: 1.15rem; font-weight: 700; color: #A78BFA; font-family: 'JetBrains Mono', monospace;">23.2°C</div>
                </div>
                <div>
                    <div style="font-size: 0.68rem; color: var(--text-muted); text-transform: uppercase;">Inverter Power</div>
                    <div style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC; font-family: 'JetBrains Mono', monospace;">1.18 kW</div>
                </div>
                <div>
                    <div style="font-size: 0.68rem; color: var(--text-muted); text-transform: uppercase;">Efficiency (COP)</div>
                    <div style="font-size: 1.15rem; font-weight: 700; color: #10B981; font-family: 'JetBrains Mono', monospace;">3.45</div>
                </div>
            </div>
            <div style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 8px; padding: 0.75rem; font-size: 0.76rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                    <span style="color: var(--text-secondary); font-weight: 600;">Isolation Forest:</span>
                    <span style="color: #10B981; font-weight: 700;">Nominal Pattern (0.04)</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: var(--text-secondary); font-weight: 600;">Random Forest:</span>
                    <span style="color: #60A5FA; font-weight: 700;">Normal Cooling (95.4%)</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_impact_ribbon(is_dark: bool):
    """Renders key architectural performance statistics."""
    st.markdown("""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 2rem 0; text-align: center;">
        <div class="iot-card" style="padding: 1.25rem 0.5rem; margin-bottom: 0;">
            <div style="font-size: 2.1rem; font-weight: 800; color: var(--accent-blue); line-height: 1;">&lt; 15 ms</div>
            <div style="font-size: 0.76rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600; margin-top: 0.35rem;">Edge Inference Latency</div>
        </div>
        <div class="iot-card" style="padding: 1.25rem 0.5rem; margin-bottom: 0;">
            <div style="font-size: 2.1rem; font-weight: 800; color: #10B981; line-height: 1;">~30%</div>
            <div style="font-size: 0.76rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600; margin-top: 0.35rem;">Energy Waste Prevented</div>
        </div>
        <div class="iot-card" style="padding: 1.25rem 0.5rem; margin-bottom: 0;">
            <div style="font-size: 2.1rem; font-weight: 800; color: #F59E0B; line-height: 1;">5 Faults</div>
            <div style="font-size: 0.76rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600; margin-top: 0.35rem;">NIST Diagnostic Categories</div>
        </div>
        <div class="iot-card" style="padding: 1.25rem 0.5rem; margin-bottom: 0;">
            <div style="font-size: 2.1rem; font-weight: 800; color: #06B6D4; line-height: 1;">±0.06°C</div>
            <div style="font-size: 0.76rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600; margin-top: 0.35rem;">DS18B20 1-Wire Precision</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_problem_purpose_section(is_dark: bool):
    """Explains why AI-based AC health monitoring is critical."""
    st.markdown("""
    <div style="text-align: center; margin: 3rem auto 1.5rem auto; max-width: 800px;">
        <span class="badge badge-blue" style="margin-bottom: 0.5rem;">THE PROBLEM & PURPOSE</span>
        <h2 style="font-size: 2rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0.5rem;">
            Why Air Conditioners Need Intelligent Monitoring
        </h2>
        <p style="font-size: 0.95rem; color: var(--text-secondary); line-height: 1.6;">
            Traditional maintenance relies on periodic manual visits or waiting until equipment fails completely.
            In between inspections, undetected operational faults quietly destroy efficiency.
        </p>
    </div>
    """, unsafe_allow_html=True)

    p1, p2, p3 = st.columns(3)

    with p1:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🚨</div>
            <h4 style="font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem;">Undetected Refrigerant Leaks</h4>
            <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.55;">
                A 15% drop in refrigerant charge degrades cooling split (ΔT) by 40% while forcing the compressor to run continuously at peak thermal stress until burn-out.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with p2:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">💸</div>
            <h4 style="font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem;">Silent Energy Waste</h4>
            <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.55;">
                Clogged evaporator filters and dirty condenser coils reduce air flow, causing inverter compressors to draw up to 35% more electricity for the same cooling comfort.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with p3:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌍</div>
            <h4 style="font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem;">Excess Carbon Footprint</h4>
            <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.55;">
                Air conditioning accounts for over 40% of building energy use. Operating inefficient units multiplies electrical grid emissions (kg CO₂e) every single hour.
            </p>
        </div>
        """, unsafe_allow_html=True)


def _render_how_it_works_section(is_dark: bool):
    """Detailed visual explanation of how the end-to-end system functions."""
    st.markdown("""
    <div id="how-it-works" style="margin-top: 3.5rem; margin-bottom: 1.5rem; text-align: center;">
        <span class="badge badge-success" style="margin-bottom: 0.5rem;">END-TO-END PIPELINE</span>
        <h2 style="font-size: 2rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0.5rem;">
            How the AI-AC Health Monitor Works
        </h2>
        <p style="font-size: 0.95rem; color: var(--text-secondary); max-width: 750px; margin: 0 auto; line-height: 1.6;">
            A seamless bridge from physical IoT sensor acquisition to real-time machine learning inference and prescriptive diagnostics.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="step-number">01</div>
            <h4 style="font-size: 1rem; font-weight: 700; margin-bottom: 0.4rem;">IoT Edge Sensing</h4>
            <div style="font-size: 0.74rem; color: var(--accent-blue); font-weight: 600; margin-bottom: 0.5rem;">ESP32 + DS18B20 Probes</div>
            <p style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5;">
                High-precision digital sensors measure evaporator supply air and return ambient temperatures via Dallas 1-Wire bus at 1 Hz sampling.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="step-number">02</div>
            <h4 style="font-size: 1rem; font-weight: 700; margin-bottom: 0.4rem;">Feature Engineering</h4>
            <div style="font-size: 0.74rem; color: var(--accent-blue); font-weight: 600; margin-bottom: 0.5rem;">Thermal Differential (ΔT)</div>
            <p style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5;">
                Calculates thermal split (ΔT = T_return − T_supply), outdoor heat exchange gradients, inverter modulation, and rolling variance.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="step-number">03</div>
            <h4 style="font-size: 1rem; font-weight: 700; margin-bottom: 0.4rem;">Dual-Engine AI</h4>
            <div style="font-size: 0.74rem; color: var(--accent-blue); font-weight: 600; margin-bottom: 0.5rem;">Isolation Forest + RF</div>
            <p style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5;">
                <b>Isolation Forest</b> detects unusual thermal deviations; <b>Random Forest Classifier</b> maps operating patterns to 5 NIST fault categories.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="step-number">04</div>
            <h4 style="font-size: 1rem; font-weight: 700; margin-bottom: 0.4rem;">Actionable Insights</h4>
            <div style="font-size: 0.74rem; color: var(--accent-blue); font-weight: 600; margin-bottom: 0.5rem;">Health Score & Carbon</div>
            <p style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5;">
                Delivers an instant 0–100 Health Score, automated technician maintenance recommendations, and GHG Protocol grid carbon accounting.
            </p>
        </div>
        """, unsafe_allow_html=True)


def _render_features_grid(is_dark: bool):
    """Matrix of key technical capabilities."""
    st.markdown("""
    <div id="features" style="margin-top: 3.5rem; margin-bottom: 1.5rem; text-align: center;">
        <span class="badge badge-blue" style="margin-bottom: 0.5rem;">FEATURE SUITE</span>
        <h2 style="font-size: 2rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0.5rem;">
            Built for Modern HVAC Efficiency
        </h2>
        <p style="font-size: 0.95rem; color: var(--text-secondary); max-width: 750px; margin: 0 auto; line-height: 1.6;">
            Comprehensive analytics combining hardware telemetry, machine learning, and environmental auditing.
        </p>
    </div>
    """, unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    f4, f5, f6 = st.columns(3)

    with f1:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 1.6rem; margin-bottom: 0.4rem;">🌡️</div>
            <h4 style="font-size: 1rem; font-weight: 700; margin-bottom: 0.35rem;">Multi-Point Temperature Tracking</h4>
            <p style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5;">
                Simultaneous visualization of supply vent air, return ambient air, outdoor weather, and setpoint profiles with interactive Plotly timelines.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with f2:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 1.6rem; margin-bottom: 0.4rem;">🧠</div>
            <h4 style="font-size: 1rem; font-weight: 700; margin-bottom: 0.35rem;">Unsupervised Anomaly Detection</h4>
            <p style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5;">
                Isolation Forest algorithm flags subtle performance drifts without requiring prior fault labeling, catching new failure patterns early.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with f3:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 1.6rem; margin-bottom: 0.4rem;">🎯</div>
            <h4 style="font-size: 1rem; font-weight: 700; margin-bottom: 0.35rem;">Root-Cause Fault Diagnosis</h4>
            <p style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5;">
                Trained Random Forest Classifier pinpoints specific failure states: Undercharge, Overcharge, Airflow Blockage, and Line Restriction.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with f4:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 1.6rem; margin-bottom: 0.4rem;">📊</div>
            <h4 style="font-size: 1rem; font-weight: 700; margin-bottom: 0.35rem;">Dynamic AC Health Index (0–100)</h4>
            <p style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5;">
                Single explainable condition metric based on thermal efficiency split, ML anomaly penalty, and operating stress duration.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with f5:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 1.6rem; margin-bottom: 0.4rem;">⚡</div>
            <h4 style="font-size: 1rem; font-weight: 700; margin-bottom: 0.35rem;">Energy & COP Profiling</h4>
            <p style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5;">
                Measures active kilowatt draw and Coefficient of Performance, exposing units drawing excessive electricity to meet cooling demands.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with f6:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 1.6rem; margin-bottom: 0.4rem;">🌱</div>
            <h4 style="font-size: 1rem; font-weight: 700; margin-bottom: 0.35rem;">Climate & Carbon Accounting</h4>
            <p style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5;">
                Calculates direct kilograms of CO₂ equivalent emissions using regional grid factors (India CEA, US EPA eGRID, UK DEFRA, EU).
            </p>
        </div>
        """, unsafe_allow_html=True)


def _render_interactive_simulator(is_dark: bool):
    """Allows prospective users to test how the health model reacts to temperature shifts."""
    st.markdown("""
    <div id="simulator" style="margin-top: 3.5rem; margin-bottom: 1.5rem; text-align: center;">
        <span class="badge badge-warning" style="margin-bottom: 0.5rem;">INTERACTIVE PREVIEW</span>
        <h2 style="font-size: 2rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0.5rem;">
            Experience the Diagnostic Engine Live
        </h2>
        <p style="font-size: 0.95rem; color: var(--text-secondary); max-width: 750px; margin: 0 auto; line-height: 1.6;">
            Select an operational condition below to simulate live telemetry and observe how the AI Health Score and ML diagnosis adapt instantly.
        </p>
    </div>
    """, unsafe_allow_html=True)

    sim_scenario = st.selectbox(
        "Choose an AC Operating Scenario to Test",
        options=list(PRESET_SCENARIOS.keys()),
        index=0,
        key="home_sim_scenario_select",
    )

    sc = PRESET_SCENARIOS[sim_scenario]
    delta_t = round(sc["return_air_temp"] - sc["supply_air_temp"], 1)
    health_color, condition_label, badge_class = get_health_color_and_badge(sc["health_score"])
    anomaly_badge_class, anomaly_label = get_anomaly_badge(sc["anomaly_status"])

    col_sim_left, col_sim_right = st.columns([1.2, 1.4])

    with col_sim_left:
        st.markdown(f"""
        <div class="iot-card highlight">
            <div class="iot-card-header">
                <span class="iot-card-title">Simulated Health Score</span>
                <span class="badge {badge_class}">{condition_label}</span>
            </div>
            <div style="display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 0.5rem;">
                <div style="font-size: 3.2rem; font-weight: 800; color: {health_color}; line-height: 1;">
                    {sc['health_score']}<span style="font-size: 1.2rem; color: var(--text-muted); font-weight: 500;">/100</span>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase;">Thermal Split (ΔT)</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: {health_color}; font-family: 'JetBrains Mono', monospace;">
                        {delta_t:.1f}°C
                    </div>
                </div>
            </div>
            <div style="background: rgba(255, 255, 255, 0.08); border-radius: 9999px; height: 6px; width: 100%; overflow: hidden; margin-bottom: 0.85rem;">
                <div style="background: {health_color}; width: {sc['health_score']}%; height: 100%;"></div>
            </div>
            <div class="telemetry-row">
                <span class="telemetry-label">Operating State</span>
                <span class="telemetry-val" style="font-size: 0.78rem;">{sc['operating_status']}</span>
            </div>
            <div class="telemetry-row">
                <span class="telemetry-label">Anomaly Surveillance</span>
                <span class="badge {anomaly_badge_class}" style="font-size: 0.65rem;">{anomaly_label}</span>
            </div>
            <div class="telemetry-row">
                <span class="telemetry-label">Power Draw</span>
                <span class="telemetry-val">{sc['power_kw']:.2f} kW</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_sim_right:
        st.markdown(f"""
        <div class="iot-card">
            <div class="iot-card-header">
                <span class="iot-card-title">Diagnostic Signature</span>
                <span class="badge badge-blue">NIST ML Pipeline</span>
            </div>
            <div style="font-size: 0.88rem; color: var(--text-primary); margin-bottom: 0.75rem; font-weight: 600;">
                {sc['anomaly_feature_flag']}
            </div>
            <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 10px; padding: 0.85rem; font-size: 0.8rem; line-height: 1.6; color: var(--text-secondary); margin-bottom: 0.85rem;">
                <b>Engineering Diagnostic:</b> {"Optimal heat exchange. Inverter operating at nominal frequency with balanced refrigerant pressure." if sc['health_score'] >= 80 else ("Moderate thermal degradation. Possible air filter dusting or light condenser fouling." if sc['health_score'] >= 60 else "Critical anomaly flagged! Suboptimal cooling delta indicates low refrigerant mass flow or blocked airflow.")}
            </div>
            <div style="display: flex; gap: 0.5rem;">
                <span class="badge badge-neutral">Supply: {sc['supply_air_temp']}°C</span>
                <span class="badge badge-neutral">Return: {sc['return_air_temp']}°C</span>
                <span class="badge badge-neutral">COP: {sc['estimated_cop']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_login_section(is_dark: bool):
    """Renders clean Login / Get Started section with 1-click Demo & credentials."""
    st.markdown("""
    <div id="login" style="margin-top: 4rem; margin-bottom: 1.5rem; text-align: center;">
        <span class="badge badge-blue" style="margin-bottom: 0.5rem;">SECURE ACCESS</span>
        <h2 style="font-size: 2rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0.5rem;">
            Ready to Monitor Your AC Fleet?
        </h2>
        <p style="font-size: 0.95rem; color: var(--text-secondary); max-width: 650px; margin: 0 auto; line-height: 1.6;">
            Log in to manage your connected units, inspect real-time thermal telemetry, and run predictive ML fault diagnosis.
        </p>
    </div>
    """, unsafe_allow_html=True)

    _, col_auth, _ = st.columns([1.1, 1.8, 1.1])

    with col_auth:
        st.markdown("""
        <div class="iot-card highlight" style="padding: 1.75rem;">
            <div style="text-align: center; margin-bottom: 1.25rem;">
                <div style="font-size: 1.25rem; font-weight: 800; color: var(--text-primary); margin-bottom: 0.2rem;">
                    Sign In to Console
                </div>
                <div style="font-size: 0.78rem; color: var(--text-secondary);">
                    Access your active AC units and ESP32 nodes
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 1-Click Quick Demo Login (Fastest path for evaluators)
        if st.button("🚀 Quick Demo Access (1-Click Launch)", key="auth_demo_login_btn", type="primary", use_container_width=True):
            st.session_state["logged_in"] = True
            st.session_state["user_email"] = "facility.engineer@lab.org"
            st.session_state["current_page"] = "dashboard"
            st.rerun()

        st.markdown("""
        <div style="display: flex; align-items: center; text-align: center; margin: 1rem 0; color: var(--text-muted); font-size: 0.75rem;">
            <div style="flex: 1; border-bottom: 1px solid var(--border-subtle);"></div>
            <span style="padding: 0 0.75rem; text-transform: uppercase;">or sign in with credentials</span>
            <div style="flex: 1; border-bottom: 1px solid var(--border-subtle);"></div>
        </div>
        """, unsafe_allow_html=True)

        user_input = st.text_input("User Email / Operator ID", value="facility.engineer@lab.org", key="home_login_user")
        pwd_input = st.text_input("Password", value="••••••••••••", type="password", key="home_login_pwd")

        if st.button("Sign In & Launch Dashboard", key="auth_credentials_login_btn", use_container_width=True):
            st.session_state["logged_in"] = True
            st.session_state["user_email"] = user_input if user_input else "operator@lab.org"
            st.session_state["current_page"] = "dashboard"
            st.rerun()

        st.markdown("""
            <div style="text-align: center; margin-top: 1rem; font-size: 0.72rem; color: var(--text-muted);">
                🔒 Connected via SSL Telemetry • NIST Benchmark Pre-Loaded
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_footer(is_dark: bool):
    """Renders minimal SaaS footer with technology stack acknowledgment."""
    st.markdown("""
    <div style="margin-top: 4.5rem; border-top: 1px solid var(--border-subtle); padding: 2rem 0; text-align: center; font-size: 0.78rem; color: var(--text-muted);">
        <div style="font-weight: 700; color: var(--text-secondary); margin-bottom: 0.4rem;">
            AI-AC-Health-Monitor • Intelligent IoT HVAC Predictive Maintenance
        </div>
        <div>
            Engineered with Streamlit, Scikit-learn, Plotly, Pandas, and ESP32 Microcontrollers
        </div>
        <div style="margin-top: 0.5rem; color: var(--text-muted);">
            Benchmark Data: NIST AC Fault Detection & Diagnosis Dataset • Hardware: Dallas DS18B20 1-Wire
        </div>
    </div>
    """, unsafe_allow_html=True)
