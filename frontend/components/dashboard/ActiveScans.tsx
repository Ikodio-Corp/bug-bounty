"use client";

import { motion } from 'framer-motion';
import { Search, Shield, CheckCircle, Clock, Plus, Play, Pause, Square } from 'lucide-react';
import { useState } from 'react';

interface Scan {
  id: string;
  name: string;
  url: string;
  status: 'scanning' | 'analyzing' | 'completed';
  progress: number;
  startedTime: string;
  findings: number;
  severity?: 'critical' | 'normal' | 'clean';
  icon: any;
  gradient: string;
}

const scansData: Scan[] = [
  {
    id: '1',
    name: 'E-commerce Platform API',
    url: 'shop.example.com/api',
    status: 'scanning',
    progress: 67,
    startedTime: '12 minutes ago',
    findings: 8,
    icon: Search,
    gradient: 'from-gray-400 to-gray-500',
  },
  {
    id: '2',
    name: 'Banking Application',
    url: 'secure.bank.com',
    status: 'analyzing',
    progress: 89,
    startedTime: '25 minutes ago',
    findings: 3,
    severity: 'critical',
    icon: Shield,
    gradient: 'from-red-500 to-red-600',
  },
  {
    id: '3',
    name: 'Healthcare Portal',
    url: 'patient.health.com',
    status: 'completed',
    progress: 100,
    startedTime: '1 hour ago',
    findings: 0,
    severity: 'clean',
    icon: CheckCircle,
    gradient: 'from-emerald-500 to-emerald-600',
  },
];

export function ActiveScans() {
  const [scans] = useState(scansData);

  return (
    <motion.section
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.8 }}
      className="dashboard-section mb-6 p-7 rounded-2xl border border-white/8 backdrop-blur-md"
      style={{
        background: 'rgba(30, 41, 59, 0.5)',
      }}
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-xl font-bold text-white mb-1">Active Scans</h2>
          <p className="text-sm text-white/50">
            Real-time monitoring of ongoing security scans
          </p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 text-sm font-semibold text-white/70 bg-transparent border border-white/10 rounded-lg hover:bg-white/5 transition-colors">
            View All
          </button>
          <button className="px-4 py-2 text-sm font-semibold text-black bg-white rounded-lg hover:bg-gray-200 hover:scale-[1.02] transition-all shadow-lg flex items-center gap-2">
            <Plus className="w-4 h-4" />
            New Scan
          </button>
        </div>
      </div>

      {/* Scans List */}
      <div className="space-y-4">
        {scans.map((scan, index) => (
          <motion.div
            key={scan.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: 0.9 + index * 0.1 }}
            className="p-5 bg-white/2 border border-white/6 rounded-xl hover:bg-white/4 hover:border-white/12 transition-all group"
          >
            {/* Scan Header */}
            <div className="flex items-start gap-4 mb-4">
              <motion.div
                whileHover={{ scale: 1.05, rotate: 5 }}
                className={`w-12 h-12 rounded-lg bg-gradient-to-br ${scan.gradient} flex items-center justify-center shadow-lg flex-shrink-0`}
                style={{
                  boxShadow: `0 4px 12px ${scan.gradient.includes('blue') ? 'rgba(59, 130, 246, 0.3)' :
                             scan.gradient.includes('red') ? 'rgba(239, 68, 68, 0.3)' :
                             'rgba(16, 185, 129, 0.3)'}`
                }}
              >
                <scan.icon className="w-6 h-6 text-white" />
              </motion.div>

              <div className="flex-1 min-w-0">
                <h4 className="text-base font-semibold text-white mb-1">
                  {scan.name}
                </h4>
                <p className="text-sm text-white/50 font-mono">
                  {scan.url}
                </p>
              </div>

              <div className={`px-3 py-1 rounded-md text-xs font-semibold border ${
                scan.status === 'scanning' 
                  ? 'bg-gray-500/15 border-gray-500/30 text-gray-400 animate-pulse'
                  : scan.status === 'analyzing'
                  ? 'bg-white/15 border-white/30 text-white'
                  : 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400'
              }`}>
                {scan.status.charAt(0).toUpperCase() + scan.status.slice(1)}
              </div>
            </div>

            {/* Progress Bar */}
            <div className="mb-3">
              <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${scan.progress}%` }}
                  transition={{ duration: 1, delay: 1 + index * 0.1 }}
                  className="h-full bg-gradient-to-r from-gray-500 to-white rounded-full relative overflow-hidden"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" />
                </motion.div>
              </div>
              <span className="text-xs text-white/60 font-semibold mt-1 inline-block">
                {scan.progress}% Complete
              </span>
            </div>

            {/* Scan Details */}
            <div className="flex items-center gap-5 mb-3 text-xs text-white/50">
              <div className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5" />
                <span>Started {scan.startedTime}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5" />
                <span>
                  {scan.findings > 0 
                    ? `${scan.findings} vulnerabilities found`
                    : 'No vulnerabilities'
                  }
                </span>
              </div>
            </div>

            {/* Scan Actions */}
            <div className="flex gap-2">
              <button className="px-3 py-1.5 text-xs font-semibold text-white/70 bg-white/5 border border-white/8 rounded-md hover:bg-white/10 transition-colors">
                View Details
              </button>
              {scan.status !== 'completed' && (
                <>
                  <button className="px-3 py-1.5 text-xs font-semibold text-white/70 bg-white/5 border border-white/8 rounded-md hover:bg-white/10 transition-colors flex items-center gap-1.5">
                    <Pause className="w-3 h-3" />
                    Pause
                  </button>
                  <button className="px-3 py-1.5 text-xs font-semibold text-red-400 bg-red-500/10 border border-red-500/30 rounded-md hover:bg-red-500/20 transition-colors flex items-center gap-1.5">
                    <Square className="w-3 h-3" />
                    Stop
                  </button>
                </>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Empty State (commented out - shown when no scans) */}
      {/* 
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="w-32 h-32 rounded-full border-2 border-dashed border-white/10 bg-white/3 flex items-center justify-center mb-6">
          <Search className="w-16 h-16 text-white/20" strokeWidth={1.5} />
        </div>
        <h3 className="text-xl font-bold text-white mb-2">No Active Scans</h3>
        <p className="text-sm text-white/50 max-w-sm mb-6">
          Start a new security scan to begin discovering vulnerabilities
        </p>
        <button className="px-6 py-3 text-sm font-semibold text-black bg-white rounded-lg hover:bg-gray-200 hover:scale-105 transition-all shadow-lg">
          Start Your First Scan
        </button>
      </div>
      */}
    </motion.section>
  );
}
