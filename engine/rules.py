from dataclasses import dataclass
from typing import Dict, List, Optional
import math

CROPS = {
    "Soybean": {"tmax_opt": 32, "tmax_limit": 45, "gdd": (2400,3000), "rain": (450,700), "ph": (6.0,6.8), "n": (0,0.026), "sm": (50,70), "p_product": ["Stress Buster","Nutrient Booster","Yield Booster"]},
    "Corn": {"tmax_opt": 33, "tmax_limit": 44, "gdd": (2700,3100), "rain": (500,800), "ph": (6.0,6.8), "n": (0.077,0.154), "sm": (50,70), "p_product": ["Stress Buster","Nutrient Booster","Yield Booster"]},
    "Cotton": {"tmax_opt": 32, "tmax_limit": 38, "gdd": (2200,2600), "rain": (700,1300), "ph": (6.0,6.5), "n": (0.051,0.092), "sm": (50,70), "p_product": ["Stress Buster","Yield Booster"]},
    "Rice": {"tmax_opt": 32, "tmax_limit": 38, "gdd": (2000,2500), "rain": (1000,1500), "ph": (5.5,6.5), "n": (0.051,0.103), "sm": (80,80), "p_product": ["Stress Buster","Yield Booster"]},
    "Wheat": {"tmax_opt": 25, "tmax_limit": 32, "gdd": (2000,2500), "rain": (1000,1500), "ph": (5.5,6.5), "n": (0.051,0.103), "sm": (80,80), "p_product": ["Stress Buster","Yield Booster"]},
}

def clamp(x, lo=0.0, hi=9.0):
    return max(lo, min(hi, float(x)))

def heat_stress(tmax, crop):
    c=CROPS[crop]
    if tmax <= c['tmax_opt']: return 0.0
    if tmax >= c['tmax_limit']: return 9.0
    return clamp(9*(tmax-c['tmax_opt'])/(c['tmax_limit']-c['tmax_opt']))

def frost_stress(tmin, no_frost=4.0, frost_limit=-3.0):
    if tmin >= no_frost: return 0.0
    if tmin <= frost_limit: return 9.0
    return clamp(9*abs(tmin-no_frost)/abs(frost_limit-no_frost))

def range_distance(value, optimum, direction='inside'):
    lo, hi = optimum
    if lo == hi:
        return min(1.0, abs(value-lo)/max(abs(lo),1))
    if lo <= value <= hi: return 0.0
    if value < lo: return min(1.0, (lo-value)/max(abs(lo),1))
    return min(1.0, (value-hi)/max(abs(hi),1))

def drought_index(rain, et, soil_moisture, temp):
    # Parenthesized exactly as the organizer text implies: DI=(P-E+SM)/T.
    return (rain - et + soil_moisture) / max(temp, 0.1)

def yield_risk(gdd, rain, ph, n, crop, weights=(0.3,0.3,0.2,0.2)):
    c=CROPS[crop]
    # Convert deviations to normalized 0..1 penalties, preserving the supplied weighted structure.
    dg=range_distance(gdd,c['gdd']); dp=range_distance(rain,c['rain']); dph=range_distance(ph,c['ph']); dn=range_distance(n,c['n'])
    return min(1.0, weights[0]*dg + weights[1]*dp + weights[2]*dph + weights[3]*dn)

def nue_n(yield_kg_ha, n_applied, rain, soil_moisture, crop):
    c=CROPS[crop]; rmid=sum(c['rain'])/2; smid=sum(c['sm'])/2
    rf=rain/rmid if rmid else 1
    smf=soil_moisture/smid if smid else 1
    nue=(yield_kg_ha/max(n_applied,0.001))*rf*smf
    return nue, rf, smf

def pue(yield_t_ha, p_applied, ph, soil_moisture, rain, crop):
    c=CROPS[crop]; pmid=sum(c['ph'])/2; smid=sum(c['sm'])/2; rmid=sum(c['rain'])/2
    phf=min(1, ph/pmid) if ph<=pmid else min(1, pmid/ph)
    smf=min(1, soil_moisture/smid) if soil_moisture<=smid else min(1, smid/soil_moisture)
    rf=min(1, rain/rmid) if rain<=rmid else min(1, rmid/rain)
    sf=(phf+smf+rf)/3
    return (yield_t_ha/max(p_applied,0.001))*sf, sf

def readiness(crop, tmax, tmin, rain7, et7, soil_moisture, temp_avg, gdd, ph, n, yield_kg, n_applied, p_yield_t, p_applied):
    hs=heat_stress(tmax,crop); fs=frost_stress(tmin)
    di=drought_index(rain7,et7,soil_moisture,temp_avg)
    # Drought flag follows organizer interpretation: DI > 1 no risk; <=1 risk.
    drought_risk=max(0.0,min(1.0,1-di)) if di<=1 else 0.0
    yr=yield_risk(gdd,rain7,ph,n,crop)
    nue,rf,smf=nue_n(yield_kg,n_applied,rain7,soil_moisture,crop)
    pue_v,sf=pue(p_yield_t,p_applied,ph,soil_moisture,rain7,crop)
    # Readiness: lower stress/risk => higher immediate readiness, with agronomic safety gates.
    risk=(0.30*(hs/9)+0.20*(fs/9)+0.20*drought_risk+0.15*yr+0.10*(1-min(nue/40,1))+0.05*(1-min(pue_v/0.15,1)))
    score=round(100*(1-risk),1)
    products=[]
    reasons=[]
    if hs>=3 or fs>=3 or drought_risk>=0.25: products.append('Stress Buster'); reasons.append('abiotic stress signal')
    if nue<40: products.append('Nutrient Booster'); reasons.append('N-use efficiency below high-NUE band')
    if yr>0.20: products.append('Yield Booster'); reasons.append('yield-risk signal')
    # Deduplicate and respect crop applicability.
    products=[p for i,p in enumerate(products) if p in CROPS[crop]['p_product'] and p not in products[:i]]
    if not products: reasons.append('no major stress trigger detected')
    return {
        'score':score,'heat_stress':round(hs,2),'frost_stress':round(fs,2),'drought_index':round(di,3),
        'drought_risk':round(drought_risk,3),'yield_risk':round(yr,3),'nue':round(nue,2),'pue':round(pue_v,3),
        'products':products,'reasons':reasons,'rf':round(rf,3),'smf':round(smf,3),'sf':round(sf,3)
    }

def score_forecast(rows: List[Dict], **base):
    out=[]
    for r in rows:
        x=readiness(tmax=r['tmax'],tmin=r['tmin'],rain7=base['rain7'],et7=base['et7'],soil_moisture=base['soil_moisture'],temp_avg=r['temp'],gdd=base['gdd'],ph=base['ph'],n=base['n'],yield_kg=base['yield_kg'],n_applied=base['n_applied'],p_yield_t=base['p_yield_t'],p_applied=base['p_applied'],crop=base['crop'])
        out.append({**r,**x})
    return out
