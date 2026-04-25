# GCS Hardware, Software & Cybersecurity

**Type:** Presentation
**Duration:** 30 minutes
**Section:** Day 1 – Ground Control

---

## Objectives

- Identify the hardware and software components of a GCS
- Compare dedicated hardware GCS (3DR Sololink) vs. tablet/phone-based GCS
- Understand the network architecture between GCS and drone
- Map GCS components to cybersecurity attack surface

---

## What is a Ground Control Station?

The **GCS** is any system used to monitor and control a UAV. It receives telemetry, displays a map, and sends commands.

**GCS form factors:**

| Type | Examples |
|------|---------|
| Dedicated hardware | 3DR Sololink, DJI RC Pro, Skydio Remote |
| Android tablet/phone | DJI Fly, Solex, QGroundControl |
| Laptop/desktop | QGroundControl, Mission Planner, MAVProxy |
| Web browser | Auterion Suite, custom dashboards |

---

## 3DR Sololink: Dedicated GCS Hardware

The **3DR Sololink** is the dedicated RC controller + GCS for the 3DR Solo.

**Hardware:**
- ARM Cortex-A9 (i.MX6) — same family as the Solo UAV companion computer
- Embedded Linux (OpenEmbedded / Yocto)
- 802.11n 2.4 GHz WiFi radio (both client and AP modes)
- Physical RC sticks and buttons
- Android tablet mount (optional)

**Software:**
- Runs a Linux OS with systemd
- Creates WiFi AP: `SoloLink_XXXXXXXX` (2.4 GHz)
- Bridges RC input to MAVLink MANUAL_CONTROL messages
- Hosts STM32-based front panel controller (buttons, LEDs)
- Runs `sololink` service that manages the GCS-UAV connection

**Network architecture:**
```
[Android Phone / Solex App]
          |  WiFi (SoloLink AP)
    [3DR Sololink GCS]
          |  WiFi (SoloLink-to-Solo bridge)
    [3DR Solo UAV]
          |  UART
    [ArduCopter FC]
```

**Attack surface:**
- SSH service accessible on SoloLink network (root login enabled by default)
- Web API for controller configuration
- STM32 serial interface
- UART console accessible via physical teardown


## GCS Software: Mission Planner

**Mission Planner** (Windows, open source) is the reference GCS for ArduPilot.

**Features:**
- Full parameter editor
- Flight data display
- Flight planning and simulation (with X-Plane)
- Log analysis (MAVExplorer integration)
- Firmware flashing

**Attack surface:**
- Connects to flight controller via serial or network
- Will execute arbitrary MAVLink commands against the connected vehicle
---
## GCS Software: QGroundControl (QGC)

**QGroundControl** is the primary cross-platform GCS for both ArduPilot and PX4.

**Capabilities:**
- Live telemetry display (attitude, position, battery, GPS)
- Mission planning (upload/download waypoints)
- Parameter viewer and editor
- Log download and review
- Firmware update

---

## GCS Network Architecture

Understanding the network is essential for assessing the GCS.

**3DR Solo networks:**

| SSID | Role | Subnet |
|------|------|--------|
| `SoloLink_XXXXXXXX` | GCS WiFi AP | 10.1.1.0/24 |
| (Solo internal) | UAV-GCS link | 10.1.1.0/24 |

**IP addresses:**
- `10.1.1.1` — Sololink GCS
- `10.1.1.10` — 3DR Solo UAV

## Services 

**Services on the GCS (Sololink):**
```
22/tcp  SSH   (root login enabled)
5502/tcp      Sololink API
```

**Services on the UAV (Solo):**
```
22/tcp  SSH   (root login enabled)
14550/udp     MAVLink (GCS telemetry)
14551/udp     MAVLink (secondary)
80/tcp  HTTP  (if GoPro is mounted: 10.5.5.9)
```

---

## GCS Exploitation Pathway

A typical GCS attack chain:

1. **Connect** to the GCS WiFi network (SoloLink_XXXXXXXX, default password: sololink)
2. **Enumerate** hosts with `nmap 10.1.1.0/24`
3. **Identify** SSH on GCS (10.1.1.1:22) and UAV (10.1.1.10:22)
4. **Access** SSH with default credentials (root, no password)
5. **Pivot** from GCS to UAV
6. **Interact** with MAVLink directly from the UAV shell
7. **Exfiltrate** flight logs, WiFi credentials, and configuration

---

## Summary

| Component | Key Risk |
|-----------|---------|
| 3DR Sololink | SSH root login, no password, exposed on WiFi |
| Specta Remote | Android ADB, APK vulnerabilities |
| SoloLink WiFi | WPA2 with default/known passphrase |
| MAVLink endpoint | Unauthenticated, accessible to all on network |
| GCS software | Full drone control plane — high-value target |
