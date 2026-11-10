import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Simulate what climate_impact_view does
from dashboard.utils.theme import get_plot_layout, get_axis_colors
import plotly.graph_objects as go

theme_mode = "dark"
plot_layout = get_plot_layout(theme_mode)
axis_colors = get_axis_colors(theme_mode)

print("plot_layout keys:", list(plot_layout.keys()))

# Test the _render_regional_comparison_chart call pattern
fig = go.Figure(go.Bar(x=[1,2], y=["a","b"], orientation="h"))
try:
    fig.update_layout(
        **plot_layout,
        margin=dict(l=10, r=80, t=40, b=10),
        height=220,
        title=dict(text="Test", font=dict(size=13, color=axis_colors["title_color"]), x=0.01),
        xaxis=dict(showgrid=True, gridcolor=axis_colors["gridcolor"], title="kg CO2e"),
        yaxis=dict(showgrid=False, autorange="reversed"),
    )
    print("SUCCESS: _render_regional_comparison_chart pattern works")
except TypeError as e:
    print(f"FAIL: {e}")

# Test _render_efficiency_chart pattern
fig2 = go.Figure()
try:
    fig2.update_layout(
        **plot_layout,
        margin=dict(l=40, r=20, t=40, b=30),
        height=240,
        barmode="group",
        title=dict(text="COP", font=dict(size=13, color=axis_colors["title_color"]), x=0.01),
        yaxis=dict(title="COP", showgrid=True, gridcolor=axis_colors["gridcolor"], range=[0, 5]),
    )
    print("SUCCESS: _render_efficiency_chart pattern works")
except TypeError as e:
    print(f"FAIL: {e}")

