#!/bin/bash
# Keep the vite preview server alive on port 3000.
# Restarts it if it dies. Logs to /home/z/my-project/logs/preview-watchdog.log.

cd /home/z/my-project/cafe-miniapp

LOG=/home/z/my-project/logs/vite-preview.log
WATCHDOG_LOG=/home/z/my-project/logs/preview-watchdog.log

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] watchdog started" >> "$WATCHDOG_LOG"

while true; do
  # Check if port 3000 is listening
  if ! ss -tlnp 2>/dev/null | grep -q ':3000'; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] port 3000 not listening — starting vite preview" >> "$WATCHDOG_LOG"

    # Make sure node_modules exists; reinstall if wiped
    if [ ! -x node_modules/.bin/vite ]; then
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] node_modules missing — running npm install" >> "$WATCHDOG_LOG"
      npm install --no-audit --no-fund >> "$WATCHDOG_LOG" 2>&1
    fi

    # Make sure dist exists; rebuild if wiped
    if [ ! -f dist/index.html ]; then
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] dist missing — running vite build" >> "$WATCHDOG_LOG"
      node_modules/.bin/vite build >> "$WATCHDOG_LOG" 2>&1
    fi

    # Start vite preview fully detached
    nohup node_modules/.bin/vite preview --host --port 3000 \
      > "$LOG" 2>&1 < /dev/null &
    PREVIEW_PID=$!
    disown $PREVIEW_PID 2>/dev/null
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] started vite preview pid=$PREVIEW_PID" >> "$WATCHDOG_LOG"

    # Give it a moment to bind
    sleep 3
  fi

  # Sleep before next check
  sleep 10
done
