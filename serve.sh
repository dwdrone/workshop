#!/usr/bin/env bash
# Launch the Hack Our Drone local server (Kali / Linux / macOS).
# Usage: ./serve.sh            (then open the printed URL)
#        ./serve.sh --host 0.0.0.0   (share on the classroom LAN)
DIR="$(cd "$(dirname "$0")" && pwd)"
PY="$(command -v python3 || command -v python)"
if [ -z "$PY" ]; then
    echo "Python 3 not found. On Kali:  sudo apt install -y python3"
    exit 1
fi
exec "$PY" "$DIR/serve.py" "$@"
