import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score

# load model
xgb = joblib.load("models/xgb_model.pkl")

# load test data (adjust path accordingly)
df = pd.read_csv("datasets/xgb_test.csv")

X = df.drop("label", axis=1)
y = df["label"]

pred = xgb.predict(X)
acc = accuracy_score(y, pred)

print("XGBoost Accuracy:", acc)
