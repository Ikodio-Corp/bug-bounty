#!/bin/bash

# Start IKODIO BugBounty on Server
# Server: 192.168.100.6:7420

echo "🚀 Starting IKODIO BugBounty on Server..."
echo ""

sshpass -p 'Mi252512@' ssh -p 7420 ikodioxlapo@192.168.100.6 << 'ENDSSH'
cd /home/ikodioxlapo/ikodio-bugbounty

echo "Starting Backend (Port 8000)..."
cd backend
nohup venv/bin/python3 start_simple.py > backend.log 2>&1 &
echo $! > backend.pid
echo "✓ Backend started (PID: $(cat backend.pid))"

echo ""
echo "Starting Frontend (Port 3000)..."
cd ../frontend
nohup npm start > frontend.log 2>&1 &
echo $! > frontend.pid
echo "✓ Frontend started (PID: $(cat frontend.pid))"

echo ""
echo "========================================="
echo "   ✅ Services Started Successfully!"
echo "========================================="
echo ""
echo "Access:"
echo "  Frontend: http://192.168.100.6:3000"
echo "  Backend:  http://192.168.100.6:8000"
echo "  API Docs: http://192.168.100.6:8000/api/docs"
echo ""
echo "View logs:"
echo "  Backend:  tail -f ~/ikodio-bugbounty/backend/backend.log"
echo "  Frontend: tail -f ~/ikodio-bugbounty/frontend/frontend.log"
echo ""

ENDSSH

echo "✅ Done!"
