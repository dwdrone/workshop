# Hack Our Drone: 2-Day UAS Cybersecurity Workshop

## Course Description

The recent expansion of Uncrewed Autonomous Systems (UAS) across various sectors presents significant security challenges. Rapid adoption often outpaces cybersecurity engineering, leaving many systems vulnerable. This intensive two-day program provides a comprehensive, hands-on understanding of drone security vulnerabilities and the techniques to assess and mitigate them.

The curriculum spans the full UAS architecture: Unmanned Aerial Vehicle (UAV), Ground Control Station (GCS), RF communication protocols, payloads, and log analysis. Through expert-led instruction and hands-on lab exercises, participants gain proficiency in identifying, exploiting, and reporting vulnerabilities across all components.

## Difficulty Level

**Beginner / Intermediate**

- Students should be comfortable with the Linux command line
- A foundational understanding of network security or embedded systems is helpful but not required
- Thorough lab manuals are provided to address prerequisite knowledge gaps

## Student Kit

Each student workstation includes:
- Dell laptop running Kali Linux (Dark Wolf customization)
- USB thumb drive with workshop files (~/workshop)
- TP-Link USB WiFi dongle
- HackRF One SDR
- SiK Radio pair
- USB cables (Micro, Mini, USB-A/C)
- Teardown kit: spludge, guitar pick, cups, mat

Lab hardware (shared or per-group):
- 3DR Solo UAV + Sololink GCS + GoPro Hero 4
- Specta Mini UAV + RC remote
- Android phone with Solex app
- GL.iNet MT300N travel router (OpenWRT)
- ESP32-C3 or ESP32-S3 (Remote ID)

---

## Schedule

### Day 1: UAV, Ground Control Systems & Logging

| Time | Module | Type |
|------|--------|------|
| 09:00 | Welcome & Introductions | |
| 09:30 | 01 – UAS Cybersecurity | Presentation |
| 10:30 | 02 – Attack Surface | Activity |
| 11:00 | 03 – UAV Hardware, Software & Cybersecurity | Presentation |
| 12:00 | *Lunch* | |
| 13:00 | 04 – Lab: UAV Firmware Analysis | Lab |
| 14:00 | 05 – UAV Flight Controllers | Presentation |
| 14:30 | 06 – Lab: QGroundControl & Mission Planning | Lab |
| 15:30 | 07 – Introduction to Android Cybersecurity | Presentation |
| 16:00 | 08 – Lab: Android GCS Application Analysis | Lab |
| 17:00 | 09 – GCS Hardware, Software & Cybersecurity | Presentation |
| 17:30 | 10 – Lab: GCS Exploitation | Lab |
| 18:00 | 21 – UAS Logging | Presentation |
| 18:15 | 22 – Lab: Adversarial Forensics on UAS Logs | Lab |

### Day 2: RF Communications & Payloads

| Time | Module | Type |
|------|--------|------|
| 09:00 | 11 – UAS RF Communications | Presentation |
| 10:00 | 12 – Lab: Cracking Wireless Communications | Lab |
| 11:00 | 13 – DroneID & Remote ID | Presentation |
| 11:30 | 14 – Lab: Remote ID | Lab |
| 12:00 | *Lunch* | |
| 13:00 | 15 – SiK Telemetry Radios | Presentation |
| 13:30 | 16 – Lab: SiK Radio Hacks | Lab |
| 14:15 | 17 – MAVLink Telemetry for C2 | Presentation |
| 14:45 | 18 – Lab: MAVLink Sniffing & Spoofing | Lab |
| 15:30 | 19 – UAV Cameras: Digital & Analog | Presentation |
| 16:00 | 20 – Lab: Analog Video Transmission Sniffing | Lab |
| 16:30 | 23 – UAS Cybersecurity Review | Presentation |

---

## File Index

### Day 1

| File | Title | Type |
|------|-------|------|
| day1/01-uas-cybersecurity.md | UAS Cybersecurity | Presentation |
| day1/02-attack-surface-activity.md | Attack Surface | Activity |
| day1/03-uav-hardware-software.md | UAV Hardware, Software & Cybersecurity | Presentation |
| day1/04-lab-firmware-analysis.md | UAV Firmware Analysis | Lab |
| day1/05-uav-flight-controllers.md | UAV Flight Controllers | Presentation |
| day1/06-lab-qgroundcontrol.md | QGroundControl & Mission Planning | Lab |
| day1/07-android-cybersecurity.md | Introduction to Android Cybersecurity | Presentation |
| day1/08-lab-android-gcs.md | Android GCS Application Analysis | Lab |
| day1/09-gcs-hardware-software.md | GCS Hardware, Software & Cybersecurity | Presentation |
| day1/10-lab-gcs-exploitation.md | GCS Exploitation | Lab |
| day1/21-uas-logging.md | UAS Logging | Presentation |
| day1/22-lab-forensics.md | Adversarial Forensics on UAS Logs | Lab |

### Day 2

| File | Title | Type |
|------|-------|------|
| day2/11-rf-communications.md | UAS RF Communications | Presentation |
| day2/12-lab-cracking-wireless.md | Cracking Wireless Communications | Lab |
| day2/13-droneid-remoteid.md | DroneID & Remote ID | Presentation |
| day2/14-lab-remoteid.md | Remote ID Lab | Lab |
| day2/15-sik-telemetry-radios.md | SiK Telemetry Radios | Presentation |
| day2/16-lab-sik-hacks.md | SiK Radio Hacks | Lab |
| day2/17-mavlink.md | MAVLink Telemetry for C2 | Presentation |
| day2/18-lab-mavlink-sniffing.md | MAVLink Sniffing & Spoofing | Lab |
| day2/19-uav-cameras.md | UAV Cameras: Digital & Analog | Presentation |
| day2/20-lab-analog-video.md | Analog Video Transmission Sniffing | Lab |
| day2/23-cybersecurity-review.md | UAS Cybersecurity Review | Presentation |
