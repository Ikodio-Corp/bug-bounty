#!/bin/bash
# Restart backend script

# Kill all uvicorn processes
pkill -9 -f "python.*uvicorn.*main:app"

# Wait
sleep 2

# Go to backend directory
cd ~/ikodio-bugbounty/backend

# Activate venv and start
source venv/bin/activate

# Start backend in background
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8002 > /tmp/backend_restart.log 2>&1 &

# Wait for startup
sleep 3

# Test
curl -s http://localhost:8002/ | head -1

echo "Backend restarted"
