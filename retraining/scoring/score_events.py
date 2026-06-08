import joblib
import numpy as np
from features.feature_engineering import load_and_prepare

IF_PATH = "models/isolation_forest/isolation_forest.pkl"
SUP_PATH = "models/supervised/lightgbm.pkl"
DATA_PATH = "PROJECT\datasets\ML.csv"

def normalize(x):
    return (x - x.min()) / (x.max() - x.min() + 1e-9)

df = load_and_prepare(DATA_PATH)

X = df.drop(columns=['label'], errors='ignore')

if_model = joblib.load(IF_PATH)
sup_model = joblib.load(SUP_PATH)

# Isolation Forest (lower = anomaly)
if_raw = -if_model.score_samples(X)
if_score = normalize(if_raw)

# Supervised probability
sup_prob = sup_model.predict_proba(X)[:, 1]
sup_score = normalize(sup_prob)

# Fusion
final_score = 0.6 * if_score + 0.4 * sup_score
df['final_anomaly_score'] = final_score
df['is_anomaly'] = df['final_anomaly_score'] >= 0.65

print(df[['final_anomaly_score', 'is_anomaly']].head())
