import pandas as pd
import json
import numpy as np
import os

# -------------------------------
# HARD-CODED DATASET PATH (YOUR PATH)
# -------------------------------
DATASET_PATH = r"C:\Users\Mithil K Gowda\OneDrive\Desktop\PROJECT 7TH SEM\PROJECT\datasets\ML.csv"

def load_and_prepare(csv_path: str = None):
    """
    Loads and prepares features for training.
    If csv_path is not provided, uses the default ML.csv path.
    """

    path = csv_path if csv_path else DATASET_PATH
    df = pd.read_csv(path)

    # -------------------------------
    # Timestamp features (safe)
    # -------------------------------
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        df['hour_of_day'] = df['created_at'].dt.hour.fillna(0)
        df['day_of_week'] = df['created_at'].dt.dayofweek.fillna(0)
        df.drop(columns=['created_at'], inplace=True, errors='ignore')
    else:
        df['hour_of_day'] = 0
        df['day_of_week'] = 0

    # -------------------------------
    # Event encoding
    # -------------------------------
    if 'event' in df.columns:
        df['event'] = df['event'].fillna("unknown")
        df = pd.get_dummies(df, columns=['event'], drop_first=True)

    # -------------------------------
    # Meta JSON features
    # -------------------------------
    if 'meta' in df.columns:
        def extract_meta_features(x):
            try:
                meta = json.loads(x) if isinstance(x, str) else {}
            except Exception:
                meta = {}
            return pd.Series({
                "ua_length": len(str(meta.get("user_agent", ""))),
                "has_sql_keywords": int(
                    any(k in str(meta).lower() for k in ["select", "union", "drop", "or 1=1"])
                )
            })

        meta_features = df['meta'].apply(extract_meta_features)
        df = pd.concat([df.drop(columns=['meta']), meta_features], axis=1)
    else:
        df['ua_length'] = 0
        df['has_sql_keywords'] = 0

    # -------------------------------
    # Cleanup
    # -------------------------------
    df = df.replace([np.inf, -np.inf], 0)
    df = df.fillna(0)
    # -------------------------------
    # Keep only numeric columns (CRITICAL for Isolation Forest)
    # -------------------------------
    df = df.select_dtypes(include=["number"])

    return df
