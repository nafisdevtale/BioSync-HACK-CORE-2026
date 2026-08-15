# BioSync — Biological Application Timing & Readiness Engine

**HACK CORE 2026 | PS-01 — Biological application timing & readiness scoring**

BioSync is a prototype decision-support system that converts historical/forecast weather and crop conditions into an explainable biological application readiness score and recommended intervention window.

## What is implemented
- Crop-aware heat and frost stress calculations from the organizer's Algorithm Logic document.
- Drought, yield-risk, nitrogen-use-efficiency and phosphorus-use-efficiency modules using the supplied formulas/thresholds.
- A unified 0–100 readiness score with transparent evidence and safety gates.
- 7-day forecast simulation input for a practical application window.
- Optional Gemini explanation layer: turns the structured score into a concise, farmer-facing explanation without changing the deterministic score.
- Streamlit dashboard for a tangible prototype.

## Important disclosure
The agronomic equations and thresholds are transcribed from the HACK CORE 2026 organizer-provided algorithm document. No claim is made that the prototype has been field-validated. The Gemini layer is an explanation/decision-support layer, not a substitute for agronomic validation.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

Optional Gemini:
```bash
export GEMINI_API_KEY="YOUR_KEY"
streamlit run app/streamlit_app.py
```

## Proposed production architecture
CE Hub historical/forecast APIs -> ingestion/normalization -> BigQuery -> agronomic rules + ML/AI layer -> readiness window -> farmer/agronomist UI.

Google Cloud candidates: Cloud Run, BigQuery, Vertex AI/Gemini, Cloud Storage, Secret Manager and Cloud Scheduler.

## Recommended demo story
Select Soybean and enter a hot/low-rainfall scenario. Show the score, stress breakdown and 7-day window. Then change Tmax/rainfall to demonstrate the recommendation moving from RED/YELLOW to GREEN. This makes the prototype visibly decision-oriented rather than a static dashboard.
