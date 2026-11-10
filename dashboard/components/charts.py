"""
charts.py - Plotly Visualizations for Temperature & Energy Monitoring

Provides high-resolution, interactive charts styled with a dark navy/charcoal IoT aesthetic:
- Multi-series Temperature Tracking (Supply, Return, Setpoint, Outdoor, ESP32 probe)
- Power Draw & Delta-T Modulation Overview
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


from dashboard.utils.theme import get_plot_layout, get_current_theme, get_axis_colors

DARK_PLOT_LAYOUT = get_plot_layout("dark")


def render_temperature_chart(df: pd.DataFrame, time_range_label: str, theme_mode: str = None):
    """
    Renders the primary multi-channel temperature monitoring line chart.
    """
    if theme_mode is None:
        theme_mode = get_current_theme()
    plot_layout = get_plot_layout(theme_mode)
    axis_colors = get_axis_colors(theme_mode)

    fig = go.Figure()

    # Outdoor Ambient Temp
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["outdoor_ambient_temp"],
        name="Outdoor Ambient",
        mode="lines",
        line=dict(color="#F59E0B", width=1.6, dash="dot"),
        hovertemplate="Outdoor: %{y:.1f}°C<extra></extra>"
    ))

    # Return Air Temp (Indoor ambient)
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["return_air_temp"],
        name="Return Air (Indoor)",
        mode="lines",
        line=dict(color="#A78BFA", width=2.2),
        hovertemplate="Return Air: %{y:.1f}°C<extra></extra>"
    ))

    # Setpoint Temp
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["setpoint_temp"],
        name="Setpoint",
        mode="lines",
        line=dict(color="#64748B", width=1.5, dash="dash"),
        hovertemplate="Setpoint: %{y:.1f}°C<extra></extra>"
    ))

    # Supply Air Temp (Evaporator coil)
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["supply_air_temp"],
        name="Supply Air (Vent)",
        mode="lines",
        line=dict(color="#38BDF8", width=2.5),
        hovertemplate="Supply Air: %{y:.1f}°C<extra></extra>"
    ))

    # ESP32 DS18B20 Telemetry sample points (subsampled for clean display)
    step = max(1, len(df) // 25)
    sample_df = df.iloc[::step]
    fig.add_trace(go.Scatter(
        x=sample_df["timestamp"],
        y=sample_df["esp32_ds18b20_temp"],
        name="ESP32 DS18B20",
        mode="markers",
        marker=dict(color="#10B981", size=6, symbol="diamond-open", line=dict(width=1.5, color="#10B981")),
        hovertemplate="ESP32 Probe: %{y:.2f}°C<extra></extra>"
    ))

    # Axes styling
    fig.update_layout(
        **plot_layout,
        height=380,
        margin=dict(l=40, r=20, t=35, b=40),
        title=dict(
            text=f"<b>Multi-Point Temperature Dynamics</b> ({time_range_label})",
            font=dict(size=14, color=axis_colors["title_color"]),
            x=0.01,
            y=0.98
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor=axis_colors["gridcolor"],
            zeroline=False,
            showline=True,
            linecolor=axis_colors["linecolor"],
            tickformat="%H:%M"
        ),
        yaxis=dict(
            title=dict(
                text="Temperature (°C)",
                font=dict(color=axis_colors["text_color"], size=11)
            ),
            showgrid=True,
            gridcolor=axis_colors["gridcolor"],
            zeroline=False,
            showline=True,
            linecolor=axis_colors["linecolor"]
        )
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_energy_and_delta_t_chart(df: pd.DataFrame, theme_mode: str = None):
    """
    Renders synchronized twin-panel view:
    1. Thermal Delta-T (Return - Supply) with optimal performance bands
    2. Power Consumption Draw (kW)
    """
    if theme_mode is None:
        theme_mode = get_current_theme()
    plot_layout = get_plot_layout(theme_mode)
    axis_colors = get_axis_colors(theme_mode)
    is_dark = (theme_mode == "dark")
    annotation_color = "#E2E8F0" if is_dark else "#0F172A"
    yaxis_color = axis_colors["text_color"]

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        subplot_titles=(
            "Thermal Differential (ΔT = Return − Supply)",
            "Compressor Power Profile (kW)"
        )
    )

    # 1. Delta-T trace
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["delta_t"],
            name="ΔT Differential",
            mode="lines",
            line=dict(color="#06B6D4", width=2.2),
            fill="tozeroy",
            fillcolor="rgba(6, 182, 212, 0.08)",
            hovertemplate="ΔT: %{y:.1f}°C<extra></extra>"
        ),
        row=1, col=1
    )

    # Benchmark guideline at 8.0°C (Healthy cooling threshold)
    fig.add_hline(
        y=8.0,
        line=dict(color="#10B981", width=1.2, dash="dash"),
        annotation_text="Healthy Min Threshold (8°C)",
        annotation_position="bottom right",
        annotation_font=dict(color="#10B981", size=9),
        row=1, col=1
    )

    # 2. Power Consumption trace
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["power_kw"],
            name="Power Draw",
            mode="lines",
            line=dict(color="#3B82F6", width=2),
            fill="tozeroy",
            fillcolor="rgba(59, 130, 246, 0.1)",
            hovertemplate="Power: %{y:.2f} kW<extra></extra>"
        ),
        row=2, col=1
    )

    fig.update_layout(
        **plot_layout,
        height=380,
        margin=dict(l=40, r=20, t=35, b=40),
        showlegend=False,
    )

    # Style subplot title colors
    for annotation in fig["layout"]["annotations"]:
        annotation["font"] = dict(size=12, color=annotation_color)

    fig.update_xaxes(
        showgrid=True,
        gridcolor=axis_colors["gridcolor"],
        linecolor=axis_colors["linecolor"],
        tickformat="%H:%M",
        row=2, col=1
    )
    fig.update_yaxes(
        title_text="ΔT (°C)",
        title_font=dict(size=10, color=yaxis_color),
        showgrid=True,
        gridcolor=axis_colors["gridcolor"],
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="Power (kW)",
        title_font=dict(size=10, color=yaxis_color),
        showgrid=True,
        gridcolor=axis_colors["gridcolor"],
        row=2, col=1
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
