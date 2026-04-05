# ============================================================
#  pages/3_🌍_Compare.py  —  World Comparison
# ============================================================

import streamlit as st
import plotly.graph_objects as go
from src import get_historical_df, WORLD_SHARE, build_share_chart, COLORS

st.set_page_config(page_title="Compare | India PopPredict", page_icon="🌍", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');
html,body,.stApp{font-family:'Inter',sans-serif!important;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:1.5rem 2rem 3rem!important;max-width:1400px!important;}
[data-testid="metric-container"]{background:#111827!important;border:1px solid rgba(255,255,255,.07)!important;border-radius:14px!important;padding:16px 20px!important;}
[data-testid="stMetricLabel"]{font-size:.72rem!important;text-transform:uppercase;letter-spacing:.08em;color:#94a3b8!important;}
[data-testid="stMetricValue"]{font-family:'Space Grotesk',sans-serif!important;font-size:1.45rem!important;font-weight:700!important;}
[data-testid="stPlotlyChart"]{border:1px solid rgba(255,255,255,.07);border-radius:14px;overflow:hidden;}
[data-testid="stPlotlyChart"]:hover{border-color:rgba(59,130,246,.25);box-shadow:0 4px 40px rgba(0,0,0,.4);}
hr{border-color:rgba(255,255,255,.07)!important;}
.page-title{font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:800;
            background:linear-gradient(135deg,#f97316,#ec4899);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:.25rem;}
.page-sub{color:#94a3b8;font-size:.9rem;margin-bottom:1.5rem;}
.section-title{font-family:'Space Grotesk',sans-serif;font-size:1rem;font-weight:700;color:#f0f6ff;}
.section-sub{font-size:.75rem;color:#94a3b8;margin-bottom:.75rem;}
.country-card{background:#111827;border:1px solid rgba(255,255,255,.07);border-radius:14px;padding:1.25rem 1.5rem;}
.country-flag{font-size:2rem;margin-bottom:.5rem;}
.country-name{font-family:'Space Grotesk',sans-serif;font-size:.95rem;font-weight:700;color:#f0f6ff;}
.country-pop{font-family:'Space Grotesk',sans-serif;font-size:1.5rem;font-weight:800;
             background:linear-gradient(135deg,#3b82f6,#8b5cf6);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.country-rank{font-size:.72rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.08em;}
</style>""", unsafe_allow_html=True)

# ── Country data ──────────────────────────────────────────────
COUNTRIES_2024 = [
    ("🇮🇳","India",         1_441_719_852, "#f97316", 1),
    ("🇨🇳","China",         1_419_321_278, "#3b82f6", 2),
    ("🇺🇸","USA",             341_814_420, "#10b981", 3),
    ("🇮🇩","Indonesia",       277_534_122, "#8b5cf6", 4),
    ("🇵🇰","Pakistan",        245_209_815, "#ec4899", 5),
    ("🇧🇷","Brazil",          215_313_498, "#f59e0b", 6),
    ("🇳🇬","Nigeria",         229_152_217, "#14b8a6", 7),
    ("🇧🇩","Bangladesh",      173_562_364, "#6366f1", 8),
]

# ── Page header ───────────────────────────────────────────────
st.markdown('<div class="page-title">🌍 Global Comparison</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">India\'s place in the world — share of global population, rank history, and country-by-country comparison</div>', unsafe_allow_html=True)

# ── Top country cards ─────────────────────────────────────────
st.markdown('<div class="section-title">Top 8 Most Populous Countries (2024)</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Showing raw population numbers and world rank</div>', unsafe_allow_html=True)

cols = st.columns(8)
for col,(flag,name,pop,color,rank) in zip(cols,COUNTRIES_2024):
    with col:
        st.markdown(f"""
        <div class="country-card" style="border-color:{color}33;">
          <div class="country-flag">{flag}</div>
          <div class="country-name">{name}</div>
          <div class="country-pop" style="background:linear-gradient(135deg,{color},{color}99);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            {pop/1e9:.2f}B
          </div>
          <div class="country-rank">#{rank} World</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── World population bar chart ────────────────────────────────
st.markdown('<div class="section-title">Population Comparison Bar Chart</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Absolute population (billions) — India leads since 2023</div>', unsafe_allow_html=True)

fig_bar = go.Figure(go.Bar(
    x=[c[1] for c in COUNTRIES_2024],
    y=[c[2]/1e9 for c in COUNTRIES_2024],
    text=[f"{c[2]/1e9:.2f}B" for c in COUNTRIES_2024],
    textposition="outside",
    textfont=dict(color="#f0f6ff", size=11),
    marker=dict(
        color=[c[3] for c in COUNTRIES_2024],
        cornerradius=6,
        line=dict(width=0),
    ),
    hovertemplate="<b>%{x}</b><br>Population: %{y:.3f}B<extra></extra>",
))
fig_bar.update_layout(
    paper_bgcolor=COLORS["card"], plot_bgcolor=COLORS["card"],
    font=dict(family="Inter,sans-serif", color=COLORS["muted"]),
    yaxis=dict(title="Population (Billions)", gridcolor=COLORS["grid"],
               linecolor=COLORS["border"], tickfont=dict(color=COLORS["muted"])),
    xaxis=dict(gridcolor="transparent", linecolor=COLORS["border"]),
    margin=dict(l=20,r=20,t=30,b=30), height=320,
    showlegend=False,
    hoverlabel=dict(bgcolor="#0d1117", bordercolor=COLORS["blue"], font=dict(color=COLORS["text"])),
)
st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── India vs China share chart ────────────────────────────────
col1, col2 = st.columns([2,1])
with col1:
    st.markdown('<div class="section-title">India vs China — Share of World Population</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Percentage of global population since 1950, with projections to 2050</div>', unsafe_allow_html=True)
    st.plotly_chart(build_share_chart(WORLD_SHARE), use_container_width=True)

with col2:
    st.markdown('<div class="section-title">World Share Snapshot</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Key years comparison</div>', unsafe_allow_html=True)
    snap_years = [1950, 1980, 2000, 2023, 2024, 2050]
    snap_india  = [14.2, 15.2, 16.5, 17.8, 17.8, 16.4]
    snap_china  = [21.7, 22.1, 20.6, 17.8, 17.6, 15.0]
    import pandas as pd
    snap_df = pd.DataFrame({
        "Year":  snap_years,
        "🇮🇳 India (%)": snap_india,
        "🇨🇳 China (%)": snap_china,
        "Gap":  [round(c-i,1) for i,c in zip(snap_india,snap_china)],
    })
    st.dataframe(snap_df, use_container_width=True, hide_index=True, height=260)
    st.caption("Negative gap = India leads. India surpassed China in 2023.")

st.markdown("<br>", unsafe_allow_html=True)

# ── Context callouts ──────────────────────────────────────────
st.markdown('<div class="section-title">📌 Why India Surpassed China in 2023</div>', unsafe_allow_html=True)
c1,c2,c3 = st.columns(3)
for col,title,body in zip([c1,c2,c3],[
    "🇨🇳 China's One-Child Policy",
    "🇮🇳 India's Younger Demographics",
    "📉 Diverging Trajectories",
],[
    "China's strict one-child policy (1980–2015) dramatically slowed its birth rate, causing its population to plateau and begin declining after 2022.",
    "India has a much younger median age (~28 vs ~39 in China), meaning more people in reproductive age cohorts, sustaining higher birth rates.",
    "China's population is now declining while India's still growing (≈0.89%/yr). By 2050, India is projected to have ~200M more people than China.",
]):
    with col:
        st.markdown(f"""
        <div style="background:#111827;border:1px solid rgba(255,255,255,.07);border-radius:14px;padding:1.25rem 1.5rem;">
          <div style="font-family:'Space Grotesk',sans-serif;font-size:.9rem;font-weight:700;
                      color:#f0f6ff;margin-bottom:.4rem;">{title}</div>
          <div style="font-size:.78rem;color:#94a3b8;line-height:1.7;">{body}</div>
        </div>""", unsafe_allow_html=True)
