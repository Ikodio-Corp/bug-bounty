"use client";

import { motion } from 'framer-motion';
import { Pause, Eye, X, Play, Activity } from 'lucide-react';
import { useState } from 'react';

interface ScanStatus {
  id: string;
  target: string;
  url: string;
  status: 'running' | 'paused' | 'completed';
  progress: number;
  startedAt: string;
  findings: number;
}

const statusColors = {
  running: { text: 'text-blue-400', bg: 'bg-blue-400', label: 'RUNNING' },
  paused: { text: 'text-orange-400', bg: 'bg-orange-400', label: 'PAUSED' },
  completed: { text: 'text-emerald-400', bg: 'bg-emerald-400', label: 'COMPLETED' },
};

function ProgressBar({ progress, status }: { progress: number; status: ScanStatus['status'] }) {
  const colors = statusColors[status];

  return (
    <div className="w-24">
      <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
        <motion.div
          className={`h-full ${colors.bg}`}
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
      </div>
      <div className="text-xs text-slate-400 mt-1 text-right tabular-nums">
        {progress}%
      </div>
    </div>
  );
}

function ScanItem({ scan }: { scan: ScanStatus }) {
  const [isPaused, setIsPaused] = useState(scan.status === 'paused');
  const colors = statusColors[scan.status];

  return (
    <motion.div
      className="flex items-center gap-4 p-4 rounded-lg border border-slate-800/80 bg-slate-900/40 hover:border-slate-700/80 transition-all duration-200"
      whileHover={{ x: 2 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
    >
      <div className="flex items-center gap-3 min-w-0 flex-1">
        <div className={`w-2 h-2 rounded-full ${colors.bg} ${scan.status === 'running' ? 'animate-pulse' : ''}`} />
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="text-sm font-medium text-slate-200 truncate">
              {scan.target}
            </h4>
            <span className={`text-[10px] font-semibold ${colors.text} uppercase tracking-wider`}>
              {colors.label}
            </span>
          </div>
          <p className="text-xs font-mono text-slate-500 truncate">
            {scan.url}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-4 text-xs text-slate-400 flex-shrink-0">
        <span className="tabular-nums">{scan.startedAt}</span>
        <span>|</span>
        <span className="text-slate-300 font-medium">{scan.findings} findings</span>
      </div>

      <ProgressBar progress={scan.progress} status={scan.status} />

      <div className="flex items-center gap-1 flex-shrink-0">
        <motion.button
          className="p-2 rounded-md hover:bg-slate-800/80 text-slate-400 hover:text-slate-200 transition-colors"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsPaused(!isPaused)}
          title={isPaused ? 'Resume' : 'Pause'}
        >
          {isPaused ? <Play size={14} /> : <Pause size={14} />}
        </motion.button>
        <motion.button
          className="p-2 rounded-md hover:bg-slate-800/80 text-slate-400 hover:text-slate-200 transition-colors"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          title="View Details"
        >
          <Eye size={14} />
        </motion.button>
        <motion.button
          className="p-2 rounded-md hover:bg-red-500/10 text-slate-400 hover:text-red-400 transition-colors"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          title="Stop Scan"
        >
          <X size={14} />
        </motion.button>
      </div>
    </motion.div>
  );
}

export function RefinedActiveScans() {
  const scans: ScanStatus[] = [
    {
      id: '1',
      target: 'E-commerce Platform',
      url: 'https://shop.example.com',
      status: 'running',
      progress: 67,
      startedAt: '2h 34m',
      findings: 12,
    },
    {
      id: '2',
      target: 'Banking Portal',
      url: 'https://banking.acme.io',
      status: 'running',
      progress: 89,
      startedAt: '45m',
      findings: 3,
    },
    {
      id: '3',
      target: 'Healthcare API',
      url: 'https://api.health.org',
      status: 'completed',
      progress: 100,
      startedAt: '8h',
      findings: 24,
    },
  ];

  return (
    <div className="mb-6">
      <div className="flex items-center gap-2 mb-4">
        <Activity size={18} className="text-slate-400" />
        <h2 className="text-base font-semibold text-slate-200 uppercase tracking-wide">Active Security Scans</h2>
        <span className="text-xs text-slate-500 ml-auto">{scans.length} running</span>
      </div>
      
      <div className="space-y-2">
        {scans.map((scan) => (
          <ScanItem key={scan.id} scan={scan} />
        ))}
      </div>
    </div>
  );
}
