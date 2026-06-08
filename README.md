MULTI-AI-DEFENSE-

Multi-Agent Defense Against AI-Powered Attacks

📌 Project Overview

This project is a multi-agent cyber defense system designed to protect critical infrastructure from AI-powered attacks. The system integrates:

Detection (Machine Learning & Deep Learning)

Deception (Honeypots, Moving Target Defense)

Neutralization (Automated blocking, redirection)

Learning (Reinforcement Learning, adversarial retraining)

Repetition (continuous feedback loop for improvement)

Our goal is to build a real-time, adaptive, and intelligent defense framework that evolves with every attack attempt.

📂 Project Structure
MULTI-AI-DEFENSE-/
│
├── app/                        # Flask web application
│   ├── templates/              # HTML frontend (dashboard, login, results)
│   ├── static/                 # CSS, JS, images
│   ├── routes.py               # API endpoints
│   ├── models.py               # Database schema
│   └── ml_serving.py           # Model serving integration
│
├── datasets/                   # CICIDS/UNSW datasets + preprocessing
│   ├── preprocess.py
│   └── eda.ipynb
│
├── ml_models/                   # ML/DL models
│   ├── train_baseline.py
│   ├── rf_model.pkl
│   ├── cnn_model.h5
│   └── schema.json
│
├── honeypot/                   # Honeypot + Moving Target Defense scripts
│   ├── cowrie_config/
│   ├── redirect.py
│   └── mtd.py
│
├── docs/                       # Documentation & reports
│   ├── report.docx
│   ├── presentation.pptx
│   └── references.bib
│
├── tests/                      # Test scripts
│   └── test_predict.py
│
├── requirements.txt            # Python dependencies
├── run.py                      # Main Flask entry point
└── README.md                   # This file

🚀 How It Works (High-Level Workflow)

Incoming traffic is captured and passed into the detection agent.

Detection Layer uses ML/DL models (RF, XGBoost, CNN, LSTM) to classify traffic.

If traffic is malicious → it is redirected to honeypot or blocked.

Response logs are saved into database + shown in dashboard.

Reinforcement Learning agent updates defense strategies.

System repeats the cycle → becomes stronger with every attack.

👥 Team Workflow

ML Team (2 members)

Work in datasets/ and ml_models/

Tasks: preprocessing, training, saving models, defining feature schema

App Team (2 members)

Work in app/ and honeypot/

Tasks: Flask app, dashboard, honeypot integration, response scripts

All members workflow in GitHub:

git pull origin main before starting work

git checkout -b feature-<task> → new branch for your work

Make changes → git add . && git commit -m "msg"

Push branch → git push origin feature-<task>

Open Pull Request → review → merge into main

🛠️ Tech Stack

Languages: Python (Flask, scikit-learn, TensorFlow/PyTorch)

Frontend: HTML, CSS, JS, Chart.js

Database: MySQL / MongoDB

Defense Tools: Cowrie Honeypot, Moving Target Defense scripts

Collaboration: GitHub, VS Code

📊 Expected Results

High accuracy intrusion detection

Adaptive defense system with feedback loop

Real-time dashboard with KPIs: Detection Accuracy, False Positive Rate, MTTD, MTTR, Attacker Dwell Time

📖 References

CICIDS 2017 Dataset

UNSW-NB15 Dataset

Related IEEE and ACM research papers on IDS, Honeypots, and MTD