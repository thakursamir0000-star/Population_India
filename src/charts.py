# ============================================================
#  charts.py  –  Plotly chart builders
# ============================================================

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# ── Theme palette ─────────────────────────────────────────────
COLORS = {
    "bg":        "#060814",
    "surface":   "#0d1117",
    "card":      "#111827",
    "border":    "rgba(255,255,255,0.07)",
    "blue":      "#3b82f6",
    "orange":    "#f97316",
    "green":     "#10b981",
    "purple":    "#8b5cf6",
    "pink":      "#ec4899",
    "yellow":    "#f59e0b",
    "text":      "#f0f6ff",
    "muted":     "#94a3b8",
    "grid":      "rgba(255,255,255,0.05)",
}

BASE_LAYOUT = dict(
    paper_bgcolor = COLORS["card"],
    plot_bgcolor  = COLORS["card"],
    font          = dict(family="Inter, sans-serif", color=COLORS["muted"], size=12),
    margin        = dict(l=20, r=20, t=40, b=20),
    legend        = dict(
        bgcolor      = "rgba(255,255,255,0.04)",
        bordercolor  = COLORS["border"],
        borderwidth  = 1,
        font         = dict(size=11, color=COLORS["text"]),
    ),
    xaxis = dict(
        gridcolor   = COLORS["grid"],
        linecolor   = COLORS["border"],
        tickfont    = dict(color=COLORS["muted"]),
        zerolinecolor = COLORS["border"],
    ),
    yaxis = dict(
        gridcolor   = COLORS["grid"],
        linecolor   = COLORS["border"],
        tickfont    = dict(color=COLORS["muted"]),
        zerolinecolor = COLORS["border"],
    ),
    hoverlabel = dict(
        bgcolor   = "#0d1117",
        bordercolor = COLORS["blue"],
        font      = dict(color=COLORS["text"], size=12),
    ),
)


# ════════════════════════════════════════════════════════
#  1. MAIN FORECAST CHART  (historical + 3 model lines)
# ════════════════════════════════════════════════════════
def build_forecast_chart(hist_df: pd.DataFrame, forecast_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    # Historical area
    fig.add_trace(go.Scatter(
        x=hist_df["year"], y=hist_df["population_B"],
        name="Historical",
        mode="lines",
        line=dict(color=COLORS["blue"], width=3),
        fill="tozeroy",
        fillcolor="rgba(59,130,246,0.12)",
        hovertemplate="<b>%{x}</b><br>Population: %{y:.3f}B<extra></extra>",
    ))

    model_cfg = [
        ("Linear",     COLORS["orange"], "dot"),
        ("Polynomial", COLORS["green"],  "solid"),
        ("Logistic",   COLORS["purple"], "dash"),
    ]

    for col, color, dash in model_cfg:
        fig.add_trace(go.Scatter(
            x=forecast_df["year"],
            y=forecast_df[col] / 1e9,
            name=col,
            mode="lines",
            line=dict(color=color, width=2.5, dash=dash),
            hovertemplate=f"<b>%{{x}}</b><br>{col}: %{{y:.3f}}B<extra></extra>",
        ))

    # Vertical "now" line
    current_year = hist_df["year"].max()
    fig.add_vline(
        x=current_year, line_dash="dot", line_color="rgba(255,255,255,0.25)",
        annotation_text=f"{current_year} (Now)", annotation_font_color=COLORS["muted"],
        annotation_position="top right",
    )

    layout = BASE_LAYOUT.copy()
    layout.update(
        title=dict(text="India Population Forecast: 1950 – 2075",
                   font=dict(size=16, color=COLORS["text"]), x=0.01),
        yaxis_title="Population (Billions)",
        xaxis_title="Year",
        height=420,
        legend=dict(**BASE_LAYOUT["legend"], orientation="h", x=0.01, y=1.12),
        margin=dict(l=20, r=20, t=60, b=30),
    )
    fig.update_layout(**layout)
    return fig


# ════════════════════════════════════════════════════════
#  2. ANNUAL GROWTH RATE CHART
# ════════════════════════════════════════════════════════
def build_growth_chart(hist_df: pd.DataFrame) -> go.Figure:
    df = hist_df.dropna(subset=["growth_rate"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["year"], y=df["growth_rate"],
        mode="lines",
        name="Growth Rate",
        line=dict(color=COLORS["green"], width=2.5),
        fill="tozeroy",
        fillcolor="rgba(16,185,129,0.12)",
        hovertemplate="<b>%{x}</b><br>Growth: %{y:.3f}%<extra></extra>",
    ))

    layout = BASE_LAYOUT.copy()
    layout.update(
        title=dict(text="Annual Growth Rate (%)", font=dict(size=14, color=COLORS["text"]), x=0.01),
        yaxis_title="Growth Rate (%)",
        height=280,
        margin=dict(l=20, r=20, t=45, b=20),
    )
    fig.update_layout(**layout)
    return fig


# ════════════════════════════════════════════════════════
#  3. DECADAL GROWTH BAR CHART
# ════════════════════════════════════════════════════════
def build_decadal_chart(decadal_data: dict) -> go.Figure:
    colors_grad = [
        "#3b82f6","#6366f1","#8b5cf6","#a855f7",
        "#ec4899","#f43f5e","#f97316",
    ]
    fig = go.Figure(go.Bar(
        x=decadal_data["period"],
        y=decadal_data["rate"],
        marker=dict(
            color=colors_grad,
            line=dict(width=0),
            cornerradius=6,
        ),
        text=[f"{r}%" for r in decadal_data["rate"]],
        textposition="outside",
        textfont=dict(color=COLORS["text"], size=11),
        hovertemplate="<b>%{x}</b><br>Growth: %{y}%<extra></extra>",
    ))
    layout = BASE_LAYOUT.copy()
    layout.update(
        title=dict(text="Decadal Census Growth Rate", font=dict(size=14, color=COLORS["text"]), x=0.01),
        yaxis_title="Growth Rate (%)",
        height=310,
        margin=dict(l=20, r=20, t=45, b=30),
        showlegend=False,
    )
    fig.update_layout(**layout)
    return fig


# ════════════════════════════════════════════════════════
#  4. MILESTONES BAR CHART
# ════════════════════════════════════════════════════════
def build_milestones_chart(milestone_data: dict) -> go.Figure:
    palette = [
        "#3b82f6","#6366f1","#8b5cf6","#a855f7","#ec4899",
        "#f43f5e","#f97316","#f59e0b","#eab308","#84cc16",
        "#22c55e","#10b981","#14b8a6",
    ]
    fig = go.Figure(go.Bar(
        x=milestone_data["milestone"],
        y=milestone_data["years_taken"],
        marker=dict(
            color=palette[:len(milestone_data["milestone"])],
            line=dict(width=0),
            cornerradius=6,
        ),
        text=milestone_data["years_taken"],
        textposition="outside",
        textfont=dict(color=COLORS["text"], size=11),
        hovertemplate="<b>%{x}</b><br>Took %{y} years<extra></extra>",
    ))
    layout = BASE_LAYOUT.copy()
    layout.update(
        title=dict(text="Years to Add Each 100 Million People", font=dict(size=14, color=COLORS["text"]), x=0.01),
        yaxis_title="Years",
        height=310,
        margin=dict(l=20, r=20, t=45, b=30),
        showlegend=False,
    )
    fig.update_layout(**layout)
    return fig


# ════════════════════════════════════════════════════════
#  5. WORLD SHARE LINE CHART
# ════════════════════════════════════════════════════════
def build_share_chart(share_data: dict) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=share_data["year"], y=share_data["india_share"],
        name="🇮🇳 India",
        mode="lines+markers",
        line=dict(color=COLORS["orange"], width=3),
        fill="tozeroy", fillcolor="rgba(249,115,22,0.1)",
        marker=dict(size=7, color=COLORS["orange"]),
        hovertemplate="<b>%{x}</b><br>India share: %{y}%<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=share_data["year"], y=share_data["china_share"],
        name="🇨🇳 China",
        mode="lines+markers",
        line=dict(color=COLORS["blue"], width=2.5, dash="dot"),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.07)",
        marker=dict(size=7, color=COLORS["blue"]),
        hovertemplate="<b>%{x}</b><br>China share: %{y}%<extra></extra>",
    ))
    layout = BASE_LAYOUT.copy()
    layout.update(
        title=dict(text="India vs China — % of World Population", font=dict(size=14, color=COLORS["text"]), x=0.01),
        yaxis_title="Share of World Population (%)",
        height=310,
        margin=dict(l=20, r=20, t=45, b=30),
        legend=dict(**BASE_LAYOUT["legend"], orientation="h", x=0.01, y=1.18),
    )
    fig.update_layout(**layout)
    return fig


# ════════════════════════════════════════════════════════
#  6. PREDICTION GAUGE CHART
# ════════════════════════════════════════════════════════
def build_confidence_gauge(confidence: int) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=confidence,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Confidence", "font": {"size": 14, "color": COLORS["muted"]}},
        number={"suffix": "%", "font": {"size": 28, "color": COLORS["text"]}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": COLORS["muted"], "tickfont": {"color": COLORS["muted"]}},
            "bar": {"color": COLORS["blue"]},
            "bgcolor": COLORS["card"],
            "borderwidth": 0,
            "steps": [
                {"range": [0,  50], "color": "rgba(239,68,68,0.15)"},
                {"range": [50, 75], "color": "rgba(245,158,11,0.15)"},
                {"range": [75,100], "color": "rgba(16,185,129,0.15)"},
            ],
            "threshold": {
                "line": {"color": COLORS["green"], "width": 2},
                "thickness": 0.8, "value": confidence,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        height=200,
        margin=dict(l=10, r=10, t=30, b=10),
        font=dict(color=COLORS["text"]),
    )
    return fig


# ════════════════════════════════════════════════════════
#  7. MODEL COMPARISON SCATTER  (R² bar chart)
# ════════════════════════════════════════════════════════
def build_model_accuracy_chart(stats_df: pd.DataFrame) -> go.Figure:
    r2_vals = [float(r.replace("R²: ", "")) for r in stats_df["R² Score"]]
    colors  = [COLORS["orange"], COLORS["green"], COLORS["purple"]]

    fig = go.Figure(go.Bar(
        x=stats_df["Model"],
        y=[float(v) for v in stats_df["R² Score"]],
        marker=dict(color=colors, cornerradius=6, line=dict(width=0)),
        text=[v for v in stats_df["R² Score"]],
        textposition="outside",
        textfont=dict(color=COLORS["text"], size=11),
        hovertemplate="<b>%{x}</b><br>R²: %{y:.6f}<extra></extra>",
    ))
    layout = BASE_LAYOUT.copy()
    layout.update(
        title=dict(text="Model R² Accuracy", font=dict(size=14, color=COLORS["text"]), x=0.01),
        yaxis=dict(**BASE_LAYOUT["yaxis"], range=[0.9, 1.0], title="R² Score"),
        height=250,
        margin=dict(l=20, r=20, t=45, b=20),
        showlegend=False,
    )
    fig.update_layout(**layout)
    return fig
