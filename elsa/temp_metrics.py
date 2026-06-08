import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import sys
import os
sys.path.append(os.path.abspath('..'))

from backend.hybrid_decision import predict_combined
from backend.xgboost_module import predict_xgb
from backend.dqn_module import predict_dqn
from backend.cnn_lstm_module import predict_cnn_lstm

print("Loading data...")
df = pd.read_csv("../datasets/ML.csv")
y = df["label"]
X = df.drop("label", axis=1)

def run_evaluation(seed):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=seed, stratify=y)
    test_size = min(len(X_test), 500)
    X_test_sub = X_test.iloc[:test_size]
    y_test_sub = y_test.iloc[:test_size]

    xgb_preds, cnn_preds, dqn_preds, hybrid_preds = [], [], [], []
    
    for i in range(len(X_test_sub)):
        row_dict = X_test_sub.iloc[i].to_dict()
        row_df = pd.DataFrame([row_dict])
        
        out_xgb = predict_xgb(row_dict)
        xgb_preds.append(int(out_xgb["prediction"]))
        
        score_cnn = predict_cnn_lstm(row_df)
        cnn_preds.append(1 if score_cnn > 0.5 else 0)
        
        action = predict_dqn(row_df)
        dqn_preds.append(1 if int(action) == 2 else 0)
        
        out_hybrid = predict_combined(row_dict)
        hybrid_preds.append(1 if out_hybrid["final_score"] >= 0.5 else 0)
        
    return {
        "hybrid": {
            "acc": accuracy_score(y_test_sub, hybrid_preds),
            "prec": precision_score(y_test_sub, hybrid_preds, zero_division=0),
            "rec": recall_score(y_test_sub, hybrid_preds, zero_division=0),
            "f1": f1_score(y_test_sub, hybrid_preds, zero_division=0)
        },
        "xgb": accuracy_score(y_test_sub, xgb_preds),
        "cnn": accuracy_score(y_test_sub, cnn_preds),
        "dqn": accuracy_score(y_test_sub, dqn_preds)
    }

results = []
for s in [42, 100, 2023]:
    results.append(run_evaluation(s))

hyb_acc = [r["hybrid"]["acc"] for r in results]
hyb_prec = [r["hybrid"]["prec"] for r in results]
hyb_rec = [r["hybrid"]["rec"] for r in results]
hyb_f1 = [r["hybrid"]["f1"] for r in results]

print(f"Hybrid Accuracy: {np.mean(hyb_acc):.4f} ± {np.std(hyb_acc):.4f}")
print(f"Hybrid Precision: {np.mean(hyb_prec):.4f} ± {np.std(hyb_prec):.4f}")
print(f"Hybrid Recall: {np.mean(hyb_rec):.4f} ± {np.std(hyb_rec):.4f}")
print(f"Hybrid F1: {np.mean(hyb_f1):.4f} ± {np.std(hyb_f1):.4f}")

xgb_acc = [r["xgb"] for r in results]
cnn_acc = [r["cnn"] for r in results]
dqn_acc = [r["dqn"] for r in results]

print(f"XGB Only Acc: {np.mean(xgb_acc):.4f}")
print(f"CNN Only Acc: {np.mean(cnn_acc):.4f}")
print(f"DQN Only Acc: {np.mean(dqn_acc):.4f}")
