from pymavlink import mavutil
import time

conn = mavutil.mavlink_connection('udp:10.1.1.10:14550')
conn.wait_heartbeat()
print("Connected")

# Request all parameters
conn.mav.param_request_list_send(conn.target_system, conn.target_component)

params = {}
while True:
    msg = conn.recv_match(type='PARAM_VALUE', blocking=True, timeout=5)
    if msg is None:
        break
    params[msg.param_id] = msg.param_value
    print(f"{msg.param_id}: {msg.param_value}")

print(f"\nTotal parameters received: {len(params)}")

# Show security-relevant parameters
security_params = ['ARMING_CHECK', 'FS_THR_ENABLE', 'FS_GCS_ENABLE',
                   'FENCE_ENABLE', 'SYSID_THISMAV', 'BRD_SAFETYENABLE']
print("\n--- Security-relevant parameters ---")
for p in security_params:
    if p in params:
        print(f"{p}: {params[p]}")