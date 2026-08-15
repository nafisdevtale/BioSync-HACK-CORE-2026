"""Optional constrained Gemini/Vertex AI explanation adapter.
The model receives only structured engine output and must not alter the score.
"""
import os

def build_prompt(result):
    return f"""You are an agricultural decision-support explainer. Do not invent weather, agronomic thresholds, efficacy claims, or product facts. Do not change the numeric recommendation. Explain only the supplied structured result in <=80 words for an agronomist. Clearly label uncertainty. Structured result: {result}"""

def enabled():
    return bool(os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_CLOUD_PROJECT'))
