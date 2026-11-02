# TRIMFUSE Streamlit-only QA report

Validation performed after removing the FastAPI/Uvicorn runtime path:

| Check | Result |
|---|---|
| Python compilation of `app.py` and in-process backend modules | Passed |
| Four source datasets load and contain unique Die IDs | Passed |
| Dataset-mode inference: MCU, PMIC, Sensor, SoC | Passed |
| Manual-mode inference: MCU, PMIC, Sensor, SoC | Passed |
| Isolation Forest screen returned for all four dataset-mode examples | Passed |
| Missing mandatory model features rejected | Passed |
| Engineering validation and memory-repair constraints | Passed |
| SoC die-to-memory-repair bitmap join | Passed |
| Report payload JSON serialization | Passed |
| Automated test suite (`python -m pytest -q`) | 17 passed |

The Streamlit package itself was not available in the build runtime, so browser launch and interactive UI behavior were not executed here. Install `requirements.txt` and run `python -m streamlit run app.py` on the target Windows machine to verify the local UI.

These tests validate software behavior against the supplied assessment datasets and synthetic models; they do not establish silicon characterization, physical calibration, or production qualification.
