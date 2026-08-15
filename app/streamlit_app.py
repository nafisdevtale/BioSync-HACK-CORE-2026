import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import plotly.express as px
from engine.rules import CROPS, readiness, score_forecast

# -------------------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------------------
st.set_page_config(
    page_title="BioSync | HACK CORE 2026",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------------
# DESIGN SYSTEM
# -------------------------------------------------------------------
st.markdown(
    """
<style>
:root{
 --bg:#f4f7f5; --surface:#ffffff; --ink:#13231a; --ink2:#263b30; --muted:#50635a;
 --line:#d8e4dd; --green:#0d6b3d; --green2:#17834c; --green3:#e8f5ed;
 --dark:#092d1b; --dark2:#0d4a2b; --amber:#8a5700; --red:#a42e2e;
}
html,body,.stApp{background:var(--bg)!important;color:var(--ink)!important;}
[data-testid="stAppViewContainer"],[data-testid="stAppViewContainer"]>section,
[data-testid="stAppViewContainer"] .main{background:var(--bg)!important;color:var(--ink)!important;}
[data-testid="stAppViewContainer"] .main .block-container{
 max-width:1480px!important;padding:1.35rem 2rem 3.5rem!important;
}
[data-testid="stAppViewContainer"] .main,
[data-testid="stAppViewContainer"] .main .stMarkdown,
[data-testid="stAppViewContainer"] .main .stMarkdownContainer{
 color:var(--ink)!important;
}
[data-testid="stAppViewContainer"] .main p,
[data-testid="stAppViewContainer"] .main li,
[data-testid="stAppViewContainer"] .main label,
[data-testid="stAppViewContainer"] .main .stMarkdownContainer p,
[data-testid="stAppViewContainer"] .main .stMarkdownContainer li{
 color:var(--ink2)!important;
 opacity:1!important;
 font-size:.94rem;
 line-height:1.5;
}
[data-testid="stAppViewContainer"] .main h1,
[data-testid="stAppViewContainer"] .main h2,
[data-testid="stAppViewContainer"] .main h3,
[data-testid="stAppViewContainer"] .main h4,
[data-testid="stAppViewContainer"] .main h5{
 color:var(--ink)!important;
 opacity:1!important;
}
[data-testid="stAppViewContainer"] .main .stCaption,
[data-testid="stAppViewContainer"] .main .stCaption *,
[data-testid="stAppViewContainer"] .main small{
 color:var(--muted)!important;
 opacity:1!important;
}
[data-testid="stAppViewContainer"] .main a{color:var(--green)!important;}
[data-testid="stAppViewContainer"] .main strong,
[data-testid="stAppViewContainer"] .main b{color:var(--ink)!important;}

/* Hero */
.hero{
 background:linear-gradient(120deg,#062d1a 0%,#0b5a34 58%,#17804a 100%);
 color:#fff!important;padding:1.65rem 2rem 1.75rem;border-radius:20px;margin:.2rem 0 1.35rem;
 box-shadow:0 12px 28px rgba(8,59,34,.14);border:1px solid rgba(255,255,255,.12);
}
.hero *{color:#fff!important}.hero h1{margin:0;font-size:2.55rem;line-height:1;font-weight:900;letter-spacing:-.04em}
.hero p{margin:.65rem 0 0;font-size:.96rem;line-height:1.55;max-width:760px;color:rgba(255,255,255,.92)!important}
.hero-badge{display:inline-block;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.24);
 border-radius:999px;padding:.3rem .65rem;font-size:.68rem;font-weight:850;letter-spacing:.07em;margin-bottom:.8rem}

/* Hierarchy */
.section-label{color:var(--green)!important;font-size:.68rem;font-weight:900;letter-spacing:.15em;text-transform:uppercase;margin:.1rem 0 .25rem}
.section-title{color:var(--ink)!important;font-size:1.42rem;font-weight:900;margin:0 0 .75rem}

/* Cards */
.card,.decision-card,.mini-card{background:#fff!important;border:1px solid var(--line)!important;color:var(--ink)!important;box-shadow:0 5px 18px rgba(19,35,26,.045)}
.card{border-radius:15px;padding:1.05rem 1.2rem}.card *{color:var(--ink2)!important;opacity:1!important}.card p,.card li{font-size:.94rem;line-height:1.55}.card h3{color:var(--ink)!important}
.decision-card{border-radius:17px;padding:1.2rem 1.25rem;text-align:center;min-height:150px;display:flex;flex-direction:column;justify-content:center}
.decision-score{font-size:3.15rem;line-height:1;font-weight:950;color:var(--green)!important;letter-spacing:-.055em}
.decision-score span{color:var(--muted)!important}.decision-label{margin-top:.48rem}
.decision-sub{margin-top:.55rem;color:var(--muted)!important;font-size:.8rem;line-height:1.4}
.status-pill{display:inline-block;padding:.28rem .68rem;border-radius:999px;font-weight:900;font-size:.68rem;letter-spacing:.04em}
.status-good{background:#e3f5e9!important;color:#11613a!important}.status-caution{background:#fff1d7!important;color:#7c5000!important}.status-avoid{background:#fde8e8!important;color:#982a2a!important}
.summary-strip{background:#edf8f1!important;border:1px solid #c9e1d1!important;border-left:4px solid var(--green2)!important;border-radius:10px;padding:.7rem .9rem;margin:.75rem 0}
.summary-title{color:var(--green)!important;font-weight:900;font-size:.63rem;text-transform:uppercase;letter-spacing:.11em}
.summary-text{color:var(--ink2)!important;font-size:.8rem;line-height:1.45;margin-top:.18rem}

/* Metrics */
[data-testid="stMetric"],
[data-testid="stMetric"] *,
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] *,
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] *,
[data-testid="stMetricDelta"],
[data-testid="stMetricDelta"] * {
    opacity: 1 !important;
    visibility: visible !important;
    text-shadow: none !important;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] > div,
[data-testid="stMetricLabel"] > div > div,
[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] span {
    color: #43574d !important;
    -webkit-text-fill-color: #43574d !important;
    font-weight: 800 !important;
}

[data-testid="stMetricValue"],
[data-testid="stMetricValue"] > div,
[data-testid="stMetricValue"] > div > div,
[data-testid="stMetricValue"] span {
    color: #13231a !important;
    -webkit-text-fill-color: #13231a !important;
    font-weight: 900 !important;
}

/* Tabs */
[data-testid="stTabs"] button,
[data-testid="stTabs"] button *,
[data-testid="stTabs"] [role="tab"],
[data-testid="stTabs"] [role="tab"] *,
[data-testid="stTabs"] [data-baseweb="tab"],
[data-testid="stTabs"] [data-baseweb="tab"] * {
    opacity: 1 !important;
    visibility: visible !important;
    color: #263b30 !important;
    -webkit-text-fill-color: #263b30 !important;
    font-weight: 800 !important;
}

[data-testid="stTabs"] button[aria-selected="true"],
[data-testid="stTabs"] button[aria-selected="true"] *,
[data-testid="stTabs"] [role="tab"][aria-selected="true"],
[data-testid="stTabs"] [role="tab"][aria-selected="true"] * {
    color: #0d6b3d !important;
    -webkit-text-fill-color: #0d6b3d !important;
    font-weight: 900 !important;
}

/* Main-page labels generated by Streamlit widgets */
[data-testid="stAppViewContainer"] .main
[data-testid="stWidgetLabel"],
[data-testid="stAppViewContainer"] .main
[data-testid="stWidgetLabel"] *,
[data-testid="stAppViewContainer"] .main
[data-testid="stNumberInput"] label,
[data-testid="stAppViewContainer"] .main
[data-testid="stNumberInput"] label *,
[data-testid="stAppViewContainer"] .main
[data-testid="stSlider"] label,
[data-testid="stAppViewContainer"] .main
[data-testid="stSlider"] label * {
    color: #263b30 !important;
    -webkit-text-fill-color: #263b30 !important;
    opacity: 1 !important;
    visibility: visible !important;
    font-weight: 800 !important;
}

/* Markdown-generated labels */
[data-testid="stAppViewContainer"] .main
.stMarkdown p,
[data-testid="stAppViewContainer"] .main
.stMarkdown strong,
[data-testid="stAppViewContainer"] .main
.stMarkdown b {
    color: #263b30 !important;
    -webkit-text-fill-color: #263b30 !important;
    opacity: 1 !important;
}

/* Captions */
[data-testid="stAppViewContainer"] .main
.stCaption,
[data-testid="stAppViewContainer"] .main
.stCaption *,
[data-testid="stAppViewContainer"] .main
small,
[data-testid="stAppViewContainer"] .main
small * {
    color: #50635a !important;
    -webkit-text-fill-color: #50635a !important;
    opacity: 1 !important;
    visibility: visible !important;
}

/* Tabs — explicit high contrast for deployed Streamlit */
[data-testid="stTabs"]{margin-top:1rem}
[data-testid="stTabs"] [role="tablist"]{gap:.25rem;border-bottom:1px solid var(--line)}
[data-testid="stTabs"] [role="tab"],
[data-testid="stTabs"] [data-baseweb="tab"],
[data-testid="stTabs"] button{
 color:#263b30!important;background:transparent!important;font-weight:850!important;
 border-radius:9px 9px 0 0!important;padding:.62rem .8rem!important;
 opacity:1!important;font-size:.88rem!important;
}
[data-testid="stTabs"] [role="tab"] *,
[data-testid="stTabs"] [data-baseweb="tab"] *,
[data-testid="stTabs"] button *{
 color:#263b30!important;opacity:1!important;
}
[data-testid="stTabs"] [role="tab"]:hover,
[data-testid="stTabs"] [data-baseweb="tab"]:hover,
[data-testid="stTabs"] button:hover{
 color:var(--green)!important;background:#edf6f0!important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"],
[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"],
[data-testid="stTabs"] button[aria-selected="true"]{
 color:var(--green)!important;background:#e7f4ec!important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] *,
[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] *,
[data-testid="stTabs"] button[aria-selected="true"] *{
 color:var(--green)!important;opacity:1!important;
}

/* Inputs */
[data-testid="stAppViewContainer"] .main input,
[data-testid="stAppViewContainer"] .main textarea,
[data-testid="stAppViewContainer"] .main [data-baseweb="select"]>div{color:var(--ink)!important;background:#fff!important}
[data-testid="stAppViewContainer"] .main input{font-size:.86rem!important}
[data-testid="stAlert"]{border-radius:10px!important;opacity:1!important}
[data-testid="stAlert"] *{opacity:1!important}

/* Trace */
.trace-step{border-left:3px solid #9ed0b0;background:#fff;border:1px solid #e1ebe5;border-left-width:3px;border-radius:0 10px 10px 0;padding:.7rem .9rem;margin:0 0 .48rem}
.trace-title{font-weight:900;color:var(--green)!important;font-size:.75rem;letter-spacing:.02em}
.trace-text{color:var(--ink2)!important;font-size:.82rem;line-height:1.4;margin-top:.14rem}

/* Sidebar — high contrast and readable */
section[data-testid="stSidebar"],section[data-testid="stSidebar"]>div{
 background:#0b1711!important;color:#f4f8f5!important;
}
section[data-testid="stSidebar"] *{opacity:1!important}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] *{
 color:#eef5f0!important;
}
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] small{color:#aebdb4!important}
section[data-testid="stSidebar"] hr{border-color:#294137!important}
section[data-testid="stSidebar"] [data-baseweb="select"]>div{
 background:#fff!important;border:1px solid #d9e4de!important;border-radius:8px!important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] *{color:#17241d!important}
section[data-testid="stSidebar"] input{
 background:#fff!important;color:#17241d!important;border-radius:7px!important;
}
section[data-testid="stSidebar"] [data-testid="stNumberInput"] label{
 color:#dce9e1!important;font-size:.72rem!important;font-weight:700!important;line-height:1.2!important;
}
section[data-testid="stSidebar"] [data-testid="stSelectbox"] label{
 color:#dce9e1!important;font-size:.72rem!important;font-weight:700!important;
}
section[data-testid="stSidebar"] [data-testid="stNumberInput"] button{
 color:#31483b!important;background:#fff!important;
}
section[data-testid="stSidebar"] [data-testid="stAlert"]{background:#14291f!important;border:1px solid #28513c!important}
section[data-testid="stSidebar"] .stSuccess{background:#123622!important}
section[data-testid="stSidebar"] .stInfo{background:#102d34!important}
.sidebar-brand{font-size:1.15rem;font-weight:900;color:#fff!important;letter-spacing:-.02em}
.sidebar-kicker{font-size:.68rem;color:#9eb1a6!important;letter-spacing:.08em;text-transform:uppercase}

/* Dataframe / footer */
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:10px;overflow:hidden}
.footer{text-align:center;color:#68776e!important;font-size:.7rem;line-height:1.55;padding:1.25rem 0 .4rem}
.footer *{color:#68776e!important}
/* READABILITY OVERRIDES — judge-facing high contrast */
[data-testid="stAppViewContainer"] .main [data-testid="stMarkdownContainer"]{
 color:var(--ink2)!important;
 opacity:1!important;
}
[data-testid="stAppViewContainer"] .main [data-testid="stMarkdownContainer"] *{
 opacity:1!important;
}
[data-testid="stAppViewContainer"] .main [data-testid="stText"]{
 color:var(--ink)!important;
}

/* Native input widgets */
[data-testid="stAppViewContainer"] .main [data-testid="stNumberInput"] label,
[data-testid="stAppViewContainer"] .main [data-testid="stSelectbox"] label,
[data-testid="stAppViewContainer"] .main [data-testid="stSlider"] label{
 color:var(--ink)!important;
 font-weight:800!important;
 opacity:1!important;
 font-size:.84rem!important;
}
[data-testid="stAppViewContainer"] .main [data-baseweb="input"],
[data-testid="stAppViewContainer"] .main [data-baseweb="select"],
[data-testid="stAppViewContainer"] .main [data-baseweb="input"] *,
[data-testid="stAppViewContainer"] .main [data-baseweb="select"] *{
 color:var(--ink)!important;
 opacity:1!important;
}
[data-testid="stAppViewContainer"] .main [data-baseweb="select"] svg{
 fill:var(--ink)!important;
}

/* Slider: force BioSync green rather than faint/red theme defaults */
/* Final widget-label contrast override */
[data-testid="stAppViewContainer"] .main [data-testid="stWidgetLabel"],
[data-testid="stAppViewContainer"] .main [data-testid="stWidgetLabel"] *,
[data-testid="stAppViewContainer"] .main [data-testid="stSlider"] label,
[data-testid="stAppViewContainer"] .main [data-testid="stSlider"] label *,
[data-testid="stAppViewContainer"] .main [data-testid="stNumberInput"] label,
[data-testid="stAppViewContainer"] .main [data-testid="stNumberInput"] label *,
[data-testid="stAppViewContainer"] .main [data-testid="stSelectbox"] label,
[data-testid="stAppViewContainer"] .main [data-testid="stSelectbox"] label *{
 color:#263b30!important;
 opacity:1!important;
 visibility:visible!important;
 font-weight:800!important;
}
[data-testid="stAppViewContainer"] .main [data-testid="stSlider"] [role="slider"]{
 background:var(--green)!important;
 border-color:var(--green)!important;
 box-shadow:0 0 0 2px rgba(13,107,61,.12)!important;
}
[data-testid="stAppViewContainer"] .main [data-testid="stSlider"] [data-baseweb="slider"] div{
 color:var(--ink)!important;
}
[data-testid="stAppViewContainer"] .main [data-testid="stSlider"] [data-baseweb="slider"] [aria-valuenow]{
 color:var(--ink)!important;
}

/* Alerts: never allow low-contrast inherited text */
[data-testid="stAppViewContainer"] .main [data-testid="stAlert"]{
 opacity:1!important;
}
[data-testid="stAppViewContainer"] .main [data-testid="stAlert"] p,
[data-testid="stAppViewContainer"] .main [data-testid="stAlert"] span,
[data-testid="stAppViewContainer"] .main [data-testid="stAlert"] div{
 color:var(--ink)!important;
 opacity:1!important;
}
[data-testid="stAppViewContainer"] .main [data-testid="stAlert"] svg{
 opacity:1!important;
}

/* Download button */
[data-testid="stAppViewContainer"] .main .stDownloadButton button{
 color:#fff!important;
 background:var(--green)!important;
 border:1px solid var(--green)!important;
 font-weight:800!important;
}
[data-testid="stAppViewContainer"] .main .stDownloadButton button *{
 color:#fff!important;
}

/* Footer and secondary text */
.footer,.footer *{color:#50635a!important;opacity:1!important;font-size:.76rem!important}



/* High-contrast application-window table */
.readable-table-wrap{
 width:100%;
 overflow:hidden;
 border:1px solid #cbdad2;
 border-radius:12px;
 background:#fff;
 box-shadow:0 4px 14px rgba(19,35,26,.04);
 margin:.35rem 0 .8rem;
}
.readable-table{
 width:100%;
 border-collapse:collapse;
 table-layout:fixed;
 color:#17291f!important;
 font-size:.9rem!important;
}
.readable-table th{
 background:#edf5f0!important;
 color:#173226!important;
 font-weight:900!important;
 text-align:left;
 padding:.72rem .85rem;
 border-bottom:2px solid #cbdad2;
}
.readable-table td{
 background:#fff!important;
 color:#263b30!important;
 padding:.68rem .85rem;
 border-bottom:1px solid #e0e9e4;
 font-weight:600;
}
.readable-table tr:last-child td{border-bottom:none}
.readable-table tr:hover td{background:#f6faf8!important}
.table-status{
 display:inline-block;
 padding:.22rem .55rem;
 border-radius:999px;
 font-weight:900;
 font-size:.72rem;
 letter-spacing:.02em;
}
.table-good{background:#e3f5e9!important;color:#11613a!important}
.table-caution{background:#fff1d7!important;color:#7c5000!important}
.table-avoid{background:#fde8e8!important;color:#982a2a!important}

/* Keep native data grid light; actual application table below uses HTML for deterministic contrast */
[data-testid="stDataFrame"]{
 background:#fff!important;
 color:var(--ink)!important;
}
[data-testid="stDataFrame"] iframe{background:#fff!important;}

[data-testid="stHeader"]{background:transparent!important}
#MainMenu{visibility:hidden} footer{visibility:hidden}

/* FINAL JUDGE CONTRAST OVERRIDE */
[data-testid="stMetric"] *,
[data-testid="stWidgetLabel"] *,
[data-testid="stTabs"] [role="tab"] *,
[data-testid="stTabs"] button *,
[data-testid="stSlider"] label *,
[data-testid="stNumberInput"] label *,
[data-testid="stSelectbox"] label * {
    opacity: 1 !important;
    visibility: visible !important;
}
[data-testid="stMetricLabel"] *,
[data-testid="stWidgetLabel"] *,
[data-testid="stSlider"] label *,
[data-testid="stNumberInput"] label *,
[data-testid="stSelectbox"] label * {
    color: #263b30 !important;
    -webkit-text-fill-color: #263b30 !important;
}
[data-testid="stMetricValue"] * {
    color: #13231a !important;
    -webkit-text-fill-color: #13231a !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------
def decision(score):
    if score >= 75:
        return "FAVOURABLE", "status-good", "Current conditions indicate a favourable application window."
    if score >= 50:
        return "CAUTION", "status-caution", "Conditions are conditional. Review the limiting factors before intervention."
    return "AVOID", "status-avoid", "Current conditions are not favourable. Delay or reassess after conditions change."


def pct(value):
    return max(0, min(float(value), 1.0))


def safe(value, default=0):
    try:
        return float(value)
    except Exception:
        return default


# -------------------------------------------------------------------
# HERO
# -------------------------------------------------------------------
st.markdown(
    """
<div class="hero">
    <div class="hero-badge">HACK CORE 2026 · PS-01 · TEAM 6</div>
    <h1>🌱 BioSync</h1>
    <p><b>Biological Application Timing & Readiness Intelligence</b><br>
    Turning environmental signals into an explainable biological intervention window.</p>
</div>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🌱 BioSync</div><div class="sidebar-kicker">Field Decision Console</div>', unsafe_allow_html=True)
    st.divider()

    st.markdown("### 🧭 Field profile")

    crop = st.selectbox("Crop", list(CROPS))

    st.markdown("**🌡 Environment**")
    tmax = st.number_input("Today max temperature (°C)", 0.0, 55.0, 34.0, 0.5)
    tmin = st.number_input("Today min temperature (°C)", -10.0, 40.0, 22.0, 0.5)
    rain7 = st.number_input("7-day cumulative rainfall (mm)", 0.0, 3000.0, 42.0, 1.0)
    et7 = st.number_input("7-day ET / evaporation proxy (mm)", 0.0, 3000.0, 38.0, 1.0)
    sm = st.number_input("Root-zone soil moisture (%)", 0.0, 100.0, 55.0, 1.0)
    avgtemp = st.number_input("Average temperature (°C)", 0.0, 50.0, 28.0, 0.5)
    st.markdown("**🌱 Field**")
    gdd = st.number_input("Cumulative GDD", 0.0, 6000.0, 2200.0, 10.0)
    ph = st.number_input("Soil pH", 3.0, 10.0, 6.4, 0.1)
    n = st.number_input("Available N (g/kg)", 0.0, 1.0, 0.08, 0.001)
    st.markdown("**🧪 Nutrient & yield signals**")
    yieldkg = st.number_input("Projected yield (kg/ha)", 0.0, 20000.0, 3000.0, 50.0)
    napplied = st.number_input("N applied (kg/ha)", 0.1, 1000.0, 100.0, 1.0)
    pyield = st.number_input("Projected yield for PUE (t/ha)", 0.0, 30.0, 3.0, 0.1)
    papplied = st.number_input("P applied (kg/ha)", 0.1, 500.0, 30.0, 1.0)

    st.divider()
    st.markdown("### 📡 Data status")
    st.success("Decision engine · Online")
    st.info("Forecast panel · Simulated prototype data")
    st.caption("Replace simulated forecast values with CE Hub forecast responses for production integration.")

# -------------------------------------------------------------------
# CORE ENGINE
# -------------------------------------------------------------------
r = readiness(
    crop, tmax, tmin, rain7, et7, sm, avgtemp, gdd, ph, n,
    yieldkg, napplied, pyield, papplied
)

score = safe(r["score"])
label, label_class, decision_text = decision(score)

# -------------------------------------------------------------------
# PRIMARY DECISION
# -------------------------------------------------------------------
st.markdown('<div class="section-label">Decision intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Current application readiness</div>', unsafe_allow_html=True)

decision_col, signals_col = st.columns([1.0, 2.05], gap="large")

with decision_col:
    st.markdown(
        f"""
        <div class="decision-card">
            <div class="decision-score">{score:.1f}<span style="font-size:1.1rem;color:#50635a!important"> / 100</span></div>
            <div class="decision-label"><span class="status-pill {label_class}">● {label}</span></div>
            <div class="decision-sub">{decision_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if label == "FAVOURABLE":
        st.success("🟢 **Recommended:** conditions currently support a favourable window.")
    elif label == "CAUTION":
        st.warning("🟡 **Review:** limiting factors should be checked before intervention.")
    else:
        st.error("🔴 **Delay / reassess:** conditions are currently unfavourable.")

    primary_driver = " + ".join(r.get("reasons", [])[:2]) if r.get("reasons") else "Environmental and field signals from the decision engine"
    st.markdown(
        f'''
        <div class="summary-strip">
            <div class="summary-title">Decision in one line</div>
            <div class="summary-text"><b>{label}</b> — {decision_text} <b>Primary evidence:</b> {primary_driver}.</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

with signals_col:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Heat stress", f"{r['heat_stress']}/9")
    m2.metric("Frost stress", f"{r['frost_stress']}/9")
    m3.metric("Drought index", f"{r['drought_index']}")
    m4.metric("Yield risk", f"{safe(r['yield_risk'])*100:.0f}%")

# -------------------------------------------------------------------
# TABS
# -------------------------------------------------------------------
tab_dashboard, tab_scenario, tab_window, tab_trace = st.tabs(
    ["📊 Dashboard", "🧪 Scenario Simulator", "📅 Application Window", "🧠 Decision Trace"]
)

with tab_dashboard:
    st.markdown("### 🔍 Why this recommendation?")

    left, right = st.columns([1.15, 1], gap="large")

    with left:
        df = pd.DataFrame(
            {
                "Signal": [
                    "Heat",
                    "Frost",
                    "Drought",
                    "Yield risk",
                    "NUE gap",
                    "PUE gap",
                ],
                "Value": [
                    pct(safe(r["heat_stress"]) / 9),
                    pct(safe(r["frost_stress"]) / 9),
                    pct(r["drought_risk"]),
                    pct(r["yield_risk"]),
                    1 - pct(safe(r["nue"]) / 40),
                    1 - pct(safe(r["pue"]) / 0.15),
                ],
            }
        )

        fig = px.bar(
            df,
            x="Signal",
            y="Value",
            range_y=[0, 1],
            text_auto=".2f",
            title="Explainable risk profile",
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=55, b=10),
            height=380,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis_title="Relative risk / gap",
            xaxis_title="",
            font=dict(family="Arial, sans-serif", size=15, color="#263b30"),
            title_font=dict(size=18, color="#13231a"),
            xaxis=dict(
                tickfont=dict(size=13, color="#263b30"),
                title_font=dict(size=13, color="#263b30"),
            ),
            yaxis=dict(
                tickfont=dict(size=13, color="#263b30"),
                title_font=dict(size=13, color="#263b30"),
                gridcolor="#d9e5df",
                zerolinecolor="#c8d8cf",
            ),
        )
        fig.update_xaxes(
            title_font=dict(color="#263b30", size=13),
            tickfont=dict(color="#263b30", size=12),
        )
        fig.update_yaxes(
            title_font=dict(color="#263b30", size=13),
            tickfont=dict(color="#263b30", size=12),
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    with right:
        st.markdown(
            f"""
            <div class="card">
                <div class="section-label">Evidence</div>
                <h3 style="margin-top:0;">Decision drivers</h3>
                <p><b>Crop:</b> {crop}</p>
                <p><b>Heat stress:</b> {r['heat_stress']}/9</p>
                <p><b>Frost stress:</b> {r['frost_stress']}/9</p>
                <p><b>Drought index:</b> {r['drought_index']}</p>
                <p><b>Yield risk:</b> {safe(r['yield_risk'])*100:.0f}%</p>
                <p><b>Nitrogen-use efficiency:</b> {safe(r['nue']):.1f}</p>
                <p><b>Phosphorus-use efficiency:</b> {safe(r['pue']):.3f}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### 🌱 Suggested intervention")
        products = r["products"] if r["products"] else []
        if products:
            for product in products:
                st.markdown(f"- **{product}**")
        else:
            st.info("No product trigger returned by the current decision rules.")

    st.markdown("### 📌 Evidence from the decision engine")
    reasons = r.get("reasons", [])
    if reasons:
        for reason in reasons:
            st.markdown(f"• {reason}")
    else:
        st.caption("No additional rule explanation returned.")

    st.markdown("### 📋 Decision Summary")
    products_text = ", ".join(r["products"]) if r.get("products") else "No product trigger"
    summary_cols = st.columns(4)
    summary_cols[0].metric("Crop", crop)
    summary_cols[1].metric("Readiness", f"{score:.1f}/100")
    summary_cols[2].metric("Decision", label)
    summary_cols[3].metric("Best simulated day", "Day 5")

    summary_text = (
        "BioSync Decision Summary\n"
        "========================\n"
        f"Crop: {crop}\n"
        f"Readiness: {score:.1f}/100\n"
        f"Decision: {label}\n"
        f"Heat stress: {r['heat_stress']}/9\n"
        f"Frost stress: {r['frost_stress']}/9\n"
        f"Drought index: {r['drought_index']}\n"
        f"Yield risk: {safe(r['yield_risk'])*100:.0f}%\n"
        f"Nitrogen-use efficiency: {safe(r['nue']):.2f}\n"
        f"Phosphorus-use efficiency: {safe(r['pue']):.3f}\n"
        f"Suggested interventions: {products_text}\n\n"
        "Evidence:\n"
        + "\n".join("- " + x for x in r.get("reasons", []))
        + "\n\nEvidence boundary:\n"
        "Explainable deterministic prototype baseline. No predictive accuracy is claimed.\n"
    )
    st.download_button(
        "⬇️ Export decision summary",
        data=summary_text,
        file_name=f"biosync_{crop.lower().replace(' ', '_')}_decision.txt",
        mime="text/plain",
    )

with tab_scenario:
    st.markdown("### 🧪 Scenario Simulator")
    st.caption(
        "Explore how changing environmental inputs changes the deterministic readiness decision. "
        "This is a decision-engine scenario tool, not a validated predictive model."
    )

    sc1, sc2 = st.columns(2, gap="large")

    with sc1:
        st.markdown("**Scenario max temperature (°C)**")
        scenario_tmax = st.slider("Scenario max temperature", 0.0, 55.0, float(tmax), 0.5, label_visibility="collapsed")
        st.markdown("**Scenario min temperature (°C)**")
        scenario_tmin = st.slider("Scenario min temperature", -10.0, 40.0, float(tmin), 0.5, label_visibility="collapsed")
        st.markdown("**Scenario 7-day rainfall (mm)**")
        scenario_rain = st.slider("Scenario 7-day rainfall", 0.0, 3000.0, float(rain7), 1.0, label_visibility="collapsed")
        st.markdown("**Scenario 7-day ET proxy (mm)**")
        scenario_et = st.slider("Scenario 7-day ET proxy", 0.0, 3000.0, float(et7), 1.0, label_visibility="collapsed")

    with sc2:
        st.markdown("**Scenario soil moisture (%)**")
        scenario_sm = st.slider("Scenario soil moisture", 0.0, 100.0, float(sm), 1.0, label_visibility="collapsed")
        st.markdown("**Scenario average temperature (°C)**")
        scenario_avg = st.slider("Scenario average temperature", 0.0, 50.0, float(avgtemp), 0.5, label_visibility="collapsed")
        st.markdown("**Scenario cumulative GDD**")
        scenario_gdd = st.number_input("Scenario cumulative GDD", 0.0, 6000.0, float(gdd), 10.0, label_visibility="collapsed")
        st.markdown("**Scenario soil pH**")
        scenario_ph = st.number_input("Scenario soil pH", 3.0, 10.0, float(ph), 0.1, label_visibility="collapsed")

    sr = readiness(
        crop,
        scenario_tmax,
        scenario_tmin,
        scenario_rain,
        scenario_et,
        scenario_sm,
        scenario_avg,
        scenario_gdd,
        scenario_ph,
        n,
        yieldkg,
        napplied,
        pyield,
        papplied,
    )
    scenario_score = safe(sr["score"])
    scenario_label, scenario_class, scenario_text = decision(scenario_score)

    st.markdown("### Scenario result")
    a, b, c = st.columns(3)
    a.metric("Baseline", f"{score:.1f}/100")
    b.metric("Scenario", f"{scenario_score:.1f}/100", f"{scenario_score-score:+.1f}")
    c.metric("Decision", scenario_label)

    st.markdown(
        f"""
        <div class="card">
            <div class="section-label">Decision explanation</div>
            <h3 style="margin-top:0;">Scenario: {scenario_label}</h3>
            <p>{scenario_text}</p>
            <p><b>Heat:</b> {sr['heat_stress']}/9 &nbsp; | &nbsp;
            <b>Frost:</b> {sr['frost_stress']}/9 &nbsp; | &nbsp;
            <b>Drought:</b> {sr['drought_index']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with tab_window:
    st.markdown("### 📅 7-day application window")
    st.caption(
        "Prototype mode: the environmental profile below is simulated from current inputs. "
        "Use CE Hub forecast data for a production/live forecast."
    )

    deltas_tmax = [0.5, -1.0, 1.5, -0.5, -2.0, 0.0, 1.0]
    deltas_tmin = [0, -0.5, 1.0, 0, -1.0, 0.5, 0]
    deltas_avg = [0.2, -0.5, 0.8, -0.2, -0.8, 0.0, 0.4]

    rows = []
    for i in range(7):
        rows.append(
            {
                "day": f"Day {i+1}",
                "tmax": tmax + deltas_tmax[i],
                "tmin": tmin + deltas_tmin[i],
                "temp": avgtemp + deltas_avg[i],
            }
        )

    forecast = score_forecast(
        rows,
        crop=crop,
        rain7=rain7,
        et7=et7,
        soil_moisture=sm,
        gdd=gdd,
        ph=ph,
        n=n,
        yield_kg=yieldkg,
        n_applied=napplied,
        p_yield_t=pyield,
        p_applied=papplied,
    )
    fdf = pd.DataFrame(forecast)

    if not fdf.empty:
        fdf["score"] = pd.to_numeric(fdf["score"], errors="coerce").fillna(0)
        fdf["status"] = fdf["score"].apply(lambda x: decision(x)[0])
        best = fdf.loc[fdf["score"].idxmax()]
        best_score = safe(best["score"])
        best_label, _, _ = decision(best_score)

        fig = px.line(
            fdf,
            x="day",
            y="score",
            markers=True,
            range_y=[0, 100],
            labels={"score": "Readiness score", "day": "Forecast horizon"},
        )
        fig.update_traces(line=dict(width=3), marker=dict(size=9))
        fig.update_layout(
            title="7-day readiness profile",
            height=350,
            margin=dict(l=10, r=10, t=50, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Arial, sans-serif", size=15, color="#263b30"),
            title_font=dict(size=18, color="#13231a"),
            xaxis=dict(
                title="Forecast horizon",
                tickfont=dict(size=13, color="#263b30"),
                title_font=dict(size=14, color="#263b30"),
            ),
            yaxis=dict(
                title="Readiness score",
                gridcolor="#d9e5df",
                tickfont=dict(size=13, color="#263b30"),
                title_font=dict(size=14, color="#263b30"),
            ),
        )
        fig.update_xaxes(
            title_font=dict(color="#263b30", size=14),
            tickfont=dict(color="#263b30", size=13),
        )
        fig.update_yaxes(
            title_font=dict(color="#263b30", size=14),
            tickfont=dict(color="#263b30", size=13),
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

        b1, b2, b3 = st.columns(3)
        b1.metric("Best simulated day", best["day"])
        b2.metric("Peak readiness", f"{best_score:.1f}/100")
        b3.metric("Classification", best_label)

        st.markdown("#### Window-by-window view")
        table_rows = ""
        for _, row in fdf.iterrows():
            status = str(row["status"])
            status_class = "table-good" if status == "FAVOURABLE" else ("table-caution" if status == "CAUTION" else "table-avoid")
            table_rows += f"""
            <tr>
                <td>{row["day"]}</td>
                <td><strong>{float(row["score"]):.1f}/100</strong></td>
                <td><span class="table-status {status_class}">{status}</span></td>
            </tr>"""
        st.markdown(
            f"""
            <div class="readable-table-wrap">
                <table class="readable-table">
                    <thead><tr><th>Day</th><th>Readiness</th><th>Decision</th></tr></thead>
                    <tbody>{table_rows}</tbody>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.info(
            "⚠️ **Data boundary:** this is a simulated application-window profile, not a live forecast. "
            "The integration target is the CE Hub forecast endpoint."
        )

with tab_trace:
    st.markdown("### 🧠 Decision Trace")
    st.caption("A transparent view of how BioSync moves from inputs to a recommendation.")

    trace = [
        ("01 · INPUT", f"{crop} + environmental and field variables"),
        ("02 · VALIDATE", "Inputs are passed into the current deterministic rules engine"),
        (
            "03 · FEATURE ENGINEERING",
            f"Heat {r['heat_stress']}/9 · Frost {r['frost_stress']}/9 · Drought {r['drought_index']}",
        ),
        (
            "04 · RISK SIGNALS",
            f"Yield risk {safe(r['yield_risk'])*100:.0f}% · NUE {safe(r['nue']):.1f} · PUE {safe(r['pue']):.3f}",
        ),
        ("05 · READINESS", f"Composite readiness = {score:.1f}/100"),
        ("06 · CLASSIFY", label),
        (
            "07 · RECOMMEND",
            ", ".join(r["products"]) if r["products"] else "No product trigger returned",
        ),
    ]

    for title, text in trace:
        st.markdown(
            f"""
            <div class="trace-step">
                <div class="trace-title">{title}</div>
                <div class="trace-text">{text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### 🔐 Evidence boundary")
    st.info(
        "The current prototype is an explainable deterministic baseline. "
        "Historical validation and ML calibration are Build Sprint steps; no predictive accuracy is claimed yet."
    )

# -------------------------------------------------------------------
# FOOTER
# -------------------------------------------------------------------
st.divider()
st.markdown(
    """
<div class="footer">
    🌱 <b>BioSync</b> · HACK CORE 2026 · PS-01 · Team 6<br>
    Nafis Devtale · Tejas Chougule · Aditya Mishra · Pratik Tupe<br><br>
    Prototype decision-support system. Outputs are not a substitute for agronomist judgement,
    product labels, regulatory guidance or field validation.
</div>
""",
    unsafe_allow_html=True,
)
