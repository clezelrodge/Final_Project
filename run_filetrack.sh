#!/bin/zsh

cd "/Users/glazyindon/Downloads/Project 2" || exit 1

PORT="${FILETRACK_PORT:-5001}"

echo "Starting FileTrack from Project 2..."
echo ""

old_server_pids=$(lsof -tiTCP:$PORT -sTCP:LISTEN 2>/dev/null)
if [ -n "$old_server_pids" ]; then
  echo "Stopping old FileTrack server on port $PORT..."
  kill $old_server_pids 2>/dev/null
  sleep 1
fi

echo "Checking database..."
.venv/bin/python setup_db.py

echo ""
echo "FileTrack Website Link:"
echo "http://127.0.0.1:$PORT/login"
echo ""
echo "For ESP32 integration, use your Mac IP with:"
echo "http://YOUR_MAC_IP:$PORT/api/hardware/scan"
echo ""
echo "Login accounts:"
echo "Admin: admin / 12345"
echo "User:  user  / 123"
echo ""

.venv/bin/python app.py
