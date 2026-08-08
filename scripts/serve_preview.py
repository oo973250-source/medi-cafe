#!/usr/bin/env python3
"""
Stable preview server for the cafe-miniapp.
Uses Python's built-in http.server, serving the dist/ folder.
Daemonized with double-fork so it survives the bash session ending.
"""
import os, sys, time, subprocess, signal

ROOT = '/home/z/my-project/cafe-miniapp'
DIST = os.path.join(ROOT, 'dist')
PID_FILE = '/tmp/cafe_preview.pid'
LOG_FILE = '/home/z/my-project/logs/preview.log'
PORT = 3000

os.makedirs('/home/z/my-project/logs', exist_ok=True)

# Kill any existing server on this port
try:
    with open(PID_FILE, 'r') as f:
        old_pid = int(f.read().strip())
    os.kill(old_pid, signal.SIGTERM)
    time.sleep(0.5)
except (FileNotFoundError, ProcessLookupError, ValueError):
    pass

# Spawn a detached process
log_fp = open(LOG_FILE, 'w')
proc = subprocess.Popen(
    ['python3', '-m', 'http.server', str(PORT), '--directory', DIST],
    stdout=log_fp,
    stderr=log_fp,
    stdin=subprocess.DEVNULL,
    start_new_session=True,  # detach from controlling terminal
)

with open(PID_FILE, 'w') as f:
    f.write(str(proc.pid))

print(f"Preview server started: PID={proc.pid}, port={PORT}")
print(f"Serving: {DIST}")
print(f"Log: {LOG_FILE}")
print(f"URL: http://127.0.0.1:{PORT}/")
