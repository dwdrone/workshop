# UAS Logging

**Type:** Presentation
**Duration:** 15 minutes
**Section:** Day 2 – Payloads & Logging

---

## Objectives

- Understand what data UAS systems log and where it is stored
- Identify log formats for ArduPilot and PX4
- Know the tools for analyzing UAS logs
- Recognize the forensic and OPSEC significance of UAS logs

---

## Why Drones Log

Drone autopilots generate detailed flight logs for:
- **Safety:** Crash investigation and root cause analysis
- **Performance:** Tuning PID controllers and flight behavior
- **Compliance:** Evidence of flight operations for regulatory purposes
- **Debugging:** Diagnosing sensor failures or software bugs

>**For a security assessor:** logs are a goldmine of intelligence about the drone, the operator, and past operations.

---

## ArduPilot: DataFlash Logs

**ArduPilot** stores logs in **DataFlash** format (binary `.BIN` files).

**Storage location:**
- SD card: `/LOGS/` directory (e.g., `1.BIN`, `2.BIN`, ...)
- Memory: on-board flash if no SD card

**Log naming:** Sequential numbers — 1.BIN is the oldest, highest number is the most recent.

## Key log messages (record types):

| Message | Content |
|---------|---------|
| `GPS` | Lat, lon, alt, speed, satellite count, fix type |
| `ATT` | Roll, pitch, yaw, RC input |
| `RCIN` | Raw RC input channel values |
| `RCOU` | Motor output values |
| `BAT` | Battery voltage, current, remaining |
| `MODE` | Flight mode changes with timestamp |
| `CMD` | Mission commands executed |
| `EV` | System events (arm, disarm, crash) |
| `ERR` | Errors and failsafe triggers |
| `PARM` | Parameter values at time of flight |
| `MSG` | Statustext messages (armed, mode changed, etc.) |

**Format:** Binary — requires Mission Planner, QGroundControl, or pymavlink/MAVExplorer to read.

---

## PX4: ULog Format

**PX4** stores logs in **ULog** format (`.ulg` files).

- Logged with the **logger** module
- Started at arm, stopped at disarm (or continuously if configured)
- Stored on SD card: `/log/` directory
- File naming: timestamp-based (`YYYY-MM-DD/HH-MM-SS.ulg`)

**Viewing tools:**
- **QGroundControl** — built-in ULog viewer
- **PlotJuggler** — time-series visualization
- **pyulog** — Python library for ULog analysis
- **Flight Review** — web-based (log.px4.io)

---

## What Logs Reveal

| Data | Forensic Value |
|------|---------------|
| GPS track | Complete flight path: where the drone went, how fast |
| Takeoff/landing locations | Home base of the operator |
| Mission waypoints | Pre-planned targets or routes |
| Timestamps | When flights occurred (correlated with events) |
| RC input | Pilot flying behavior and skill level |
| Parameter snapshot | How the drone was configured at flight time |
| Mode changes | When manual control was taken or autonomous mode engaged |
| Error events | What went wrong — crash analysis |
| Arming events | Number of flights, duration |

---

## Log Analysis Tools

### Mission Planner (Windows)
- Log Review: `Ctrl+F → Flight Data → Dataflash Logs`
- **MAVExplorer** — interactive graphing of log fields
- Flight path playback on Google Maps

### QGroundControl (Cross-platform)
- Analyze → Log Files → Open Log
- Built-in viewer for both DataFlash and ULog

### MAVExplorer (CLI)
```bash
mavlogdump.py 1.BIN --type GPS
# Dumps all GPS messages from the log

MAVExplorer.py 1.BIN
# Interactive graph tool
```

### pymavlink (Python)
```python
from pymavlink import mavutil

log = mavutil.mavlink_connection('1.BIN')
while True:
    msg = log.recv_match(type='GPS', blocking=True)
    if msg is None:
        break
    print(f"Time: {msg.TimeUS}, Lat: {msg.Lat/1e7}, Lon: {msg.Lng/1e7}, Alt: {msg.Alt}")
```

---

## OPSEC Considerations for Drone Operators
UAS logs create a persistent record of all operations. Operators should be aware:
1. **Logs persist on the SD card** even if the operator attempts to delete flight records from the GCS
2. **Home location** is stored in every log — identifies the operator's base
3. **Timestamps** are GPS-synchronized — accurate to within seconds
4. **Parameter snapshots** reveal the operator's configuration and any custom settings
5. **Logs are accessible via SSH** (on 3DR Solo) to anyone with network access

---

## Summary

| Platform | Format | Tool | Location |
|----------|--------|------|----------|
| ArduPilot | DataFlash .BIN | Mission Planner, MAVExplorer | /LOGS/ on SD card |
| PX4 | ULog .ulg | QGC, PlotJuggler, pyulog | /log/ on SD card |
| 3DR Solo | DataFlash .BIN | Accessible via SSH root@10.1.1.10 | /log/ |
