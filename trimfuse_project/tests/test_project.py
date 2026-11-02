import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from backend.app.config import DATA_DIR, MODEL_DIR, REPORT_DIR
from backend.app.data import chip_frame, get_die, dataset_summary
from backend.app.ml import model_inventory
from backend.app.core import run_analysis
from backend.app.engineering import validate_otp_request, validate_mcu_fuse_word, min_vertex_cover_repair

@pytest.mark.parametrize("chip,filename,prefix",[
 ("MCU","mcu_trim_fuse.csv","MCU-"),("PMIC","pmic_trim_otp.csv","PMIC-"),
 ("Sensor","sensor_calibration.csv","SNS-"),("SoC","soc_binning_harvesting.csv","SOC-")])
def test_dataset_lookup_and_prefix(chip,filename,prefix):
    df=pd.read_csv(DATA_DIR/filename)
    assert get_die(chip,df.iloc[0].die_id)["die_id"]==df.iloc[0].die_id
    with pytest.raises(ValueError): get_die(chip,"BAD-0001")

def test_all_datasets_load_and_have_unique_die_ids():
    for chip in ["MCU","PMIC","Sensor","SoC"]:
        df=chip_frame(chip)
        assert len(df)>0 and df.die_id.is_unique and not df.duplicated().any()

def test_dataset_summary_includes_supporting_files():
    summary=dataset_summary()
    assert len(summary)>=9 and "Memory repair bitmaps" in summary
    assert summary["MCU main"]["rows"]==8420

def test_otp_rules_reproduce_assessment_labels():
    df=pd.read_csv(DATA_DIR/"pmic_otp_config_requests.csv")
    labels=[validate_otp_request(r.to_dict())["rule_label"] for _,r in df.iterrows()]
    assert labels==df.label.tolist()

def test_fuse_validation_rejects_bad_hex():
    assert not validate_mcu_fuse_word("not-hex","MCU-A")["valid"]

def test_memory_repair_constraints():
    solved=min_vertex_cover_repair("1:10;1:11;2:11;3:12",2,2)
    assert solved["repairable"] and solved["minimum_rows"]<=2 and solved["minimum_cols"]<=2
    assert not min_vertex_cover_repair("1:10;2:10;3:10;4:10;5:10",0,0)["repairable"]

@pytest.mark.parametrize("chip,die",[("MCU","MCU-000001"),("PMIC","PMIC-000001"),("Sensor","SNS-000001"),("SoC","SOC-000001")])
def test_dataset_inference_all_categories(chip,die):
    result=run_analysis(chip,"dataset",die)
    assert result["predictions"]
    assert result["anomaly_screen"]["method"]=="IsolationForest"
    assert all(np.isfinite(v["prediction"]) for v in result["predictions"].values())

def test_manual_missing_features_rejected():
    with pytest.raises(ValueError, match="Missing mandatory model features"):
        run_analysis("MCU","manual",features={"bg_untrim_V":1.2})

def test_model_inventory_and_algorithms():
    inventory=model_inventory()
    assert len(inventory)>=20
    for name in ["mcu_bg","mcu_hsi","mcu_ldo","mcu_ts_hot","pmic_buck1","sensor_x_tco_true_mg_per_C","soc_slowest_fmax","soc_worst_vmin"]:
        artifact=__import__("joblib").load(MODEL_DIR/f"{name}.joblib")
        assert artifact["pipeline"] is not None
        assert artifact.get("method", "ExtraTreesRegressor") in ["ExtraTreesRegressor", "supervised_regression"]

def test_soc_memory_repair_join():
    result=run_analysis("SoC","dataset","SOC-005713")
    assert result["memory_repair_allocations"]
    assert result["memory_repair_allocations"][0]["allocation"]["repairable"] is True

def test_report_payload_serializes():
    result=run_analysis("MCU","dataset","MCU-000001")
    payload=json.dumps(result, default=str)
    parsed=json.loads(payload)
    assert parsed["chip"]=="MCU" and parsed["predictions"]
