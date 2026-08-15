import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import streamlit as st
import pandas as pd
import plotly.express as px
from engine.rules import CROPS, readiness, score_forecast

st.set_page_config(page_title='BioSync | HACK CORE 2026', page_icon='🌱', layout='wide')
st.title('🌱 BioSync')
st.caption('Biological Application Timing & Readiness Intelligence — HACK CORE 2026 | PS-01')

with st.sidebar:
    st.header('Field profile')
    crop=st.selectbox('Crop',list(CROPS))
    tmax=st.number_input('Today max temperature (°C)',0.0,55.0,34.0,0.5)
    tmin=st.number_input('Today min temperature (°C)',-10.0,40.0,22.0,0.5)
    rain7=st.number_input('7-day cumulative rainfall (mm)',0.0,3000.0,42.0,1.0)
    et7=st.number_input('7-day ET / evaporation proxy (mm)',0.0,3000.0,38.0,1.0)
    sm=st.number_input('Root-zone soil moisture (%)',0.0,100.0,55.0,1.0)
    avgtemp=st.number_input('Average temperature (°C)',0.0,50.0,28.0,0.5)
    gdd=st.number_input('Cumulative GDD',0.0,6000.0,2200.0,10.0)
    ph=st.number_input('Soil pH',3.0,10.0,6.4,0.1)
    n=st.number_input('Available N (g/kg)',0.0,1.0,0.08,0.001)
    yieldkg=st.number_input('Projected yield (kg/ha)',0.0,20000.0,3000.0,50.0)
    napplied=st.number_input('N applied (kg/ha)',0.1,1000.0,100.0,1.0)
    pyield=st.number_input('Projected yield for PUE (t/ha)',0.0,30.0,3.0,0.1)
    papplied=st.number_input('P applied (kg/ha)',0.1,500.0,30.0,1.0)

r=readiness(crop,tmax,tmin,rain7,et7,sm,avgtemp,gdd,ph,n,yieldkg,napplied,pyield,papplied)

c1,c2,c3,c4=st.columns(4)
c1.metric('Readiness score',f"{r['score']}/100")
c2.metric('Heat stress',f"{r['heat_stress']}/9")
c3.metric('Frost stress',f"{r['frost_stress']}/9")
c4.metric('Drought index',f"{r['drought_index']}")

st.subheader('Decision')
if r['score']>=75: st.success('🟢 READY / FAVOURABLE WINDOW')
elif r['score']>=50: st.warning('🟡 CONDITIONAL / REVIEW WINDOW')
else: st.error('🔴 NOT FAVOURABLE / DELAY OR REASSESS')
st.write('**Suggested biological interventions:**', ', '.join(r['products']) if r['products'] else 'No product trigger')
st.write('**Evidence:** ' + '; '.join(r['reasons']))

left,right=st.columns([1,1])
with left:
    st.subheader('Explainable risk profile')
    df=pd.DataFrame({'Signal':['Heat','Frost','Drought','Yield risk','NUE gap','PUE gap'], 'Value':[r['heat_stress']/9,r['frost_stress']/9,r['drought_risk'],r['yield_risk'],1-min(r['nue']/40,1),1-min(r['pue']/0.15,1)]})
    fig=px.bar(df,x='Signal',y='Value',range_y=[0,1],text_auto='.2f')
    st.plotly_chart(fig,use_container_width=True)
with right:
    st.subheader('Why this recommendation?')
    st.markdown(f"- Crop: **{crop}**\n- Heat stress: **{r['heat_stress']}/9**\n- Frost stress: **{r['frost_stress']}/9**\n- Drought index: **{r['drought_index']}**\n- Yield risk: **{r['yield_risk']*100:.0f}%**\n- Nitrogen use efficiency: **{r['nue']:.1f}**\n- Phosphorus use efficiency: **{r['pue']:.3f}**")

st.subheader('7-day application window simulator')
rows=[]
for i in range(7):
    day=f'Day {i+1}'
    # Demo forecast profile; replace with CE Hub forecast endpoint in production.
    rows.append({'day':day,'tmax':tmax + [0.5,-1.0,1.5,-0.5,-2.0,0.0,1.0][i],'tmin':tmin + [0,-0.5,1.0,0,-1.0,0.5,0][i],'temp':avgtemp + [0.2,-0.5,0.8,-0.2,-0.8,0.0,0.4][i]})
forecast=score_forecast(rows,crop=crop,rain7=rain7,et7=et7,soil_moisture=sm,gdd=gdd,ph=ph,n=n,yield_kg=yieldkg,n_applied=napplied,p_yield_t=pyield,p_applied=papplied)
fdf=pd.DataFrame(forecast)
fig=px.line(fdf,x='day',y='score',markers=True,range_y=[0,100],labels={'score':'Readiness score','day':'Forecast horizon'})
st.plotly_chart(fig,use_container_width=True)
best=fdf.loc[fdf['score'].idxmax()]
st.info(f"Best simulated window: **{best['day']}** with readiness **{best['score']}/100**. In production this panel should be driven directly by CE Hub forecast data.")

st.divider()
st.caption('Prototype note: organizer-provided formulas are used as the deterministic agronomic baseline. Forecast values in this demo are simulated UI inputs and must be replaced by CE Hub API data before deployment.')
