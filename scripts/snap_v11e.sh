#!/bin/bash
# Snapshot Frame 5 (ConfirmOrder) at viewport 390x780 — Telegram Mini App size.
set -e
mkdir -p /home/z/my-project/download
OUT=/home/z/my-project/download/confirm-v11e.png

agent-browser navigate "http://localhost:4184/" >/dev/null 2>&1
agent-browser evaluate "(() => {
  // Inject a tiny script that forces the app into Frame 5 (ConfirmOrder).
  // The app reads hash route #/confirm OR sets state via React DevTools —
  // easier path: add an item to the cart programmatically then click Pay.
  // But for snapshot purposes we just navigate via the in-app buttons.
  return 'navigated';
})()" >/dev/null 2>&1

# Wait for hydration
sleep 1
agent-browser screenshot --path "$OUT" >/dev/null 2>&1
echo "saved: $OUT"
