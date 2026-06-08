# backend/feature_builder.py
import os
import joblib
import pandas as pd
import numpy as np

# paths
XGB_FEATURES_PATH = os.path.join("models", "xgb", "xgb_feature_names.joblib")
CNN_FEATURES_PATH = os.path.join("models", "cnn_lstm", "cnn_feature_names.joblib")
DQN_FEATURES_PATH = os.path.join("models", "dqn", "dqn_feature_names.joblib")
DQN_SCALER_PATH = os.path.join("models", "dqn", "dqn_scaler.joblib")

def _load_joblib(path):
    if os.path.exists(path):
        try:
            return joblib.load(path)
        except Exception:
            return None
    return None

XGB_FEATURES = _load_joblib(XGB_FEATURES_PATH)
CNN_FEATURES = _load_joblib(CNN_FEATURES_PATH)
DQN_FEATURES = _load_joblib(DQN_FEATURES_PATH)
DQN_SCALER = _load_joblib(DQN_SCALER_PATH)

def _apply_protocol_dummies(df: pd.DataFrame, expected_cols):
    """
    If 'Protocol Type' exists in the input df and expected_cols contain one-hot names,
    create dummies and keep only those expected columns.
    """
    if 'Protocol Type' in df.columns:
        dummies = pd.get_dummies(df['Protocol Type'], prefix='Protocol Type')
        df = pd.concat([df.drop(columns=['Protocol Type']), dummies], axis=1)

    # Some training code may have created columns like 'Protocol Type_TCP' or 'TCP' etc.
    # We'll not invent names — reindexing step will add missing expected cols as zeros.
    return df

def build_for_models(input_features: dict):
    """
    input_features: dict of raw incoming features (from frontend/test payload)
    returns:
      - xgb_df: pd.DataFrame with 1 row aligned to XGB_FEATURES (or raw DataFrame fallback)
      - cnn_df: pd.DataFrame with 1 row aligned to CNN_FEATURES
      - dqn_obs: numpy 1D array ready for dqn_model.predict (after scaler if present)
    """
    # Start with DataFrame of single row
    df = pd.DataFrame([input_features])

    # Normalize column names: strip whitespace (training might have trimmed)
    df.columns = [c.strip() for c in df.columns]

    # 1) Prepare XGB DataFrame
    if XGB_FEATURES:
        # We will attempt to create numeric columns only for XGB (pipeline may handle categoricals)
        # First try to convert obvious numeric columns
        xgb_df = df.copy()
        # If Protocol Type present and XGB expected columns contain one-hot names, expand
        xgb_df = _apply_protocol_dummies(xgb_df, XGB_FEATURES)
        # Reindex to expected features (add missing with 0)
        xgb_df = xgb_df.reindex(columns=XGB_FEATURES, fill_value=0)
        # Ensure numeric types where possible
        for col in xgb_df.columns:
            try:
                xgb_df[col] = pd.to_numeric(xgb_df[col], errors='coerce').fillna(0)
            except Exception:
                xgb_df[col] = xgb_df[col].astype(object)
    else:
        # fallback: use provided df but convert numeric where possible
        xgb_df = df.copy()
        xgb_df = xgb_df.apply(pd.to_numeric, errors='ignore')

    # 2) Prepare CNN DataFrame
    if CNN_FEATURES:
        cnn_df = df.copy()
        cnn_df = _apply_protocol_dummies(cnn_df, CNN_FEATURES)
        cnn_df = cnn_df.reindex(columns=CNN_FEATURES, fill_value=0)
        # numeric coercion
        cnn_df = cnn_df.apply(pd.to_numeric, errors='coerce').fillna(0.0)
    else:
        cnn_df = df.copy()
        cnn_df = cnn_df.apply(pd.to_numeric, errors='coerce').fillna(0.0)

    # 3) Prepare DQN observation (1D numpy)
    if DQN_FEATURES:
        dqn_df = df.copy()
        dqn_df = _apply_protocol_dummies(dqn_df, DQN_FEATURES)
        dqn_df = dqn_df.reindex(columns=DQN_FEATURES, fill_value=0)
        dqn_df = dqn_df.apply(pd.to_numeric, errors='coerce').fillna(0.0)
        arr = dqn_df.values.astype(float)  # shape (1, n)
        arr = arr.reshape(-1)  # 1D
        if DQN_SCALER is not None:
            try:
                obs = DQN_SCALER.transform(arr.reshape(1, -1))[0].astype(np.float32)
            except Exception:
                # fallback if scaler expects DataFrame
                try:
                    obs = DQN_SCALER.transform(pd.DataFrame([arr]))[0].astype(np.float32)
                except Exception:
                    obs = arr.astype(np.float32)
        else:
            obs = arr.astype(np.float32)
    else:
        # fallback: use numeric columns from df in sorted order
        temp = df.copy().apply(pd.to_numeric, errors='coerce').fillna(0.0)
        arr = temp.values.astype(float).reshape(-1)
        obs = arr.astype(np.float32)

    return xgb_df, cnn_df, obs
