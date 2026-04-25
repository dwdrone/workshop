# Attack Surface Activity

**Type:** Activity
**Duration:** 30 minutes
**Section:** Day 1 – UAV & Drone

---

## Objectives

- Define attack surface as it applies to a UAS
- Map all entry points, interfaces, and trust boundaries of a target system
- Practice identifying attack surface without touching the device

---

## What is an Attack Surface?

The **attack surface** is the sum of all points where an unauthorized user can try to enter, extract data from, or attack a system.

## For a UAS, this includes:
- Every physical port and interface
- Every wireless link
- Every piece of software and firmware
- Every user account and authentication boundary
- Every protocol and data format

Reducing attack surface = removing unnecessary interfaces, disabling unused services, and enforcing least privilege.

---

## Attack Surface Categories: Physical Interfaces
- UART debug console (JST, pads, header pins)
- USB (ADB, serial, mass storage)
- JTAG / SWD (firmware debugging)
- SD card slot
- Camera/gimbal connector
- CAN bus, I2C, SPI

## Attack Surface Categories: RF/Wireless Interfaces
- RC control link (2.4 GHz / 900 MHz)
- Telemetry link (SiK radio, 433 / 915 MHz)
- WiFi (2.4 GHz / 5 GHz) – GCS hotspot
- Bluetooth – pairing, setup
- GPS/GNSS reception (passive – but spoofable)
- Remote ID broadcast (WiFi Beacon / BLE)
- FPV video downlink (5.8 GHz analog or digital)

## Attack Surface Categories: Software & Firmware
- Flight controller firmware (ArduPilot, PX4)
- Companion computer OS (Linux Yocto, Ubuntu)
- GCS application (Android APK, Windows app)
- Embedded web interface (HTTP, REST API)
- SSH / Telnet services
- Update mechanisms (OTA firmware updates)

## Attack Surface Categories: Data
- Flight logs (GPS track, telemetry history)
- Configuration files (WiFi credentials, parameters)
- Mission plans (waypoints)
- Camera footage / SD card contents

## Attack Surface Categories: Supply Chain
- Manufacturer firmware repositories
- Third-party plugins or payloads
- Android application stores

---

## Activity: Map the 3DR Solo Attack Surface

**Time:** 20 minutes

### Instructions

Working in pairs, draw an attack surface diagram for the **3DR Solo UAS system**. Your diagram should include:

For each component, list:
- Physical interfaces
- Wireless interfaces
- Software entry points
- Trust boundaries (where authentication should occur)

## 3DR Solo System Facts

| Component | Details |
|-----------|---------|
| UAV | ArduCopter (ArduPilot fork), iMX6 companion computer, Pixhawk-based flight controller |
| Sololink | Runs embedded Linux, creates two WiFi SSIDs (SoloLink_XXXX) |
| WiFi link | UAV-GCS: 2.4 GHz 802.11n, WPA2 |
| Telemetry | MAVLink over WiFi (UDP 14550) |
| RC | 2.4 GHz proprietary from Solo to UAV |
| GoPro | WiFi-connected (10.5.5.9), HTTP API on port 80 |
| Solex App | Android APK, communicates with Sololink |


---

## Discuss:
- Which attack surfaces are most exposed?
- Which are hardest to remediate?
- What would be the first step in an actual assessment?
