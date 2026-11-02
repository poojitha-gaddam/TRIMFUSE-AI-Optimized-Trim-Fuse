from pathlib import Path
import os
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.getenv("TRIMFUSE_DATA_DIR", ROOT / "datasets" / "original"))
MODEL_DIR = Path(os.getenv("TRIMFUSE_MODEL_DIR", ROOT / "backend" / "models"))
REPORT_DIR = Path(os.getenv("TRIMFUSE_REPORT_DIR", ROOT / "reports"))
MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
CHIP_FILES = {
    "MCU": "mcu_trim_fuse.csv",
    "PMIC": "pmic_trim_otp.csv",
    "Sensor": "sensor_calibration.csv",
    "SoC": "soc_binning_harvesting.csv",
}
ID_COLUMNS = {"MCU":"die_id","PMIC":"die_id","Sensor":"die_id","SoC":"die_id"}
SUPPORTING_FILES = {
    "MCU fuse schema": "mcu_fuse_schema.csv",
    "MCU fuse audit": "mcu_fuse_map_audit.csv",
    "PMIC OTP requests": "pmic_otp_config_requests.csv",
    "Memory repair bitmaps": "memory_repair_bitmaps.csv",
    "SoC SKU demand": "soc_sku_demand.csv",
}
