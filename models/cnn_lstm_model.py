# aggressive_cnn_lstm_ensemble.py
import os
import numpy as np
import pandas as pd
from collections import Counter
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import RandomOverSampler
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv1D, MaxPooling1D, LSTM, Dropout, BatchNormalization, Dense, GlobalAveragePooling1D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.utils import to_categorical
import joblib

# -------------------------- SETTINGS --------------------------
CSV_PATH = r"C:\Users\Mithil K Gowda\OneDrive\Desktop\PROJECT 7TH SEM\PROJECT\datasets\ML.csv"
SEQUENCE_LENGTH = 30
STRIDE = 10
MIN_SAMPLES_PER_CLASS = 100
N_SPLITS = 5
BATCH_SIZE = 32
EPOCHS = 100
SAVE_DIR = "models/cnn_lstm"
os.makedirs(SAVE_DIR, exist_ok=True)
np.random.seed(42)
tf.random.set_seed(42)

# -------------------------- FOCAL LOSS --------------------------
def categorical_focal_loss(gamma=2.0, alpha=0.25):
    import tensorflow as tf
    def loss(y_true, y_pred):
        y_pred = tf.clip_by_value(y_pred, 1e-9, 1.0 - 1e-9)
        ce = -y_true * tf.math.log(y_pred)
        w = alpha * tf.math.pow((1 - y_pred), gamma)
        return tf.reduce_sum(w * ce, axis=1)
    return loss

# --------------------- DATA LOADING & PREPROCESS ---------------------
df = pd.read_csv(CSV_PATH)
print("Original shape:", df.shape)

raw_labels = df["Label"].values
df_features = df.drop(columns=["Label"]).copy()

df_features.replace([np.inf, -np.inf], np.nan, inplace=True)
df_features.fillna(0, inplace=True)
df_features = df_features.clip(-1e6, 1e6)

if "Protocol Type" in df_features.columns and (
    df_features["Protocol Type"].dtype == object or df_features["Protocol Type"].nunique() < 20
):
    df_features = pd.get_dummies(df_features, columns=["Protocol Type"], drop_first=True)

# --------------------- FIXED SCALER (IMPORTANT) ---------------------
scaler = MinMaxScaler()
scaler.fit(df_features)     # BEFORE: scaler.fit(df_features.values) → BAD
scaled_df = pd.DataFrame(scaler.transform(df_features), columns=df_features.columns)

# save scaler + feature list
os.makedirs("models/cnn_lstm", exist_ok=True)
joblib.dump(scaler, "models/cnn_lstm/cnn_scaler.joblib")
joblib.dump(list(df_features.columns), "models/cnn_lstm/cnn_feature_names.joblib")
print("Saved scaler and feature list.")

# ------------------- SEQUENCE BUILDING -------------------
X_seqs = []
for i in range(0, len(scaled_df) - SEQUENCE_LENGTH, STRIDE):
    X_seqs.append(scaled_df.iloc[i:i + SEQUENCE_LENGTH].values)

X_seqs = np.array(X_seqs)
print("Sequences shape:", X_seqs.shape)

# Label encoding
global_le = LabelEncoder()
global_label_ids = global_le.fit_transform(raw_labels)

y_seq_all = []
for i in range(0, len(global_label_ids) - SEQUENCE_LENGTH, STRIDE):
    y_seq_all.append(global_label_ids[i + SEQUENCE_LENGTH // 2])
y_seq_all = np.array(y_seq_all)

print("Sequence labels dist:", Counter(y_seq_all))

# Filter small classes
label_counts = Counter(y_seq_all)
valid_ids = [lbl for lbl, cnt in label_counts.items() if cnt >= MIN_SAMPLES_PER_CLASS]

if len(valid_ids) == 0:
    raise SystemExit("No classes with minimum samples.")

mask = np.isin(y_seq_all, valid_ids)
X_seqs = X_seqs[mask]
y_seq_all = y_seq_all[mask]

print("After filtering:", X_seqs.shape, Counter(y_seq_all))

# Oversample
n_samples, seq_len, n_features = X_seqs.shape
X_flat = X_seqs.reshape((n_samples, seq_len * n_features))

ros = RandomOverSampler(random_state=42)
X_res, y_res = ros.fit_resample(X_flat, y_seq_all)

X_res = X_res.reshape((-1, seq_len, n_features))
y_res = np.array(y_res)

print("After oversampling:", Counter(y_res))

# Compact labels
unique_ids = np.unique(y_res)
new_le = LabelEncoder()
new_le.fit(unique_ids)
y_compact = new_le.transform(y_res)

num_classes = len(new_le.classes_)
class_names = [
    global_le.inverse_transform([int(orig)])[0] for orig in new_le.classes_
]

y_cat = to_categorical(y_compact, num_classes=num_classes)

# ------------------- MODEL BUILDER -------------------
def build_model(input_shape, num_classes, lr=1e-3, dropout_base=0.3, lstm_units=256, conv_filters=[128, 256]):
    model = Sequential()
    model.add(Conv1D(conv_filters[0], 3, activation="relu", padding="same", input_shape=input_shape))
    model.add(BatchNormalization())
    model.add(Conv1D(conv_filters[0], 3, activation="relu", padding="same"))
    model.add(MaxPooling1D(2))
    model.add(Dropout(dropout_base))

    model.add(Conv1D(conv_filters[1], 3, activation="relu", padding="same"))
    model.add(BatchNormalization())
    model.add(MaxPooling1D(2))
    model.add(Dropout(dropout_base))

    model.add(Conv1D(conv_filters[1], 1, activation="relu"))
    model.add(GlobalAveragePooling1D())

    model.add(Dense(lstm_units, activation='relu'))
    model.add(Dropout(dropout_base))
    model.add(Dense(num_classes, activation='softmax'))

    model.compile(
        optimizer=Adam(lr),
        loss=categorical_focal_loss(),
        metrics=['accuracy']
    )
    return model

# ------------------- K-FOLD TRAINING -------------------
kf = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=42)
fold = 1
val_accs = []
oof_true = []
oof_proba_full = []

oof_pred_container = np.zeros((X_res.shape[0], num_classes))

for train_idx, val_idx in kf.split(X_res, y_compact):
    print(f"\n----- FOLD {fold} -----")
    
    X_train, X_val = X_res[train_idx], X_res[val_idx]
    y_train, y_val = y_cat[train_idx], y_cat[val_idx]
    
    y_train_compact = np.argmax(y_train, axis=1)
    y_val_compact = np.argmax(y_val, axis=1)

    cw = compute_class_weight(class_weight="balanced", classes=np.arange(num_classes), y=y_train_compact)
    cw = {i: float(w) for i, w in enumerate(cw)}
    print("Class weights:", cw)

    model = build_model((SEQUENCE_LENGTH, n_features), num_classes)

    model_path = os.path.join(SAVE_DIR, f"best_fold_{fold}.h5")
    ckpt = ModelCheckpoint(model_path, monitor="val_accuracy", save_best_only=True, mode="max", verbose=1)
    es = EarlyStopping(monitor="val_accuracy", patience=12, restore_best_weights=True, verbose=1)
    rlr = ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=5, min_lr=1e-6, verbose=1)

    model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=[ckpt, es, rlr],
        class_weight=cw,
        verbose=2
    )

    best = load_model(model_path, compile=False)
    best.compile(optimizer=Adam(1e-4), loss=categorical_focal_loss(), metrics=['accuracy'])

    preds_proba = best.predict(X_val)
    preds = np.argmax(preds_proba, axis=1)

    acc = accuracy_score(y_val_compact, preds)
    print("Fold accuracy:", acc)
    val_accs.append(acc)

    # Fill oof
    for i, idx in enumerate(val_idx):
        oof_pred_container[idx] = preds_proba[i]
        oof_true.append(y_val_compact[i])

    fold += 1

# ------------------- OOF ENSEMBLE ACCURACY -------------------
oof_true = np.array(oof_true)
oof_preds = np.argmax(oof_pred_container, axis=1)
ensemble_acc = accuracy_score(oof_true, oof_preds)

print("\nEnsemble OOF Accuracy:", ensemble_acc)

# ------------------- SAVE SCALER + FEATURES -------------------
joblib.dump(scaler, "models/cnn_lstm/cnn_scaler.joblib")
joblib.dump(list(df_features.columns), "models/cnn_lstm/cnn_feature_names.joblib")
print("Saved cnn_scaler.joblib and cnn_feature_names.joblib to models/cnn_lstm/")
