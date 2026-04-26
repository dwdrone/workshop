# Lab: QGroundControl & Mission Planning

**Type:** Lab
**Duration:** 60 minutes
**Section:** Day 1 – UAV & Drone

---

## Objectives

- Connect to a live 3DR Solo UAV via QGroundControl
- Enumerate the drone's parameters and identify security issues
- Download and examine flight logs
- Upload a custom mission plan
// - Observe MAVLink traffic on the network

---

## Prerequisites

- Laptop with QGroundControl installed
- 3DR Solo powered on (use continuous power adapter — do NOT attach propellers)
- WiFi connected to SoloLink_XXXXXXXX (password is on the Solo box)

---

## Phase 1: Connect QGroundControl to the 3DR Solo

```
# 3DR Solo network details:
SSID:     SoloLink_XXXXXXXX (XXXXXX = last 6 of MAC)
Password: sololink
MAVLink:  UDP port 14550
```

1. Connect your laptop WiFi to SoloLink_XXXXXXXX
2. Open QGroundControl
3. QGC auto-discovers the Solo on UDP 14550
4. Wait for the vehicle to appear — you will see telemetry data populate

**Verify:**
- Battery level appears in top bar
- GPS fix shows (if outdoors) or "No GPS" (indoors — normal)
- Vehicle type shows as ArduCopter

---

## Phase 2: Explore the Vehicle Parameters

```
In QGC: Vehicle Setup → Parameters
```

**Security-relevant parameters to examine:**

| Parameter | What to check |
|-----------|--------------|
| `FS_THR_ENABLE` | Throttle failsafe enabled? (should be 1) |
| `FS_GCS_ENABLE` | GCS failsafe enabled? (should be 1 or 2) |
| `FS_THR_VALUE` | Failsafe threshold value |
| `ARMING_CHECK` | Bitmask of pre-arm safety checks |
| `FENCE_ENABLE` | Geofence active? |
| `FENCE_RADIUS` | Geofence radius in meters |
| `BRD_SAFETYENABLE` | Hardware safety switch required? |
| `SYSID_THISMAV` | MAVLink system ID of this vehicle |

## Questions:
1. Is the GCS failsafe enabled? What happens if the GCS link drops?
2. Are all arming checks enabled? Which checks are disabled?
3. Is there a geofence configured?

---

## Phase 3: Connect via MAVProxy (CLI)

MAVProxy is a command-line MAVLink proxy and GCS. It gives you raw access to the MAVLink interface.

```bash
# Install if needed
pip install MAVProxy

# Connect to the Solo
mavproxy.py --master=udp:10.1.1.10:14550

# Once connected:
MAV> mode STABILIZE        # Change flight mode (drone must be disarmed)
MAV> param show FS_*       # Show all failsafe parameters
MAV> param show ARMING*    # Show arming parameters
MAV> param set FENCE_ENABLE 0  # Disable the geofence
MAV> wp list               # List current waypoints/mission
```

> **Safety:** Only run mode and parameter changes on a powered but propeller-free drone.

---

## Phase 4: Download and Review Flight Logs

```
In QGC: Analyze → Log Download
```

1. Click "Refresh" to list logs on the vehicle
2. Select a recent log file and download it
3. Open the log in QGC's log viewer

**What to look for:**
- GPS track: where has this drone been?
- Flight events: arming, disarming, mode changes, failsafes
- RC input: can you identify the pilot's inputs?
- Battery behavior: voltage curve over the flight

## CLI alternative — download logs via SSH (Optional)

```bash
ssh root@10.1.1.10

# ArduPilot DataFlash logs are stored on the Solo's filesystem
find / -name "*.BIN" 2>/dev/null
find / -name "*.log" 2>/dev/null

# Exit SSH
exit

# Copy a log file to your laptop
scp root@10.1.1.10:/log/1.BIN .
```

---

## Phase 5: Upload a Mission

1. In QGC, click the **Plan** view (map icon)
2. Select your vehicle
3. Click on the map to add waypoints
4. Set altitude for each waypoint (recommend: 10m for lab)
5. Click **Upload** to send the mission to the drone

**Observe in MAVProxy:**
```bash
MAV> wp list       # Confirm waypoints were received
MAV> wp getitem 1  # Show details of waypoint 1
```

> **Cybersecurity implication:** The drone accepted the mission with no authentication. Any device on the SoloLink network could upload a mission.

---


## Discussion Questions

1. What would happen if an attacker on the SoloLink WiFi sent a COMMAND_LONG with MAV_CMD_DO_SET_MODE to AUTO?
2. How could you use the downloaded flight logs in a threat intelligence or forensics context?
3. What single parameter change would make the drone the hardest to hijack via MAVLink?
4. In an actual penetration test, how would you document the unauthenticated MAVLink access finding?
