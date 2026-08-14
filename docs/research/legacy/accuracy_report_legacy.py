import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from tensorflow.keras.models import load_model

# Import your existing modules
from backend.hybrid_decision import predict_combined
from backend.xgboost_module import predict_xgb
from backend.dqn_module import predict_dqn
from backend.cnn_lstm_module import predict_cnn_lstm

print("\n=============== ABHEDYA – FULL MODEL EVALUATION ===============\n")

# --------------------------------------------------------
# Load the ONLY dataset you have
# --------------------------------------------------------
df = pd.read_csv("datasets\ML.csv")

if "label" not in df.columns:
    raise Exception("Your ML.csv MUST contain a column named 'label' (0/1).")

y = df["label"]
X = df.drop("label", axis=1)

# Split dataset (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print(f"Loaded ML.csv — Total rows: {len(df)}, Test rows: {len(X_test)}")


# --------------------------------------------------------
# 1. XGBOOST ACCURACY
# --------------------------------------------------------
print("\n➡ Evaluating XGBoost...")
xgb_preds = []

for i in range(len(X_test)):
    row = X_test.iloc[i].to_dict()
    out = predict_xgb(row)
    xgb_preds.append(int(out["prediction"]))

acc_xgb = accuracy_score(y_test, xgb_preds)
print(f"XGBoost Accuracy: {acc_xgb:.4f}")


# --------------------------------------------------------
# 2. CNN-LSTM ACCURACY
# --------------------------------------------------------
print("\n➡ Evaluating CNN-LSTM...")

cnn_preds = []

for i in range(len(X_test)):
    row_df = pd.DataFrame([X_test.iloc[i].to_dict()])
    score = predict_cnn_lstm(row_df)
    pred = 1 if score > 0.5 else 0
    cnn_preds.append(pred)

acc_cnn = accuracy_score(y_test, cnn_preds)
print(f"CNN-LSTM Accuracy: {acc_cnn:.4f}")


# --------------------------------------------------------
# 3. DQN policy — optional evaluation
# --------------------------------------------------------
print("\n➡ Evaluating DQN Policy... (approximate)")

dqn_preds = []
for i in range(len(X_test)):
    row_df = pd.DataFrame([X_test.iloc[i].to_dict()])
    action = predict_dqn(row_df)
    # "block" = 2 → treat as malicious
    pred = 1 if int(action) == 2 else 0
    dqn_preds.append(pred)

acc_dqn = accuracy_score(y_test, dqn_preds)
print(f"DQN Approx Accuracy (Block=Malicious): {acc_dqn:.4f}")


# --------------------------------------------------------
# 4. HYBRID ACCURACY — your real pipeline
# --------------------------------------------------------
print("\n➡ Evaluating Hybrid (XGB + CNN + DQN)...")

hybrid_preds = []

for i in range(len(X_test)):
    row = X_test.iloc[i].to_dict()
    out = predict_combined(row)
    final_score = out["final_score"]
    pred = 1 if final_score >= 0.5 else 0
    hybrid_preds.append(pred)

acc_hybrid = accuracy_score(y_test, hybrid_preds)
print(f"Hybrid Model Accuracy: {acc_hybrid:.4f}")

print("\n==============================================================")
print("               ACCURACY REPORT COMPLETED")
print("==============================================================\n")
