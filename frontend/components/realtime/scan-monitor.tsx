'use client';

import { useWebSocket } from '@/lib/hooks/useWebSocket';
import { SimpleBadge } from '@/components/ui/simple-badge';
import { useEffect, useState } from 'react';

interface ScanProgress {
  scan_id: number;
  target_url: string;
  progress: number;
  status: string;
  findings_count: number;
  current_phase: string;
}

export function LiveScanMonitor({ scanId }: { scanId: number }) {
  const [scanProgress, setScanProgress] = useState<ScanProgress | null>(null);
  
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';
  
  const { isConnected, lastMessage, sendMessage } = useWebSocket(wsUrl, {
    onMessage: (data) => {
      if (data.type === 'scan_progress' && data.scan_id === scanId) {
        setScanProgress(data);
      }
    },
    onOpen: () => {
      // Subscribe to scan updates
      sendMessage({
        type: 'subscribe',
        channel: `scan:${scanId}`,
      });
    },
  });

  if (!scanProgress) {
    return (
      <div className="text-center py-4 text-gray-500">
        Waiting for scan data...
      </div>
    );
  }

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Live Scan Progress</h3>
        <SimpleBadge variant={isConnected ? 'success' : 'error'}>
          {isConnected ? 'Live' : 'Disconnected'}
        </SimpleBadge>
      </div>

      <div className="space-y-3">
        <div>
          <p className="text-sm text-gray-400 mb-1">Target</p>
          <p className="font-medium">{scanProgress.target_url}</p>
        </div>

        <div>
          <p className="text-sm text-gray-400 mb-1">Current Phase</p>
          <p className="font-medium text-gray-400">{scanProgress.current_phase}</p>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-400">Progress</span>
            <span className="font-medium">{scanProgress.progress}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className="bg-white h-2 rounded-full transition-all duration-500"
              style={{ width: `${scanProgress.progress}%` }}
            ></div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-400">Status</p>
            <p className="font-medium">{scanProgress.status}</p>
          </div>
          <div>
            <p className="text-sm text-gray-400">Findings</p>
            <p className="font-medium text-orange-400">{scanProgress.findings_count}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
