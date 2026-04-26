# Lab: Adversarial Forensics on UAS Logs

**Type:** Lab
**Duration:** 30 minutes
**Section:** Day 2 – Payloads & Logging

---

## Objectives

- Extract flight logs from the 3DR Solo via SSH
- Analyze logs to reconstruct flight history, GPS track, and operator behavior
- Identify mission waypoints and sensitive locations
- Demonstrate the forensic intelligence value of UAS logs

---

## Background

"Adversarial forensics" means applying forensic analysis techniques from the perspective of an attacker or intelligence collector — not as a defender performing incident response, but as someone who has gained unauthorized access to the drone's data.

---

## Phase 1: Access and List Logs

```bash
# Ensure you are connected to SoloLink WiFi
# SSH to the Solo UAV
ssh root@10.1.1.10

# Find the log directory
find / -name "*.BIN" 2>/dev/null
ls -lh /log/

# List all available logs with timestamps
ls -lht /log/*.BIN | head -20
```

**Note:** Each `.BIN` file is one flight session. The file number is sequential — the highest number is the most recent flight.

---

## Phase 2: Exfiltrate Logs

```bash
# From your laptop (separate terminal, not the SSH session):
mkdir -p ~/workshop/logs/solo/

# Copy all logs from the Solo
scp -o StrictHostKeyChecking=no root@10.1.1.10:/log/*.BIN ~/workshop/logs/solo/

# Verify files were transferred
ls -lh ~/workshop/logs/solo/
```

---

## Phase 3: Analyze with MAVExplorer (CLI)

```bash
cd ~/workshop/logs/solo/

# List all message types in the log (what data was recorded)
mavlogdump.py 1.BIN --types

# Extract GPS track
mavlogdump.py 1.BIN --type GPS > gps-track.txt
cat gps-track.txt | head -20

# Extract mode change history
mavlogdump.py 1.BIN --type MODE
# Shows: timestamp, mode number, mode name

# Extract arm/disarm events
mavlogdump.py 1.BIN --type EV
# Event 10 = Armed, Event 11 = Disarmed

# Extract parameter snapshot (how the drone was configured)
mavlogdump.py 1.BIN --type PARM | grep "FS_\|ARMING\|FENCE"

# Extract any mission commands that were executed
mavlogdump.py 1.BIN --type CMD
```

---

## Phase 4: Reconstruct the Flight Path

### Option A: QGroundControl


- Open QGroundControl on your laptop
- Analyze → Log Files → Open Log → select a .BIN file
- Click the "Flight Data" tab
- The flight path is displayed on the map

## Phase 4: Reconstruct the Flight Path
### Option B: Python Script

```python
# Save as: extract_gps.py
from pymavlink import mavutil
import sys

logfile = sys.argv[1] if len(sys.argv) > 1 else '1.BIN'

print("timestamp_us,latitude,longitude,altitude_m,ground_speed")

log = mavutil.mavlink_connection(logfile)
while True:
    msg = log.recv_match(type='GPS', blocking=True)
    if msg is None:
        break
    if msg.Status >= 3:  # Only if we have a GPS fix
        print(f"{msg.TimeUS},{msg.Lat/1e7:.7f},{msg.Lng/1e7:.7f},{msg.Alt/100:.1f},{msg.Spd:.1f}")
```

```bash
python3 extract_gps.py ~/workshop/logs/solo/1.BIN > flight-path.csv

# Open in spreadsheet or mapping tool
# Or visualize with gpx:
cat flight-path.csv | head -5
```
## Phase 4: Reconstruct the Flight Path
### Option C: Convert to KML for Google Earth

```bash
# Using mavlogdump to generate KML
# (Requires Mission Planner on Windows, or use the Python approach)
mavlogdump.py 1.BIN --type GPS --format kml > flight.kml
# Open flight.kml in Google Earth or Google Maps (import file)
```

---

## Phase 5: Intelligence Extraction

Answer these questions from the log data:

1. How many total flights are in the log directory?
2. How long was the longest flight?
3. What is the home location (takeoff point)?
4. What was the maximum altitude reached?
5. Were any autonomous mission waypoints executed?

---
## Phase 5: Intellegnece Extraction (Answers)


```bash
# 1. How many total flights are in the log directory?
ls /log/*.BIN | wc -l

# 2. How long was the longest flight?
# (Check start/end timestamps in each BIN file)
mavlogdump.py 1.BIN --type GPS | awk -F',' 'NR==1{start=$1} END{print (NR>1)? "Duration (us):", $1-start : "No GPS data"}'

# 3. What is the home location (takeoff point)?
mavlogdump.py 1.BIN --type GPS | head -5
# First GPS fix = likely home location

# 4. What was the maximum altitude reached?
mavlogdump.py 1.BIN --type GPS | awk -F',' 'NR>1 && $5 > max {max=$5} END{print "Max alt (cm):", max}'

# 5. Were any autonomous mission waypoints executed?
mavlogdump.py 1.BIN --type CMD | grep -v "^#"
```
---

## Plot the operator's home location:

```python
from pymavlink import mavutil

log = mavutil.mavlink_connection('1.BIN')
first_gps = None

while True:
    msg = log.recv_match(type='GPS', blocking=True)
    if msg is None:
        break
    if msg.Status >= 3 and first_gps is None:
        first_gps = msg
        print(f"First GPS fix (likely takeoff/home location):")
        print(f"  Latitude:  {msg.Lat/1e7:.7f}")
        print(f"  Longitude: {msg.Lng/1e7:.7f}")
        print(f"  Altitude:  {msg.Alt/100:.1f} m")
        print(f"  Google Maps: https://maps.google.com/?q={msg.Lat/1e7},{msg.Lng/1e7}")
        break
```

---

## Phase 6: Check for Anomalous Events

```bash
# Check for failsafe triggers
mavlogdump.py 1.BIN --type ERR

# Check for GPS loss events
mavlogdump.py 1.BIN --type EV | grep -i "gps\|fail\|lost"

# Check for parameter changes during flight (unusual)
mavlogdump.py 1.BIN --type PARM

# Check status messages (text log)
mavlogdump.py 1.BIN --type MSG
```

---

## Findings Template

Fill in for the most recent log file:

| Intelligence Item | Value |
|------------------|-------|
| Total flights in log | |
| First flight date/time | |
| Most recent flight date/time | |
| Home/takeoff location (lat, lon) | |
| Maximum altitude | |
| Longest flight duration | |
| Autonomous waypoints used | Yes / No |
| Failsafe events | |
| Notable error messages | |

---

## Discussion Questions

1. If this drone was used by a journalist to photograph a protest, what could an attacker learn from these logs?
2. How would you detect that logs had been tampered with or deleted?
3. Should log files be protected with encryption at rest? What would be required?
4. As a drone operator running sensitive missions, what OPSEC measures would you implement to reduce forensic exposure?
