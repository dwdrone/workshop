# UAS Cybersecurity Review

**Type:** Presentation
**Duration:** 45 minutes
**Section:** Day 2 – Payloads & Logging

---

## Objectives

- Review the full UAS assessment methodology (Recon → Exploitation → Reporting)
- Survey mitigation strategies for each vulnerability class encountered
- Understand applicable cybersecurity frameworks for UAS
- Know the components of a professional security assessment report

---

## Assessment Methodology: The Dark Wolf Drone Playbook

```
┌──────────────┐
│ Reconnaissance│
└──────┬───────┘
       │
┌──────▼───────┐
│   Mapping    │
└──────┬───────┘
       │
┌──────▼───────┐
│  Discovery   │
└──────┬───────┘
       │
┌──────▼───────┐
│ Exploitation │
└──────┬───────┘
       │
┌──────▼───────┐
│   Reporting  │
└──────────────┘
```

---

## Phase 1: Reconnaissance

**Goal:** Gather all publicly available information about the target UAS before touching it.

| Technique | Tools | What to Find |
|-----------|-------|-------------|
| Online research | Google, Archive.org | Firmware versions, known CVEs, user manuals |
| FCC ID lookup | fccid.io | Hardware internals, antenna specs, test reports |
| Social media | X, Facebook, 3DRpilots.com | Operator behavior, configuration tips, known issues |
| WHOIS / DNS | whois, nslookup | Manufacturer infrastructure |
| Shodan | shodan.io | Exposed GCS or drone management servers |
| GitHub recon | github.com | Source code, hardcoded credentials, API keys |
| Employee profiling | LinkedIn, Hunter.io | Key developers and their other projects |

**3DR Solo recon yield:**
- ArduCopter fork version from GitHub (opensolo/meta-3dr)
- FCC ID 2AC3P-800 reveals internal photos
- 3DRpilots forum reveals default credentials and SSH access

---

## Phase 2: Mapping

**Goal:** Enumerate all accessible interfaces, services, and software components.

| Target | Technique | Tool |
|--------|-----------|------|
| Network | Host and port scan | `nmap -sV -p- 10.1.1.0/24` |
| WiFi | Channel and client survey | `airodump-ng` |
| RF spectrum | Wideband spectrum scan | GQRX + HackRF |
| Firmware | Download + analyze | Binwalk, FAT |
| Android app | Extract + static analysis | ADB, Jadx, APKtool, AndroBugs |
| Physical | Hardware teardown | Logic analyzer, multimeter |
| UART | Serial console | minicom + TTL-USB adapter |

---

## Phase 3: Discovery

**Goal:** Identify specific vulnerabilities within each enumerated component.

| Component | Vulnerability Check | Tool |
|-----------|--------------------|----|
| Web interface | CVE scan, default creds | Nikto, Burp Suite |
| SSH | Default creds, weak algorithms | ssh-audit, Hydra |
| Filesystem | Encrypted? Password hashes? Keys? | grep, file, hashcat |
| MAVLink | Unauthenticated access | MAVProxy, Wireshark |
| Android APK | Hardcoded secrets, exported components | AndroBugs, Frida |
| SiK radio | Encryption enabled? NET ID? | minicom AT commands |
| RC link | Protocol version, encryption | URH, HackRF |
| GPS | Spoofable? | gps-sdr-sim (controlled environment) |

---

## Phase 4: Exploitation

**Goal:** Demonstrate exploitability and business impact.

| Finding | Exploit Technique | Impact |
|---------|-------------------|--------|
| Root SSH without password | `ssh root@10.1.1.10` | Full system compromise |
| Unauthenticated MAVLink | pymavlink COMMAND_LONG | Flight control takeover |
| Default WiFi PSK | aircrack-ng + rockyou | Network access |
| Unencrypted SiK | Second radio, matching NET ID | Eavesdropping, injection |
| GoPro HTTP API | `curl http://10.5.5.9/...` | Video access, recording control |
| Signed firmware absent | Modify firmware, re-flash | Persistence, custom behavior |
| Flight log access | SSH + scp | Operator location, flight history |

---

## Phase 5: Reporting

**Goal:** Document all findings clearly for both technical and executive audiences.

### Report Structure

1. **Executive Summary** — 1 page, non-technical, high-level risk
2. **Scope and Methodology** — what was tested, how, when
3. **Findings** — each vulnerability with full detail
4. **Recommendations** — prioritized remediation guidance
5. **Appendices** — raw evidence, tool output, screenshots

### Finding Template

```
Finding #: [Number]
Title: [Short, descriptive title]
Severity: Critical / High / Medium / Low / Informational
CVSS Score: [if applicable]

Description:
[Clear explanation of the vulnerability — what it is and how it was found]

Steps to Reproduce:
1. [Exact reproduction steps]
2. ...

Evidence:
[Screenshots, command output, packet captures]

Impact:
[What an attacker could do with this vulnerability]

Recommendation:
[Specific, actionable remediation guidance]

References:
[CVEs, vendor advisories, standards]
```

### Severity Rating Guide

| Severity | Criteria | Example |
|----------|----------|---------|
| Critical | Remote, unauthenticated, full compromise | Root SSH without password |
| High | Significant data exposure or control loss | Unauthenticated MAVLink |
| Medium | Limited exploitation, some conditions needed | Weak WiFi passphrase |
| Low | Minimal direct impact, defense in depth | Verbose error messages |
| Info | No security impact, best practice note | Missing X-Frame-Options header |

---

## Mitigation Strategies by Component

### Flight Controller
- Enable MAVLink v2 message signing
- Restrict accepted GCS system ID (`SYSID_MYGCS`)
- Disable debug serial ports in production firmware
- Implement secure boot and firmware signing

### Companion Computer
- Change default SSH credentials immediately
- Disable root SSH login; use key-based authentication only
- Enable UFW/iptables firewall on all interfaces
- Disable unused services (Telnet, FTP)
- Run services as least-privileged users

### SiK Telemetry Radio
- Enable AES-128 encryption with a unique key per deployment
- Change NET ID from the default (25) to a random value
- Enable MAVLink v2 and message signing end-to-end

### GCS Application
- Use HTTPS for all API calls
- Implement certificate pinning
- Do not log sensitive data
- Store credentials in Android Keystore, not SharedPreferences

### WiFi Link
- Use WPA3-SAE if available; WPA2 with strong random passphrase (16+ chars)
- Disable WPS
- Enable client isolation to prevent lateral movement
- Use a VPN tunnel between GCS and drone for additional layer

### GPS
- Use multi-constellation receivers (GPS + GLONASS + Galileo)
- Monitor for GPS consistency with IMU (detect sudden jumps)
- Wait for Galileo OSNMA authentication deployment

---

## Applicable Cybersecurity Frameworks

### NIST Cybersecurity Framework (CSF)

| Function | UAS Application |
|----------|----------------|
| **Identify** | Asset inventory, threat modeling, risk assessment |
| **Protect** | Encryption, authentication, firmware signing, access control |
| **Detect** | Telemetry monitoring, anomaly detection, IDS on GCS network |
| **Respond** | Failsafe procedures, incident response plan |
| **Recover** | Secure backup of configuration, failover GCS |

### ETSI EN 303 645 (Consumer IoT Security)

Key provisions applicable to UAS:
- No universal default passwords
- Implement vulnerability disclosure process
- Keep software updated
- Securely store sensitive security parameters
- Communicate securely (encrypt in transit)
- Minimize exposed attack surfaces
- Ensure software integrity (firmware signing)
- Validate input data

### AUVSI Trusted Cyber / Green UAS

The AUVSI (Association for Unmanned Vehicle Systems International) operates programs to certify UAS cybersecurity:
- **Trusted Cyber** — vendor self-attestation against a control framework
- **Green UAS** — independent verification of cybersecurity controls

Compliance with these programs is increasingly required for government and critical infrastructure drone contracts.

---

## Cybersecurity Maturity Model

Drone operators and manufacturers exist at different maturity levels:

| Level | Description | UAS Indicator |
|-------|-------------|--------------|
| 1 – Initial | Ad hoc, no formal processes | Default credentials unchanged |
| 2 – Managed | Repeatable processes, some controls | Password policies, basic network segmentation |
| 3 – Defined | Organization-wide documented processes | Security testing before deployment, change management |
| 4 – Quantitatively Managed | Metrics and measurement | Continuous monitoring, KPIs for patch latency |
| 5 – Optimizing | Continuous improvement | Bug bounty program, threat intelligence feeds |

---

## Course Wrap-Up: Key Takeaways

1. **UAS is an interconnected system** — compromise one component, gain access to others
2. **Default configurations are insecure** — every default credential and setting is a vulnerability
3. **RF links are the widest attack surface** — all links except GPS can be targeted passively
4. **MAVLink without signing is an open control plane** — anyone on the network can control the drone
5. **Logs are intelligence** — flight logs reveal the operator's location, behavior, and missions
6. **Frameworks provide structure** — NIST CSF, ETSI EN 303 645, and AUVSI Trusted Cyber provide a roadmap
7. **Responsible disclosure matters** — when you find vulnerabilities, report them to the manufacturer

---

## What Comes Next

- Practice: CTF competitions focused on IoT and embedded systems
- Community: DefCon Drone Village, AUVSI, 3DRPilots forums
- Certifications: OSCP, CEH, eWPT (pentesting), CompTIA Security+
- Research: Follow ArduPilot and PX4 security mailing lists
- Labs: Build a personal drone hacking lab with a cheap quad and RTL-SDR
