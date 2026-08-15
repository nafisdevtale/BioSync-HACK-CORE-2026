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
    :root {
        --bio-green: #167a4a;
        --bio-green-dark: #0d5131;
        --bio-green-soft: #eaf7ef;
        --bio-amber: #c47a00;
        --bio-red: #c73b3b;
        --bio-ink: #17231d;
        --bio-muted: #65736b;
        --bio-border: #dfe8e2;
        --bio-bg: #f7faf8;
    }

    .stApp {
        background: linear-gradient(180deg, #f8fbf9 0%, #ffffff 32%);
    }

    [data-testid="stHeader"] {
        background: rgba(255,255,255,0);
    }

    .block-container {
        max-width: 1400px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    .hero {
        background: linear-gradient(135deg, #0d5131 0%, #167a4a 58%, #27915e 100%);
        color: white;
        padding: 2rem 2.2rem;
        border-radius: 24px;
        margin-bottom: 1.2rem;
        box-shadow: 0 14px 40px rgba(13,81,49,.16);
    }

    .hero h1 {
        margin: 0;
        font-size: 2.55rem;
        line-height: 1.05;
        color: white;
        letter-spacing: -0.03em;
    }

    .hero p {
        margin: .65rem 0 0;
        font-size: 1.05rem;
        color: rgba(255,255,255,.88);
        max-width: 850px;
    }

    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,.14);
        border: 1px solid rgba(255,255,255,.22);
        border-radius: 999px;
        padding: .35rem .75rem;
        font-size: .78rem;
        font-weight: 700;
        letter-spacing: .04em;
        margin-bottom: .85rem;
    }

    .section-label {
        color: var(--bio-green);
        font-size: .76rem;
        font-weight: 800;
        letter-spacing: .11em;
        text-transform: uppercase;
        margin: .2rem 0 .35rem;
    }

    .section-title {
        color: var(--bio-ink);
        font-size: 1.55rem;
        font-weight: 800;
        margin-bottom: .85rem;
    }

    .card {
        background: white;
        border: 1px solid var(--bio-border);
        border-radius: 18px;
        padding: 1.1rem 1.25rem;
        box-shadow: 0 5px 20px rgba(30,60,45,.05);
        height: 100%;
    }

    .decision-card {
        background: white;
        border: 1px solid var(--bio-border);
        border-radius: 22px;
        padding: 1.45rem 1.55rem;
        box-shadow: 0 10px 32px rgba(30,60,45,.07);
        text-align: center;
    }

    .decision-score {
        font-size: 3.35rem;
        line-height: 1;
        font-weight: 900;
        color: var(--bio-green-dark);
        letter-spacing: -.05em;
    }

    .decision-label {
        margin-top: .55rem;
        font-size: 1rem;
        font-weight: 800;
        color: var(--bio-green);
        letter-spacing: .06em;
    }

    .decision-sub {
        margin-top: .55rem;
        color: var(--bio-muted);
        font-size: .9rem;
    }

    .mini-card {
        background: white;
        border: 1px solid var(--bio-border);
        border-radius: 15px;
        padding: .9rem 1rem;
        min-height: 92px;
    }

    .mini-label {
        color: var(--bio-muted);
        font-size: .76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .06em;
    }

    .mini-value {
        color: var(--bio-ink);
        font-size: 1.45rem;
        font-weight: 850;
        margin-top: .25rem;
    }

    .status-pill {
        display: inline-block;
        padding: .35rem .75rem;
        border-radius: 999px;
        font-weight: 800;
        font-size: .78rem;
        letter-spacing: .04em;
    }

    .status-good {
        background: #e8f7ee;
        color: #176a40;
    }

    .status-caution {
        background: #fff3dc;
        color: #8a5700;
    }

    .status-avoid {
        background: #fdeaea;
        color: #9f2e2e;
    }

    .trace-step {
        border-left: 3px solid #b9ddc6;
        padding: .2rem 0 .8rem .85rem;
        margin-left: .35rem;
    }

    .trace-title {
        font-weight: 800;
        color: var(--bio-ink);
    }

    .trace-text {
        color: var(--bio-muted);
        font-size: .88rem;
    }

    .footer {
        text-align: center;
        color: #748078;
        font-size: .78rem;
        padding: 1.5rem 0 .5rem;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid var(--bio-border);
        padding: .8rem 1rem;
        border-radius: 15px;
        box-shadow: 0 5px 18px rgba(30,60,45,.04);
    }

    div[data-testid="stMetricLabel"] {
        color: var(--bio-muted);
    }

    div[data-testid="stMetricValue"] {
        color: var(--bio-ink);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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
    st.markdown("## 🌱 BioSync")
    st.caption("Field Decision Console")
    st.divider()

    st.markdown("### 🧭 Field profile")

    crop = st.selectbox("Crop", list(CROPS))

    tmax = st.number_input("Today max temperature (°C)", 0.0, 55.0, 34.0, 0.5)
    tmin = st.number_input("Today min temperature (°C)", -10.0, 40.0, 22.0, 0.5)
    rain7 = st.number_input("7-day cumulative rainfall (mm)", 0.0, 3000.0, 42.0, 1.0)
    et7 = st.number_input("7-day ET / evaporation proxy (mm)", 0.0, 3000.0, 38.0, 1.0)
    sm = st.number_input("Root-zone soil moisture (%)", 0.0, 100.0, 55.0, 1.0)
    avgtemp = st.number_input("Average temperature (°C)", 0.0, 50.0, 28.0, 0.5)
    gdd = st.number_input("Cumulative GDD", 0.0, 6000.0, 2200.0, 10.0)
    ph = st.number_input("Soil pH", 3.0, 10.0, 6.4, 0.1)
    n = st.number_input("Available N (g/kg)", 0.0, 1.0, 0.08, 0.001)
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
            <div class="decision-score">{score:.1f}<span style="font-size:1.1rem;color:#65736b"> / 100</span></div>
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

with signals_col:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🔥 Heat stress", f"{r['heat_stress']}/9")
    m2.metric("❄️ Frost stress", f"{r['frost_stress']}/9")
    m3.metric("💧 Drought index", f"{r['drought_index']}")
    m4.metric("🌾 Yield risk", f"{safe(r['yield_risk'])*100:.0f}%")

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
        )
        st.plotly_chart(fig, use_container_width=True)

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

with tab_scenario:
    st.markdown("### 🧪 Scenario Simulator")
    st.caption(
        "Explore how changing environmental inputs changes the deterministic readiness decision. "
        "This is a decision-engine scenario tool, not a validated predictive model."
    )

    sc1, sc2 = st.columns(2, gap="large")

    with sc1:
        scenario_tmax = st.slider("Scenario max temperature (°C)", 0.0, 55.0, float(tmax), 0.5)
        scenario_tmin = st.slider("Scenario min temperature (°C)", -10.0, 40.0, float(tmin), 0.5)
        scenario_rain = st.slider("Scenario 7-day rainfall (mm)", 0.0, 3000.0, float(rain7), 1.0)
        scenario_et = st.slider("Scenario 7-day ET proxy (mm)", 0.0, 3000.0, float(et7), 1.0)

    with sc2:
        scenario_sm = st.slider("Scenario soil moisture (%)", 0.0, 100.0, float(sm), 1.0)
        scenario_avg = st.slider("Scenario average temperature (°C)", 0.0, 50.0, float(avgtemp), 0.5)
        scenario_gdd = st.number_input("Scenario cumulative GDD", 0.0, 6000.0, float(gdd), 10.0)
        scenario_ph = st.number_input("Scenario soil pH", 3.0, 10.0, float(ph), 0.1)

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
        "Current prototype mode: simulated forecast profile. "
        "The production version should replace these values with CE Hub forecast data."
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
        fig = px.line(
            fdf,
            x="day",
            y="score",
            markers=True,
            range_y=[0, 100],
            labels={"score": "Readiness score", "day": "Forecast horizon"},
        )
        fig.update_layout(
            height=390,
            margin=dict(l=10, r=10, t=20, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

        best = fdf.loc[fdf["score"].idxmax()]
        best_score = safe(best["score"])
        best_label, _, _ = decision(best_score)

        b1, b2, b3 = st.columns(3)
        b1.metric("Best simulated day", best["day"])
        b2.metric("Peak readiness", f"{best_score:.1f}/100")
        b3.metric("Classification", best_label)

        st.info(
            "⚠️ **Prototype disclosure:** this 7-day panel uses simulated UI inputs. "
            "It must be driven by CE Hub forecast data before being presented as a live forecast."
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
