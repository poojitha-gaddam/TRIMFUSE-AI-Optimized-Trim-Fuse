"""Direct in-process analysis service; no web API server required."""
import json, pandas as pd, joblib, numpy as np
from .data import chip_frame, get_die, dataset_summary, load_csv
from .ml import predict, model_inventory
from .engineering import validate_mcu_fuse_word, validate_otp_request, min_vertex_cover_repair, soc_sku_recommendation
from .config import REPORT_DIR, MODEL_DIR, ROOT

def json_safe(value):
    if isinstance(value,dict): return {str(k):json_safe(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [json_safe(v) for v in value]
    if isinstance(value,np.generic): value=value.item()
    if isinstance(value,float) and not np.isfinite(value): return None
    try:
        if pd.isna(value): return None
    except (TypeError,ValueError): pass
    return value

def run_analysis(chip, mode, die_id=None, features=None):
    from types import SimpleNamespace
    req = SimpleNamespace(chip=chip, mode=mode, die_id=die_id, features=features)
    try:
        if req.mode=="dataset":
            if not req.die_id: raise HTTPException(422,"die_id is required for dataset mode")
            row=get_die(req.chip,req.die_id)
            features=row
        else:
            features=req.features
            if not features: raise HTTPException(422,"Manual mode requires feature values")
        result={"chip":req.chip,"mode":req.mode,"die_id":req.die_id,"input_features":features,"predictions":{},"warnings":[]}
        if req.chip=="MCU":
            for model,target in [("mcu_bg","bg_trim_code_opt"),("mcu_hsi","hsi_trim_code_opt"),("mcu_ldo","ldo_trim_code_opt"),("mcu_ts_hot","ts_cal2_110C_counts")]:
                result["predictions"][target]=predict(model,features)
            for k,lo,hi in [("bg_trim_code_opt",0,63),("hsi_trim_code_opt",0,127),("ldo_trim_code_opt",0,31)]:
                v=round(result["predictions"][k]["prediction"])
                result["predictions"][k]["proposed_code"]=int(max(lo,min(hi,v)))
            if req.mode=="dataset":
                # Engineering estimates use the assessment's documented trim transfer slopes.
                codes={k:result["predictions"][k]["proposed_code"] for k in ["bg_trim_code_opt","hsi_trim_code_opt","ldo_trim_code_opt"]}
                bg_est=float(row["bg_untrim_V"])+(codes["bg_trim_code_opt"]-32)*0.002
                hsi_est=float(row["hsi_untrim_MHz"])*(1+(codes["hsi_trim_code_opt"]-64)*0.002)
                ldo_est=float(row["ldo_untrim_V"])+(codes["ldo_trim_code_opt"]-16)*0.005
                result["trim_estimates"]={
                  "bandgap":{"estimated_sort_V":bg_est,"measured_sort_V":float(row["bg_trimmed_sort_V"]),"absolute_error_V":abs(bg_est-float(row["bg_trimmed_sort_V"]))},
                  "hsi":{"estimated_sort_MHz":hsi_est,"measured_sort_MHz":float(row["hsi_trimmed_sort_MHz"]),"absolute_error_MHz":abs(hsi_est-float(row["hsi_trimmed_sort_MHz"]))},
                  "ldo":{"estimated_sort_V":ldo_est,"measured_sort_V":float(row["ldo_trimmed_sort_V"]),"absolute_error_V":abs(ldo_est-float(row["ldo_trimmed_sort_V"]))},
                  "status":"estimated_from_documented_trim_step; measured values are source-record observations"
                }
                if row.get("derivative")=="MCU-C":
                    transfer=joblib.load(MODEL_DIR/"mcu_transfer_shift.joblib")
                    shift=float(transfer["pipeline"].predict(pd.DataFrame([{k:row[k] for k in transfer["features"]}]))[0])
                    result["transfer_learning"]={"predicted_sort_to_final_shift_mV":shift,
                      "estimated_final_bandgap_V":float(row["bg_trimmed_sort_V"])+shift/1000.0,
                      "model_evaluation":transfer["evaluation"],"status":"estimated"}
                result["engineering_checks"]={"sort_pass":bool(row["sort_pass"]),"final_pass":bool(row["final_pass"]),
                    "measured_final_bandgap_V":float(row["bg_final_V"]),"predicted_trim_is_not_physical_calibration":True}
                result["fuse_validation"]=validate_mcu_fuse_word(row["fuse_map_hex"],row["derivative"],row)
            result["warnings"].append("Trim codes are predictions; tester verification is required before any OTP programming.")
        elif req.chip=="PMIC":
            for name in ["buck1","buck2","ldo1","ldo2","ovp","uvlo","ilim"]:
                result["predictions"][name+"_trim_code_opt"]=predict("pmic_"+name,features)
            for name,hi in [("buck1",63),("buck2",63),("ldo1",63),("ldo2",63),("ovp",15),("uvlo",15),("ilim",31)]:
                key=name+"_trim_code_opt"
                result["predictions"][key]["proposed_code"]=int(max(0,min(hi,round(result["predictions"][key]["prediction"]))))
            if req.mode=="dataset":
                rails={}
                for n,target_col,untrim_col,base_code,step in [
                  ("buck1","buck1_target_V","buck1_untrim_V",32,0.002),("buck2","buck2_target_V","buck2_untrim_V",32,0.002),
                  ("ldo1","ldo1_target_V","ldo1_untrim_V",32,0.002),("ldo2","ldo2_target_V","ldo2_untrim_V",32,0.002)]:
                    code=result["predictions"][n+"_trim_code_opt"]["proposed_code"]
                    rails[n]={"proposed_code":code,"estimated_post_trim_V":float(row[untrim_col])+float(row[target_col])*(code-base_code)*step}
                for n,entry in rails.items():
                    measured=float(row[n+"_trimmed_sort_V"])
                    entry["measured_sort_V"]=measured
                    entry["absolute_error_V"]=abs(entry["estimated_post_trim_V"]-measured)
                result["rail_trim_estimates"]={"rails":rails,"status":"estimated_from_documented_0.2_percent_per_LSB; measured values are source-record observations"}
                result["engineering_checks"]={"sort_pass":bool(row["sort_pass"]),"final_pass":bool(row["final_pass"]),
                    "measured_final_reference_V":float(row["vref_final_V"])}
            result["warnings"].append("No OTP image is programmed. Verify rail behavior with hardware-in-the-loop.")
        elif req.chip=="Sensor":
            for axis in "xyz":
                for suffix in ["tco_true_mg_per_C","tcs_true_ppm_per_C","post_reflow_offset_shift_mg"]:
                    key=f"{axis}_{suffix}"
                    result["predictions"][key]=predict("sensor_"+axis+"_"+suffix,features)
            if req.mode=="dataset":
                comparisons={}
                for axis in "xyz":
                    for suffix,target_col in [("tco_true_mg_per_C",f"tco_{axis}_true_mg_per_C"),
                      ("tcs_true_ppm_per_C",f"tcs_{axis}_true_ppm_per_C"),
                      ("post_reflow_offset_shift_mg",f"post_reflow_offset_shift_{axis}_mg")]:
                        pred_key=f"{axis}_{suffix}"
                        actual=float(row[target_col]); predicted=float(result["predictions"][pred_key]["prediction"])
                        comparisons[target_col]={"source_label":actual,"prediction":predicted,"absolute_error":abs(actual-predicted)}
                result["label_comparisons"]=comparisons
            result["warnings"].append("Predicted coefficients and reflow shift are estimates; full-temperature characterization remains required for safety-critical release.")
        elif req.chip=="SoC":
            result["predictions"]["slowest_core_fmax_GHz"]=predict("soc_slowest_fmax",features)
            result["predictions"]["worst_healthy_vmin_2GHz_mV"]=predict("soc_worst_vmin",features)
            if req.mode=="dataset":
                core_fmax=[float(row[f"core{i}_fmax_GHz"]) for i in range(8) if not bool(row[f"core{i}_defect"]) and pd.notna(row[f"core{i}_fmax_GHz"])]
                core_vmin=[float(row[f"core{i}_vmin_2GHz_mV"]) for i in range(8) if not bool(row[f"core{i}_defect"]) and pd.notna(row[f"core{i}_vmin_2GHz_mV"])]
                if core_fmax and core_vmin:
                    result["label_comparisons"]={
                      "slowest_healthy_fmax_GHz":{"source_label":min(core_fmax),"prediction":result["predictions"]["slowest_core_fmax_GHz"]["prediction"],
                        "absolute_error":abs(min(core_fmax)-result["predictions"]["slowest_core_fmax_GHz"]["prediction"])},
                      "worst_healthy_vmin_2GHz_mV":{"source_label":max(core_vmin),"prediction":result["predictions"]["worst_healthy_vmin_2GHz_mV"]["prediction"],
                        "absolute_error":abs(max(core_vmin)-result["predictions"]["worst_healthy_vmin_2GHz_mV"]["prediction"])}}
                result["engineering_checks"]={"rule_based_sku":row["sku_rule_based"],"l2_repairable":bool(row["l2_repairable"]),
                    "cores_disabled_mask":row["cores_disabled_mask"]}
                result["sku_recommendation"]=soc_sku_recommendation(row,load_csv("soc_sku_demand.csv"))
                result["memory_repair_summary"]={"failing_bits_total":int(sum(int(row[f"l2_slice{i}_fail_bits"]) for i in range(4))),
                    "assessment_l2_repairable":bool(row["l2_repairable"])}
                repair_rows=load_csv("memory_repair_bitmaps.csv")
                related=repair_rows[repair_rows.die_id.astype(str)==str(req.die_id)]
                allocations=[]
                for _,repair_row in related.iterrows():
                    if pd.isna(repair_row["fail_cells"]):
                        allocations.append({"array_id":repair_row["array_id"],"array":repair_row["array"],"status":"bitmap_missing"})
                    else:
                        solution=min_vertex_cover_repair(repair_row["fail_cells"],repair_row["spare_rows"],repair_row["spare_cols"])
                        allocations.append({"array_id":repair_row["array_id"],"array":repair_row["array"],"allocation":solution})
                result["memory_repair_allocations"]=allocations
            result["warnings"].append("SKU suggestion is a per-die feasibility recommendation, not a globally demand-optimized production allocation.")
        # Keep model inputs separate from the complete source record so labels are never presented as inference inputs.
        used_features=sorted({f for pred in result["predictions"].values() for f in pred.get("feature_names",[])})
        result["input_features"]={k:features[k] for k in used_features if k in features}
        if req.mode=="dataset": result["source_record"]=row
        # Apply unsupervised screening when all required measurements are available.
        anomaly_key={"MCU":"mcu","PMIC":"pmic","Sensor":"sensor","SoC":"soc"}[req.chip]
        anomaly_art=joblib.load(MODEL_DIR/f"anomaly_{anomaly_key}.joblib")
        if all(k in features and features[k] is not None for k in anomaly_art["features"]):
            ax=pd.DataFrame([{k:features[k] for k in anomaly_art["features"]}])
            result["anomaly_screen"]={"score":float(anomaly_art["pipeline"].decision_function(ax)[0]),
              "is_anomaly":bool(anomaly_art["pipeline"].predict(ax)[0]==-1),"method":"IsolationForest",
              "warning":"Screening flag only; not a defect diagnosis."}
        else:
            result["warnings"].append("Anomaly screen not run: its complete feature set was not supplied.")
        return json_safe(result)
    except Exception:
        raise

