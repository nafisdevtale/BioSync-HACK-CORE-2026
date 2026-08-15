# BioSync architecture

```text
CE Hub Historical + Forecast APIs
            |
            v
  Data normalization / QA
            |
            +--------------------+
            |                    |
            v                    v
 Organizer agronomic       AI explanation layer
 rules + thresholds        (Gemini / Vertex AI)
            |                    |
            +---------+----------+
                      v
             Readiness Engine
                      |
          +-----------+-----------+
          |                       |
          v                       v
  7-day application        Explainable advisory
       window                    card
          |                       |
          +-----------+-----------+
                      v
              Farmer / Agronomist UI
```

## AI boundary
The deterministic engine remains the source of truth for the score and product trigger. Gemini/Vertex AI is constrained to explanation, summarization, scenario comparison and natural-language advisory. It must not invent weather values, thresholds or product claims.

## Build-sprint evolution
1. Replace demo forecast vectors with CE Hub API calls.
2. Store normalized weather + recommendation traces in BigQuery.
3. Add Vertex AI/Gemini structured explanation.
4. Add calibration/validation once labeled field outcomes are available.
5. Add alerting and field-level profiles.
