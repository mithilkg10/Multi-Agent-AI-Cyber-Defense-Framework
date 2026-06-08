# backend/dqn_module.py
import os
import joblib
import numpy as np
import pandas as pd
from stable_baselines3 import DQN

# Paths (match training/save)
MODEL_PATH = os.path.join("models", "dqn", "dqn_threat_detection.zip")
SCALER_PATH = os.path.join("models", "dqn", "dqn_scaler.joblib")
FEATURES_PATH = os.path.join("models", "dqn", "dqn_feature_names.joblib")
LABEL_ENCODER_PATH = os.path.join("models", "dqn", "dqn_label_encoder.joblib")

# Load DQN model
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"DQN model not found at {MODEL_PATH}")
dqn_model = DQN.load(MODEL_PATH)
last_model_mtime = os.path.getmtime(MODEL_PATH)

# Optional: load scaler and feature names if available
scaler = joblib.load(SCALER_PATH) if os.path.exists(SCALER_PATH) else None
EXPECTED_COLS = joblib.load(FEATURES_PATH) if os.path.exists(FEATURES_PATH) else None
label_encoder = joblib.load(LABEL_ENCODER_PATH) if os.path.exists(LABEL_ENCODER_PATH) else None

def reload_dqn_model_if_needed():
    global dqn_model, last_model_mtime, scaler, EXPECTED_COLS, label_encoder
    try:
        if os.path.exists(MODEL_PATH):
            current_mtime = os.path.getmtime(MODEL_PATH)
            if current_mtime > last_model_mtime:
                print(f"[dqn_module] Reloading updated DQN model from {MODEL_PATH}...")
                dqn_model = DQN.load(MODEL_PATH)
                last_model_mtime = current_mtime
                # Reload sidecars if updated
                if os.path.exists(SCALER_PATH):
                    scaler = joblib.load(SCALER_PATH)
                if os.path.exists(FEATURES_PATH):
                    EXPECTED_COLS = joblib.load(FEATURES_PATH)
                if os.path.exists(LABEL_ENCODER_PATH):
                    label_encoder = joblib.load(LABEL_ENCODER_PATH)
                print("[dqn_module] DQN model reloaded successfully.")
    except Exception as e:
        print(f"[dqn_module] Error hot-reloading DQN model: {e}")

def _prepare_obs(input_df: pd.DataFrame) -> np.ndarray:
    """
    Align columns, scale, and return a single 1D observation (dtype float32).
    """
    if EXPECTED_COLS is not None:
        df = input_df.reindex(columns=EXPECTED_COLS, fill_value=0)
    else:
        df = input_df.copy()

    # Convert numeric columns
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0.0)

    # If scaler available, use it
    if scaler is not None:
        # scaler.transform expects a 2D array or DataFrame
        arr = scaler.transform(df)
    else:
        arr = df.values.astype(np.float32)

    # Take the first row (we expect single-sample inference)
    obs = np.asarray(arr[0], dtype=np.float32)

    # Ensure 1D shape (n_features,)
    obs = obs.reshape(-1)
    return obs

def predict_dqn(input_df: pd.DataFrame) -> int:
    """
    input_df: pandas DataFrame with a single row (features)
    returns: action (int)
    """
    try:
        reload_dqn_model_if_needed()
        obs = _prepare_obs(input_df)
        action, _states = dqn_model.predict(obs, deterministic=True)
        return int(action)
    except Exception as e:
        print(f"[predict_dqn] Error during DQN predict: {e}")
        # Fallback: return 0 as default safe action
        return 0

