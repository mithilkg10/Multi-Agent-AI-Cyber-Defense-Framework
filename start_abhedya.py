#!/usr/bin/env python3
"""
start_abhedya.py
- Automated startup orchestrator for the Abhedya Cyber Defense Framework.
- Performs port checks to avoid address conflicts.
- Automatically removes stale Zookeeper pid files and Kafka write locks to prevent startup crashes.
- Launches Zookeeper and waits for it to bind.
- Cleans stale ZooKeeper nodes (/brokers/ids/0) before starting Kafka.
- Launches Kafka Broker and waits for port 9092.
- Spawns all Python services (Main Dashboard, Decoy App, Model Prediction Consumer, Honeypot Controller).
- Neatly stream logs with colored prefixes.
- Listens for Ctrl+C to execute a graceful cleanup and reverse shutdown of all sub-processes.
"""

import os
import sys
import time
import socket
import subprocess
import threading
import signal
from pathlib import Path

# Force stdout/stderr to UTF-8 to handle emojis on Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


# ---------- CONFIGURATION ----------
KAFKA_HOME = r"C:\kafka\kafka"
ZOOKEEPER_PORT = 2181
KAFKA_PORT = 9092
DASHBOARD_PORT = 5000
DECOY_PORT = 5001

# Find correct Python executable (Virtual Environment preferred)
VENV_PYTHON = os.path.join(os.getcwd(), "venv", "Scripts", "python.exe")
if os.path.exists(VENV_PYTHON):
    PYTHON_EXE = VENV_PYTHON
else:
    PYTHON_EXE = sys.executable

print(f"[SYSTEM] Using Python Interpreter: {PYTHON_EXE}")

# ANSI Colors for Prefix Logs
COLORS = {
    "SYSTEM": "\033[95m",
    "ZOOKEEPER": "\033[96m",
    "KAFKA": "\033[94m",
    "DASHBOARD": "\033[92m",
    "DECOY_APP": "\033[93m",
    "CONSUMER": "\033[91m",
    "CONTROLLER": "\033[35m",
    "RESET": "\033[0m"
}

# Subprocess references
processes = {}
shutdown_triggered = False

def log(service, message):
    prefix = COLORS.get(service, COLORS["SYSTEM"])
    reset = COLORS["RESET"]
    print(f"{prefix}[{service}]{reset} {message}")

def is_port_open(port, host="127.0.0.1"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        try:
            s.connect((host, port))
            return True
        except Exception:
            return False

def clean_stale_locks():
    log("SYSTEM", "Performing health scan on data directories...")
    # Default ZooKeeper temp file lock location on Windows
    zk_pid = r"C:\tmp\zookeeper\zookeeper_server.pid"
    if os.path.exists(zk_pid):
        try:
            os.remove(zk_pid)
            log("SYSTEM", "[CLEANUP] Cleaned stale ZooKeeper PID lock file.")
        except Exception as e:
            log("SYSTEM", f"[WARNING] Failed to remove stale ZooKeeper PID file: {e}")

    # Default Kafka temp file write lock location on Windows
    kafka_lock = r"C:\tmp\kafka-logs\write.lock"
    if os.path.exists(kafka_lock):
        try:
            os.remove(kafka_lock)
            log("SYSTEM", "[CLEANUP] Cleaned stale Kafka write.lock file.")
        except Exception as e:
            log("SYSTEM", f"[WARNING] Failed to remove stale Kafka write lock: {e}")

def run_log_stream(name, proc):
    """Read subprocess stdout line by line and print to main console."""
    try:
        for line in iter(proc.stdout.readline, ''):
            if shutdown_triggered:
                break
            line_str = line.strip()
            if line_str:
                log(name, line_str)
    except Exception:
        pass

def spawn_process(name, cmd, cwd=None, env=None):
    """Safely spawn a subprocess and connect stdout streams."""
    if shutdown_triggered:
        return None
    try:
        # Build environment with UTF-8 encoding
        sub_env = os.environ.copy()
        sub_env["PYTHONIOENCODING"] = "utf-8"
        if env:
            sub_env.update(env)
            
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            bufsize=1,
            cwd=cwd,
            env=sub_env
        )
        processes[name] = proc
        
        # Start logging daemon thread
        t = threading.Thread(target=run_log_stream, args=(name, proc), daemon=True)
        t.start()
        return proc
    except Exception as e:
        log("SYSTEM", f"[ERROR] Failed to launch process {name}: {e}")
        return None

def start_zookeeper():
    if is_port_open(ZOOKEEPER_PORT):
        log("ZOOKEEPER", "Port 2181 is already active. Assuming ZooKeeper is running.")
        return True

    log("ZOOKEEPER", "Launching ZooKeeper Server...")
    zk_cmd = [
        os.path.join(KAFKA_HOME, "bin", "windows", "zookeeper-server-start.bat"),
        os.path.join(KAFKA_HOME, "config", "zookeeper.properties")
    ]
    
    # Check if batch file exists
    if not os.path.exists(zk_cmd[0]):
        log("ZOOKEEPER", f"[ERROR] Cannot find zookeeper script at: {zk_cmd[0]}. Please check configuration.")
        return False
        
    spawn_process("ZOOKEEPER", zk_cmd, cwd=KAFKA_HOME)

    # Wait for port to become active
    retries = 30
    log("ZOOKEEPER", "Waiting for ZooKeeper to bind to port 2181...")
    while retries > 0:
        if shutdown_triggered:
            return False
        if is_port_open(ZOOKEEPER_PORT):
            log("ZOOKEEPER", "[OK] ZooKeeper is online and listening on port 2181.")
            return True
        time.sleep(1)
        retries -= 1
        
    log("ZOOKEEPER", "[ERROR] ZooKeeper failed to start within 30 seconds.")
    return False

def clean_stale_broker_nodes():
    log("ZOOKEEPER", "Sweeping stale broker nodes from ZooKeeper shell...")
    zk_shell_path = os.path.join(KAFKA_HOME, "bin", "windows", "zookeeper-shell.bat")
    if not os.path.exists(zk_shell_path):
        log("ZOOKEEPER", "[WARNING] zookeeper-shell.bat not found. Skipping broker sweep.")
        return

    try:
        # Run cleanup synchronously with a short timeout
        cmd = [zk_shell_path, f"localhost:{ZOOKEEPER_PORT}", "deleteall", "/brokers/ids/0"]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
        log("ZOOKEEPER", "[CLEANUP] ZooKeeper broker ID 0 nodes swept.")
    except subprocess.TimeoutExpired:
        log("ZOOKEEPER", "[WARNING] ZooKeeper node sweep timed out. Continuing...")
    except Exception as e:
        log("ZOOKEEPER", f"[WARNING] Node sweep error (non-fatal): {e}")

def start_kafka():
    if is_port_open(KAFKA_PORT):
        log("KAFKA", "Port 9092 is already active. Assuming Kafka is running.")
        return True

    log("KAFKA", "Launching Kafka Broker...")
    kafka_cmd = [
        os.path.join(KAFKA_HOME, "bin", "windows", "kafka-server-start.bat"),
        os.path.join(KAFKA_HOME, "config", "server.properties")
    ]

    if not os.path.exists(kafka_cmd[0]):
        log("KAFKA", f"[ERROR] Cannot find kafka server script at: {kafka_cmd[0]}")
        return False

    spawn_process("KAFKA", kafka_cmd, cwd=KAFKA_HOME)

    retries = 30
    log("KAFKA", "Waiting for Kafka Broker to bind to port 9092...")
    while retries > 0:
        if shutdown_triggered:
            return False
        if is_port_open(KAFKA_PORT):
            log("KAFKA", "[OK] Kafka Broker is online and listening on port 9092.")
            return True
        time.sleep(1)
        retries -= 1

    log("KAFKA", "[ERROR] Kafka Broker failed to start within 30 seconds.")
    return False

def verify_pipelines():
    log("SYSTEM", "Scanning pipeline connections...")
    # Verify local databases exist or can be accessed
    db_files = ["cyber_defense.db", "honeypot.db", "intelligence_assets.db"]
    for db in db_files:
        p = Path(db)
        if p.exists():
            log("SYSTEM", f"[OK] Database connection point confirmed: {db} (Size: {p.stat().st_size} bytes)")
        else:
            log("SYSTEM", f"[WARNING] Database file not found: {db} (Will be created dynamically on boot)")

def start_app_services():
    log("SYSTEM", "Starting Abhedya application services...")

    # 1. Start Main Dashboard (Port 5000) first to initialize database tables
    if is_port_open(DASHBOARD_PORT):
        log("DASHBOARD", "[ERROR] Dashboard port 5000 is already in use. Cannot start Dashboard app.")
        return False
    spawn_process("DASHBOARD", [PYTHON_EXE, "app.py"])

    # Wait for Dashboard to bind (database init completes)
    retries = 20
    log("DASHBOARD", "Waiting for Main Dashboard to initialize...")
    while retries > 0:
        if shutdown_triggered:
            return False
        if is_port_open(DASHBOARD_PORT):
            log("DASHBOARD", "[OK] Main Dashboard is online at http://127.0.0.1:5000/")
            break
        time.sleep(1)
        retries -= 1

    if retries == 0:
        log("DASHBOARD", "[ERROR] Main Dashboard failed to initialize in time.")
        return False

    # 2. Start Honeypot Web App (Port 5001)
    if is_port_open(DECOY_PORT):
        log("DECOY_APP", "[ERROR] Decoy App port 5001 is already in use. Cannot start decoy app.")
        return False
    spawn_process("DECOY_APP", [PYTHON_EXE, "honeypot_app.py"])

    # Wait for Decoy port to bind
    retries = 10
    while retries > 0:
        if is_port_open(DECOY_PORT):
            log("DECOY_APP", "[OK] Decoy Deception Honeypot is online at http://127.0.0.1:5001/")
            break
        time.sleep(1)
        retries -= 1

    # 3. Start Model Prediction Consumer
    spawn_process("CONSUMER", [PYTHON_EXE, "kafka_models_consumer.py"])

    # 4. Start Honeypot Controller (Firewall broker)
    spawn_process("CONTROLLER", [PYTHON_EXE, "honeypot_controller.py"])

    # 5. Start Packet Sniffer / Simulation Client (feeds Kafka ingress topic 'network-traffic')
    spawn_process("SNIFFER", [PYTHON_EXE, "pyshark_to_predict.py", "--use-kafka", "--kafka-topic", "network-traffic"])

    return True

def shutdown_services(signum=None, frame=None):
    global shutdown_triggered
    if shutdown_triggered:
        return
    shutdown_triggered = True
    print("\n")
    log("SYSTEM", "[STOP] Interrupt received. Commencing graceful teardown...")

    # Shutdown python services first in reverse order
    py_services = ["SNIFFER", "DASHBOARD", "CONTROLLER", "CONSUMER", "DECOY_APP"]
    for s in py_services:
        if s in processes:
            log("SYSTEM", f"Terminating service: {s}...")
            processes[s].terminate()
            try:
                processes[s].wait(timeout=4)
                log("SYSTEM", f"Service {s} terminated.")
            except subprocess.TimeoutExpired:
                processes[s].kill()
                log("SYSTEM", f"Service {s} killed.")

    # Shutdown Kafka
    if "KAFKA" in processes:
        log("SYSTEM", "Stopping Kafka Broker process...")
        processes["KAFKA"].terminate()
        try:
            processes["KAFKA"].wait(timeout=8)
            log("SYSTEM", "Kafka Broker terminated.")
        except subprocess.TimeoutExpired:
            processes["KAFKA"].kill()
            log("SYSTEM", "Kafka Broker killed.")

    # Shutdown ZooKeeper
    if "ZOOKEEPER" in processes:
        log("SYSTEM", "Stopping ZooKeeper process...")
        processes["ZOOKEEPER"].terminate()
        try:
            processes["ZOOKEEPER"].wait(timeout=6)
            log("SYSTEM", "ZooKeeper terminated.")
        except subprocess.TimeoutExpired:
            processes["ZOOKEEPER"].kill()
            log("SYSTEM", "ZooKeeper killed.")

    log("SYSTEM", "[CLEAN] All Abhedya services stopped cleanly. Safe to close.")
    sys.exit(0)

# Register signals for clean exit
signal.signal(signal.SIGINT, shutdown_services)
signal.signal(signal.SIGTERM, shutdown_services)

def main():
    log("SYSTEM", "Starting Abhedya Adaptive Cyber Defense Orchestrator...")
    
    # 1. Clean locks
    clean_stale_locks()
    
    # 2. Check pipelines
    verify_pipelines()
    
    # 3. Start Zookeeper
    if not start_zookeeper():
        log("SYSTEM", "[ERROR] Aborting startup due to ZooKeeper failure.")
        shutdown_services()
        
    # 4. Clean Zookeeper stale nodes
    clean_stale_broker_nodes()
    
    # 5. Start Kafka
    if not start_kafka():
        log("SYSTEM", "[ERROR] Aborting startup due to Kafka Broker failure.")
        shutdown_services()

    # 6. Start Application services
    if not start_app_services():
        log("SYSTEM", "[ERROR] Failed to start application services.")
        shutdown_services()

    log("SYSTEM", "[OK] Abhedya pipeline is fully active. Press Ctrl+C to terminate all services.")
    
    # Keep main thread alive
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            shutdown_services()
            break

if __name__ == "__main__":
    main()
