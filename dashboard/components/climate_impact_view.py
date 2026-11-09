"""
climate_impact_view.py — Live Energy & Climate Impact Dashboard View

Renders real energy and carbon emission calculations using
src/climate_impact.py, based on the current ACSystemState telemetry.
"""

from __future__ import annotations

from typing import Optional

import plotly.graph_objects as go
import streamlit as st

from dashboard.utils.ml_inference import MLInferenceResult, models_available
from dashboard.utils.sample_data import ACSystemState


def render_climate_impact_view(state: ACSystemState, ml_result: Optional[MLInferenceResult] = None):
    """
    Main entry point for the Energy & Climate Impact page.

    Parameters
    ----------
    state     : Current ACSystemState
    ml_result : MLInferenceResult (optional — for COP accuracy)
    """
    # Page header
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.6rem; font-weight: 800; color: #F8FAFC; margin-bottom: 0.25rem;">
            Energy &amp; Climate Impact
        </h2>
        <div class="header-subtitle">
            Carbon Accounting • Energy Efficiency &amp; Grid Emission Estimation
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Import and run the estimator
    try:
        from src.climate_impact import (
            estimate_climate_impact,
            compare_emission_factors,
            get_available_emission_factors,
            EMISSION_FACTORS,
            format_summary,
        )
        climate_available = True
    except ImportError:
        climate_available = False

    # Emission factor selector
    col_ef, col_tariff, _ = st.columns([1.5, 1.0, 1.5])
    with col_ef:
        ef_options = list(EMISSION_FACTORS.keys()) if climate_available else ["India Grid (CEA 2023)"]
        ef_key = st.selectbox(
            "Emission Factor Region",
            options=ef_options,
            index=0,
            key="emission_factor_select",
        )
    with col_tariff:
        tariff = st.number_input(
            "Electricity Tariff (₹/kWh)",
            min_value=1.0,
            max_value=20.0,
            value=7.50,
            step=0.25,
            key="tariff_input",
        )

    # Compute using real estimator
    if climate_available:
        result = estimate_climate_impact(
            power_kw=state.power_kw,
            runtime_hours=state.cycle_runtime_hours,
            estimated_cop=state.estimated_cop,
            emission_factor_key=ef_key,
            tariff_inr_per_kwh=tariff,
            is_power_estimated=True,
        )
        _render_kpi_row(result)
        _render_detail_cards(result)
        _render_regional_comparison_chart(result.energy_kwh)
        _render_efficiency_chart(state, result)
    else:
        st.warning(
            "Climate impact module not found. "
            "Ensure `src/climate_impact.py` exists and re-run the app."
        )
        _render_formula_placeholder()


# ---------------------------------------------------------------------------
# Sub-components
# ---------------------------------------------------------------------------

def _render_kpi_row(result):
    from src.climate_impact import ClimateResult
    col1, col2, col3, col4 = st.columns(4)

    kpis = [
        (col1, "⚡ Energy Used", f"{result.energy_kwh:.2f} kWh", "#60A5FA", "badge-blue", "Actual"),
        (col2, "🌱 Carbon Footprint", f"{result.carbon_kg_co2e:.3f} kg CO₂e", "#10B981", "badge-success", "Actual"),
        (col3, "💸 Electricity Cost", f"₹{result.cost_inr:.2f}", "#A78BFA", "badge-neutral", "Estimated"),
        (col4, "⚠ Excess Emissions", f"{result.excess_carbon_kg_co2e:.3f} kg CO₂e", "#F59E0B", "badge-warning", "Avoidable"),
    ]

    for col, title, value, color, badge, badge_text in kpis:
        with col:
            st.markdown(f"""
            <div class="iot-card">
                <div class="iot-card-header">
                    <span class="iot-card-title" style="font-size: 0.75rem;">{title}</span>
                    <span class="badge {badge}" style="font-size: 0.6rem;">{badge_text}</span>
                </div>
                <div style="font-size: 1.55rem; font-weight: 800; color: {color}; margin-top: 0.25rem;">
                    {value}
                </div>
                <div style="font-size: 0.72rem; color: #64748B; margin-top: 0.25rem;">
                    Over {result.runtime_hours:.1f}h run at {result.power_kw:.2f} kW avg
                </div>
            </div>
            """, unsafe_allow_html=True)


def _render_detail_cards(result):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="iot-card">
            <div class="iot-card-header">
                <span class="iot-card-title">Energy Calculation</span>
                <span class="badge badge-blue">Formula</span>
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;
                 background: rgba(10,15,25,0.8); padding: 0.75rem; border-radius: 6px;
                 color: #38BDF8; margin-bottom: 0.75rem; line-height: 1.8;">
                Energy = {result.power_kw:.3f} kW × {result.runtime_hours:.2f} h<br>
                       = <strong>{result.energy_kwh:.3f} kWh</strong>
            </div>
            <div class="telemetry-row">
                <span class="telemetry-label">Nominal Energy (Healthy COP)</span>
                <span class="telemetry-val">{result.nominal_energy_kwh:.3f} kWh</span>
            </div>
            <div class="telemetry-row">
                <span class="telemetry-label">Excess Energy (Wasted)</span>
                <span class="telemetry-val" style="color: #F59E0B;">{result.excess_energy_kwh:.3f} kWh</span>
            </div>
            <div class="telemetry-row">
                <span class="telemetry-label">Estimated COP</span>
                <span class="telemetry-val">{result.estimated_cop:.2f}</span>
            </div>
            {"<div style='margin-top:0.5rem; font-size:0.72rem; color:#F59E0B;'>⚠ Power is estimated — install a smart meter for measured values.</div>" if result.is_power_estimated else ""}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="iot-card">
            <div class="iot-card-header">
                <span class="iot-card-title">Carbon Calculation</span>
                <span class="badge badge-success">GHG Protocol</span>
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;
                 background: rgba(10,15,25,0.8); padding: 0.75rem; border-radius: 6px;
                 color: #34D399; margin-bottom: 0.75rem; line-height: 1.8;">
                CO₂e = {result.energy_kwh:.3f} kWh × {result.emission_factor_value} kg/kWh<br>
                     = <strong>{result.carbon_kg_co2e:.4f} kg CO₂e</strong>
            </div>
            <div class="telemetry-row">
                <span class="telemetry-label">Emission Factor</span>
                <span class="telemetry-val">{result.emission_factor_key}</span>
            </div>
            <div class="telemetry-row">
                <span class="telemetry-label">Avoidable Carbon</span>
                <span class="telemetry-val" style="color: #F59E0B;">{result.excess_carbon_kg_co2e:.4f} kg CO₂e</span>
            </div>
            <div class="telemetry-row">
                <span class="telemetry-label">Avoidable Cost</span>
                <span class="telemetry-val" style="color: #F59E0B;">₹{result.excess_cost_inr:.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_regional_comparison_chart(energy_kwh: float):
    from src.climate_impact import compare_emission_factors
    comparison = compare_emission_factors(energy_kwh)

    fig = go.Figure(go.Bar(
        x=list(comparison.values()),
        y=list(comparison.keys()),
        orientation="h",
        marker_color=["#3B82F6", "#10B981", "#34D399", "#60A5FA", "#6EE7B7"],
        text=[f"{v:.4f} kg" for v in comparison.values()],
        textposition="outside",
        textfont=dict(color="#94A3B8", size=10),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.5)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#94A3B8", size=11),
        margin=dict(l=10, r=80, t=40, b=10),
        height=220,
        title=dict(
            text=f"<b>Carbon Footprint by Grid Region</b> ({energy_kwh:.2f} kWh)",
            font=dict(size=13, color="#F8FAFC"), x=0.01,
        ),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="kg CO₂e"),
        yaxis=dict(showgrid=False, autorange="reversed"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _render_efficiency_chart(state: ACSystemState, result):
    """Bar chart comparing actual vs nominal COP."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Nominal COP (Healthy)",
        x=["COP Reference"],
        y=[3.5],
        marker_color="#10B981",
        width=0.3,
    ))
    fig.add_trace(go.Bar(
        name="Estimated COP (Current)",
        x=["COP Reference"],
        y=[state.estimated_cop],
        marker_color="#3B82F6" if state.estimated_cop >= 3.0 else ("#F59E0B" if state.estimated_cop >= 2.0 else "#EF4444"),
        width=0.3,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.5)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#94A3B8", size=11),
        margin=dict(l=40, r=20, t=40, b=30),
        height=240,
        barmode="group",
        title=dict(text="<b>COP Efficiency Comparison</b>", font=dict(size=13, color="#F8FAFC"), x=0.01),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=11, color="#CBD5E1"), bgcolor="rgba(15,23,42,0.7)"),
        yaxis=dict(title="COP", showgrid=True, gridcolor="rgba(255,255,255,0.05)", range=[0, 5]),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _render_formula_placeholder():
    st.markdown("""
    <div class="iot-card">
        <div class="iot-card-header">
            <span class="iot-card-title">Carbon Emission Formula</span>
            <span class="badge badge-success">GHG Protocol</span>
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;
             background: rgba(10,15,25,0.8); padding: 0.75rem; border-radius: 6px;
             color: #38BDF8; margin-bottom: 0.75rem;">
            CO2e (kg) = Energy (kWh) × Regional Emission Factor (kg/kWh)
        </div>
    </div>
    """, unsafe_allow_html=True)

