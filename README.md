AI-Driven SIEM & Active Deception Framework
*(Formerly Multi-Agent Defense Against AI-Powered Attacks)*

 Project Overview
This project is an enterprise-ready, metaheuristic multi-agent cyber defense platform designed to protect critical infrastructure from AI-powered and traditional network attacks. The system integrates advanced **Detection**, **Active Deception**, and **Automated Neutralization** using a continuous Reinforcement Learning loop.

By replacing static rule-based systems with dynamic, learning AI, this framework evolves in real-time.

 Key Features

* **Hybrid Intelligence Engine**: A multi-model ensemble classification engine combining:
  * **XGBoost**: For high-speed tabular feature extraction and baseline anomaly detection.
  * **CNN-LSTM**: For deep sequence learning on network packets to identify complex patterns.
  * **Deep Q-Learning (DQN)**: For autonomous decision making, reinforcement, and threat mitigation.
* **Active Deception (Custom-Designed Honeypots)**: Integrated, custom-built honeypot decoy system simulating **SCADA, Financial, and Military** network personas. It features real-time beacon tracking to lure attackers away from critical nodes. *(Note: This system relies entirely on custom-designed deceptive architecture, not off-the-shelf tools like Cowrie).*
* **Automated RL Retraining Loop**: Continuous Reinforcement Learning pipeline with hot-reloading policy weights, ensuring the models update continuously based on live traffic data.
* **Hardened SIEM Console**: Real-time MITRE ATT&CK mapping, log integrity audits using HMAC-SHA256, and an administrative "Overlord" console for manual threat mitigation and training control.
* **Zero-Breach Resilience**: Verified against a full threat matrix (DDoS, SQLi, Port Scans, and Brute-Force) with automated IP blocklisting and network isolation.

 Cybersecurity & Networking Tech Stack
* **Core Languages**: Python (Flask), HTML/CSS, JS
* **Cybersecurity Tools**: Network Traffic Analysis (Scapy, TShark, Wireshark), Custom-designed Honeypots (Active Deception), SIEM Architecture, Automated IP Blocklisting, MITRE ATT&CK Framework, Incident Response
* **AI/ML Tools**: Scikit-learn, TensorFlow / PyTorch, Stable-Baselines3 (DQN)
* **Data Pipeline & Infrastructure**: Kafka (Log Streaming), SQLite (WAL Mode for high-concurrency), Git

 System Architecture Highlights
* **app.py**: Central SIEM console and API routing.
* **backend/hybrid_decision.py**: The orchestrator for the AI ensemble, executing predictions using XGBoost, CNN-LSTM, and DQN.
* **backend/dqn_retrain.py**: Background continuous retraining loop.
* **honeypot_app.py**: The standalone Active Deception server routing attackers to simulated SCADA, Military, and Finance databases.
* **sniffer.py / anomaly_detector.py**: Live packet capture and feature extraction pipelines.

 Performance and Validation
The system has been heavily audited and stress-tested using simulated threat matrices including:
* High-volume volumetric DDoS attacks.
* Sophisticated multi-vector Brute Force.
* Automated SQL Injections.
* Stealth TCP Port Scans.

In all scenarios, the RL loop accurately detects the anomaly, logs the MITRE ATT&CK vector, issues an automated IP blocklist entry, and securely logs the transaction using HMAC-SHA256.

