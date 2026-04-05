# ============================================================
#  app.py  —  HOME PAGE
#  Run: streamlit run app.py
# ============================================================

import streamlit as st
from src import (get_historical_df, META,
                 PopulationModelSuite, fmt_pop, confidence_score,
                 build_confidence_gauge)

st.set_page_config(
    page_title  = "🇮🇳 India PopPredict",
    page_icon   = "🇮🇳",
    layout      = "wide",
    initial_sidebar_state = "expanded",
)

# ── Shared CSS (call on every page) ──────────────────────────
def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
html,body,.stApp{font-family:'Inter',sans-serif!important;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:1.5rem 2rem 3rem!important;max-width:1400px!important;}

[data-testid="stSidebar"]{border-right:1px solid rgba(255,255,255,.07)!important;}
[data-testid="stSidebarNav"] a{border-radius:10px!important;margin:2px 0;font-weight:500;}
[data-testid="stSidebarNav"] a:hover{background:rgba(59,130,246,.12)!important;}

[data-testid="metric-container"]{
    background:#111827!important;border:1px solid rgba(255,255,255,.07)!important;
    border-radius:14px!important;padding:18px 20px!important;transition:all .3s ease;}
[data-testid="metric-container"]:hover{
    border-color:rgba(59,130,246,.3)!important;
    transform:translateY(-2px);box-shadow:0 8px 40px rgba(0,0,0,.4);}
[data-testid="stMetricLabel"]{font-size:.72rem!important;text-transform:uppercase;letter-spacing:.08em;color:#94a3b8!important;}
[data-testid="stMetricValue"]{font-family:'Space Grotesk',sans-serif!important;font-size:1.55rem!important;font-weight:700!important;}
[data-testid="stMetricDelta"]{font-size:.8rem!important;font-weight:600!important;}

[data-testid="stPlotlyChart"]{
    border:1px solid rgba(255,255,255,.07);border-radius:14px;overflow:hidden;
    transition:border-color .3s,box-shadow .3s;}
[data-testid="stPlotlyChart"]:hover{border-color:rgba(59,130,246,.25);box-shadow:0 4px 40px rgba(0,0,0,.4);}

.stButton>button{
    background:linear-gradient(135deg,#3b82f6,#8b5cf6,#ec4899)!important;
    color:#fff!important;border:none!important;border-radius:10px!important;
    padding:12px 24px!important;font-weight:700!important;font-size:.9rem!important;
    width:100%!important;transition:all .3s!important;}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 30px rgba(59,130,246,.4)!important;}

.stNumberInput input,.stSelectbox>div>div{
    background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,255,255,.07)!important;border-radius:8px!important;}
.stNumberInput input:focus{border-color:#3b82f6!important;box-shadow:0 0 0 3px rgba(59,130,246,.25)!important;}

[data-testid="stDataFrame"]{border:1px solid rgba(255,255,255,.07)!important;border-radius:12px!important;overflow:hidden;}
hr{border-color:rgba(255,255,255,.07)!important;}

.hero{background:linear-gradient(135deg,rgba(59,130,246,.08),rgba(139,92,246,.08));
      border:1px solid rgba(59,130,246,.15);border-radius:20px;
      padding:2.5rem 3rem;margin-bottom:1.5rem;text-align:center;}
.hero-title{font-family:'Space Grotesk',sans-serif;font-size:2.8rem;font-weight:800;
            background:linear-gradient(135deg,#3b82f6,#8b5cf6,#ec4899);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.hero-sub{color:#94a3b8;font-size:1rem;}
.badge{display:inline-block;background:rgba(59,130,246,.12);border:1px solid rgba(59,130,246,.3);
       border-radius:99px;padding:4px 16px;font-size:.7rem;font-weight:600;
       letter-spacing:.12em;color:#3b82f6;text-transform:uppercase;margin-bottom:.75rem;}
.section-title{font-family:'Space Grotesk',sans-serif;font-size:1.05rem;font-weight:700;color:#f0f6ff;}
.section-sub{font-size:.75rem;color:#94a3b8;margin-bottom:.75rem;}
.pred-box{background:linear-gradient(135deg,rgba(59,130,246,.08),rgba(139,92,246,.08));
          border:1px solid rgba(59,130,246,.25);border-radius:14px;padding:1.5rem;text-align:center;}
.pred-year{font-size:.72rem;color:#3b82f6;text-transform:uppercase;letter-spacing:.12em;font-weight:600;}
.pred-pop{font-family:'Space Grotesk',sans-serif;font-size:1.9rem;font-weight:800;
          background:linear-gradient(135deg,#3b82f6,#8b5cf6,#ec4899);
          -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.pred-model{font-size:.72rem;color:#94a3b8;}
.info-card{background:#111827;border:1px solid rgba(255,255,255,.07);border-radius:14px;padding:1.25rem 1.5rem;}
.info-num{font-family:'Space Grotesk',sans-serif;font-size:1.5rem;font-weight:700;
          background:linear-gradient(135deg,#3b82f6,#8b5cf6);
          -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.info-label{font-size:.72rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.08em;}
.live-dot{display:inline-block;width:8px;height:8px;background:#10b981;
          border-radius:50%;animation:pulse 2s infinite;margin-right:6px;}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.6}}
</style>""", unsafe_allow_html=True)

inject_css()

# ── Cache model suite ─────────────────────────────────────────
@st.cache_resource(show_spinner="⚙️ Fitting prediction models…")
def load_suite():
    hist  = get_historical_df()
    suite = PopulationModelSuite()
    suite.fit(hist["year"].tolist(), hist["population"].tolist())
    return suite, hist

suite, hist_df = load_suite()

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:.5rem 0 1rem;">
        <div style="font-size:2.5rem;">🇮🇳</div>
        <div style="font-family:'Space Grotesk';font-weight:700;font-size:1rem;
                    background:linear-gradient(135deg,#3b82f6,#8b5cf6,#ec4899);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            India PopPredict
        </div>
        <div style="font-size:.62rem;color:#4b5563;text-transform:uppercase;letter-spacing:.12em;">
            Demographics Analytics
        </div>
        <hr style="border-color:rgba(255,255,255,.07);margin:.75rem 0;">
    </div>""", unsafe_allow_html=True)

    st.markdown("**🎯 Quick Predictor**")
    pred_year  = st.number_input("Target Year", 1950, 2100, 2040, key="home_year")
    pred_model = st.selectbox("Model", ["Polynomial","Linear","Logistic"], key="home_model")
    go = st.button("🔮 Predict Population", key="home_go")

    st.markdown("---")
    st.caption("📂 **Navigate using pages above ↑**")
    st.caption("Data: UN World Population Prospects & Census of India")

# ── Hero ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="badge">🇮🇳 Population Intelligence Platform</div>
  <div class="hero-title">India's Population Forecast</div>
  <div class="hero-sub">
    Advanced demographic forecasting · Linear, Polynomial &amp; Logistic Regression<br>
    Historical data 1950–2025 · Projections through 2075
  </div>
</div>""", unsafe_allow_html=True)

# ── KPI Metrics ───────────────────────────────────────────────
curr = META["current_pop"]
p30  = suite.polynomial.predict(2030)
p50  = suite.logistic.predict(2050)
p75  = suite.logistic.predict(2075)
peak = suite.find_peak_year()

k1,k2,k3,k4,k5 = st.columns(5)
with k1: st.metric("🌏 Population (2025)", "1.442 B",          f"+{META['growth_rate']}% annual")
with k2: st.metric("📈 Predicted 2030",    fmt_pop(p30,True),  f"+{(p30-curr)/curr*100:.1f}% vs today")
with k3: st.metric("🔮 Predicted 2050",    fmt_pop(p50,True),  f"{(p50-curr)/curr*100:+.1f}% vs today")
with k4: st.metric("🌐 Predicted 2075",    fmt_pop(p75,True),  f"{(p75-curr)/curr*100:+.1f}% vs today")
with k5: st.metric("⏰ Peak Year",          str(peak),          "Logistic model apex")

st.markdown("<br>", unsafe_allow_html=True)

# ── Prediction result ─────────────────────────────────────────
model_map = {"Polynomial":suite.polynomial,"Linear":suite.linear,"Logistic":suite.logistic}
if go or "home_pred" not in st.session_state:
    r = model_map[pred_model].predict(int(pred_year))
    st.session_state["home_pred"] = dict(
        year=pred_year, pop=r, model=pred_model,
        conf=confidence_score(int(pred_year), META["current_year"]))

p = st.session_state["home_pred"]
pc1, pc2 = st.columns([3,1])
with pc1:
    st.markdown(f"""
    <div class="pred-box">
      <div class="pred-year">YEAR {p['year']} PREDICTION</div>
      <div class="pred-pop">{fmt_pop(p['pop'])}</div>
      <div class="pred-model">{p['model']} Regression Model &nbsp;·&nbsp;
        <span style="color:#10b981;font-weight:600;">{p['conf']}% Confidence</span>
      </div>
    </div>""", unsafe_allow_html=True)
with pc2:
    st.plotly_chart(build_confidence_gauge(p["conf"]),
                    use_container_width=True, config={"displayModeBar":False})

st.markdown("<br>", unsafe_allow_html=True)

# ── Quick Fact Cards ──────────────────────────────────────────
st.markdown('<div class="section-title">📌 Key Demographic Facts</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Snapshot of India\'s current demographic indicators</div>', unsafe_allow_html=True)

facts = [
    ("1.442 B",  "Total Population 2025"), ("464 /km²", "Population Density"),
    ("#1",        "World Rank (since 2023)"),("28.2 yrs", "Median Age"),
    ("0.89%",     "Annual Growth Rate"),    ("~6.5M",    "Net Annual Increase"),
    ("67.9%",     "Working-age Share"),     ("~2075",    "Projected Peak Year"),
]
cols = st.columns(4)
for i,(num,label) in enumerate(facts):
    with cols[i%4]:
        st.markdown(f"""
        <div class="info-card" style="margin-bottom:1rem;">
          <div class="info-num">{num}</div>
          <div class="info-label">{label}</div>
        </div>""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#4b5563;font-size:.72rem;line-height:2;">
  🇮🇳 <b style="color:#94a3b8;">India PopPredict</b> &nbsp;|&nbsp;
  Data: UN World Population Prospects &amp; Census of India &nbsp;|&nbsp;
  Built with Python · Streamlit · Plotly · scikit-learn · scipy
</div>""", unsafe_allow_html=True)
