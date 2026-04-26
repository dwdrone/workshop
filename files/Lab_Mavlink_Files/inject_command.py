from pymavlink import mavutil
import time

# Connect to the drone
conn = mavutil.mavlink_connection('udp:10.1.1.10:14550')

# Wait for heartbeat to get target sysid/compid
print("Waiting for heartbeat...")
conn.wait_heartbeat()
print(f"Connected: system {conn.target_system}, component {conn.target_component}")

# --- Safe commands for lab use (drone disarmed, no props) ---

# Request autopilot version info (completely safe)
conn.mav.command_long_send(
    conn.target_system,
    conn.target_component,
    mavutil.mavlink.MAV_CMD_REQUEST_AUTOPILOT_CAPABILITIES,
    0,    # confirmation
    1, 0, 0, 0, 0, 0, 0
)

# Wait for response
msg = conn.recv_match(type='AUTOPILOT_VERSION', blocking=True, timeout=5)
if msg:
    print(f"Firmware version: {msg.flight_sw_version}")
    print(f"Middleware version: {msg.middleware_sw_version}")
    print(f"OS version: {msg.os_sw_version}")
    print(f"Board version: {msg.board_version}")

# Request all data streams (will generate a burst of telemetry)
conn.mav.request_data_stream_send(
    conn.target_system,
    conn.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_ALL,
    4,   # 4 Hz
    1    # start
)

time.sleep(3)

# Read a few messages
for i in range(20):
    msg = conn.recv_match(blocking=True, timeout=1)
    if msg:
        print(f"MSG: {msg.get_type()}")

print("Done.")
