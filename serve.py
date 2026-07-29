#!/usr/bin/env python3
"""
serve.py — Serve the Hack Our Drone slides & labs over a local web server.

Why not just double-click index.html?
    The slide pages reference images with paths like ../img/foo.png. Opening a
    file directly (file://) makes some browsers block those and other resources.
    Serving over http:// makes every link, image, and lab page resolve cleanly,
    exactly as it will in class.

Usage:
    python serve.py                 # serve on http://localhost:8000 and open the dashboard
    python serve.py --port 9000     # pick a different port
    python serve.py --host 0.0.0.0  # let other machines on the LAN view it (share the room)
    python serve.py --no-browser    # don't auto-open a browser

Requirements: Python 3 only (already installed on Kali). No internet needed to
run the server itself — but the slide decks pull reveal.js from a CDN, so the
presentation view still needs internet. The lab pages work fully offline.

Stop the server with Ctrl+C.
"""

import argparse
import http.server
import os
import socket
import sys
import webbrowser
from functools import partial

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LANDING = "/slides/index.html"  # the dashboard


class Handler(http.server.SimpleHTTPRequestHandler):
    """Serve the repo root, but send visitors to the dashboard by default."""

    def do_GET(self):
        # Bare root or /index.html -> redirect to the slide dashboard
        if self.path in ("/", "/index.html", "/slides", "/slides/"):
            self.send_response(302)
            self.send_header("Location", LANDING)
            self.end_headers()
            return
        super().do_GET()

    def log_message(self, fmt, *args):
        # Quieter, friendlier logging; ignore favicon noise
        msg = fmt % args
        if "favicon.ico" in msg:
            return
        sys.stdout.write("  %s\n" % msg)


def find_free_port(host, start, attempts=20):
    """Return the first bindable port at or after `start`."""
    for port in range(start, start + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind((host, port))
                return port
            except OSError:
                continue
    return None


def lan_ip():
    """Best-effort local network IP (no traffic actually sent)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Serve the Hack Our Drone slides & labs locally.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--host", default="127.0.0.1",
                        help="Interface to bind. Use 0.0.0.0 to share on the LAN "
                             "(default: 127.0.0.1, this machine only).")
    parser.add_argument("--port", type=int, default=8000,
                        help="Preferred port (default: 8000; auto-increments if busy).")
    parser.add_argument("--no-browser", action="store_true",
                        help="Do not automatically open a browser.")
    args = parser.parse_args()

    if not os.path.isfile(os.path.join(BASE_DIR, "slides", "index.html")):
        print("[ERROR] Could not find slides/index.html next to this script.")
        print("        Run serve.py from the workshop folder, and build the")
        print("        slides first with:  python build_slides.py")
        sys.exit(1)

    port = find_free_port(args.host, args.port)
    if port is None:
        print(f"[ERROR] No free port found near {args.port}. Try --port <N>.")
        sys.exit(1)

    os.chdir(BASE_DIR)
    handler = partial(Handler, directory=BASE_DIR)
    httpd = http.server.ThreadingHTTPServer((args.host, port), handler)

    local_url = f"http://localhost:{port}{LANDING}"

    print("=" * 60)
    print("  Hack Our Drone — local server running")
    print("=" * 60)
    print(f"  Dashboard:  {local_url}")
    if args.host == "0.0.0.0":
        ip = lan_ip()
        if ip:
            print(f"  On the LAN: http://{ip}:{port}{LANDING}")
            print("  (other students on the same network can open that link)")
    print()
    print("  Press Ctrl+C to stop.")
    print("=" * 60)

    if not args.no_browser:
        try:
            webbrowser.open(local_url)
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down. See you in class.")
        httpd.shutdown()


if __name__ == "__main__":
    main()
