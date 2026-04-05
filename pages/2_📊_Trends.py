# ============================================================
#  pages/2_📊_Trends.py  —  Growth Analysis
# ============================================================

import streamlit as st
from src import (get_historical_df, DECADAL_DATA, MILESTONE_DATA,
                 build_growth_chart, build_decadal_chart, build_milestones_chart)

st.set_page_config(page_title="Trends | India PopPredict", page_icon="📊", layout="wide")

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
            background:linear-gradient(135deg,#10b981,#3b82f6);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:.25rem;}
.page-sub{color:#94a3b8;font-size:.9rem;margin-bottom:1.5rem;}
.section-title{font-family:'Space Grotesk',sans-serif;font-size:1rem;font-weight:700;color:#f0f6ff;}
.section-sub{font-size:.75rem;color:#94a3b8;margin-bottom:.75rem;}
.insight-card{background:#111827;border:1px solid rgba(255,255,255,.07);border-radius:14px;padding:1.25rem 1.5rem;margin-bottom:1rem;}
.insight-title{font-family:'Space Grotesk',sans-serif;font-size:.9rem;font-weight:700;color:#f0f6ff;margin-bottom:.4rem;}
.insight-body{font-size:.8rem;color:#94a3b8;line-height:1.7;}
</style>""", unsafe_allow_html=True)

@st.cache_resource(show_spinner="⚙️ Loading data…")
def load_data():
    return get_historical_df()

hist_df = load_data()

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 Display Options")
    yr_range = st.slider("Year Range", 1950, 2025, (1950, 2025))
    st.markdown("---")
    st.caption("Showing annual & decadal growth trends based on UN data and Census of India.")

# ── Page header ───────────────────────────────────────────────
st.markdown('<div class="page-title">📊 Growth Trends Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Detailed breakdown of India\'s population growth patterns across different time horizons</div>', unsafe_allow_html=True)

# ── Summary metrics ───────────────────────────────────────────
df_filtered = hist_df[(hist_df["year"]>=yr_range[0]) & (hist_df["year"]<=yr_range[1])]
peak_gr  = df_filtered["growth_rate"].max()
peak_yr  = int(df_filtered.loc[df_filtered["growth_rate"].idxmax(), "year"])
avg_gr   = df_filtered["growth_rate"].mean()
total_added = int(df_filtered["population"].iloc[-1] - df_filtered["population"].iloc[0])

m1,m2,m3,m4 = st.columns(4)
with m1: st.metric("📈 Peak Growth Rate",  f"{peak_gr:.2f}%", f"in {peak_yr}")
with m2: st.metric("📉 Avg Growth Rate",   f"{avg_gr:.2f}%",  f"{yr_range[0]}–{yr_range[1]}")
with m3: st.metric("➕ People Added",      f"{total_added/1e6:.0f}M", f"over {yr_range[1]-yr_range[0]} years")
with m4: st.metric("📅 Years Analysed",    str(yr_range[1]-yr_range[0]), f"{yr_range[0]} to {yr_range[1]}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Annual growth rate chart ──────────────────────────────────
st.markdown('<div class="section-title">Annual Growth Rate (%)</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Year-over-year percentage change in population within your selected range</div>', unsafe_allow_html=True)

fig_gr = build_growth_chart(df_filtered)
fig_gr.update_layout(height=320)
st.plotly_chart(fig_gr, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Decadal + Milestones side-by-side ────────────────────────
col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="section-title">Decadal Census Growth Rate</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Official census-recorded growth % per decade</div>', unsafe_allow_html=True)
    st.plotly_chart(build_decadal_chart(DECADAL_DATA), use_container_width=True)

with col2:
    st.markdown('<div class="section-title">Population Milestone Speed</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Years taken to add each successive 100 million people</div>', unsafe_allow_html=True)
    st.plotly_chart(build_milestones_chart(MILESTONE_DATA), use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Key insights ─────────────────────────────────────────────
st.markdown('<div class="section-title">📌 Key Insights</div>', unsafe_allow_html=True)

i1,i2,i3 = st.columns(3)
with i1:
    st.markdown("""
    <div class="insight-card">
      <div class="insight-title">🏆 Fastest Growth Period</div>
      <div class="insight-body">India's fastest decadal growth was <b style="color:#10b981;">24.8%</b>
      during 1961–71, adding ~100M people in just 10 years.
      This was driven by improved healthcare reducing mortality rates.</div>
    </div>""", unsafe_allow_html=True)
with i2:
    st.markdown("""
    <div class="insight-card">
      <div class="insight-title">📉 Growth Slowdown</div>
      <div class="insight-body">Growth rate fell from <b style="color:#3b82f6;">2.22%</b> (peak, 1974)
      to <b style="color:#8b5cf6;">0.89%</b> by 2024 — a 60% reduction — driven by
      urbanization, education, and family planning programs.</div>
    </div>""", unsafe_allow_html=True)
with i3:
    st.markdown("""
    <div class="insight-card">
      <div class="insight-title">⚡ Billion Milestone</div>
      <div class="insight-body">India crossed <b style="color:#f97316;">1 Billion</b> in 2000,
      taking just 3 years to go from 900M to 1B — the fastest 100M addition
      in its history at the time.</div>
    </div>""", unsafe_allow_html=True)
