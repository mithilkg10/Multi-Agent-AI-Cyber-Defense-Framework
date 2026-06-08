# pyshark_to_predict.py (Refactored to use optimized Scapy sniffer)
import argparse
import time
import json
import requests
import sys
import os
import subprocess
from datetime import datetime

# Automatic installation of Scapy if missing
try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP
    HAS_SCAPY = True
except ImportError:
    print("[SYSTEM] Scapy not found. Attempting to install scapy automatically...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "scapy"], check=True)
        from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP
        HAS_SCAPY = True
        print("[SYSTEM] Scapy installed successfully!")
    except Exception as e:
        print(f"[WARNING] Scapy installation failed: {e}. Falling back to simulation mode.")
        HAS_SCAPY = False

# Try loading Kafka
try:
    from kafka import KafkaProducer
except ImportError:
    KafkaProducer = None

PREDICT_URL = "http://127.0.0.1:5000/predict"
DEFAULT_IFACE = "Wi-Fi"
DEFAULT_COUNT = 50
KAFKA_TOPIC = "abhedya_packets"
KAFKA_BOOTSTRAP = "localhost:9092"

def extract_scapy_features(pkt):
    feat = {}
    feat["Tot size"] = len(pkt)
    
    proto = "TCP"
    if pkt.haslayer(TCP):
        proto = "TCP"
    elif pkt.haslayer(UDP):
        proto = "UDP"
    elif pkt.haslayer(ICMP):
        proto = "ICMP"
    elif pkt.haslayer(ARP):
        proto = "ARP"
    
    feat["Protocol Type"] = proto
    
    feat["fin_flag_number"] = 0
    feat["syn_flag_number"] = 0
    feat["rst_flag_number"] = 0
    feat["psh_flag_number"] = 0
    feat["ack_flag_number"] = 0
    feat["ece_flag_number"] = 0
    feat["cwr_flag_number"] = 0
    
    if pkt.haslayer(TCP):
        try:
            val = int(pkt[TCP].flags)
            feat["fin_flag_number"] = 1 if (val & 0x01) else 0
            feat["syn_flag_number"] = 1 if (val & 0x02) else 0
            feat["rst_flag_number"] = 1 if (val & 0x04) else 0
            feat["psh_flag_number"] = 1 if (val & 0x08) else 0
            feat["ack_flag_number"] = 1 if (val & 0x10) else 0
            feat["ece_flag_number"] = 1 if (val & 0x40) else 0
            feat["cwr_flag_number"] = 1 if (val & 0x80) else 0
        except Exception:
            pass
        
    feat["ack_count"] = 0
    feat["syn_count"] = 0
    feat["fin_count"] = 0
    feat["rst_count"] = 0
    
    feat["Header_Length"] = 0
    feat["Time_To_Live"] = 0
    if pkt.haslayer(IP):
        feat["Header_Length"] = getattr(pkt[IP], "ihl", 5) * 4
        feat["Time_To_Live"] = getattr(pkt[IP], "ttl", 64)
        
    feat["Rate"] = 0.0
    feat["IAT"] = 0.0
    feat["Tot sum"] = feat["Tot size"]
    feat["AVG"] = feat["Tot size"]
    feat["Std"] = 0.0
    feat["Variance"] = 0.0
    feat["Min"] = feat["Tot size"]
    feat["Max"] = feat["Tot size"]
    feat["Number"] = 1
    
    # Layer indicators
    feat["HTTP"] = 1 if pkt.haslayer(TCP) and (pkt[TCP].sport == 80 or pkt[TCP].dport == 80) else 0
    feat["HTTPS"] = 1 if pkt.haslayer(TCP) and (pkt[TCP].sport == 443 or pkt[TCP].dport == 443) else 0
    feat["DNS"] = 1 if pkt.haslayer(UDP) and (pkt[UDP].sport == 53 or pkt[UDP].dport == 53) else 0
    feat["SSH"] = 1 if pkt.haslayer(TCP) and (pkt[TCP].sport == 22 or pkt[TCP].dport == 22) else 0
    feat["TCP"] = 1 if pkt.haslayer(TCP) else 0
    feat["UDP"] = 1 if pkt.haslayer(UDP) else 0
    feat["ICMP"] = 1 if pkt.haslayer(ICMP) else 0
    feat["ARP"] = 1 if pkt.haslayer(ARP) else 0
    feat["DHCP"] = 1 if pkt.haslayer(UDP) and (pkt[UDP].sport in (67, 68) or pkt[UDP].dport in (67, 68)) else 0
    
    return feat

def get_simulated_packet():
    import random
    proto = random.choice(["TCP", "UDP", "ICMP", "ARP"])
    size = random.randint(40, 1500)
    feat = {
        "Tot size": size,
        "Protocol Type": proto,
        "fin_flag_number": 0,
        "syn_flag_number": 1 if proto == "TCP" and random.random() < 0.2 else 0,
        "rst_flag_number": 1 if proto == "TCP" and random.random() < 0.05 else 0,
        "psh_flag_number": 0,
        "ack_flag_number": 1 if proto == "TCP" and random.random() < 0.8 else 0,
        "ece_flag_number": 0,
        "cwr_flag_number": 0,
        "ack_count": 0,
        "syn_count": 0,
        "fin_count": 0,
        "rst_count": 0,
        "Header_Length": 20 if proto in ("TCP", "UDP") else 0,
        "Time_To_Live": random.choice([64, 128]),
        "Rate": round(random.uniform(10.0, 150.0), 2),
        "IAT": round(random.uniform(0.001, 0.05), 4),
        "Tot sum": size,
        "AVG": size,
        "Std": 0.0,
        "Variance": 0.0,
        "Min": size,
        "Max": size,
        "Number": 1,
        "HTTP": 1 if proto == "TCP" and random.random() < 0.1 else 0,
        "HTTPS": 1 if proto == "TCP" and random.random() < 0.3 else 0,
        "DNS": 1 if proto == "UDP" and random.random() < 0.15 else 0,
        "SSH": 1 if proto == "TCP" and random.random() < 0.05 else 0,
        "TCP": 1 if proto == "TCP" else 0,
        "UDP": 1 if proto == "UDP" else 0,
        "ICMP": 1 if proto == "ICMP" else 0,
        "ARP": 1 if proto == "ARP" else 0,
        "DHCP": 0
    }
    return feat

def run_live(interface, batch_count, use_kafka=False, kafka_bootstrap=None, topic=None, max_batches=None, post_delay=0.05):
    if use_kafka and KafkaProducer is None:
        raise RuntimeError("kafka-python not installed. Install with pip install kafka-python")

    kafka_producer = None
    if use_kafka:
        kafka_bootstrap = kafka_bootstrap or KAFKA_BOOTSTRAP
        kafka_producer = KafkaProducer(bootstrap_servers=[kafka_bootstrap],
                                       value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    batch = []
    batches_sent = 0
    
    # If Scapy is present, try to sniff. If it fails (e.g. no WinPcap/Npcap), fall back to simulated streams.
    use_simulation = not HAS_SCAPY
    if HAS_SCAPY:
        print(f"[SNIFFER] Starting live Scapy packet capture on '{interface}'")
        
        # Scapy packet callback
        def packet_callback(pkt):
            try:
                f = extract_scapy_features(pkt)
                f["_ts"] = datetime.utcnow().isoformat()
                batch.append(f)
            except Exception as e:
                print("[SNIFFER] extract error:", e)
                
            if len(batch) >= batch_count:
                send_batch()

        def send_batch():
            nonlocal batches_sent, batch
            for rec in batch:
                try:
                    if use_kafka:
                        kafka_producer.send(topic or KAFKA_TOPIC, rec)
                    else:
                        r = requests.post(PREDICT_URL, json=rec, timeout=5)
                        print("[SNIFFER->HTTP]", r.status_code, r.text[:60])
                    time.sleep(post_delay)
                except Exception as e:
                    print("[SNIFFER->SEND] error:", e)
            batch = []
            batches_sent += 1
            time.sleep(0.2)

        try:
            # Sniff continuously in Scapy
            sniff(iface=interface, prn=packet_callback, store=0)
        except Exception as e:
            print(f"[WARNING] Scapy sniff failed (possibly missing WinPcap/Npcap driver): {e}")
            print("[SNIFFER] Switching to optimized simulation mode.")
            use_simulation = True

    if use_simulation:
        print("[SNIFFER] Simulation Mode active. Injecting synthetic traffic flow telemetry...")
        while True:
            pkt_data = get_simulated_packet()
            pkt_data["_ts"] = datetime.utcnow().isoformat()
            batch.append(pkt_data)
            
            if len(batch) >= batch_count:
                for rec in batch:
                    try:
                        if use_kafka:
                            kafka_producer.send(topic or KAFKA_TOPIC, rec)
                        else:
                            r = requests.post(PREDICT_URL, json=rec, timeout=5)
                            print("[SIMULATOR->HTTP]", r.status_code, r.text[:60])
                        time.sleep(post_delay)
                    except Exception as e:
                        print("[SIMULATOR->SEND] error:", e)
                batch = []
                batches_sent += 1
                if max_batches is not None and batches_sent >= max_batches:
                    print(f"[SIMULATOR] reached max_batches={max_batches} - exiting cleanly")
                    break
                time.sleep(0.2)
            time.sleep(0.01)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--iface", default=DEFAULT_IFACE)
    p.add_argument("--count", type=int, default=DEFAULT_COUNT)
    p.add_argument("--use-kafka", action="store_true")
    p.add_argument("--kafka-bootstrap", default=KAFKA_BOOTSTRAP)
    p.add_argument("--kafka-topic", default=KAFKA_TOPIC)
    p.add_argument("--max-batches", type=int, default=None)
    p.add_argument("--post-delay", type=float, default=0.05)
    args = p.parse_args()
    
    run_live(args.iface, args.count, use_kafka=args.use_kafka, kafka_bootstrap=args.kafka_bootstrap, topic=args.kafka_topic, max_batches=args.max_batches, post_delay=args.post_delay)
