import sys
import os
import joblib
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ---------------- PATH FIX ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from retraining.features.feature_engineering import load_and_prepare

# ---------------- LOAD DATA ----------------
df = load_and_prepare()   # uses ML.csv internally

# ---------------- PSEUDO-LABELING ----------------
# Adjust column names if present in your CSV
if 'attack_type' in df.columns:
    df['label'] = (df['attack_type'] != 'NORMAL').astype(int)
elif 'final_score' in df.columns:
    df['label'] = (df['final_score'] > 0.8).astype(int)
else:
    raise ValueError("No column available for pseudo-labeling")

# ---------------- FEATURES & LABEL ----------------
X = df.drop(columns=['label'], errors='ignore')
y = df['label']

# ---------------- TRAIN / TEST SPLIT ----------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ---------------- MODEL ----------------
model = LGBMClassifier(
    n_estimators=300,
    learning_rate=0.05,
    random_state=42
)

model.fit(X_train, y_train)

# ---------------- EVALUATION ----------------
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# ---------------- SAVE MODEL ----------------
MODEL_PATH = os.path.join(BASE_DIR, "models", "supervised", "lightgbm.pkl")
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
joblib.dump(model, MODEL_PATH)

print("✅ Supervised model retrained and saved at:", MODEL_PATH)
