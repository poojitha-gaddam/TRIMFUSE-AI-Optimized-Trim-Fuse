import json, joblib
import numpy as np
import pandas as pd
from pathlib import Path
from .config import MODEL_DIR

def model_path(name):
    return MODEL_DIR / f"{name}.joblib"

def predict(model_name, values):
    path = model_path(model_name)
    if not path.exists():
        raise RuntimeError(f"Model {model_name} is not trained. Run: python -m backend.training.train_models")
    artifact = joblib.load(path)
    features = artifact["features"]
    missing=[k for k in features if k not in values or values.get(k) is None or (isinstance(values.get(k),float) and not np.isfinite(values.get(k)))]
    if missing:
        raise ValueError("Missing mandatory model features: " + ", ".join(missing))
    row = {k: values.get(k) for k in features}
    for k in artifact.get("numeric_features",[]):
        try: row[k]=float(row[k])
        except (TypeError,ValueError): raise ValueError(f"{k} must be numeric")
        if not np.isfinite(row[k]): raise ValueError(f"{k} must be finite")
    X = pd.DataFrame([row], columns=features)
    pred = np.asarray(artifact["pipeline"].predict(X)).reshape(-1)[0]
    input_warnings=[]
    for k,bounds in artifact.get("feature_ranges",{}).items():
        if row[k] < bounds["p005"] or row[k] > bounds["p995"]:
            input_warnings.append(f"{k} is outside the central 99% training range [{bounds['p005']:.4g}, {bounds['p995']:.4g}]")
    if not np.isfinite(float(pred)):
        raise ValueError("Model returned a non-finite prediction")
    return {
        "model": model_name, "model_version": artifact["version"],
        "prediction": float(pred), "target": artifact["target"],
        "evaluation": artifact["evaluation"], "feature_names": features,
        "prediction_type": "model_prediction", "input_warnings": input_warnings
    }

def model_inventory():
    items=[]
    for p in sorted(MODEL_DIR.glob("*.joblib")):
        a=joblib.load(p)
        items.append({"name":p.stem,"target":a.get("target","anomaly_screen"),"version":a.get("version","1.0.0"),"evaluation":a.get("evaluation",{"method":a.get("method","unsupervised")})})
    return items
