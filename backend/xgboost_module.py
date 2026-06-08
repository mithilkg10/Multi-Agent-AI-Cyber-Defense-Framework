# backend/xgboost_module.py
import os
import joblib
import pandas as pd
import numpy as np

# Paths (match training save)
PIPELINE_PATH = os.path.join("models", "xgb", "xgb_pipeline.joblib")
FEATURES_PATH = os.path.join("models", "xgb", "xgb_feature_names.joblib")

# Load pipeline and expected feature list
if not os.path.exists(PIPELINE_PATH):
    raise FileNotFoundError(f"XGBoost pipeline not found at: {PIPELINE_PATH}")
pipeline = joblib.load(PIPELINE_PATH)

if os.path.exists(FEATURES_PATH):
    EXPECTED_COLS = joblib.load(FEATURES_PATH)
else:
    # If feature list isn't available, we'll attempt to use pipeline as-is, but warn
    EXPECTED_COLS = None

def _prepare_df(input_features: dict) -> pd.DataFrame:
    df = pd.DataFrame([input_features])
    if EXPECTED_COLS is not None:
        # Reindex to expected columns (adds missing with 0, drops extra)
        df = df.reindex(columns=EXPECTED_COLS, fill_value=0)
    # Ensure numeric where possible
    df = df.apply(pd.to_numeric, errors="ignore")
    return df

def predict_xgb(features: dict):
    try:
        df = _prepare_df(features)
        probas = pipeline.predict_proba(df)[0]
        prediction = int(np.argmax(probas))
        return {
            "prediction": prediction,
            "probabilities": [float(p) for p in probas]
        }
    except Exception as e:
        # Defensive fallback - return neutral probabilities if something goes wrong
        print(f"[predict_xgb] Error during prediction: {e}")
        n_classes = getattr(pipeline, "n_classes_", None)
        if n_classes is None:
            # try to infer from last estimator if possible
            try:
                n_classes = pipeline.named_steps['classifier'].n_classes_
            except Exception:
                n_classes = 2
        neutral = [1.0 / n_classes] * n_classes
        return {
            "prediction": 0,
            "probabilities": neutral
        }
