# ============================================================
#  app.py  –  India Population Prediction Dashboard
#  Run:  streamlit run app.py
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np

from data   import (get_historical_df, DECADAL_DATA, MILESTONE_DATA,
                    WORLD_SHARE, META)
from models import PopulationModelSuite, fmt_pop, confidence_score
from charts import (build_forecast_chart, build_growth_chart,
                    build_decadal_chart, build_milestones_chart,
                    build_share_chart,  build_confidence_gauge,
                    build_model_accuracy_chart)

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title  = "🇮🇳 India PopPredict | Demographics Dashboard",
    page_icon   = "🇮🇳",
    layout      = "wide",
    initial_sidebar_state = "expanded",
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
/* ---- Google Fonts ---- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ---- Root variables ---- */
:root {
    --bg:      #060814;
    --surface: #0d1117;
    --card:    #111827;
    --border:  rgba(255,255,255,0.07);
    --blue:    #3b82f6;
    --green:   #10b981;
    --orange:  #f97316;
    --purple:  #8b5cf6;
    --text:    #f0f6ff;
    --muted:   #94a3b8;
}

/* ---- Global ---- */
html, body, .stApp {
    background-color: var(--bg) !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--text) !important;
}

/* ---- Hide Streamlit chrome ---- */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 1400px !important; }

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stNumberInput label {
    color: var(--muted) !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ---- Metric cards (st.metric) ---- */
[data-testid="metric-container"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 18px 20px !important;
    transition: all 0.3s ease;
}
[data-testid="metric-container"]:hover {
    border-color: rgba(59,130,246,0.3) !important;
    transform: translateY(-2px);
    box-shadow: 0 8px 40px rgba(0,0,0,0.4);
}
[data-testid="stMetricLabel"]  { color: var(--muted) !important; font-size: 0.72rem !important; text-transform: uppercase; letter-spacing: 0.08em; }
[data-testid="stMetricValue"]  { color: var(--text)  !important; font-family: 'Space Grotesk', sans-serif !important; font-size: 1.6rem !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"]  { font-size: 0.8rem !important; font-weight: 600 !important; }

/* ---- Plotly charts ---- */
[data-testid="stPlotlyChart"] {
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
[data-testid="stPlotlyChart"]:hover {
    border-color: rgba(59,130,246,0.25);
    box-shadow: 0 4px 40px rgba(0,0,0,0.4);
}

/* ---- Buttons ---- */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.02em !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(59,130,246,0.4) !important;
}

/* ---- Inputs ---- */
.stNumberInput input, .stSelectbox select,
[data-testid="stNumberInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
}
.stNumberInput input:focus { border-color: var(--blue) !important; box-shadow: 0 0 0 3px rgba(59,130,246,0.25) !important; }

/* ---- Selectbox ---- */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

/* ---- Dataframe / table ---- */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    overflow: hidden;
}

/* ---- Divider ---- */
hr { border-color: var(--border) !important; }

/* ── Custom components ── */
.hero-header {
    background: linear-gradient(135deg, rgba(59,130,246,0.08), rgba(139,92,246,0.08));
    border: 1px solid rgba(59,130,246,0.15);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin: 0 0 0.5rem;
}
.hero-sub {
    color: #94a3b8;
    font-size: 1rem;
    max-width: 600px;
    margin: 0 auto;
}
.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #f0f6ff;
    margin: 0 0 0.25rem;
}
.section-sub {
    font-size: 0.75rem;
    color: #94a3b8;
    margin-bottom: 1rem;
}
.pred-result-box {
    background: linear-gradient(135deg, rgba(59,130,246,0.08), rgba(139,92,246,0.08));
    border: 1px solid rgba(59,130,246,0.25);
    border-radius: 14px;
    padding: 1.5rem;
    text-align: center;
    margin-top: 1rem;
}
.pred-year  { font-size: 0.75rem; color: #3b82f6; text-transform: uppercase; letter-spacing: 0.12em; font-weight: 600; }
.pred-pop   { font-family: 'Space Grotesk'; font-size: 1.8rem; font-weight: 800; background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 6px 0; }
.pred-model { font-size: 0.72rem; color: #94a3b8; }
.live-dot   { display: inline-block; width: 8px; height: 8px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite; margin-right: 6px; }
.badge      { display: inline-block; background: rgba(59,130,246,0.12); border: 1px solid rgba(59,130,246,0.3); border-radius: 99px; padding: 4px 14px; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em; color: #3b82f6; text-transform: uppercase; }
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.6;} }

/* ---- Slider ---- */
.stSlider [data-testid="stThumbValue"] { color: var(--text) !important; }
.stSlider [data-baseweb="slider"] div  { background: var(--blue) !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  Load & cache models
# ═══════════════════════════════════════════════════════════
@st.cache_resource(show_spinner="⚙️ Fitting prediction models…")
def load_models():
    hist = get_historical_df()
    suite = PopulationModelSuite()
    suite.fit(hist["year"].tolist(), hist["population"].tolist())
    return suite, hist

suite, hist_df = load_models()

# Forecast for 2026-2075
current_year = META["current_year"]
future_years = list(range(current_year + 1, 2076))
forecast_df  = suite.forecast_df(future_years)

peak_year = suite.find_peak_year()
pred_2030 = suite.polynomial.predict(2030)
pred_2050 = suite.logistic.predict(2050)
pred_2075 = suite.logistic.predict(2075)
curr_pop  = META["current_pop"]


# ═══════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 1.5rem;">
        <div style="font-size:3rem;">🇮🇳</div>
        <div style="font-family:'Space Grotesk';font-weight:700;font-size:1.1rem;
                    background:linear-gradient(135deg,#3b82f6,#8b5cf6,#ec4899);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;">
            India PopPredict
        </div>
        <div style="font-size:0.65rem;color:#4b5563;text-transform:uppercase;letter-spacing:0.12em;">
            Demographics Analytics
        </div>
        <hr style="border-color:rgba(255,255,255,0.07);margin:1rem 0 0.5rem;">
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">🎯 Year Predictor</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Predict population for any year</div>', unsafe_allow_html=True)

    pred_year  = st.number_input("Target Year", min_value=1950, max_value=2100,
                                 value=2040, step=1, key="pred_year_input")
    pred_model = st.selectbox("Model", ["Polynomial", "Linear", "Logistic"],
                              index=0, key="pred_model_sel")

    predict_clicked = st.button("🔮 Predict Population", key="pred_btn")

    st.markdown("---")
    st.markdown('<div class="section-title">⚙️ Display Options</div>', unsafe_allow_html=True)
    show_linear     = st.checkbox("Show Linear Model",     value=True)
    show_poly       = st.checkbox("Show Polynomial Model", value=True)
    show_logistic   = st.checkbox("Show Logistic Model",   value=True)

    st.markdown("---")
    st.markdown('<div class="section-title">📊 Model Stats</div>', unsafe_allow_html=True)
    stats_df = suite.model_stats()
    st.dataframe(stats_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.65rem;color:#4b5563;line-height:1.8;text-align:center;">
        <span class='live-dot'></span>Data: UN World Population Prospects<br>
        + Census of India<br>
        Models: sklearn + scipy
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  HERO HEADER
# ═══════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-header">
    <span class="badge">POPULATION INTELLIGENCE PLATFORM</span>
    <div class="hero-title" style="margin-top:0.75rem;">
        India's Population Forecast
    </div>
    <div class="hero-sub">
        Advanced demographic forecasting using Linear, Polynomial & Logistic Regression.
        Historical data 1950–2024 with projections through 2075.
    </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  KPI METRICS ROW
# ═══════════════════════════════════════════════════════════
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("🌏 Population (2024)", "1.442 Billion",
              delta=f"+{META['growth_rate']}% annual")
with c2:
    pct30 = ((pred_2030 - curr_pop) / curr_pop * 100)
    st.metric("📈 Predicted 2030", fmt_pop(pred_2030, short=True),
              delta=f"+{pct30:.1f}% vs today")
with c3:
    pct50 = ((pred_2050 - curr_pop) / curr_pop * 100)
    st.metric("🔮 Predicted 2050", fmt_pop(pred_2050, short=True),
              delta=f"{pct50:+.1f}% vs today")
with c4:
    pct75 = ((pred_2075 - curr_pop) / curr_pop * 100)
    st.metric("🌐 Predicted 2075", fmt_pop(pred_2075, short=True),
              delta=f"{pct75:+.1f}% vs today")
with c5:
    st.metric("⏰ Peak Year (Logistic)", str(peak_year),
              delta="Population apex")

st.markdown("<br>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  PREDICTION RESULT  (sidebar button → main area)
# ═══════════════════════════════════════════════════════════
if predict_clicked or "last_pred" not in st.session_state:
    model_map = {
        "Polynomial": suite.polynomial,
        "Linear":     suite.linear,
        "Logistic":   suite.logistic,
    }
    chosen   = model_map[pred_model]
    result   = chosen.predict(int(pred_year))
    conf     = confidence_score(int(pred_year))
    st.session_state["last_pred"] = {
        "year":   pred_year,
        "pop":    result,
        "model":  pred_model,
        "conf":   conf,
    }

if "last_pred" in st.session_state:
    p = st.session_state["last_pred"]
    pred_col1, pred_col2 = st.columns([3, 1])

    with pred_col1:
        st.markdown(f"""
        <div class="pred-result-box">
            <div class="pred-year">YEAR {p['year']} PREDICTION</div>
            <div class="pred-pop">{fmt_pop(p['pop'])}</div>
            <div class="pred-model">{p['model']} Regression Model &nbsp;·&nbsp;
                <span style="color:#10b981;font-weight:600;">{p['conf']}% Confidence</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with pred_col2:
        fig_gauge = build_confidence_gauge(p["conf"])
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  MAIN FORECAST CHART  (full width)
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📈 Population Forecast: 1950 – 2075</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Historical record with three predictive model projections through 2075</div>', unsafe_allow_html=True)

# Filter models per checkbox
filtered_forecast = forecast_df.copy()
if not show_linear:   filtered_forecast["Linear"]     = None
if not show_poly:     filtered_forecast["Polynomial"] = None
if not show_logistic: filtered_forecast["Logistic"]   = None

fig_main = build_forecast_chart(hist_df, filtered_forecast)
st.plotly_chart(fig_main, use_container_width=True, config={"displayModeBar": True})

st.markdown("<br>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  ROW 2 — Growth Rate + Decadal Chart
# ═══════════════════════════════════════════════════════════
col_a, col_b = st.columns(2)

with col_a:
    st.markdown('<div class="section-title">📉 Annual Growth Rate Trend</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Year-over-year population growth percentage, 1951–2024</div>', unsafe_allow_html=True)
    fig_growth = build_growth_chart(hist_df)
    st.plotly_chart(fig_growth, use_container_width=True, config={"displayModeBar": False})

with col_b:
    st.markdown('<div class="section-title">📊 Decadal Census Growth Rate</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Official census-based growth percentage per decade</div>', unsafe_allow_html=True)
    fig_decadal = build_decadal_chart(DECADAL_DATA)
    st.plotly_chart(fig_decadal, use_container_width=True, config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  ROW 3 — Milestones + World Share
# ═══════════════════════════════════════════════════════════
col_c, col_d = st.columns(2)

with col_c:
    st.markdown('<div class="section-title">🏆 Population Growth Milestones</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Years taken to add each successive 100 million people</div>', unsafe_allow_html=True)
    fig_miles = build_milestones_chart(MILESTONE_DATA)
    st.plotly_chart(fig_miles, use_container_width=True, config={"displayModeBar": False})

with col_d:
    st.markdown('<div class="section-title">🌍 India vs China — World Share</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Each country\'s share of total global population over time</div>', unsafe_allow_html=True)
    fig_share = build_share_chart(WORLD_SHARE)
    st.plotly_chart(fig_share, use_container_width=True, config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  ROW 4 — Model accuracy + Projection Table
# ═══════════════════════════════════════════════════════════
col_e, col_f = st.columns([1, 2])

with col_e:
    st.markdown('<div class="section-title">🎯 Model Accuracy (R²)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">R² score on historical training data</div>', unsafe_allow_html=True)
    fig_acc = build_model_accuracy_chart(stats_df)
    st.plotly_chart(fig_acc, use_container_width=True, config={"displayModeBar": False})

with col_f:
    st.markdown('<div class="section-title">📋 Projection Table (2025–2075)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Side-by-side comparison of all three models</div>', unsafe_allow_html=True)
    table_years = [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2065, 2070, 2075]
    table_data  = []
    for y in table_years:
        preds = suite.predict_all(y)
        table_data.append({
            "Year":            y,
            "Linear":          fmt_pop(preds["Linear"],     short=True),
            "Polynomial":      fmt_pop(preds["Polynomial"], short=True),
            "Logistic":        fmt_pop(preds["Logistic"],   short=True),
        })
    tdf = pd.DataFrame(table_data)
    st.dataframe(
        tdf.style.applymap(lambda _: "background-color: rgba(59,130,246,0.07);", subset=["Polynomial"]),
        use_container_width=True,
        hide_index=True,
        height=330,
    )


# ═══════════════════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#4b5563;font-size:0.75rem;padding:1rem 0 2rem;line-height:2;">
    🇮🇳 <strong style="color:#94a3b8;">India PopPredict Dashboard</strong><br>
    Data sourced from UN World Population Prospects &amp; Census of India.<br>
    Models: Linear Regression · Polynomial Regression (deg 3) · Logistic S-Curve<br>
    Built with Python · Streamlit · Plotly · scikit-learn · scipy
</div>
""", unsafe_allow_html=True)
