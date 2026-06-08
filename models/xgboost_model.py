import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from xgboost import XGBClassifier
import warnings

warnings.filterwarnings("ignore")

# Load dataset
df = pd.read_csv(
    r"C:\Users\Mithil K Gowda\OneDrive\Desktop\PROJECT 7TH SEM\PROJECT\datasets\ML.csv",
    low_memory=False
)

# Clean column names
df.columns = [c.strip() for c in df.columns]

# Ensure Label column exists
if 'Label' not in df.columns:
    candidates = [c for c in df.columns if c.lower() in ('label', 'target', 'class', 'y')]
    if candidates:
        df.rename(columns={candidates[0]: 'Label'}, inplace=True)
    else:
        raise SystemExit("❌ No 'Label' column found.")

# Drop NaNs and infinite values
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.dropna(inplace=True)

# Encode labels (same logic)
df['Label'] = df['Label'].astype(str)
label_mapping = {label: idx for idx, label in enumerate(df['Label'].unique())}
df['Label'] = df['Label'].map(label_mapping)

# Group the labels into classes
def group_label(l):
    if l in [0, 1, 2, 3]: return 0
    elif l in [4, 5, 6, 7]: return 1
    elif l in [8, 9, 10, 11]: return 2
    elif l in [12, 13, 14, 15]: return 3
    else: return 4

df['Label'] = df['Label'].apply(group_label)

X = df.drop('Label', axis=1)
y = df['Label']

# Detect feature types
numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
categorical_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()

low_card_cats = [c for c in categorical_cols if X[c].nunique() <= 25]
high_card_cats = [c for c in categorical_cols if X[c].nunique() > 25]

# Drop high cardinal categorical columns
X = X.drop(columns=high_card_cats)
categorical_cols = low_card_cats

# Build preprocessor
preprocessor = ColumnTransformer([
    ("num", StandardScaler(), numeric_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols)
])

# XGBoost model (your parameters exactly same)
model = XGBClassifier(
    n_estimators=300,
    max_depth=8,
    learning_rate=0.1,
    subsample=0.9,
    colsample_bytree=0.9,
    gamma=0.1,
    reg_lambda=1.5,
    reg_alpha=0.3,
    min_child_weight=2,
    eval_metric='mlogloss',
    tree_method='hist',
    verbosity=0
)

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", model)
])

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)

print("✔ Evaluation Metrics")
print(f"Accuracy  : {accuracy_score(y_test, y_pred):.4f}")
print(f"Precision : {precision_score(y_test, y_pred, average='weighted'):.4f}")
print(f"Recall    : {recall_score(y_test, y_pred, average='weighted'):.4f}")
print(f"F1 Score  : {f1_score(y_test, y_pred, average='weighted'):.4f}")
print("\n✔ Classification Report:")
print(classification_report(y_test, y_pred))

# -----------------------------
#  SAVE MODEL + FEATURE NAMES
# -----------------------------
os.makedirs("models/xgb", exist_ok=True)

joblib.dump(pipeline, "models/xgb/xgb_pipeline.joblib")
joblib.dump(list(X.columns), "models/xgb/xgb_feature_names.joblib")

print("✅ Saved model to: models/xgb/xgb_pipeline.joblib")
print("✅ Saved feature names to: models/xgb/xgb_feature_names.joblib")
