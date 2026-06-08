import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import joblib
import os

# Load the Excel file just uploaded
file_path = r"C:\Users\Mithil K Gowda\OneDrive\Desktop\PROJECT 7TH SEM\PROJECT\datasets\ML.csv"
df = pd.read_csv(file_path)

# Drop the Label column
df_features = df.drop(columns=['Label'])

# Clean the data
df_features.replace([np.inf, -np.inf], np.nan, inplace=True)
df_features.fillna(0, inplace=True)
df_features = df_features.clip(-1e6, 1e6)

# One-hot encode Protocol Type if applicable
if 'Protocol Type' in df_features.columns and (
    df_features['Protocol Type'].dtype == object or df_features['Protocol Type'].nunique() < 20):
    df_features = pd.get_dummies(df_features, columns=['Protocol Type'], drop_first=True)

# Fit the scaler
scaler = MinMaxScaler()
scaler.fit(df_features)

# Save the scaler
os.makedirs("models/cnn_lstm", exist_ok=True)
save_path = "models/cnn_lstm/cnn_scaler.joblib"
joblib.dump(scaler, save_path)

save_path  # to return for verification or use
