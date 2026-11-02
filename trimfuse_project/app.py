"""TRIMFUSE single-process Streamlit application. Frontend-only UI revision."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import streamlit as st

from backend.app.config import DATA_DIR, MODEL_DIR, REPORT_DIR, CHIP_FILES
from backend.app.data import chip_frame, get_die, dataset_summary, load_csv
from backend.app.ml import model_inventory
from backend.app.core import run_analysis

CHIPS = ["MCU", "PMIC", "Sensor", "SoC"]
PREFIX = {"MCU":"MCU-", "PMIC":"PMIC-", "Sensor":"SNS-", "SoC":"SOC-"}

st.set_page_config(page_title="TRIMFUSE | Trim & Fuse Intelligence", page_icon="🔬", layout="wide")
st.title("🔬 TRIMFUSE — AI-Optimized Trim & Fuse")
st.caption("Pandas · NumPy · ExtraTreesRegressor · Isolation Forest · Advisory analysis only")

@st.cache_data(show_spinner=False)
def overview():
    return dataset_summary()

@st.cache_resource(show_spinner=False)
def model_artifacts():
    return {p.stem: joblib.load(p) for p in MODEL_DIR.glob("*.joblib")}

def safe_json(data):
    def convert(x):
        if isinstance(x, np.generic): return x.item()
        if isinstance(x, (np.ndarray,)): return x.tolist()
        return str(x)
    return json.dumps(data, indent=2, default=convert, allow_nan=False)

def feature_defaults(chip):
    df = chip_frame(chip)
    artifacts = model_artifacts()
    relevant = {
        "MCU": ["mcu_bg", "mcu_hsi", "mcu_ldo", "mcu_ts_hot", "anomaly_mcu"],
        "PMIC": [f"pmic_{x}" for x in ["buck1","buck2","ldo1","ldo2","ovp","uvlo","ilim"]] + ["anomaly_pmic"],
        "Sensor": [f"sensor_{a}_{s}" for a in "xyz" for s in ["tco_true_mg_per_C","tcs_true_ppm_per_C","post_reflow_offset_shift_mg"]] + ["anomaly_sensor"],
        "SoC": ["soc_slowest_fmax", "soc_worst_vmin", "anomaly_soc"],
    }[chip]
    cols=[]
    for name in relevant:
        art=artifacts.get(name)
        if art:
            for col in art.get("features", []):
                if col not in cols: cols.append(col)
    defaults={}
    for col in cols:
        if col not in df.columns: defaults[col] = ""
        elif pd.api.types.is_numeric_dtype(df[col]):
            val=df[col].median(); defaults[col] = float(val) if pd.notna(val) else 0.0
        else:
            modes=df[col].dropna().astype(str).mode(); defaults[col] = str(modes.iloc[0]) if len(modes) else "unknown"
    return cols, defaults, df

def display_predictions(chip, predictions):
    st.subheader("4. Predicted Outputs")
    if chip == "MCU":
        mapping=[("BG trim code","bg_trim_code_opt"),("HSI trim code","hsi_trim_code_opt"),("LDO trim code","ldo_trim_code_opt")]
    elif chip == "PMIC":
        mapping=[(f"{n.upper()} trim code",f"{n}_trim_code_opt") for n in ["buck1","buck2","ldo1","ldo2","ovp","uvlo","ilim"]]
    elif chip == "Sensor":
        mapping=[]
        for axis in "xyz":
            mapping += [(f"{axis.upper()} TCO",f"{axis}_tco_true_mg_per_C"),(f"{axis.upper()} TCS",f"{axis}_tcs_true_ppm_per_C"),(f"{axis.upper()} offset shift",f"{axis}_post_reflow_offset_shift_mg")]
    else:
        mapping=[("Slowest healthy Fmax","slowest_core_fmax_GHz"),("Worst healthy Vmin","worst_healthy_vmin_2GHz_mV")]
    cols=st.columns(min(3,len(mapping)))
    for i,(label,key) in enumerate(mapping):
        item=predictions.get(key)
        if item is None: continue
        value=item.get("proposed_code") if "proposed_code" in item else item.get("prediction")
        with cols[i % len(cols)]:
            st.metric(label, "N/A" if value is None else (str(value) if isinstance(value,int) else f"{float(value):.4f}"))
    if chip == "MCU" and "ts_cal2_110C_counts" in predictions:
        st.caption(f"Temperature calibration prediction (kept in report): {predictions['ts_cal2_110C_counts'].get('prediction')}")

def status_row(label, status, good=True):
    c1,c2=st.columns([4,1]); c1.write(label)
    (c2.success if good else c2.warning)(status)

def show_result(result, report_path):
    chip=result["chip"]; predictions=result.get("predictions",{})
    display_predictions(chip,predictions)
    st.subheader("5. Trim Estimates")
    estimates=result.get("trim_estimates") or result.get("rail_trim_estimates") or result.get("label_comparisons")
    if estimates:
        with st.expander("View trim estimates and measurement comparisons", expanded=False):
            st.json(estimates)
    else:
        st.caption("No trim-estimate comparison is available for this analysis mode or chip category.")
    st.subheader("6. Analysis Results")
    anomaly=result.get("anomaly_screen")
    if anomaly:
        status_row("Anomaly Screening", "Anomaly Detected" if anomaly.get("is_anomaly") else "Normal", not anomaly.get("is_anomaly"))
    else: status_row("Anomaly Screening", "Not available", False)
    eng=result.get("engineering_checks")
    if eng:
        passed=bool(eng.get("sort_pass",True) and eng.get("final_pass",True))
        status_row("Engineering Checks", "Pass" if passed else "Review", passed)
    elif chip=="Sensor": status_row("Engineering Checks", "Not applicable", True)
    else: status_row("Engineering Checks", "Not available", False)
    fuse=result.get("fuse_validation")
    if fuse:
        # Validation payloads may expose valid or pass fields depending on schema version.
        passed=bool(fuse.get("valid", fuse.get("passed", fuse.get("is_valid",False))))
        status_row("Fuse Validation", "Pass" if passed else "Review", passed)
    elif chip!="MCU": status_row("Fuse Validation", "Not applicable", True)
    else: status_row("Fuse Validation", "Not available", False)
    st.caption("Actual status comes from validation results. Sample statuses are never substituted for missing checks.")
    st.subheader("7. Model Input Measurements")
    with st.expander("View model input measurements", expanded=False): st.json(result.get("input_features",{}))
    st.subheader("8. Source Dataset Record")
    if result.get("source_record"):
        with st.expander("View complete source dataset record", expanded=False): st.json(result["source_record"])
    else: st.caption("Manual-input mode: no source dataset record was selected.")
    st.subheader("9. Download Report (JSON)")
    st.caption(f"Report saved automatically in reports folder: {report_path.name}")
    st.download_button("⬇ Download Report (JSON)", data=safe_json(result), file_name=report_path.name, mime="application/json", use_container_width=True)

with st.sidebar:
    st.header("Navigation")
    page=st.radio("Open", ["Chip Analysis", "Dataset Overview", "Model Inventory"])
    st.divider(); st.caption("Streamlit only — no FastAPI or Uvicorn.")

if page == "Chip Analysis":
    st.header("Chip Analysis")
    st.subheader("1. Chip Selection")
    chip=st.selectbox("Select chip category", CHIPS, key="chip_select")
    st.subheader("2. Record Selection / Manual Inputs")
    mode=st.radio("Choose input method", ["Record Selection", "Manual Inputs"], horizontal=True)
    df=chip_frame(chip)
    die_id=None; manual_features=None
    if mode == "Record Selection":
        ids=sorted(df["die_id"].dropna().astype(str).unique().tolist())
        die_id=st.selectbox("Select Die ID", ids, key=f"die_{chip}")
    else:
        cols,defaults,_=feature_defaults(chip)
        st.caption("Enter the model-required measurements below. Fields are generated from the selected chip's trained models.")
        manual_features={}
        with st.form(f"manual_form_{chip}"):
            for col in cols:
                default=defaults[col]
                if isinstance(default,(int,float)):
                    manual_features[col]=st.number_input(col, value=float(default), key=f"manual_{chip}_{col}")
                else:
                    manual_features[col]=st.text_input(col, value=str(default), key=f"manual_{chip}_{col}")
            run=st.form_submit_button("3. Run Chip Analysis", type="primary", use_container_width=True)
    if mode == "Record Selection":
        run=st.button("3. Run Chip Analysis", type="primary", use_container_width=True)
    if run:
        try:
            with st.spinner("Running chip analysis..."):
                if mode == "Record Selection":
                    result=run_analysis(chip,"dataset",die_id=die_id)
                else:
                    result=run_analysis(chip,"manual",features=manual_features)
                REPORT_DIR.mkdir(parents=True,exist_ok=True)
                stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
                report_path=REPORT_DIR/f"{chip.lower()}_analysis_{stamp}.json"
                report_path.write_text(safe_json(result),encoding="utf-8")
                st.session_state["last_analysis_result"]=result
                st.session_state["last_analysis_path"]=str(report_path)
            st.success("Chip analysis completed. JSON report saved in reports folder.")
        except Exception as e:
            st.error(f"Chip analysis failed: {e}")
    if st.session_state.get("last_analysis_result"):
        show_result(st.session_state["last_analysis_result"],Path(st.session_state["last_analysis_path"]))

elif page == "Dataset Overview":
    st.header("Dataset Overview")
    try:
        summary=overview(); rows=[]
        for label,item in summary.items():
            rows.append({"Dataset":label,"File":item["file"],"Rows":item["rows"],"Columns":item["columns"],"Missing cells":sum(item["missing_by_column"].values()),"Duplicate IDs":item.get("duplicate_ids")})
        st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
        selected=st.selectbox("Inspect dataset",list(summary)); info=summary[selected]
        st.write(f"**File:** `{info['file']}` · **Rows:** {info['rows']:,} · **Columns:** {info['columns']}")
        if info["missing_by_column"]: st.dataframe(pd.DataFrame([{"Column":k,"Missing":v} for k,v in info["missing_by_column"].items()]),hide_index=True)
        full_df=load_csv(info["file"])
        st.caption(f"Showing all {len(full_df):,} rows and {len(full_df.columns):,} columns.")
        st.dataframe(full_df,use_container_width=True,height=650)
    except Exception as e: st.error(f"Dataset inspection failed: {e}")

else:
    st.header("Model Inventory")
    try:
        inventory=model_inventory()
        st.dataframe(pd.DataFrame([{"Model":m["name"],"Target":m["target"],"Version":m["version"],"Method":m["evaluation"].get("method","ExtraTreesRegressor"),"MAE":m["evaluation"].get("mae")} for m in inventory]),hide_index=True,use_container_width=True)
        st.caption("ExtraTreesRegressor is the supervised regression algorithm. Isolation Forest models provide unsupervised anomaly screening.")
    except Exception as e: st.error(str(e))
