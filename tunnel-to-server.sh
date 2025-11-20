#!/bin/bash
# SSH Tunnel untuk akses IKODIO BugBounty dari Mac
# Jalankan script ini, lalu akses via localhost

echo "🚇 Creating SSH Tunnel to Production Server..."
echo ""
echo "Setelah tunnel terbentuk, akses via:"
echo "  Frontend: http://localhost:3003"
echo "  Backend:  http://localhost:8001"
echo ""
echo "Press Ctrl+C untuk stop tunnel"
echo ""

# Forward port 3003 (frontend) dan 8001 (backend)
sshpass -p 'Mi252512@' ssh -p 7420 \
  -L 3003:localhost:3003 \
  -L 8001:localhost:8001 \
  -N ikodioxlapo@192.168.100.6
