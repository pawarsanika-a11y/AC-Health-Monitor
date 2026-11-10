"""
fault_analysis_view.py — Live Fault Analysis Dashboard View

Renders real ML-backed fault analysis when models are trained, or
a detailed placeholder with status when they are not.
"""

from __future__ import annotations

from typing import Optional

import plotly.graph_objects as go
import streamlit as st

from dashboard.utils.ml_inference import (
    MLInferenceResult,
    fault_model_available,
    models_available,
)
from dashboard.utils.sample_data import ACSystemState
from dashboard.utils.theme import get_current_theme, get_plot_layout, get_axis_colors


def render_fault_analysis_view(state: ACSystemState, ml_result: Optional[MLInferenceResult] = None):
    """
    Main entry point for the Fault Analysis page.

    Parameters
    ----------
    state     : Current ACSystemState (always present — used for telemetry context)
    ml_result : MLInferenceResult from run_inference(); None if models unavailable
    """
    # Page header
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.6rem; font-weight: 800; color: var(--text-primary); margin-bottom: 0.25rem;">
            Fault Analysis &amp; Diagnosis
        </h2>
        <div class="header-subtitle">
            Machine Learning Diagnostics • Isolation Forest + Random Forest Multi-Class Classifier
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ML readiness banner
    _render_model_status_banner(ml_result)

    # Main content
    col_left, col_right = st.columns([1.1, 1.0])

    with col_left:
        _render_anomaly_card(state, ml_result)
        _render_fault_card(state, ml_result)

    with col_right:
        _render_recommendation_card(ml_result)
        _render_fault_probability_chart(ml_result)


# ---------------------------------------------------------------------------
# Sub-components
# ---------------------------------------------------------------------------

def _render_model_status_banner(ml_result: Optional[MLInferenceResult]):
    if ml_result is None or ml_result.source == "demo_fallback":
        st.markdown("""
        <div class="iot-card highlight" style="margin-bottom: 1.5rem; border-color: rgba(245, 158, 11, 0.4);">
            <div style="display: flex; align-items: flex-start; gap: 1rem;">
                <div style="background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.3);
                     border-radius: 10px; width: 44px; height: 44px; display: flex; align-items: center;
                     justify-content: center; font-size: 1.4rem; flex-shrink: 0;">⚠️</div>
                <div>
                    <div style="font-size: 1rem; font-weight: 700; color: #FBBF24; margin-bottom: 0.3rem;">
                        Models Not Trained — Demo Mode Active
                    </div>
                    <div style="font-size: 0.84rem; color: #94A3B8; line-height: 1.5;">
                        Place NIST AC fault dataset CSV files in <code>data/raw/</code> and run
                        <code>python src/train_models.py</code> to activate real ML inference.
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif not fault_model_available():
        st.markdown("""
        <div class="iot-card highlight" style="margin-bottom: 1.5rem; border-color: rgba(59, 130, 246, 0.4);">
            <div style="display: flex; align-items: flex-start; gap: 1rem;">
                <div style="background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3);
                     border-radius: 10px; width: 44px; height: 44px; display: flex; align-items: center;
                     justify-content: center; font-size: 1.4rem; flex-shrink: 0;">🤖</div>
                <div>
                    <div style="font-size: 1rem; font-weight: 700; color: #60A5FA; margin-bottom: 0.3rem;">
                        Anomaly Detection Active — Fault Classifier Not Available
                    </div>
                    <div style="font-size: 0.84rem; color: #94A3B8; line-height: 1.5;">
                        Isolation Forest is running live. Random Forest fault classifier requires
                        labelled NIST fault data (<code>fault_label</code> column).
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="iot-card highlight" style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: flex-start; gap: 1rem;">
                <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3);
                     border-radius: 10px; width: 44px; height: 44px; display: flex; align-items: center;
                     justify-content: center; font-size: 1.4rem; flex-shrink: 0;">🧠</div>
                <div>
                    <div style="font-size: 1rem; font-weight: 700; color: #34D399; margin-bottom: 0.3rem;">
                        Full ML Pipeline Active
                    </div>
                    <div style="font-size: 0.84rem; color: #94A3B8; line-height: 1.5;">
                        Isolation Forest + Random Forest classifier both running on live telemetry.
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_anomaly_card(state: ACSystemState, ml_result: Optional[MLInferenceResult]):
    if ml_result is not None and ml_result.source == "ml_model":
        confidence = ml_result.anomaly_confidence
        status = ml_result.anomaly_status
    else:
        confidence = state.anomaly_confidence
        status = state.anomaly_status

    badge_cls = {
        "Normal Operation": "badge-success",
        "Warning Anomaly": "badge-warning",
        "Critical Anomaly": "badge-danger",
    }.get(status, "badge-neutral")

    bar_color = {
        "Normal Operation": "#10B981",
        "Warning Anomaly": "#F59E0B",
        "Critical Anomaly": "#EF4444",
    }.get(status, "#94A3B8")

    source_tag = "(Live ML)" if ml_result and ml_result.source == "ml_model" else "(Demo)"

    st.markdown(f"""
    <div class="iot-card">
        <div class="iot-card-header">
            <span class="iot-card-title">Anomaly Detection {source_tag}</span>
            <span class="badge {badge_cls}">
                <span class="badge-dot"></span>{status}
            </span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Model</span>
            <span class="telemetry-val" style="color: #60A5FA;">Isolation Forest</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Anomaly Confidence</span>
            <span class="telemetry-val">{confidence:.2f}</span>
        </div>
        <div style="margin-top: 0.75rem;">
            <div style="font-size: 0.72rem; color: #64748B; margin-bottom: 0.3rem; text-transform: uppercase;">Anomaly Index</div>
            <div style="background: rgba(255,255,255,0.08); border-radius: 9999px; height: 8px; overflow: hidden;">
                <div style="background: {bar_color}; width: {min(confidence * 100, 100):.1f}%;
                     height: 100%; border-radius: 9999px; transition: width 0.4s ease;"></div>
            </div>
        </div>
        <div style="margin-top: 0.75rem; font-size: 0.78rem; color: #94A3B8;">
            {state.anomaly_feature_flag}
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_fault_card(state: ACSystemState, ml_result: Optional[MLInferenceResult]):
    if ml_result and ml_result.predicted_fault is not None:
        fault = ml_result.predicted_fault
        prob = ml_result.fault_probability or 0.0
        severity = ml_result.fault_severity
        source_tag = "(Live RF)"
        prob_str = f"{prob * 100:.1f}%"
    else:
        fault = "Classifier not trained"
        prob_str = "N/A"
        severity = 0
        source_tag = "(Pending)"

    sev_color = "#10B981" if severity == 0 else ("#F59E0B" if severity < 25 else "#EF4444")

    st.markdown(f"""
    <div class="iot-card">
        <div class="iot-card-header">
            <span class="iot-card-title">Fault Diagnosis {source_tag}</span>
            <span class="badge badge-blue">Random Forest</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Predicted Fault</span>
            <span class="telemetry-val" style="color: {sev_color};">{fault}</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Model Confidence</span>
            <span class="telemetry-val">{prob_str}</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Severity Score</span>
            <span class="telemetry-val" style="color: {sev_color};">{severity} / 40</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Anomaly Penalty Applied</span>
            <span class="telemetry-val">{ml_result.anomaly_penalty if ml_result else '—'} pts</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_recommendation_card(ml_result: Optional[MLInferenceResult]):
    if ml_result and ml_result.recommendation:
        text = ml_result.recommendation
    else:
        text = "Train models with <code>python src/train_models.py</code> for automated fault recommendations."

    st.markdown(f"""
    <div class="iot-card">
        <div class="iot-card-header">
            <span class="iot-card-title">Maintenance Advisory</span>
            <span class="badge badge-warning">Advisory</span>
        </div>
        <div style="font-size: 0.84rem; color: #CBD5E1; line-height: 1.65; padding: 0.25rem 0;">
            {text}
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_fault_probability_chart(ml_result: Optional[MLInferenceResult]):
    """Render horizontal bar chart of fault class probabilities."""
    if ml_result is None or ml_result.all_fault_probabilities is None:
        # Placeholder chart with greyed-out bars
        labels = [
            "Normal", "Refrigerant Undercharge",
            "Refrigerant Overcharge", "Outdoor Airflow Restriction",
            "Liquid Line Restriction",
        ]
        values = [0.0] * len(labels)
        title = "Fault Class Probabilities (Awaiting Model)"
        bar_colors = ["#334155"] * len(labels)
    else:
        probs = ml_result.all_fault_probabilities
        labels = list(probs.keys())
        values = list(probs.values())
        title = "Fault Class Probabilities (Live RF)"
        bar_colors = []
        for lbl in labels:
            if lbl == ml_result.predicted_fault:
                bar_colors.append("#3B82F6")
            elif (probs.get(lbl, 0) or 0) > 0.15:
                bar_colors.append("#F59E0B")
            else:
                bar_colors.append("#1E293B")

    theme_mode = get_current_theme()
    plot_layout = get_plot_layout(theme_mode)
    axis_colors = get_axis_colors(theme_mode)

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker_color=bar_colors,
        text=[f"{v*100:.1f}%" for v in values],
        textposition="outside",
        textfont=dict(color=axis_colors["text_color"], size=11),
    ))
    fig.update_layout(
        **plot_layout,
        margin=dict(l=10, r=60, t=40, b=10),
        height=240,
        title=dict(text=f"<b>{title}</b>", font=dict(size=13, color=axis_colors["title_color"]), x=0.01),
        xaxis=dict(range=[0, 1.1], showgrid=True, gridcolor=axis_colors["gridcolor"], tickformat=".0%"),
        yaxis=dict(showgrid=False, autorange="reversed"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

