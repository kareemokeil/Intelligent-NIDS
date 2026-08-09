"""
utils/report_generator.py
----------------------------
The ONLY module that knows about Gemini and (indirectly, via utils.rag)
FAISS. Pages call exactly one function:

    generate_report(sample, predicted_class, confidence, shap_df) -> str

Internally this module:
  1. Retrieves supporting knowledge-base documents (utils.rag.retrieve_context)
  2. Builds the SHAP summary block from shap_df
  3. Builds the retrieved-knowledge context block
  4. Constructs the tuned SOC-analyst prompt
  5. Calls Gemini
  6. Returns the Markdown report

Ported from Kareem's 5_LLM_Integration.ipynb.

SECURITY NOTE
-------------
The original notebook had the Gemini API key hardcoded directly in the
source. That key should be treated as compromised — regenerate it in
Google AI Studio and never paste a real key into code again. This file
reads the key ONLY from the environment variable GEMINI_API_KEY.

Set it before running the dashboard:
    Windows (PowerShell):  $env:GEMINI_API_KEY = "your-new-key"
    Windows (persistent):  setx GEMINI_API_KEY "your-new-key"   (restart terminal)
    macOS/Linux:            export GEMINI_API_KEY="your-new-key"
"""

import os
import re
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

from utils.rag import retrieve_context

load_dotenv()

GEMINI_MODEL_NAME = "gemini-flash-latest"

def _clean_content(text: str) -> str:
    """Collapse multiple blank lines and strip leading/trailing whitespace."""
    text = text.strip()
    return re.sub(r"\n{2,}", "\n\n", text)


def _build_shap_summary(shap_df: pd.DataFrame, top_n: int = 5) -> str:
    """Same block format as the notebook's `shap_summary` variable."""
    summary = ""
    for _, row in shap_df.head(top_n).iterrows():
        summary += f"""
Rank: {row['Rank']}
Feature: {row['Feature']}
Observed Value: {row['Observed Value']:.2f}
SHAP Contribution: {row['SHAP Value']:.4f}
Contribution Direction: {row['Direction']}
Impact Level: {row['Impact']}

"""
    return summary


def _build_retrieved_context(retrieved_docs: list) -> str:
    """Same block format as the notebook's `context` variable."""
    if not retrieved_docs:
        return "No relevant documents were retrieved from the knowledge base for this prediction."

    parts = []
    for i, doc in enumerate(retrieved_docs, start=1):
        attack_name = doc.get("attack", "Unknown")
        source = doc.get("title", "Unknown")
        content = _clean_content(doc.get("content", ""))
        parts.append(f"[Document {i} | Attack: {attack_name} | Source: {source}]\n{content}")
    return "\n\n".join(parts)


def _build_prompt(report_id, report_date, predicted_class, confidence, shap_summary, context) -> str:
    """Identical structure/wording to the notebook's tuned prompt."""
    return f"""
You are a Senior SOC Analyst, Threat Hunter, and Incident Response Specialist.

Generate a professional, evidence-based cybersecurity incident report in Markdown.

Your report MUST rely exclusively on the following evidence:

1. Machine Learning prediction
2. SHAP explainability results
3. Retrieved cybersecurity knowledge (RAG)

Do not use external cybersecurity knowledge.
Do not fabricate technical details.
If the supplied evidence is insufficient, clearly state that additional investigation is required.

---

# Incident Metadata

Report ID: {report_id}

Report Date: {report_date}

Attack Type: {predicted_class}

Prediction Confidence: {confidence * 100:.2f}%

Machine Learning Model: Random Forest

Dataset: CICIDS2017

Explainability Method: SHAP

Knowledge Base: FAISS Retrieval-Augmented Generation (RAG)

---

# SHAP Explainability Results

{shap_summary}

---

# Retrieved Cybersecurity Knowledge

{context}

---

# Required Report Structure

## Executive Summary

Summarize:

- suspected attack
- potential operational impact
- analyst recommendation

Do not describe the incident as confirmed.

---

## Attack Characteristics

Present as a Markdown table containing:

- Attack Type
- Prediction Confidence
- Machine Learning Model
- Dataset
- Explainability Method
- Knowledge Base

---

## Evidence Sources

Present as a Markdown table.

Include:

- Prediction -> Random Forest
- Confidence -> Random Forest
- Explainability -> SHAP
- Threat Intelligence -> FAISS RAG

---

## Attack Description

Describe the observed attack behavior using ONLY the retrieved cybersecurity knowledge.

---

## Prediction Confidence Assessment

Explain that the confidence score represents the Random Forest model's prediction confidence.

Clearly state that it is NOT proof of malicious activity.

Recommend analyst verification before containment.

---

## Explainable AI Analysis (SHAP)

Interpret every SHAP feature separately.

For each feature include:

- Feature Name
- Observed Feature Value
- SHAP Contribution
- Contribution Direction
- Impact Level
- Explain ONLY how the feature influenced the machine learning prediction.

Never interpret SHAP values as proof of an attack.

---

## Indicators of Compromise (IoCs)

Summarize ONLY the IoCs contained in the retrieved knowledge.

---

## MITRE ATT&CK Mapping

Include ONLY mappings explicitly present in the retrieved knowledge.

---

## Recommended Mitigation

Summarize ONLY the mitigation recommendations from the retrieved knowledge.

---

## Incident Response Actions

Provide practical SOC actions including:

- validation
- log analysis
- containment
- monitoring
- evidence collection

---

## False Positive Considerations

Summarize any legitimate scenarios described in the retrieved knowledge.

If unavailable, recommend analyst validation.

---

## Risk Assessment

Estimate:

- Likelihood
- Business Impact
- Overall Risk Level

Base the assessment ONLY on the supplied evidence.

---

## SOC Analyst Conclusion

Combine:

- Machine Learning prediction
- Prediction confidence
- SHAP explainability
- Retrieved cybersecurity knowledge

Provide a concise recommendation for the SOC team.

---

# Writing Rules

- Professional Markdown.
- Concise SOC writing style.
- Evidence-based conclusions only.
- Never fabricate IoCs, MITRE techniques, mitigations, or attack behavior.
- Never claim that prediction confidence confirms an attack.
- Never infer causation from SHAP values.
- Explain SHAP only as model explainability.
- Integrate retrieved knowledge naturally instead of copying it verbatim.
- Keep the report concise, technical, and suitable for SOC documentation.
"""


def generate_report(sample: pd.Series, predicted_class: str, confidence: float,
                     shap_df: pd.DataFrame) -> str:
    """
    The ONLY function the Streamlit app calls. Everything else in this
    module is a private implementation detail.

    Raises RuntimeError with a clear, user-facing message on any failure
    (missing API key, FAISS error, Gemini API error) — the calling page
    catches this and shows st.error() instead of crashing.
    """
    from google import genai  # lazy import: keeps google-genai an optional dependency

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set. "
            "See the security note at the top of utils/report_generator.py."
        )

    try:
        retrieved_docs = retrieve_context(predicted_class)
    except RuntimeError:
        raise  # already a clear message from utils.rag
    except Exception as e:
        raise RuntimeError(f"Knowledge retrieval failed: {e}") from e

    report_id = f"IR-{datetime.now():%Y%m%d-%H%M%S}"
    report_date = datetime.now().strftime("%Y-%m-%d")

    shap_summary = _build_shap_summary(shap_df)
    context = _build_retrieved_context(retrieved_docs)
    prompt = _build_prompt(report_id, report_date, predicted_class, confidence, shap_summary, context)

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=GEMINI_MODEL_NAME, contents=prompt)
    except Exception as e:
        raise RuntimeError(f"Gemini report generation failed: {e}") from e

    return response.text
