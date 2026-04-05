# ============================================================
#  pages/4_📋_Data_Explorer.py  —  Raw Data + Download
# ============================================================

import io
import streamlit as st
import pandas as pd
from src import get_historical_df, META, PopulationModelSuite, fmt_pop

st.set_page_config(page_title="Data Explorer | India PopPredict", page_icon="📋", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');
html,body,.stApp{font-family:'Inter',sans-serif!important;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:1.5rem 2rem 3rem!important;max-width:1400px!important;}
[data-testid="metric-container"]{background:#111827!important;border:1px solid rgba(255,255,255,.07)!important;border-radius:14px!important;padding:16px 20px!important;}
[data-testid="stMetricLabel"]{font-size:.72rem!important;text-transform:uppercase;letter-spacing:.08em;color:#94a3b8!important;}
[data-testid="stMetricValue"]{font-family:'Space Grotesk',sans-serif!important;font-size:1.45rem!important;font-weight:700!important;}
[data-testid="stDataFrame"]{border:1px solid rgba(255,255,255,.07)!important;border-radius:12px!important;overflow:hidden;}
.stButton>button{background:linear-gradient(135deg,#3b82f6,#8b5cf6)!important;color:#fff!important;border:none!important;border-radius:10px!important;padding:12px!important;font-weight:700!important;width:100%!important;}
hr{border-color:rgba(255,255,255,.07)!important;}
.page-title{font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:800;
            background:linear-gradient(135deg,#f59e0b,#10b981);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:.25rem;}
.page-sub{color:#94a3b8;font-size:.9rem;margin-bottom:1.5rem;}
.section-title{font-family:'Space Grotesk',sans-serif;font-size:1rem;font-weight:700;color:#f0f6ff;}
.section-sub{font-size:.75rem;color:#94a3b8;margin-bottom:.75rem;}
</style>""", unsafe_allow_html=True)

@st.cache_resource(show_spinner="⚙️ Loading data…")
def load_suite():
    hist  = get_historical_df()
    suite = PopulationModelSuite()
    suite.fit(hist["year"].tolist(), hist["population"].tolist())
    return suite, hist

suite, hist_df = load_suite()

# ── Sidebar filters ───────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📋 Filter Data")
    yr_range  = st.slider("Year Range", 1950, 2025, (1950, 2025))
    show_proj = st.checkbox("Include Projections (2026–2075)", value=True)
    proj_step = st.selectbox("Projection Step", [1,5,10], index=1, format_func=lambda x: f"Every {x} year(s)")
    st.markdown("---")
    st.caption("Data: UN World Population Prospects & Census of India")

# ── Page header ───────────────────────────────────────────────
st.markdown('<div class="page-title">📋 Data Explorer</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Browse, filter, and download the complete historical + projected population dataset</div>', unsafe_allow_html=True)

# ── Summary metrics ───────────────────────────────────────────
df = hist_df[(hist_df["year"]>=yr_range[0]) & (hist_df["year"]<=yr_range[1])].copy()
m1,m2,m3,m4 = st.columns(4)
with m1: st.metric("📅 Years in View",   len(df))
with m2: st.metric("👥 Start Population", fmt_pop(int(df["population"].iloc[0]),  True))
with m3: st.metric("👥 End Population",   fmt_pop(int(df["population"].iloc[-1]), True))
with m4: st.metric("📊 Data Points",      len(df))

st.markdown("<br>", unsafe_allow_html=True)

# ── Historical data table ─────────────────────────────────────
st.markdown('<div class="section-title">Historical Population Data</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Year-by-year data with growth rates</div>', unsafe_allow_html=True)

display_df = df[["year","population","population_B","growth_rate"]].copy()
display_df.columns = ["Year", "Population", "Population (B)", "Growth Rate (%)"]
display_df["Population"]     = display_df["Population"].apply(lambda x: f"{int(x):,}")
display_df["Population (B)"] = display_df["Population (B)"].apply(lambda x: f"{x:.4f}")
display_df["Growth Rate (%)"]= display_df["Growth Rate (%)"].apply(lambda x: f"{x:.3f}%" if pd.notna(x) else "—")

st.dataframe(display_df, use_container_width=True, hide_index=True, height=340)

# ── Download historical ───────────────────────────────────────
csv_hist = df.to_csv(index=False).encode("utf-8")
xl_buf   = io.BytesIO()
with pd.ExcelWriter(xl_buf, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Historical")

dc1,dc2,_ = st.columns([1,1,2])
with dc1:
    st.download_button("⬇️ Download CSV", csv_hist, "india_population_historical.csv",
                       "text/csv", use_container_width=True)
with dc2:
    st.download_button("⬇️ Download Excel", xl_buf.getvalue(),
                       "india_population_historical.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Projection table ──────────────────────────────────────────
if show_proj:
    st.markdown('<div class="section-title">Population Projections (2026–2075)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">All three model outputs — best used together for a range estimate</div>', unsafe_allow_html=True)

    proj_years = list(range(META["current_year"]+1, 2076, proj_step))
    proj_rows  = []
    for y in proj_years:
        preds = suite.predict_all(y)
        proj_rows.append({
            "Year":       y,
            "Linear":     preds["Linear"],
            "Polynomial": preds["Polynomial"],
            "Logistic":   preds["Logistic"],
            "Avg Estimate": int((preds["Linear"]+preds["Polynomial"]+preds["Logistic"])/3),
        })

    proj_df = pd.DataFrame(proj_rows)

    display_proj = proj_df.copy()
    for col in ["Linear","Polynomial","Logistic","Avg Estimate"]:
        display_proj[col] = display_proj[col].apply(lambda x: f"{x/1e9:.4f}B")
    st.dataframe(display_proj, use_container_width=True, hide_index=True, height=340)

    # Download projections
    csv_proj = proj_df.to_csv(index=False).encode("utf-8")
    xl_proj  = io.BytesIO()
    with pd.ExcelWriter(xl_proj, engine="openpyxl") as writer:
        proj_df.to_excel(writer, index=False, sheet_name="Projections")
        df.to_excel(writer,      index=False, sheet_name="Historical")

    dp1,dp2,_ = st.columns([1,1,2])
    with dp1:
        st.download_button("⬇️ Projections CSV", csv_proj, "india_population_projections.csv",
                           "text/csv", use_container_width=True)
    with dp2:
        st.download_button("⬇️ Full Excel (Both Sheets)", xl_proj.getvalue(),
                           "india_population_full.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           use_container_width=True)

st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#4b5563;font-size:.72rem;line-height:2;">
  🇮🇳 Data: UN World Population Prospects 2022 &amp; Census of India (1951–2011) &nbsp;|&nbsp;
  Projections based on ML models trained on historical data
</div>""", unsafe_allow_html=True)
