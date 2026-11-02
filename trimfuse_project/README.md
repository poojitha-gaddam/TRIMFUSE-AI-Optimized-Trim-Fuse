# TRIMFUSE — Single Streamlit Application

This version runs the complete TRIMFUSE workflow in one Python process. **FastAPI and Uvicorn are not used or required.** Streamlit calls the data, ML, and engineering modules directly.

## Start the application

From the project root (the folder containing `app.py`):

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

On Windows, you can alternatively double-click `start_windows.bat` after installing the requirements. The application opens in your browser, normally at `http://localhost:8501`.

## Application workflow

1. Select one chip category: MCU, PMIC, Sensor, or SoC.
2. Choose Dataset Testing to find a die ID in the original assessment dataset, or Manual Testing to enter model features.
3. Run chip-specific predictions and engineering checks.
4. Review the Isolation Forest screening result, warnings, and validation outputs.
5. Download the engineering report as JSON or save it under `reports/`.

## Algorithms and processing

- **ExtraTreesRegressor** is the only supervised regression algorithm used for trim/target prediction.
- **Isolation Forest** is used only for unsupervised anomaly screening; its flag is not a defect diagnosis.
- Pandas loads and inspects the assessment CSV datasets. NumPy/Pandas support numeric validation and preprocessing. The persisted scikit-learn pipelines contain the preprocessing fitted during training.
- Existing trained model artifacts are under `backend/models/`. Training source is under `backend/training/`.
- Chip categories are analyzed independently; selecting one category does not generate all other chip outputs.

## Project layout

- `app.py` — Streamlit UI and workflow
- `backend/app/core.py` — in-process analysis orchestration (no HTTP API)
- `backend/app/data.py` — dataset loading and die lookup
- `backend/app/ml.py` — model prediction and inventory
- `backend/app/engineering.py` — engineering validation and memory repair
- `backend/models/` — trained ExtraTrees and Isolation Forest artifacts
- `backend/training/` — model training workflow
- `datasets/original/` — assessment datasets
- `reports/` — generated reports and QA evidence
- `tests/` — tests for data, ML inference, and engineering rules

## Important limitations

This is advisory software. Predictions do not physically trim/calibrate a device and do not program fuses or OTP. Validate all proposals with tester measurements, signed product specifications, and hardware-in-the-loop qualification before production use. The SoC SKU suggestion is per-die feasibility logic, not global demand optimization.
