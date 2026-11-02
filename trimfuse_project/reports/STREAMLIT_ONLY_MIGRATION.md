# Streamlit-only migration

- Removed the FastAPI/Uvicorn runtime dependency and HTTP client integration.
- Replaced the API-calling frontend with root-level `app.py`.
- Added `backend/app/core.py`, which executes the prior chip-specific analysis logic directly in-process.
- Preserved trained model artifacts, source datasets, engineering calculations, and JSON report payload structure.
- Updated tests to exercise the in-process workflow instead of REST endpoints.

Run with `python -m streamlit run app.py`.
