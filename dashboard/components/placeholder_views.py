"""
placeholder_views.py - Navigation Placeholders for Upcoming Modules

Provides informative, well-designed placeholder views for:
1. Fault Analysis (Isolation Forest + Random Forest classifier)
2. Energy & Climate Impact (kWh & kg CO2e emissions modeling)
"""

import streamlit as st


def render_fault_analysis_placeholder():
    """Renders the placeholder view for upcoming Fault Analysis module."""
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.6rem; font-weight: 800; color: #F8FAFC; margin-bottom: 0.25rem;">
            Fault Analysis & Diagnosis
        </h2>
        <div class="header-subtitle">
            Machine Learning Diagnostics • Random Forest Multi-Class Fault Classification
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Info banner
    st.markdown("""
    <div class="iot-card highlight" style="margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: flex-start; gap: 1rem;">
            <div style="background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 10px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; flex-shrink: 0;">
                🧠
            </div>
            <div>
                <div style="font-size: 1rem; font-weight: 700; color: #F8FAFC; margin-bottom: 0.3rem;">
                    Phase 2 Integration: Supervised Fault Classification
                </div>
                <div style="font-size: 0.84rem; color: #94A3B8; line-height: 1.5;">
                    The Fault Analysis pipeline is currently in development. Once trained against the NIST AC fault dataset,
                    this view will diagnose specific fault categories including <b>Refrigerant Undercharge</b>, 
                    <b>Refrigerant Overcharge</b>, <b>Outdoor Airflow Restriction</b>, and <b>Liquid Line Restrictions</b>.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Architectural Blueprint Preview
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="iot-card">
            <div class="iot-card-header">
                <span class="iot-card-title">Planned Classifier</span>
                <span class="badge badge-blue">Random Forest</span>
            </div>
            <div style="font-size: 0.82rem; color: #94A3B8; line-height: 1.5;">
                Multi-class ensemble model mapping thermal vectors, pressure differentials, and power signatures to 5 NIST fault states.
            </div>
            <hr style="margin: 0.75rem 0;"/>
            <div class="telemetry-row">
                <span class="telemetry-label">Target Accuracy</span>
                <span class="telemetry-val" style="color: #10B981;">> 92%</span>
            </div>
            <div class="telemetry-row">
                <span class="telemetry-label">Persistence</span>
                <span class="telemetry-val">joblib</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="iot-card">
            <div class="iot-card-header">
                <span class="iot-card-title">Fault Signatures</span>
                <span class="badge badge-neutral">NIST Spec</span>
            </div>
            <div style="font-size: 0.82rem; color: #94A3B8; line-height: 1.5;">
                Supports detection of low evaporator temperature gradients, abnormal condenser approach, and elevated continuous current.
            </div>
            <hr style="margin: 0.75rem 0;"/>
            <div class="telemetry-row">
                <span class="telemetry-label">Input Vectors</span>
                <span class="telemetry-val">7 Channels</span>
            </div>
            <div class="telemetry-row">
                <span class="telemetry-label">Real-time Inference</span>
                <span class="telemetry-val">&lt; 15 ms</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="iot-card">
            <div class="iot-card-header">
                <span class="iot-card-title">Prescriptive Action</span>
                <span class="badge badge-warning">Advisory</span>
            </div>
            <div style="font-size: 0.82rem; color: #94A3B8; line-height: 1.5;">
                Will provide automated maintenance severity ratings and recommendations to guide facility technicians.
            </div>
            <hr style="margin: 0.75rem 0;"/>
            <div class="telemetry-row">
                <span class="telemetry-label">Severity Levels</span>
                <span class="telemetry-val">3 Tiers</span>
            </div>
            <div class="telemetry-row">
                <span class="telemetry-label">Inspection Guide</span>
                <span class="telemetry-val" style="color: #60A5FA;">Automated</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_climate_impact_placeholder():
    """Renders the placeholder view for upcoming Energy & Climate Impact module."""
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.6rem; font-weight: 800; color: #F8FAFC; margin-bottom: 0.25rem;">
            Energy & Climate Impact
        </h2>
        <div class="header-subtitle">
            Carbon Accounting • Energy Efficiency & Grid Emission Impact
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="iot-card highlight" style="margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: flex-start; gap: 1rem;">
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; flex-shrink: 0;">
                🌱
            </div>
            <div>
                <div style="font-size: 1rem; font-weight: 700; color: #F8FAFC; margin-bottom: 0.3rem;">
                    Phase 3 Integration: Carbon Emissions & Efficiency Modeling
                </div>
                <div style="font-size: 0.84rem; color: #94A3B8; line-height: 1.5;">
                    Quantifies the environmental penalty of degraded AC operating conditions. Faulty units draw up to 40%
                    more electricity, multiplying carbon footprint and utility expenses.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="iot-card">
            <div class="iot-card-header">
                <span class="iot-card-title">Carbon Emission Formulation</span>
                <span class="badge badge-success">GHG Protocol</span>
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; background: rgba(10, 15, 25, 0.8); padding: 0.75rem; border-radius: 6px; color: #38BDF8; margin-bottom: 0.75rem;">
                CO2e (kg) = Energy (kWh) × Regional Emission Factor (kg/kWh)
            </div>
            <div style="font-size: 0.82rem; color: #94A3B8; line-height: 1.5;">
                Will calculate both actual measured footprint and excess emissions attributed to faulty operation.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="iot-card">
            <div class="iot-card-header">
                <span class="iot-card-title">Efficiency Degrade Tracking</span>
                <span class="badge badge-neutral">COP & SEER</span>
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; background: rgba(10, 15, 25, 0.8); padding: 0.75rem; border-radius: 6px; color: #FBBF24; margin-bottom: 0.75rem;">
                Excess Cost ($) = (kW_actual − kW_nominal) × Hours × Tariff
            </div>
            <div style="font-size: 0.82rem; color: #94A3B8; line-height: 1.5;">
                Translates machine degradation into financial savings potential and carbon offset equivalents.
            </div>
        </div>
        """, unsafe_allow_html=True)

