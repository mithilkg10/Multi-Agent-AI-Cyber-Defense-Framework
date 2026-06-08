# backend/cnn_lstm_module.py
import os
import glob
import joblib
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model

# Paths
MODEL_DIR = os.path.join("models", "cnn_lstm")
DEFAULT_MODEL_PATH = os.path.join(MODEL_DIR, "best_fold_1.h5")
SCALER_PATH = os.path.join(MODEL_DIR, "cnn_scaler.joblib")
FEATURES_PATH = os.path.join(MODEL_DIR, "cnn_feature_names.joblib")

# Helper: find a model file if DEFAULT_MODEL_PATH missing
def _find_model_path():
    if os.path.exists(DEFAULT_MODEL_PATH):
        return DEFAULT_MODEL_PATH
    # search for any best_fold_*.h5 in the model dir
    pattern = os.path.join(MODEL_DIR, "best_fold_*.h5")
    candidates = sorted(glob.glob(pattern))
    if candidates:
        return candidates[0]
    # fallback to any .h5 in the directory
    any_model = glob.glob(os.path.join(MODEL_DIR, "*.h5"))
    if any_model:
        return any_model[0]
    raise FileNotFoundError(f"No model found. Expected {DEFAULT_MODEL_PATH} or pattern {pattern}")

# Load model
MODEL_PATH = _find_model_path()
model = load_model(MODEL_PATH, compile=False)

# Load scaler (required)
if not os.path.exists(SCALER_PATH):
    raise FileNotFoundError(f"Scaler not found at {SCALER_PATH}. Train and save scaler to that path.")
scaler = joblib.load(SCALER_PATH)

# Determine expected columns
if hasattr(scaler, "feature_names_in_"):
    EXPECTED_COLS = list(scaler.feature_names_in_)
elif os.path.exists(FEATURES_PATH):
    EXPECTED_COLS = joblib.load(FEATURES_PATH)
else:
    raise RuntimeError(
        "No feature names found. Save a feature list at training time to "
        f"{FEATURES_PATH} or fit scaler on a DataFrame so scaler.feature_names_in_ exists."
    )

DEBUG_PREPROCESS = False  # set True during debugging

def _apply_protocol_dummies(df: pd.DataFrame) -> pd.DataFrame:
    if 'Protocol Type' in df.columns:
        df = pd.get_dummies(df, columns=['Protocol Type'], drop_first=True)
    return df

def preprocess_sequence(df_in):
    """
    Accepts: dict (single example) or pandas.DataFrame (one or more rows)
    Returns: X_seq shaped to model input: (n_samples, seq_len, n_features)
    If model expects seq_len > 1 and only a single timestep is provided, the row will be repeated.
    """
    if isinstance(df_in, dict):
        df = pd.DataFrame([df_in])
    elif isinstance(df_in, pd.DataFrame):
        df = df_in.copy()
    else:
        raise ValueError("preprocess_sequence expects dict or pandas.DataFrame")

    # Apply same categorical encoding used in training
    df = _apply_protocol_dummies(df)

    # Align columns to expected order (add missing with 0, drop extras)
    df_aligned = df.reindex(columns=EXPECTED_COLS, fill_value=0)

    # Ensure numeric dtypes
    df_aligned = df_aligned.apply(pd.to_numeric, errors='coerce').fillna(0.0)

    if DEBUG_PREPROCESS:
        incoming_keys = list(df.columns)
        missing = [c for c in EXPECTED_COLS if c not in incoming_keys]
        extra = [c for c in incoming_keys if c not in EXPECTED_COLS]
        print("[cnn_preprocess] incoming keys:", incoming_keys)
        print("[cnn_preprocess] expected cols:", EXPECTED_COLS)
        print("[cnn_preprocess] added missing:", missing)
        print("[cnn_preprocess] dropped extra:", extra)
        print("[cnn_preprocess] aligned shape:", df_aligned.shape)

    # Scale (pass DataFrame so sklearn sees feature names)
    X_scaled = scaler.transform(df_aligned)

    # Determine expected model input shape
    # Keras shape often like (None, seq_len, n_features)
    model_shape = model.input_shape
    try:
        # handle shapes like (None, seq_len, n_features)
        _, seq_len_expected, feat_expected = model_shape
    except Exception:
        # fallback: inspect tuple more carefully
        if isinstance(model_shape, tuple) and len(model_shape) == 3:
            seq_len_expected, feat_expected = model_shape[1], model_shape[2]
        else:
            # assume single-timestep with features = X_scaled.shape[1]
            seq_len_expected, feat_expected = 1, X_scaled.shape[1]

    # Build sequence dimension:
    if X_scaled.ndim == 2:
        n_samples, n_feats = X_scaled.shape
        if seq_len_expected > 1:
            # repeat the single timestep to match expected sequence length
            X_seq = np.repeat(X_scaled[:, np.newaxis, :], seq_len_expected, axis=1)
        else:
            X_seq = X_scaled.reshape((n_samples, 1, n_feats))
    else:
        X_seq = X_scaled  # already sequence-shaped

    # final check: feature count must match
    if X_seq.shape[-1] != feat_expected:
        raise ValueError(f"Feature count mismatch: model expects {feat_expected} features, got {X_seq.shape[-1]}")

    return X_seq

def predict_cnn_lstm(df_features):
    """
    df_features: dict or pandas.DataFrame (single/multi-row)
    returns: float score between 0..1 representing model confidence (mean of max class probabilities)
    """
    X_seq = preprocess_sequence(df_features)
    if X_seq.size == 0:
        return 0.5

    preds = model.predict(X_seq)  # preds shape depends on model -> (n, num_classes) or (n,1) etc.
    preds = np.asarray(preds)

    # Convert predictions to a per-sample confidence in [0,1]:
    # - For multiclass softmax: take max probability per sample
    # - For binary sigmoid shaped (n,1): take sigmoid output (already 0..1)
    if preds.ndim == 2 and preds.shape[1] >= 2:
        per_sample_conf = np.max(preds, axis=1)  # highest softmax probability
    elif preds.ndim == 2 and preds.shape[1] == 1:
        per_sample_conf = preds[:, 0]  # sigmoid output
    elif preds.ndim == 1:
        per_sample_conf = preds  # direct probabilities
    else:
        per_sample_conf = preds.reshape((preds.shape[0], -1)).mean(axis=1)

    avg_score = float(np.mean(per_sample_conf))
    return avg_score
