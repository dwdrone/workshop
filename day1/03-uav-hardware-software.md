# UAV Hardware, Software & Cybersecurity

**Type:** Presentation
**Duration:** 60 minutes
**Section:** Day 1 – UAV & Drone

---

## Objectives

- Identify the major hardware components of a consumer/prosumer UAV
- Understand the software stack running on each component
- Map hardware and software components to cybersecurity considerations

---

## UAS Overview

A UAS is not a single device — it is a **system of systems**. Think of it like a tiny aircraft *and* a tiny data center that happen to fly together.

**Why this matters for security:** each box below is a separate little computer or radio, often made by a different vendor, talking over a bus with no passwords. An attacker only has to win *one* of them. As we walk through the ten subsystems, keep asking three questions:

1. **What does it talk to?** (its interfaces = its attack surface)
2. **Is that conversation encrypted or authenticated?** (usually: no)
3. **What happens if I lie to it?** (spoofing, injection, DoS)

<img src="../img/holybro-uav-diagram.jpg" style="width: 68%; height: auto;" align="center">

*A typical autopilot wiring diagram — every labeled wire is a bus or link an attacker could tap. Keep this "map" in mind for the rest of the day.*


| ID | Subsystem Name | ID | Subsystem Name|
| :-- | :--- | :-- |---: |
| 1 | **Flight Computer** | 6 | **RC Receiver** |
| 2 | **Companion Computer** | 7 | **IMU (Inertial Measurement Unit)** |
| 3 | **Motors & ESC** | 8 | **GPS/GNSS Receiver** |
| 4 | **Power Distribution Board** | 9 | **ADS-B Receiver/Transmitter** |
| 5 | **Telemetry Radios** | 10 | **Camera / Gimbal** |


---

## 1. Flight Controller (Autopilot)

The **flight controller (FC)** is the brain of the drone. It stabilizes the aircraft, interprets RC commands, executes missions, and communicates with the GCS.
<img src="../img/3dr-cube-ventral.jpeg" style="float: right; width: 400px; margin-left: 20px;">

## Flight Controller Common Firmware:

| Firmware | Description |
|----------|-------------|
| **ArduPilot** | Open source, broad hardware support, large community |
| **PX4** | Open source, professional/commercial focus |
| **DJI Naza** | Proprietary, DJI drones |
| **Betaflight** | Open source, racing and freestyle FPV |

**Hardware platforms:** Pixhawk, Cube Orange, Holybro, MatekSys, SpeedyBee

**OS:** RTOS (NuttX for PX4/ArduPilot on bare metal) or Linux (ArduPilot on Linux)

---

## Flight Computer (Cybersecurity)
- Parameters stored in EEPROM — readable/writable via MAVLink with no authentication
- Serial console often accessible via UART with root-equivalent access
- No secure boot on most commercial flight controllers
- Firmware update via USB with no signature verification

---

## 2. Companion Computer

Many advanced drones pair the flight controller with a **companion computer** for higher-level processing.
<img src="../img/3dr-solo-imx6-dorsal.png" style="float: right; width: 500px; margin-left: 20px;">

## Companion Computer Examples:
- 3DR Solo: Freescale iMX6 (ARM Cortex-A9), runs Linux Yocto
- DJI Manifold: NVIDIA Jetson
- Generic: Raspberry Pi, NVIDIA Jetson Nano, Intel NUC

### Responsibilities:
- Payload processing (computer vision, object tracking)
- Advanced mission logic
- Telemetry forwarding between flight controller and GCS
- Running companion apps and scripts

---

## Companion Computer Cybersecurity:
- Full Linux environment — all Linux attack surface applies
- Often has SSH enabled with weak or default credentials
- WiFi access point hosted by companion computer
- Accessible from GCS network

---

## 3. Motors & ESC

**Brushless DC (BLDC) motors** are standard for consumer and commercial drones.

**Beginner note:** a brushless motor cannot be driven by plain battery voltage — it needs its three coils energized in a precise, fast sequence. The **ESC** is the little controller that does that sequencing. The flight controller doesn't move the motor directly; it just tells each ESC "spin this fast," thousands of times per second.

<img src="../img/3dr-solo-esc.jpg" style="float: right; width: 34%; margin-left: 18px;">

**How the FC talks to the ESC:** the classic method is a **PWM** pulse (1000 µs = stop, 2000 µs = full throttle). Newer digital protocols — **DShot**, **BLHeli** — send exact numeric values and can even read RPM back. That two-way BLHeli link is convenient for tuning but is also how an attacker could **reflash the ESC firmware** through the flight controller.

<img src="../img/uav-motor-annotated.jpeg" style="float: right; width: 500px; margin-left: 20px;">

## ESC (Electronic Speed Controller):
- Converts DC power to 3-phase AC for the BLDC motor
- Receives PWM or DSHOT signal from flight controller
- Can be programmed via BLHeliSuite over USB or signal wire
- BLHeli32 supports firmware updates over the air via the flight controller

---

## ESC Cybersecurity:

- ESC firmware can be modified to alter motor behavior
- BLHeli passthrough allows reprogramming ESCs through the flight controller
- DoS: corrupted ESC signal causes motor failure in flight

---

## 4. Power Distribution Board & BEC

**PDB (Power Distribution Board):**
- Routes battery power to motors, ESC, and other components
- Some PDBs include a built-in voltage regulator

**BEC (Battery Eliminator Circuit):**
- Steps down battery voltage (11.1V / 14.8V) to regulated 5V or 12V
- Powers flight controller, servos, and accessories

<img src="../img/uav-pdu-amazon.jpeg" style="float: right; width: 300px; margin-left: 20px;">

## PDB Cybersecurity:
- Physical: access to power rails allows hardware implant
- Shared power bus means a shorted component can affect all subsystems

---

## 5. Telemetry Radio

<img src="../img/3dr-sik-telemetry-radio.png" style="float: right; width: 30%; margin-left: 18px;">

The telemetry radio is the drone's **live data link back to the operator** — battery, GPS, attitude, and the channel a GCS uses to send commands. It is separate from the RC control link. We spend all of Module 15–16 on these.

**SiK Radios (RFDesign, HolyBro, 3DR):**
- 433 MHz (EU/Asia) or 915 MHz (USA)
- 250 mW typical output
- Bidirectional: carries MAVLink from drone to GCS
- Parameters: NET ID, AIR SPEED, DUTY CYCLE, ECC

## Telemetry Radio Cybersecurity:
- AES-128 encryption available but rarely configured
- Default NET ID (25) means any SiK radio can receive traffic
- Passive capture with HackRF or RTL-SDR
- Replay of captured MAVLink frames

---

## 6. RC Receiver

**RC protocols:**

| Protocol | Description |
|----------|-------------|
| **PWM** | One wire per channel, no feedback, analog |
| **PPM** | All channels on one wire, sequential pulses |
| **SBUS** | Frsky/Futaba serial protocol, inverted UART |
| **DSM2/DSMX** | Spektrum 2.4 GHz spread spectrum |
| **CRSF** | ExpressLRS/TBS Crossfire, bidirectional, encrypted |

## RC Cybersecurity:
- Older protocols (PWM, PPM, SBUS) have no authentication or encryption
- DSM2 vulnerable to replay attack: capture bind sequence, replay to take over
- DSMX: harder but still documented vulnerabilities
- RC jamming forces failsafe behavior (RTL, land, or hover)

---

## 7. IMU (Inertial Measurement Unit)

The IMU is the drone's **sense of balance** — the equivalent of your inner ear. Without it, the aircraft cannot tell which way is up and falls out of the sky. It is a cluster of tiny sensors that measure the drone's physical state hundreds of times per second:

<img src="../img/rpi-imu-axis.png" style="float: right; width: 32%; margin-left: 18px;">

**The three axes** you'll see everywhere: **roll** (tilt left/right), **pitch** (nose up/down), and **yaw** (spin left/right). The accelerometer and gyroscope each measure all three. These are **MEMS** chips — microscopic mechanical structures on silicon — which is exactly why they can be disturbed by loud sound or vibration at their resonant frequency (acoustic injection).

- **Accelerometers** – measure linear acceleration (3 axes)
- **Gyroscopes** – measure angular velocity (3 axes)
- **Magnetometer/Compass** – measure magnetic heading (3 axes)
- **Barometer** – measure altitude by air pressure

**Common IMU chips:** ICM-42688-P, ICM-20689, MPU-6000, MS5611

## IMU Cybersecurity:
- Sensor spoofing: acoustic injection (laser or sound waves at resonant frequency)
- Magnetic spoofing: external magnetic field corrupts heading
- Barometric spoofing: localized pressure changes (rare but demonstrated)

---

## 8. GPS / GNSS Receiver

Provides absolute position (latitude, longitude, altitude) and time.

**GPS vs. GNSS:** *GPS* is the American satellite system specifically; *GNSS* is the umbrella term for all of them (GPS, GLONASS, Galileo, BeiDou). Modern receivers listen to several at once for a better fix. The receiver works by timing how long signals take to arrive from 4+ satellites — which is exactly why it can be fooled: the signals are faint, unencrypted, and carry no proof of who sent them (Module 13).

<img src="../img/3dr-solo-gps.png" style="float: right; width: 34%; margin-left: 18px;">

**On the 3DR Solo** the GPS is a **u-blox NEO-7** module on its own little board with a patch antenna facing the sky. It outputs position over a serial link in the **NMEA** and **UBX** formats (Module 13). Because it needs a clear view of the sky, its signal is weak and easily overpowered by a ground-based spoofer.

**Satellite constellations:**
- GPS (US) – L1: 1575.42 MHz
- GLONASS (Russia)
- BeiDou (China)
- Galileo (EU)

**Common receivers:**
- u-blox NEO-7N (3DR Solo)
- u-blox M8/M9/F9 series


## GNSS Cybersecurity:
- GPS signals are unencrypted and unauthenticated — anyone can spoof them
- GPS spoofing demonstrated against DJI, commercial, and military drones
- Inertial navigation (dead reckoning) as fallback is limited

---

## 9. ADS-B/ Remote ID

**Automatic Dependent Surveillance-Broadcast (ADS-B):**
- 1090 MHz
- Broadcasts: ICAO address, position, altitude, velocity, callsign
- Standard in manned aviation; increasingly required for UAV

**ADS-B In** (receive only): drone listens for nearby aircraft, avoids collision
**ADS-B Out** (transmit): drone broadcasts its own position

## ADSB Cybersecurity:
- ADS-B is unauthenticated — trivially spoofable
- False aircraft injection causes GCS/autopilot alerts
- Suppression of own signal causes detection gap

---

## 10. Camera & Gimbal

<img src="../img/gopro-hero4.png" style="float: right; width: 30%; margin-left: 18px;">

**Camera types:**
- GoPro (WiFi-enabled, HTTP API — the 3DR Solo uses a Hero 4)
- DJI integrated cameras
- Thermal / multispectral sensors
- FPV cameras (analog or digital)

The camera is usually the whole *reason* the drone exists — and on the Solo it is a stock GoPro with an open WiFi HTTP API we will drive by hand in Labs 10 and 19.

**Gimbal:**
- 2-axis or 3-axis stabilization
- Controlled via MAVLink or dedicated serial protocol
- Some support pan/tilt from GCS

## Camera Cybersecurity:
- GoPro WiFi exposes HTTP API (port 80) — no authentication on older models
- Analog video downlink is unencrypted and eavesdroppable
- Digital video streams (RTP/RTSP) often unencrypted on local WiFi

---

## Assessment Summary by Component

| Component | Key Vulnerabilities |
|-----------|---------------------|
| Flight controller | UART shell, unsigned firmware, unauthenticated MAVLink |
| Companion computer | SSH default creds, open ports, no hardening |
| RC receiver | No encryption (PWM/PPM/SBUS), DSM2 replay |
| Telemetry radio | Unencrypted by default, global NET ID |
| GPS | Spoofable — unencrypted satellite signals |
| GoPro / camera | Unauthenticated HTTP API, unencrypted video |
| ESC | BLHeli passthrough, firmware modification |
