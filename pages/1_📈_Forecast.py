# ============================================================
#  pages/1_📈_Forecast.py  —  Forecast Models
# ============================================================

import streamlit as st
import pandas as pd
from src import (get_historical_df, META,
                 PopulationModelSuite, fmt_pop, confidence_score,
                 build_forecast_chart, build_confidence_gauge)

st.set_page_config(page_title="Forecast | India PopPredict", page_icon="📈", layout="wide")

# ── CSS (inline, minimal) ─────────────────────────────────────
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
.stButton>button{background:linear-gradient(135deg,#3b82f6,#8b5cf6,#ec4899)!important;color:#fff!important;border:none!important;border-radius:10px!important;padding:12px!important;font-weight:700!important;width:100%!important;}
.stSelectbox>div>div,.stNumberInput input{background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,255,255,.07)!important;border-radius:8px!important;}
hr{border-color:rgba(255,255,255,.07)!important;}
.page-title{font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:800;
            background:linear-gradient(135deg,#3b82f6,#8b5cf6,#ec4899);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:.25rem;}
.page-sub{color:#94a3b8;font-size:.9rem;margin-bottom:1.5rem;}
.section-title{font-family:'Space Grotesk',sans-serif;font-size:1rem;font-weight:700;color:#f0f6ff;}
.section-sub{font-size:.75rem;color:#94a3b8;margin-bottom:.75rem;}
.pred-box{background:linear-gradient(135deg,rgba(59,130,246,.08),rgba(139,92,246,.08));
          border:1px solid rgba(59,130,246,.25);border-radius:14px;padding:1.5rem;text-align:center;margin-top:.5rem;}
.pred-year{font-size:.72rem;color:#3b82f6;text-transform:uppercase;letter-spacing:.12em;font-weight:600;}
.pred-pop{font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:800;
          background:linear-gradient(135deg,#3b82f6,#8b5cf6,#ec4899);
          -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.pred-model{font-size:.75rem;color:#94a3b8;}
.model-card{background:#111827;border:1px solid rgba(255,255,255,.07);border-radius:14px;padding:1.25rem 1.5rem;height:100%;}
.model-name{font-family:'Space Grotesk',sans-serif;font-size:1rem;font-weight:700;color:#f0f6ff;margin-bottom:.3rem;}
.model-desc{font-size:.75rem;color:#94a3b8;line-height:1.7;}
.metric-pill{display:inline-block;background:rgba(16,185,129,.12);border:1px solid rgba(16,185,129,.25);
             border-radius:99px;padding:3px 12px;font-size:.7rem;font-weight:600;color:#10b981;margin-top:.5rem;}
</style>""", unsafe_allow_html=True)

@st.cache_resource(show_spinner="⚙️ Fitting models…")
def load_suite():
    hist  = get_historical_df()
    suite = PopulationModelSuite()
    suite.fit(hist["year"].tolist(), hist["population"].tolist())
    return suite, hist

suite, hist_df = load_suite()
curr = META["current_pop"]

# ── Sidebar controls ──────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📈 Forecast Controls")
    show_lin  = st.checkbox("Show Linear Model",     value=True)
    show_poly = st.checkbox("Show Polynomial Model", value=True)
    show_log  = st.checkbox("Show Logistic Model",   value=True)
    st.markdown("---")
    st.markdown("### 🎯 Year Predictor")
    yr    = st.number_input("Year", 1950, 2100, 2040)
    model = st.selectbox("Model", ["Polynomial","Linear","Logistic"])
    go    = st.button("🔮 Predict")

# ── Page header ───────────────────────────────────────────────
st.markdown('<div class="page-title">📈 Population Forecast</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Three machine-learning models projecting India\'s population from 1950 through 2075</div>', unsafe_allow_html=True)

# ── Prediction result ─────────────────────────────────────────
model_map = {"Polynomial":suite.polynomial,"Linear":suite.linear,"Logistic":suite.logistic}
if go or "fc_pred" not in st.session_state:
    r = model_map[model].predict(int(yr))
    st.session_state["fc_pred"] = dict(year=yr,pop=r,model=model,conf=confidence_score(int(yr)))

p = st.session_state["fc_pred"]
pc1,pc2 = st.columns([3,1])
with pc1:
    st.markdown(f"""
    <div class="pred-box">
      <div class="pred-year">YEAR {p['year']} — {p['model'].upper()} MODEL</div>
      <div class="pred-pop">{fmt_pop(p['pop'])}</div>
      <div class="pred-model">Confidence: <span style="color:#10b981;font-weight:600;">{p['conf']}%</span>
        &nbsp;·&nbsp; Change vs today: <span style="color:#3b82f6;font-weight:600;">
        {(p['pop']-curr)/curr*100:+.2f}%</span>
      </div>
    </div>""", unsafe_allow_html=True)
with pc2:
    st.plotly_chart(build_confidence_gauge(p["conf"]), use_container_width=True, config={"displayModeBar":False})

st.markdown("<br>", unsafe_allow_html=True)

# ── Main forecast chart ───────────────────────────────────────
st.markdown('<div class="section-title">Population Forecast: 1950 – 2075</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Historical record (blue) with model projections from 2026 onwards</div>', unsafe_allow_html=True)

future_years = list(range(META["current_year"]+1, 2076))
forecast_df  = suite.forecast_df(future_years)
if not show_lin:  forecast_df["Linear"]     = None
if not show_poly: forecast_df["Polynomial"] = None
if not show_log:  forecast_df["Logistic"]   = None

fig = build_forecast_chart(hist_df, forecast_df)
fig.update_layout(height=460)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Model stats KPIs ─────────────────────────────────────────
st.markdown('<div class="section-title">Model Performance Comparison</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">R² score and Mean Absolute Error on historical training data</div>', unsafe_allow_html=True)

m1,m2,m3 = st.columns(3)
models_info = [
    (suite.linear,     "📉 Linear Regression",        "#f97316",
     "Fits a straight line through historical data. Simple & interpretable but can't model acceleration."),
    (suite.polynomial, "📈 Polynomial (deg 3)",        "#10b981",
     "Captures the acceleration in growth. Best fit for historical data with high R² score."),
    (suite.logistic,   "〰️ Logistic S-Curve",         "#8b5cf6",
     "Models demographic transition — growth slows as population approaches carrying capacity (~1.75B)."),
]
for col,(m,name,color,desc) in zip([m1,m2,m3], models_info):
    with col:
        st.markdown(f"""
        <div class="model-card">
          <div class="model-name" style="color:{color};">{name}</div>
          <div class="model-desc">{desc}</div>
          <div class="metric-pill">R² = {m.r2:.6f}</div>
          <div class="metric-pill" style="background:rgba(59,130,246,.12);border-color:rgba(59,130,246,.25);color:#3b82f6;">
            MAE = {m.mae/1e6:.1f}M
          </div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Projection table ──────────────────────────────────────────
st.markdown('<div class="section-title">Projection Table (2025 – 2075)</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">All three models side-by-side for key years</div>', unsafe_allow_html=True)

table_years = list(range(2025, 2076, 5))
rows = []
for y in table_years:
    preds = suite.predict_all(y)
    pct   = lambda v: f"{(v-curr)/curr*100:+.1f}%"
    rows.append({"Year":y,
                 "Linear":     f"{fmt_pop(preds['Linear'],True)} ({pct(preds['Linear'])})",
                 "Polynomial": f"{fmt_pop(preds['Polynomial'],True)} ({pct(preds['Polynomial'])})",
                 "Logistic":   f"{fmt_pop(preds['Logistic'],True)} ({pct(preds['Logistic'])})"})

st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=380)
