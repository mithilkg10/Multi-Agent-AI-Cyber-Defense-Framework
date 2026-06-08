# backend/dqn_retrain.py
import os
import sys
import json
import time
import sqlite3
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import DQN

# Ensure project root is in path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Paths matching prediction configuration
MODEL_PATH = os.path.join(BASE_DIR, "models", "dqn", "dqn_threat_detection.zip")
SCALER_PATH = os.path.join(BASE_DIR, "models", "dqn", "dqn_scaler.joblib")
FEATURES_PATH = os.path.join(BASE_DIR, "models", "dqn", "dqn_feature_names.joblib")
LABEL_ENCODER_PATH = os.path.join(BASE_DIR, "models", "dqn", "dqn_label_encoder.joblib")
DB_PATH = os.path.join(BASE_DIR, "cyber_defense.db")

# Load base feature list
if os.path.exists(FEATURES_PATH):
    expected_features = joblib.load(FEATURES_PATH)
else:
    expected_features = [
        'fin_flag_number', 'syn_flag_number', 'rst_flag_number', 'psh_flag_number',
        'ack_flag_number', 'ece_flag_number', 'cwr_flag_number',
        'ack_count', 'syn_count', 'fin_count', 'rst_count',
        'Protocol Type_TCP', 'Protocol Type_UDP', 'Protocol Type_ICMP', 'Protocol Type_ARP',
        'HTTP', 'HTTPS', 'DNS', 'Telnet', 'SMTP', 'SSH', 'IRC',
        'TCP', 'UDP', 'DHCP', 'ARP', 'ICMP', 'IGMP', 'IPv', 'LLC',
        'Tot sum', 'Min', 'Max', 'AVG', 'Std', 'Tot size', 'IAT', 'Number', 'Variance'
    ]

class OnlineThreatDetectionEnv(gym.Env):
    """
    Lightweight, dynamic Gymnasium environment for online DQN retraining on captured logs.
    """
    def __init__(self, X, y):
        super(OnlineThreatDetectionEnv, self).__init__()
        self.X = X
        self.y = y
        self.n_features = X.shape[1]
        # Determine correct class size from label encoder or fallback to 34
        n_classes = 34
        label_encoder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "dqn", "dqn_label_encoder.joblib")
        if os.path.exists(label_encoder_path):
            try:
                import joblib
                le = joblib.load(label_encoder_path)
                n_classes = len(le.classes_)
            except:
                pass
        self.n_classes = n_classes
        self.current_index = 0
        self.action_space = spaces.Discrete(self.n_classes)
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(self.n_features,), dtype=np.float32)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.current_index = np.random.randint(0, len(self.X))
        obs = self.X[self.current_index].astype(np.float32)
        info = {}
        return obs, info

    def step(self, action):
        correct = int(action == self.y[self.current_index])
        reward = 1.0 if correct else -1.0
        done = True
        obs, info = self.reset()
        return obs.astype(np.float32), reward, done, False, info

def trigger_background_retrain(limit=2500, timesteps=8000):
    """
    Connect to SQLite, extract raw features from detections, preprocess them,
    instantiate the training env, run DQN.learn(), and overwrite the live model.
    """
    try:
        print(f"[dqn_retrain] Initiating online retraining cycle (limit={limit}, timesteps={timesteps})...")
        
        # 1. Fetch data from detections table
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Fetch records that have raw features
        cur.execute("""
            SELECT raw, prediction, final_score 
            FROM detections 
            WHERE raw IS NOT NULL AND traffic_id IS NOT NULL 
            ORDER BY id DESC LIMIT ?
        """, (limit,))
        
        rows = cur.fetchall()
        conn.close()
        
        if len(rows) < 10:
            print(f"[dqn_retrain] Insufficient telemetry data in DB ({len(rows)} records found). Skipping retraining.")
            return {"status": "skipped", "reason": f"Only {len(rows)} detections available. Needs at least 10."}
            
        print(f"[dqn_retrain] Parsed {len(rows)} telemetry flows. Commencing feature extraction...")
        
        # 2. Extract feature sets
        feature_list = []
        labels = []
        
        # Load label encoder if present
        label_encoder = None
        if os.path.exists(LABEL_ENCODER_PATH):
            try:
                label_encoder = joblib.load(LABEL_ENCODER_PATH)
            except:
                pass
                
        for r in rows:
            try:
                # Try parsing raw features
                data = json.loads(r["raw"])
                # Extract original inputs if nested
                if "input" in data and isinstance(data["input"], dict):
                    raw_flow = data["input"]
                else:
                    raw_flow = data
                    
                # Standardize Protocol Type
                proto = str(raw_flow.get("Protocol Type") or raw_flow.get("protocol") or "TCP").upper()
                raw_flow["Protocol Type"] = proto
                
                # Apply protocol one-hot encoding manually
                for p in ["TCP", "UDP", "ICMP", "ARP"]:
                    raw_flow[f"Protocol Type_{p}"] = 1 if p == proto else 0
                    
                # Reindex to align with DQN expectations
                aligned = {}
                for col in expected_features:
                    aligned[col] = float(raw_flow.get(col, 0.0) or 0.0)
                    
                feature_list.append(aligned)
                
                # Determine pseudo-label
                pred_label = str(r["prediction"])
                if label_encoder is not None and pred_label in label_encoder.classes_:
                    lbl_idx = int(np.where(label_encoder.classes_ == pred_label)[0][0])
                else:
                    # Fallback mapping: DDoS -> 1, SQLi/Anomaly -> 2, Normal -> 0
                    score = float(r["final_score"] or 0.0)
                    if score > 0.75:
                        lbl_idx = 2  # Block / heavy anomaly
                    elif score > 0.55:
                        lbl_idx = 1  # Watch / mild anomaly
                    else:
                        lbl_idx = 0  # Ignore / safe
                labels.append(lbl_idx)
            except Exception as e:
                # Skip corrupt records
                pass
                
        if len(feature_list) < 5:
            print("[dqn_retrain] Error: No valid feature dicts could be constructed from raw database logs.")
            return {"status": "error", "reason": "No valid feature schemas found in database rows."}
            
        # 3. Scale and normalize
        df_train = pd.DataFrame(feature_list)
        df_train.fillna(0.0, inplace=True)
        
        # Scale if scaler exists
        scaler = None
        if os.path.exists(SCALER_PATH):
            try:
                scaler = joblib.load(SCALER_PATH)
                X_scaled = scaler.transform(df_train)
            except:
                scaler = None
                
        if scaler is None:
            # MinMax scaling fallback
            min_val = df_train.min()
            max_val = df_train.max()
            range_val = (max_val - min_val).replace(0.0, 1.0)
            X_scaled = ((df_train - min_val) / range_val).values
            
        y_train = np.array(labels, dtype=int)
        
        # 4. Initialize Env & Retrain model
        env = OnlineThreatDetectionEnv(X_scaled, y_train)
        
        print("[dqn_retrain] Loading existing DQN model from disk...")
        if os.path.exists(MODEL_PATH):
            model = DQN.load(MODEL_PATH, env=env)
        else:
            # Fallback initialization of base model
            model = DQN("MlpPolicy", env, learning_rate=1e-4, verbose=0)
            
        # Start learn loop
        start_time = time.time()
        print(f"[dqn_retrain] Training DQN policy agent for {timesteps} steps...")
        model.learn(total_timesteps=timesteps)
        duration = time.time() - start_time
        
        # Save model back to path
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        model.save(MODEL_PATH)
        print(f"[dqn_retrain] [OK] DQN model saved to {MODEL_PATH}")
        
        # Calculate training metrics
        correct_count = 0
        test_samples = min(200, len(X_scaled))
        for idx in range(test_samples):
            obs = X_scaled[idx]
            action, _ = model.predict(obs, deterministic=True)
            if int(action) == y_train[idx]:
                correct_count += 1
        accuracy = (correct_count / test_samples) if test_samples > 0 else 1.0
        
        # Write retraining log to DB
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO dqn_retraining_log (timestamp, duration_sec, batch_size, accuracy, model_path)
                VALUES (?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), duration, len(X_scaled), accuracy, MODEL_PATH))
            conn.commit()
            conn.close()
            print("[dqn_retrain] Retraining metrics successfully logged to database.")
        except Exception as dbe:
            print(f"[dqn_retrain] Database log insert failed: {dbe}")
            
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "batch_size": len(X_scaled),
            "accuracy": accuracy,
            "duration": round(duration, 2)
        }
        
    except Exception as err:
        print(f"[dqn_retrain] [FATAL] Online retraining loop failed: {err}")
        return {"status": "error", "reason": str(err)}

if __name__ == "__main__":
    res = trigger_background_retrain(limit=2500, timesteps=1000)
    print("Execution Result:", res)
