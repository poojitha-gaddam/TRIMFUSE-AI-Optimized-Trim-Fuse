import pandas as pd
from functools import lru_cache
from .config import DATA_DIR, CHIP_FILES, SUPPORTING_FILES

@lru_cache(maxsize=8)
def load_csv(filename):
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Required assessment dataset not found: {path}")
    return pd.read_csv(path)

def chip_frame(chip):
    if chip not in CHIP_FILES:
        raise ValueError(f"Unsupported chip category: {chip}")
    return load_csv(CHIP_FILES[chip]).copy()

def get_die(chip, die_id):
    prefixes={"MCU":"MCU-","PMIC":"PMIC-","Sensor":"SNS-","SoC":"SOC-"}
    if chip not in prefixes:
        raise ValueError(f"Unsupported chip category: {chip}")
    if not str(die_id).startswith(prefixes[chip]):
        raise ValueError(f"Die ID {die_id} does not have the expected {chip} prefix {prefixes[chip]}")
    df = chip_frame(chip)
    rows = df[df["die_id"].astype(str) == str(die_id)]
    if rows.empty:
        raise KeyError(f"{die_id} was not found in the {chip} dataset")
    if len(rows) > 1:
        raise ValueError(f"Duplicate die identifier {die_id} in {chip} dataset")
    return rows.iloc[0].to_dict()

def dataset_summary():
    result = {}
    all_files={**{f"{chip} main":name for chip,name in CHIP_FILES.items()},**SUPPORTING_FILES}
    for label, filename in all_files.items():
        df = load_csv(filename)
        id_col=next((c for c in ["array_id","request_id","die_id","field","sku"] if c in df.columns),None)
        result[label] = {
            "file": filename, "rows": int(len(df)), "columns": int(len(df.columns)),
            "column_names": list(df.columns),
            "missing_by_column": {k:int(v) for k,v in df.isna().sum().items() if v},
            "duplicate_rows": int(df.duplicated().sum()),
            "id_column":id_col,
            "duplicate_ids":int(df[id_col].duplicated().sum()) if id_col else None,
        }
    return result
