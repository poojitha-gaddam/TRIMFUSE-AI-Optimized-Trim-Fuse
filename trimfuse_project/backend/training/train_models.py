import json, sys
from pathlib import Path
import numpy as np, pandas as pd, joblib, sklearn
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from backend.app.config import DATA_DIR, MODEL_DIR

SEED=42


def grouped_holdout(X, y, groups, test_size=0.20, label="model"):
    """Split by wafer and assert that no wafer occurs in both partitions."""
    if groups.isna().any():
        raise ValueError(f"{label}: wafer_id contains missing values")
    groups = groups.astype(str)
    if groups.nunique() < 2:
        raise ValueError(f"{label}: at least two distinct wafers are required")
    splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=SEED)
    train_idx, test_idx = next(splitter.split(X, y, groups))
    train_wafers = set(groups.iloc[train_idx])
    test_wafers = set(groups.iloc[test_idx])
    overlap = train_wafers & test_wafers
    if overlap:
        raise RuntimeError(f"{label}: wafer leakage detected: {sorted(overlap)}")
    if len(train_idx) == 0 or len(test_idx) == 0:
        raise ValueError(f"{label}: empty train or test partition")
    return train_idx, test_idx


def make_preprocessor(X, features):
    numeric = [c for c in features if pd.api.types.is_numeric_dtype(X[c])]
    categorical = [c for c in features if c not in numeric]
    transformers = []
    if numeric:
        transformers.append(("num", Pipeline([
            ("impute", SimpleImputer(strategy="median"))
        ]), numeric))
    if categorical:
        transformers.append(("cat", Pipeline([
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ]), categorical))
    return ColumnTransformer(transformers, remainder="drop"), numeric, categorical


def make_regressor(prep):
    return Pipeline([
        ("prep", prep),
        ("model", ExtraTreesRegressor(
            n_estimators=80, max_depth=18, min_samples_leaf=3,
            max_features=0.9, n_jobs=-1, random_state=SEED
        ))
    ])


def fit_save(name, df, target, features, group_col="wafer_id", mask=None):
    required = list(features) + [target, group_col]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"{name}: missing required columns: {missing}")
    if not features:
        raise ValueError(f"{name}: no input features configured")

    work = df.copy()
    if mask is not None:
        work = work.loc[mask].copy()
    work[target] = pd.to_numeric(work[target], errors="coerce")
    work = work.dropna(subset=[target, group_col])
    work = work.loc[np.isfinite(work[target])].copy()
    X = work.loc[:, features].copy()
    y = work[target].copy()
    groups = work[group_col].astype(str)

    if len(y) < 80:
        raise ValueError(f"Not enough rows to train {name}: {len(y)}")

    train_idx, test_idx = grouped_holdout(X, y, groups, test_size=0.20, label=name)
    prep, numeric, categorical = make_preprocessor(X, features)
    pipe = make_regressor(prep)
    pipe.fit(X.iloc[train_idx], y.iloc[train_idx])
    pred = pipe.predict(X.iloc[test_idx])

    ev = {
        "test_rows": int(len(test_idx)),
        "train_rows": int(len(train_idx)),
        "split": "GroupShuffleSplit by wafer_id",
        "mae": float(mean_absolute_error(y.iloc[test_idx], pred)),
        "rmse": float(mean_squared_error(y.iloc[test_idx], pred) ** 0.5),
        "r2": float(r2_score(y.iloc[test_idx], pred))
    }

    # Feature-range checks are derived from training data only.
    ranges = {}
    for col in numeric:
        vals = pd.to_numeric(X.iloc[train_idx][col], errors="coerce")
        if vals.notna().any():
            ranges[col] = {
                "p005": float(vals.quantile(0.005)),
                "p995": float(vals.quantile(0.995))
            }

    artifact = {
        "pipeline": pipe, "features": features, "numeric_features": numeric,
        "categorical_features": categorical, "feature_ranges": ranges,
        "target": target, "evaluation": ev, "version": "1.0.0",
        "sklearn_version": sklearn.__version__
    }
    joblib.dump(artifact, MODEL_DIR / f"{name}.joblib", compress=3)
    return {"model": name, "target": target, "features": features, "evaluation": ev}

def main():
    MODEL_DIR.mkdir(parents=True,exist_ok=True)
    results=[]
    mcu=pd.read_csv(DATA_DIR/"mcu_trim_fuse.csv")
    mcu_feats=["bg_untrim_V","hsi_untrim_MHz","ldo_untrim_V","ts_cal1_30C_counts","die_x","die_y","x_mm","y_mm","radius_mm",
      "pcm_vth_n_mV","pcm_vth_p_mV","pcm_rs_ohm_sq","pcm_tox_A","pcm_mobility_rel","derivative","package","temp_grade"]
    for name,target in [("mcu_bg","bg_trim_code_opt"),("mcu_hsi","hsi_trim_code_opt"),("mcu_ldo","ldo_trim_code_opt"),("mcu_ts_hot","ts_cal2_110C_counts")]:
        results.append(fit_save(name,mcu,target,mcu_feats))
    pmic=pd.read_csv(DATA_DIR/"pmic_trim_otp.csv")
    base=["vref_untrim_V","die_x","die_y","x_mm","y_mm","radius_mm","pcm_vth_n_mV","pcm_vth_p_mV","pcm_rs_ohm_sq","pcm_tox_A","pcm_mobility_rel","derivative","package"]
    for name,target in [("buck1","buck1_trim_code_opt"),("buck2","buck2_trim_code_opt"),("ldo1","ldo1_trim_code_opt"),("ldo2","ldo2_trim_code_opt")]:
        results.append(fit_save("pmic_"+name,pmic,target,base))
    for name,target,extra in [
      ("ovp","ovp_trim_code_opt",["ovp_untrim_V"]),("uvlo","uvlo_trim_code_opt",["uvlo_untrim_V"]),("ilim","ilim_trim_code_opt",["ilim_untrim_A"])]:
        results.append(fit_save("pmic_"+name,pmic,target,base+extra))
    sensor=pd.read_csv(DATA_DIR/"sensor_calibration.csv")
    sensor_feats=["die_x","die_y","x_mm","y_mm","radius_mm","pcm_vth_n_mV","pcm_vth_p_mV","pcm_rs_ohm_sq","pcm_tox_A","pcm_mobility_rel",
      "stress_gauge_mV","asic_vref_mV","mems_resonance_kHz","mems_q_factor","st_response_x_mg","st_response_y_mg","st_response_z_mg",
      "offset_x_25C_mg","offset_y_25C_mg","offset_z_25C_mg","sens_x_25C_rel","sens_y_25C_rel","sens_z_25C_rel",
      "full_scale_g","derivative","package"]
    for axis in "xyz":
        for suffix,target in [("tco_true_mg_per_C",f"tco_{axis}_true_mg_per_C"),
          ("tcs_true_ppm_per_C",f"tcs_{axis}_true_ppm_per_C"),
          ("post_reflow_offset_shift_mg",f"post_reflow_offset_shift_{axis}_mg")]:
            results.append(fit_save(f"sensor_{axis}_{suffix}",sensor,target,sensor_feats,mask=sensor["characterized_3temp"].astype(bool)))
    soc=pd.read_csv(DATA_DIR/"soc_binning_harvesting.csv")
    core_targets=[f"core{i}_fmax_GHz" for i in range(8)]
    valid=soc[[f"core{i}_defect" for i in range(8)]].fillna(True).eq(False)
    fmax=soc[core_targets].where(valid.to_numpy())
    soc["slowest_healthy_fmax_GHz"]=fmax.min(axis=1,skipna=True)
    soc_feats=["die_x","die_y","x_mm","y_mm","radius_mm","pcm_vth_n_mV","pcm_vth_p_mV","pcm_rs_ohm_sq","pcm_tox_A","pcm_mobility_rel","ro_freq_MHz","cpm_path_delay_ps","iddq_25C_mA","derivative"]
    results.append(fit_save("soc_slowest_fmax",soc,"slowest_healthy_fmax_GHz",soc_feats))
    vmin_targets=[f"core{i}_vmin_2GHz_mV" for i in range(8)]
    vmin_values=soc[vmin_targets].where(valid.to_numpy())
    soc["worst_healthy_vmin_2GHz_mV"]=vmin_values.max(axis=1,skipna=True)
    results.append(fit_save("soc_worst_vmin",soc,"worst_healthy_vmin_2GHz_mV",soc_feats))
    # Unsupervised anomaly screeners use only test-time numeric measurements, never latent_defect.
    anomaly_features={
      "mcu":["bg_untrim_V","hsi_untrim_MHz","ldo_untrim_V","ts_cal1_30C_counts","x_mm","y_mm","radius_mm","pcm_vth_n_mV","pcm_vth_p_mV","pcm_rs_ohm_sq","pcm_tox_A","pcm_mobility_rel","sram_fail_bits"],
      "pmic":["vref_untrim_V","ovp_untrim_V","uvlo_untrim_V","ilim_untrim_A","cs_meas_0p5A_A","cs_meas_2p0A_A","efficiency_1A_pct","load_reg_mV","x_mm","y_mm","pcm_vth_n_mV","pcm_vth_p_mV","pcm_rs_ohm_sq","pcm_tox_A","pcm_mobility_rel"],
      "sensor":["stress_gauge_mV","asic_vref_mV","mems_resonance_kHz","mems_q_factor","st_response_x_mg","st_response_y_mg","st_response_z_mg","offset_x_25C_mg","offset_y_25C_mg","offset_z_25C_mg","sens_x_25C_rel","sens_y_25C_rel","sens_z_25C_rel","x_mm","y_mm","pcm_vth_n_mV","pcm_vth_p_mV","pcm_rs_ohm_sq","pcm_tox_A","pcm_mobility_rel"],
      "soc":["ro_freq_MHz","cpm_path_delay_ps","iddq_25C_mA","l2_slice0_fail_bits","l2_slice1_fail_bits","l2_slice2_fail_bits","l2_slice3_fail_bits","x_mm","y_mm","pcm_vth_n_mV","pcm_vth_p_mV","pcm_rs_ohm_sq","pcm_tox_A","pcm_mobility_rel"]}
    for chip,filename in [("mcu","mcu_trim_fuse.csv"),("pmic","pmic_trim_otp.csv"),("sensor","sensor_calibration.csv"),("soc","soc_binning_harvesting.csv")]:
        adf=pd.read_csv(DATA_DIR/filename)
        feats=anomaly_features[chip]
        numeric_pipe=Pipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler()),
          ("iforest",IsolationForest(n_estimators=200,contamination="auto",random_state=SEED,n_jobs=-1))])
        numeric_pipe.fit(adf[feats])
        joblib.dump({"pipeline":numeric_pipe,"features":feats,"version":"1.0.0","method":"IsolationForest; unsupervised; feature-only"},MODEL_DIR/f"anomaly_{chip}.joblib",compress=3)
    # Transfer learning: MCU-A base model; fine-tune on 50 MCU-C dies.
    # MCU-C evaluation is held out by wafer before selecting adaptation dies.
    transfer_features=["bg_trimmed_sort_V","pcm_vth_n_mV","pcm_vth_p_mV","pcm_rs_ohm_sq","pcm_tox_A","pcm_mobility_rel","x_mm","y_mm","radius_mm","package","derivative"]
    transfer_target = "bg_sort_final_shift_mV"
    transfer_required = transfer_features + ["bg_final_V", "wafer_id", "derivative"]
    missing = [c for c in transfer_required if c not in mcu.columns]
    if missing:
        raise ValueError(f"MCU transfer learning: missing required columns: {missing}")

    trdf = mcu.copy()
    trdf[transfer_target] = (
        pd.to_numeric(trdf["bg_final_V"], errors="coerce")
        - pd.to_numeric(trdf["bg_trimmed_sort_V"], errors="coerce")
    ) * 1000.0
    trdf = trdf.dropna(subset=[transfer_target, "wafer_id"])
    base_rows = trdf[trdf["derivative"] == "MCU-A"].copy()
    c_rows = trdf[trdf["derivative"] == "MCU-C"].copy()

    if len(base_rows) <= 100 or len(c_rows) <= 100:
        raise ValueError("MCU transfer learning requires more than 100 MCU-A and MCU-C rows")
    if c_rows["wafer_id"].nunique() < 2:
        raise ValueError("MCU transfer learning requires at least two MCU-C wafers")

    c_train_idx, c_test_idx = grouped_holdout(
        c_rows[transfer_features], c_rows[transfer_target],
        c_rows["wafer_id"].astype(str), test_size=0.50,
        label="MCU-C transfer evaluation"
    )
    adapt_pool = c_rows.iloc[c_train_idx].copy()
    c_test = c_rows.iloc[c_test_idx].copy()
    if len(adapt_pool) < 50:
        raise ValueError("MCU-C adaptation wafer partition has fewer than 50 dies")
    c_adapt = adapt_pool.sample(n=50, random_state=SEED)

    prep, transfer_numeric, transfer_categorical = make_preprocessor(
        trdf[transfer_features], transfer_features
    )
    transfer_pipe = make_regressor(prep)

    # Zero-shot evaluation: train only on MCU-A, test on unseen MCU-C wafers.
    transfer_pipe.fit(base_rows[transfer_features], base_rows[transfer_target])
    zero = transfer_pipe.predict(c_test[transfer_features])
    zero_mae = float(mean_absolute_error(c_test[transfer_target], zero))

    # Fine-tuning: add 50 MCU-C dies from adaptation wafers; test wafers remain untouched.
    adapted = pd.concat([base_rows, c_adapt], ignore_index=True)
    transfer_pipe.fit(adapted[transfer_features], adapted[transfer_target])
    tuned = transfer_pipe.predict(c_test[transfer_features])
    tuned_mae = float(mean_absolute_error(c_test[transfer_target], tuned))

    transfer_eval = {
        "zero_shot_mcu_c_mae_mV": zero_mae,
        "fine_tuned_50_mcu_c_mae_mV": tuned_mae,
        "fine_tune_rows": 50,
        "test_rows": int(len(c_test))
    }
    joblib.dump({
        "pipeline": transfer_pipe, "features": transfer_features,
        "target": transfer_target, "version": "1.0.0",
        "evaluation": transfer_eval
    }, MODEL_DIR / "mcu_transfer_shift.joblib", compress=3)
    results.append({"model": "mcu_transfer_shift", "evaluation": transfer_eval})
    out=Path(__file__).resolve().parents[2]/"reports"/"model_evaluation.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(results,indent=2),encoding="utf-8")
    print(json.dumps(results,indent=2))
if __name__=="__main__": main()
