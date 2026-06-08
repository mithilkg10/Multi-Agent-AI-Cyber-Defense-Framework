import pyshark

cap = pyshark.LiveCapture(interface='Wi-Fi', packet_count=5)
cap.sniff()
for pkt in cap:
    print(pkt)
