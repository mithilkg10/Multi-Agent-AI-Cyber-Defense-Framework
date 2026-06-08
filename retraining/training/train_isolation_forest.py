import sys
import os
import joblib
from sklearn.ensemble import IsolationForest

# -------------------------------
# PATH FIX
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from retraining.features.feature_engineering import load_and_prepare

# -------------------------------
# MODEL PATH
# -------------------------------
MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "isolation_forest",
    "isolation_forest.pkl"
)

# -------------------------------
# LOAD FEATURES (CSV PATH INSIDE FEATURE FILE)
# -------------------------------
df = load_and_prepare()
X = df.drop(columns=['label'], errors='ignore')

# -------------------------------
# TRAIN MODEL
# -------------------------------
model = IsolationForest(
    n_estimators=200,
    contamination=0.05,
    random_state=42
)

model.fit(X)

os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
joblib.dump(model, MODEL_PATH)

print("✅ Isolation Forest trained and saved at:", MODEL_PATH)
