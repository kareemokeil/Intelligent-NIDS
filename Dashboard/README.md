# Intelligent NIDS — SOC Console (v3, refactored)

A multi-page Streamlit dashboard for the graduation project, refactored
into a clean layered architecture:

```
UI (pages/*.py)
  -> utils/predictor.py        (prediction)
  -> utils/shap_utils.py       (explainability)
  -> utils/rag.py              (FAISS knowledge retrieval)
  -> utils/report_generator.py (prompt building + Gemini call)
```

Pages contain ONLY UI code — no model calls, no SHAP internals, no
FAISS calls, no prompt building. Every one of those lives in exactly
one `utils/` module.

## 1. Folder structure
```
nids_dashboard_v3/
├── app.py                          # Home page (UI only)
├── pages/
│   ├── 1_Detection.py              # UI only — 4 tabs: Prediction / SHAP / RAG / Report
│   ├── 2_Model_Performance.py      # UI only — uses cached batch predictions
│   ├── 3_Analytics.py              # UI only — uses cached batch predictions
│   ├── 4_History.py                # UI only
│   └── 5_About.py                  # UI only
├── utils/
│   ├── theme.py                    # CSS + sidebar + cards/badges
│   ├── artifacts_loader.py         # loads model/scaler/test set (cached)
│   ├── predictor.py                # predict() for one sample + cached batch prediction
│   ├── shap_utils.py               # explain() -> dataframe + Plotly figure + top features
│   ├── rag.py                      # retrieve_context(attack) -> FAISS results
│   ├── report_generator.py         # generate_report(...) -> calls rag + builds prompt + Gemini
│   ├── pdf_generator.py            # markdown_to_pdf_bytes()
│   └── history.py                  # save_report() / load_history()
├── artifacts/                      # you create this — model files (see step 2)
├── reports/                        # auto-created — stores every generated report
├── assets/logo.svg
├── .streamlit/config.toml
└── requirements.txt
```

## 2. What changed from the previous version (audit summary)
- Removed duplicated full-test-set prediction that ran independently
  in both Model Performance and Analytics — now goes through one
  cached function in `predictor.py` (`st.cache_data`), computed once.
- Moved all SHAP computation + chart-building out of the Detection
  page into `shap_utils.explain()` — the page now just calls it and
  renders what comes back.
- Renamed `rag_utils.py` -> `rag.py` and collapsed its two-step usage
  (build a query, then call retrieval) into one call:
  `retrieve_context(predicted_attack)`.
- Moved `report_generator.py` into `utils/` and made it call
  `utils.rag.retrieve_context()` internally — the page no longer
  passes `retrieved_docs` in; it only passes the prediction + SHAP
  results, exactly per the requested architecture.
- Split the old `report_utils.py` (which mixed history persistence
  with PDF export) into two focused modules: `history.py` and
  `pdf_generator.py`.
- Added `st.spinner()` around prediction, SHAP, and RAG retrieval, and
  wrapped every stage in `try/except` with `st.error(...)` instead of
  letting exceptions crash the page.
- Reorganized the Detection page into 4 tabs (Prediction / SHAP
  Explainability / Retrieved Knowledge / AI Incident Report) instead
  of one long scroll.

## 3. Export your model artifacts (unchanged filenames)
```python
import joblib, os
os.makedirs("artifacts", exist_ok=True)

joblib.dump(rf_model, "artifacts/rf_model.pkl")
joblib.dump(scaler, "artifacts/scaler.pkl")
joblib.dump(label_encoder, "artifacts/label_encoder.pkl")
joblib.dump(feature_names, "artifacts/feature_names.pkl")
joblib.dump(X_test, "artifacts/X_test.pkl")
joblib.dump(X_test_z, "artifacts/X_test_z.pkl")
joblib.dump(y_test, "artifacts/y_test.pkl")
joblib.dump(y_test_encoded, "artifacts/y_test_encoded.pkl")
```
Copy the resulting `artifacts/` folder into `nids_dashboard_v3/` (or
just move it over from your previous dashboard folder — file names
are identical).

## 4. Wire in FAISS RAG
Copy your `faiss_index/` folder (from `vector_db.save_local("faiss_index")`
in your notebook) into:
```
artifacts/faiss_index/index.faiss
artifacts/faiss_index/index.pkl
```
```bash
pip install langchain-community langchain-huggingface faiss-cpu sentence-transformers
```

## 5. Gemini API key — SECURITY FIRST
The original notebook had a real Gemini key hardcoded in the source.
**Regenerate that key in Google AI Studio** — treat the old one as
compromised. This dashboard reads the key only from an environment
variable, never from code:
```bash
pip install google-genai
setx GEMINI_API_KEY "your-new-key"      # Windows (restart terminal after)
export GEMINI_API_KEY="your-new-key"     # macOS/Linux
```

## 6. Run it
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Error handling you'll actually see
- Missing artifacts -> a specific list of which `.pkl` files are absent.
- Missing `GEMINI_API_KEY` -> clear message, no crash.
- FAISS not configured -> info banner in the Retrieved Knowledge tab,
  report generation still works (falls back to "no documents retrieved"
  wording in the prompt) instead of failing.
- Any SHAP/model/Gemini/FAISS runtime failure -> `st.error(...)` with
  the underlying reason, never a raw traceback.
