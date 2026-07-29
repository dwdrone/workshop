# Intro - UAS Cybersecurity

**Type:** Presentation
**Duration:** 60 minutes
**Section:** Day 1 – UAV & Drone

---
## Instructors 

**Ron Broberg**
<img src="../img/ron.png" style="width: 40%; height: auto;" align="right">

- Penetration Tester @ Dark Wolf

- Previously @ Lockheed Martin

- Specializing in UAS, IoT and RF 

- DC31 Black Badge Winner IoT CTF


## Instructors

**Rudy Mendoza**
<img src="../img/Rudy.jpg" style="width: 40%; height: auto;" align="right">

- Penetration Tester @ Dark Wolf

- Previoulsy with the U.S Air Force

- Specializing in UAS, and IoT

- DC31 Black Badge Winner IoT CTF

## Objectives

- Intro to UAS
- Identify the UAS threat landscape
- Understand attack vectors targeting UAS
- Apply core security principles to UAS contexts
- Survey the regulatory and framework landscape

---

## How These Two Days Fit Together

This course follows a drone **from the inside out** — the same order a real security assessment does.

- **Day 1 — The aircraft and its controller.** We open up the drone (hardware, firmware, flight controller), then the Ground Control Station (the Android app and the controller radio). You will pull firmware apart, read a live drone's parameters, and get a root shell on the aircraft.
- **Day 2 — The invisible layer: radio.** Every drone is really a collection of *radio links*. We study each link (WiFi, telemetry, GPS, Remote ID, video) and attack it with a Software-Defined Radio.

**Rule of thumb for the whole course:** almost every drone weakness comes down to one of three things — *no encryption, no authentication, or a default password*. Watch for those three ideas in every module.

<img src="../img/dg-attack-chain.svg" style="width: 92%; height: auto;" align="center">

*By the end of Day 1 you will walk this exact chain against a real 3DR Solo — from "connected to its WiFi" to "sending it commands."*

---

## Key Terms (You'll Hear These All Week)

New to drones or to security? Keep this list handy — every term below returns in later modules.

| Term | Plain-English meaning |
|------|----------------------|
| **UAS** | Unmanned Aircraft *System* — the whole package: the drone + controller + radio links |
| **UAV** | The flying part alone (the aircraft) |
| **GCS** | Ground Control Station — whatever you use to fly and monitor the drone (app, laptop, controller) |
| **Flight Controller (FC)** | The small computer on the drone that keeps it stable and runs the mission |
| **Autopilot firmware** | The software on the FC — usually **ArduPilot** or **PX4** |
| **MAVLink** | The "language" the drone and GCS speak to each other (Module 5, 17) |
| **Telemetry** | Live data coming *down* from the drone (battery, GPS, attitude) |
| **RF** | Radio Frequency — any wireless signal (Day 2) |
| **SDR** | Software-Defined Radio — a USB radio (like the HackRF) that can tune to almost any frequency (Module 11) |
| **GNSS / GPS** | The satellite positioning the drone uses to know where it is |
| **Payload** | Anything the drone carries — usually a camera (Module 19) |

---

## What is a UAS?

- Definition of UAS
- Components: UAV, ground control, communication links
- Civilian and military applications
- Rapid growth in usage
- Increasing complexity
 
<img src="../img/Spot+with+Sparrow+.jpg" style="float: right; width: 500px; margin-left: 20px; margin-top: -200px;">



---
## UAS Cybersecurity Overview

- Unique cyber risks for UAS
- Integration of IT and OT systems
- High-value targets
- Potential for remote attacks
- Need for robust security

<img src="../img/Man-In-The-Middle-Attack-On-Drone-32.png" style="float: right; width: 500px; margin-left: 20px; margin-top: -200px;">


## Threat Landscape

These are the five attack families you will actually perform this week. Each one maps to specific labs — so this slide is really a table of contents for the hands-on work.

### Eavesdropping
- Intercepting unencrypted telemetry, video feeds, or RC commands
- Passive capture with SDR hardware (RTL-SDR, HackRF One)
- Reveals flight paths, operator locations, payload data

### GPS Spoofing
- Feeding false GPS signals to the drone's GNSS receiver
- Causes the drone to fly to unintended locations or return to a false home
- Cheap SDR hardware can generate spoofed signals

### Command Hijacking (C2 Takeover)
- Injecting unauthorized MAVLink or RC commands
- Requires access to the control channel
- Can force landing, RTL, or custom waypoints

### Data Theft
- Exfiltrating flight logs, mission plans, camera footage
- Often accomplished via GCS network access or physical access to SD cards

### Denial of Service (DoS)
- RF jamming of control link or GPS
- Network flooding of GCS WiFi
- Forces drone into failsafe behavior (hover, RTL, land)

> **Where you'll do each one:** Eavesdropping → Modules 12, 16, 18, 20. GPS spoofing → Module 13. Command hijacking → Modules 6, 10, 18. Data theft → Modules 4, 8, 22. DoS/jamming is discussed but not performed (it is illegal to transmit interference outside a shielded lab).

---

## Attack Vectors

| Vector | Method |
|--------|--------|
| Wireless interception | Passive SDR capture of unencrypted RF |
| Network attacks | Access to GCS WiFi network, then web/SSH exploitation |
| Malware | Malicious firmware or GCS application |
| Physical access | Direct UART/USB access to flight controller or GCS |
| Insider threat | Operator with malicious intent |
| Supply chain | Compromised firmware from manufacturer or update server |

---

## Security Principles: CIA+

<img src="../img/nist-cia-triad.png" style="float: right; width: 30%; margin-left: 18px;">

Security professionals judge every system against a short checklist. Learn it once and you can reason about *any* drone link. The classic core is the **CIA triad** (Confidentiality, Integrity, Availability); for drones we add **Authenticity** and **Non-repudiation**.

**Confidentiality** – Only authorized parties can read data
*Drone example:* video and telemetry should not be readable by a stranger with an antenna.

**Integrity** – Data has not been modified in transit
*Drone example:* a mission upload should arrive exactly as sent — no injected waypoints.

**Availability** – Systems and data are accessible when needed
*Drone example:* jamming the control link breaks availability and forces a failsafe.

**Authenticity** – The source of data or commands is verified
*Drone example:* the drone should reject a command that did not come from *its* GCS.

**Non-repudiation** – Actions cannot be denied after the fact
*Drone example:* signed logs prove which GCS armed the drone and when.

> All five properties apply to UAS. A drone that cannot verify command **authenticity** is vulnerable to spoofing (Modules 13, 17). A drone with no **integrity** checking on firmware updates is vulnerable to implants (Module 4). As you go through the labs, name which of these five properties each attack breaks.

---

## Authentication & Access Control

- Default credentials on GCS web interfaces (admin/admin, root/root)
- Lack of mutual authentication between drone and GCS
- Unprotected MAVLink endpoints (no system ID enforcement)
- Bluetooth or WiFi pairing with no PIN or certificate

**Best practices:**
- Strong user authentication
- Role-based access control
- Multi-factor authentication
- Secure credential storage
- Regular access reviews
- Zero Trust

---
## Data Protection

- Data at rest
- Data in transit
- Secure data storage
- Data minimization
- Regular data backups

---
## Communication Security

### Telemetry (SiK Radio, 433/915 MHz)
- Optional AES-128 encryption via NET ID parameter
- Most deployments leave encryption unconfigured
- Vulnerable to passive eavesdropping and replay

### RC Control
- Older protocols (PWM, PPM, SBUS) have no encryption
- DSM2/DSMX vulnerable to replay and brute-force
- FrSky and newer protocols offer binding but limited authentication

### WiFi (GCS Links)
- Often WPA2-PSK with weak or default passphrases
- Narrow channel bandwidth technique can crack WPA2 handshakes
- Unencrypted HTTP management interfaces common

---

## Software & Firmware Security

- Firmware images often unsigned — no verification before flashing
- Over-the-air updates frequently unencrypted and unauthenticated
- Embedded Linux systems with no hardening (open ports, root login, no firewall)
- Android GCS applications leak credentials, API keys, or hardcoded endpoints

**Key technique:** Binwalk for firmware extraction and analysis

---

## Physical Security

- UART debug ports left accessible on production hardware
- JTAG/SWD debug interfaces enabled
- SD card accessible without authentication
- USB interfaces expose ADB, MSC, or serial console

---

## Regulatory & Framework Landscape

| Framework | Scope |
|-----------|-------|
| FAA Part 107 | US commercial UAS operations |
| FAA Part 89 | Remote ID requirements |
| NIST CSF | Risk-based cybersecurity framework |
| NIST SP 800-53 | Security controls catalog |
| ISO/IEC 27001 | Information security management |
| ETSI EN 303 645 | Consumer IoT device security |
| ENISA IoT Baseline | IoT security recommendations |

---

## Risk Assessment Process

1. **Identify** assets and systems in scope
2. **Assess** threats and vulnerabilities
3. **Determine** likelihood and impact
4. **Prioritize** risks by severity
5. **Mitigate** through controls and configuration
6. **Monitor** continuously for new threats

---

## Incident Response for UAS

When a UAS security incident occurs:

1. **Detect** — identify anomalous behavior (unexpected flight path, loss of link)
2. **Contain** — land the drone safely, isolate the GCS network
3. **Analyze** — review flight logs, telemetry, and GCS logs
4. **Remediate** — patch vulnerability, change credentials, update firmware
5. **Report** — document findings and lessons learned

---
## Case Study: GPS Spoofing Attack

- Attacker transmits fake GPS signals
- UAV receives incorrect location data
- UAV deviates from intended path
- Potential for loss or hijack
- Mitigation: multi-sensor navigation

<img src="../img/GPS-spoofing-attack-on-GPS-Enabled-Drone-36.png" style="float: right; width: 500px; margin-left: 20px; margin-top: -200px;">


---

## Case Study: Command Hijacking

- Attacker intercepts control link
- Sends unauthorized commands
- UAV performs unintended actions
- Risk of crash or theft
- Mitigation: encrypted control links

<img src="../img/Man-In-The-Middle-Attack-On-Drone-32.png" style="float: right; width: 500px; margin-left: 20px; margin-top: -200px;">

---

## Future Trends

- AI-driven threat detection
- Quantum-resistant encryption
- Autonomous security responses
- Integration with 5G networks
- Increased regulatory oversight

<img src="../img/drone-swarm-blue-skies.webp" style="float: right; width: 500px; margin-left: 20px; margin-top: -200px;">

---

## UAS Cybersecurity Challenges

- Rapid technology evolution
- Resource constraints on UAVs
- Diverse operating environments
- Balancing usability and security
- Global regulatory differences

---

## UAS Cybersecurity Opportunities

- Innovation in secure design
- Collaboration across industries
- Standardization efforts
- Advanced threat intelligence
- Public-private partnerships
---
## Key Takeaways

- UAS are complex systems with a wide attack surface spanning air, ground, and RF
- Most vulnerabilities stem from missing or misconfigured security controls, not novel exploits
- Encryption, authentication, and firmware integrity are the most impactful controls
- Operators and manufacturers share responsibility for secure operation
