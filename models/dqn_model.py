import os
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import DQN

# --------------------------
# Load and preprocess dataset
# --------------------------
df = pd.read_csv(
    r"C:\Users\Mithil K Gowda\OneDrive\Desktop\PROJECT 7TH SEM\PROJECT\datasets\ML.csv",
    low_memory=False
)

selected_features = [
    'fin_flag_number', 'syn_flag_number', 'rst_flag_number', 'psh_flag_number',
    'ack_flag_number', 'ece_flag_number', 'cwr_flag_number',
    'ack_count', 'syn_count', 'fin_count', 'rst_count',
    'Protocol Type', 'HTTP', 'HTTPS', 'DNS', 'Telnet', 'SMTP', 'SSH', 'IRC',
    'TCP', 'UDP', 'DHCP', 'ARP', 'ICMP', 'IGMP', 'IPv', 'LLC',
    'Tot sum', 'Min', 'Max', 'AVG', 'Std', 'Tot size', 'IAT', 'Number', 'Variance',
    'Label'
]

# Keep only the selected columns (if present)
df = df[[c for c in selected_features if c in df.columns]].copy()

# Convert numeric-like columns to numeric
for col in df.columns:
    if col not in ['Label', 'Protocol Type']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.fillna(0, inplace=True)

numeric_cols = df.select_dtypes(include=[np.number]).columns
df[numeric_cols] = df[numeric_cols].clip(-1e6, 1e6)

# One-hot encode Protocol Type if present (drop_first to avoid collinearity as before)
if 'Protocol Type' in df.columns:
    df = pd.get_dummies(df, columns=['Protocol Type'], drop_first=True)

# Encode labels
label_encoder = LabelEncoder()
df['Label'] = label_encoder.fit_transform(df['Label'])

# --------------------------
# Scaling and train/test split
# --------------------------
scaler = MinMaxScaler()
X = df.drop(columns=['Label'])
y = df['Label']

# Fit scaler on DataFrame (preserves feature names in scikit-learn)
X_scaled = scaler.fit_transform(X)  # OK to use fit_transform here on DataFrame

# Create models directory and save scaler + feature names + label encoder for inference consistency
os.makedirs("models/dqn", exist_ok=True)
joblib.dump(scaler, "models/dqn/dqn_scaler.joblib")
joblib.dump(list(X.columns), "models/dqn/dqn_feature_names.joblib")
joblib.dump(label_encoder, "models/dqn/dqn_label_encoder.joblib")
print("Saved scaler, feature names and label encoder to models/dqn/")

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

y_train = np.array(y_train)
y_test = np.array(y_test)

# --------------------------
# Gym environment
# --------------------------
class ThreatDetectionEnv(gym.Env):
    def __init__(self, X, y):
        super(ThreatDetectionEnv, self).__init__()
        self.X = X
        self.y = y
        self.n_features = X.shape[1]
        self.n_classes = len(np.unique(y))
        self.current_index = 0
        self.action_space = spaces.Discrete(self.n_classes)
        self.observation_space = spaces.Box(low=0, high=1, shape=(self.n_features,), dtype=np.float32)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.current_index = np.random.randint(0, len(self.X))
        obs = self.X[self.current_index].astype(np.float32)
        info = {}
        return obs, info

    def step(self, action):
        correct = int(action == self.y[self.current_index])
        reward = 1 if correct else -1
        done = True
        obs, info = self.reset()
        return obs.astype(np.float32), reward, done, False, info

# --------------------------
# Train DQN
# --------------------------
if __name__ == "__main__":
    env = ThreatDetectionEnv(X_train, y_train)
    check_env(env, warn=True)

    model = DQN(
        "MlpPolicy",
        env,
        learning_rate=1e-4,
        buffer_size=50000,
        batch_size=64,
        learning_starts=1000,
        gamma=0.99,
        train_freq=4,
        target_update_interval=1000,
        verbose=1
    )

    model.learn(total_timesteps=100000)

    # Save the trained model to models/dqn/
    os.makedirs("models/dqn", exist_ok=True)
    model.save("models/dqn/dqn_threat_detection")
    print("✅ DQN model training complete and saved to models/dqn/dqn_threat_detection")

    # --------------------------
    # Evaluate on test set (KPI)
    # --------------------------
    correct = 0
    total = 2000
    env_test = ThreatDetectionEnv(X_test, y_test)

    for _ in range(total):
        obs, info = env_test.reset()
        action, _ = model.predict(obs, deterministic=True)
        if action == env_test.y[env_test.current_index]:
            correct += 1

    accuracy = correct / total
    print(f"🎯 DQN Detection Accuracy (KPI): {accuracy * 100:.2f}%")
