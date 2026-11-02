import re
from collections import defaultdict, deque
import pandas as pd
from .data import load_csv

def validate_mcu_fuse_word(hex_word, derivative, die_record=None):
    schema=load_csv("mcu_fuse_schema.csv")
    if derivative not in ["MCU-A","MCU-B","MCU-C"]:
        raise ValueError("Unknown MCU derivative")
    try: word=int(str(hex_word),16)
    except Exception: return {"valid":False,"errors":["Fuse word is not valid hexadecimal"]}
    if word < 0 or word >= 2**64:
        return {"valid":False,"errors":["Fuse word must fit in 64 bits"]}
    errors=[]
    decoded={}
    for _,r in schema.iterrows():
        n=int(r.nbits); lsb=int(r.lsb); mask=(1<<n)-1
        val=(word>>lsb)&mask
        decoded[r.field]=val
        expected=str(r[derivative])
        if die_record is not None:
            dataset_targets={"BG_TRIM":"bg_trim_code_opt","HSI_TRIM":"hsi_trim_code_opt","LDO_TRIM":"ldo_trim_code_opt","TS_CAL1":"ts_cal1_30C_counts"}
            target=dataset_targets.get(r.field)
            if target and target in die_record and pd.notna(die_record[target]) and val != int(die_record[target]):
                errors.append(f"{r.field} does not match die sort measurement / trim record")
        if r.field=="RESERVED" and val != 0: errors.append("Reserved fuse bits must be zero")
        elif r.field=="DEBUG_LOCK" and val != 1: errors.append("DEBUG_LOCK must be set")
        elif r.field in ["FLASH_SIZE","PERIPH_EN","TEMP_GRADE","RDP"] and expected!="per-die":
            try: exp=int(expected,0)
            except ValueError: exp=int(float(expected))
            if val != exp: errors.append(f"{r.field} mismatch: expected {exp}, got {val}")
    return {"valid":not errors,"errors":errors,"decoded_fields":decoded}

def validate_otp_request(row):
    errors=[]; labels=[]
    ranges={"buck1_V":(0.60,1.30),"buck2_V":(0.90,1.50),"ldo1_V":(1.80,3.00),"ldo2_V":(3.30,3.30)}
    for k,(lo,hi) in ranges.items():
        try: v=float(row[k])
        except Exception: errors.append(f"{k} must be numeric"); labels.append("out_of_range"); continue
        if not lo <= v <= hi:
            errors.append(f"{k}={v} outside assessment-supported range [{lo}, {hi}] V"); labels.append("out_of_range")
    seq=str(row.get("sequence","")).split(">")
    expected={"buck1","buck2","ldo1","ldo2"}
    if len(seq)!=4 or set(seq)!=expected:
        errors.append("Each of buck1, buck2, ldo1 and ldo2 must appear exactly once"); labels.append("invalid_sequence")
    elif seq[0]=="ldo2":
        errors.append("ldo2 cannot be first in the power-up sequence"); labels.append("sequence_conflict")
    try:
        addr=int(str(row.get("i2c_addr","")),16)
        if addr in {0x00,0x03,0x78,0x7f}:
            errors.append("I2C address is reserved by the assessment rules"); labels.append("address_reserved")
        others=[int(x.strip(),16) for x in str(row.get("other_addresses_on_bus","")).split(";") if x.strip()]
        if addr in others: errors.append("I2C address collides with another bus address"); labels.append("address_collision")
    except Exception: errors.append("I2C address fields must be hexadecimal")
    label=labels[0] if labels else "valid"
    return {"valid":not errors,"errors":errors,"status":"valid" if not errors else "invalid","rule_label":label}

def min_vertex_cover_repair(fail_cells, spare_rows, spare_cols):
    # Exact binary optimization: x_row + y_col >= 1 for every failing cell.
    # Separate row/column budgets reflect the actual redundancy constraints.
    import numpy as np
    from scipy.optimize import milp, Bounds, LinearConstraint
    from scipy.sparse import lil_matrix
    edges=[]
    for pair in str(fail_cells or "").split(";"):
        if not pair.strip(): continue
        r,c=pair.split(":"); edges.append((int(r),int(c)))
    rows=sorted({r for r,_ in edges}); cols=sorted({c for _,c in edges})
    if not edges:
        return {"repairable":True,"minimum_rows":0,"minimum_cols":0,"rows":[],"cols":[],
                "spare_rows":int(spare_rows),"spare_cols":int(spare_cols)}
    ri={v:i for i,v in enumerate(rows)}; ci={v:i+len(rows) for i,v in enumerate(cols)}
    n=len(rows)+len(cols); A=lil_matrix((len(edges)+2,n),dtype=float)
    for j,(r,c) in enumerate(edges): A[j,ri[r]]=1; A[j,ci[c]]=1
    A[len(edges),:len(rows)]=1; A[len(edges)+1,len(rows):]=1
    lb=np.r_[np.ones(len(edges)), -np.inf, -np.inf]
    ub=np.r_[np.full(len(edges),np.inf), int(spare_rows), int(spare_cols)]
    res=milp(c=np.ones(n),integrality=np.ones(n),bounds=Bounds(np.zeros(n),np.ones(n)),
             constraints=LinearConstraint(A.tocsr(),lb,ub),options={"time_limit":3.0})
    if not res.success or res.x is None:
        return {"repairable":False,"minimum_rows":None,"minimum_cols":None,"rows":[],"cols":[],
                "spare_rows":int(spare_rows),"spare_cols":int(spare_cols),"solver_status":res.message}
    chosen_rows=[r for r in rows if res.x[ri[r]]>0.5]
    chosen_cols=[c for c in cols if res.x[ci[c]]>0.5]
    return {"repairable":True,"minimum_rows":len(chosen_rows),"minimum_cols":len(chosen_cols),
            "rows":chosen_rows,"cols":chosen_cols,"spare_rows":int(spare_rows),"spare_cols":int(spare_cols)}

def soc_sku_recommendation(die, demand_df):
    # Rule-based feasible assignment: best revenue SKU under demand cap and die limits.
    healthy=sum(not bool(die.get(f"core{i}_defect",False)) for i in range(8))
    fmax_vals=[float(die[f"core{i}_fmax_GHz"]) for i in range(8)
               if pd.notna(die.get(f"core{i}_fmax_GHz")) and not bool(die.get(f"core{i}_defect",False))]
    slowest=min(fmax_vals) if fmax_vals else 0.0
    raw_power=die.get("power_at_sku_W",0)
    power=0.0 if pd.isna(raw_power) else float(raw_power)
    feasible=[]
    for _,s in demand_df.iterrows():
        if healthy>=int(s.cores) and slowest>=float(s.fmax_GHz) and (power==0 or power<=float(s.tdp_W)):
            feasible.append((float(s.price_usd),int(s.weekly_demand_units),s.sku))
    feasible.sort(reverse=True)
    return {"healthy_cores":healthy,"slowest_healthy_core_fmax_GHz":slowest,
            "recommended_sku":feasible[0][2] if feasible else "scrap",
            "selection_method":"highest-price feasible SKU; per-die greedy recommendation",
            "global_demand_optimization":"not run for a single-die request; use batch allocation for demand-constrained optimization"}
