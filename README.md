# 🌱 BioSync — HACK CORE 2026

### Biological Application Timing & Readiness Intelligence

> **Turning environmental signals into explainable biological intervention windows.**

**HACK CORE 2026 · PS-01 · Team 6**

### Team
Nafis Devtale · Tejas Chougule · Aditya Mishra · Pratik Tupe

## 🚀 Live Prototype
https://biosync-hackcore26.streamlit.app/

## 📂 Repository
https://github.com/nafisdevtale/BioSync-HACK-CORE-2026

## Problem
Weather platforms expose environmental data, but raw data does not directly answer the operational question: **Is this a favourable biological application window, and why?**

## Solution
BioSync is an explainable decision-support layer that converts crop, field and environmental signals into:
- a 0–100 readiness score;
- Favourable / Caution / Avoid classification;
- agronomic stress and risk indicators;
- intervention class;
- evidence and decision trace.

## Decision Pipeline
```text
Weather + Field Data
        ↓
Data Validation
        ↓
Agronomic Feature Engineering
        ↓
Heat | Frost | Drought | Yield | NUE/PUE
        ↓
Readiness Decision Engine
        ↓
Application Window
        ↓
Explainable Recommendation
```

## Current Prototype
The current prototype uses a deterministic, inspectable agronomic decision engine based on the organizer-provided resources and logic. It is intentionally not presented as a validated predictive ML model.

## AI / ML Roadmap
The Build Sprint direction is:
1. historical replay;
2. labelled-outcome validation;
3. ML calibration of readiness/risk components;
4. forecast-window ranking;
5. constrained AI explanation/scenario communication;
6. agronomist/user evaluation.

No predictive accuracy is claimed before validation.

## Data & External Resources
The solution uses organizer-provided CE Hub resources, historical/forecast configurations and the supplied agronomic algorithm/threshold logic. The shared Meteoblue historical configuration and CE Hub forecast API documentation are used as specified resources.

## Google Cloud Scale Architecture
CE Hub/API ingestion → Cloud Run → BigQuery/Cloud Storage → feature engineering → Vertex AI → BioSync decision API → advisory/dashboard clients.

Secret Manager can be used for credentials where required.

## Technology
Python · Pandas · NumPy · Streamlit · REST/API architecture · CE Hub resources · Meteoblue configuration · GitHub · Streamlit Community Cloud · Google Cloud/Vertex AI/Gemini-ready architecture

## Team Contributions
- **Nafis Devtale:** solution architecture, AI/ML direction, decision-engine integration, prototype implementation, deployment and technical coordination.
- **Tejas Chougule:** data preparation, feature engineering, agronomic indicators, algorithm implementation and validation workflow.
- **Aditya Mishra:** application development, API/data integration, backend structure, testing and deployment readiness.
- **Pratik Tupe:** user workflow, dashboard experience, impact/business framing, documentation and presentation.

## Disclosure
BioSync is a team-developed HACK CORE 2026 prototype. No unrelated commercial product, proprietary codebase or third-party proprietary model has been incorporated. Public/open-source libraries and organizer-provided resources are acknowledged.

## Disclaimer
BioSync is a prototype decision-support system. Its outputs are not a substitute for agronomist judgement, product labels or field validation.
