"use client";

import { useState } from 'react';
import { Activity, Database, Server, AlertCircle } from 'lucide-react';

interface SystemMetric {
  label: string;
  value: string;
  status: 'operational' | 'warning' | 'critical';
  icon: any;
}

export function TopStatsBar() {
  const metrics: SystemMetric[] = [
    { label: 'System Status', value: 'Operational', status: 'operational', icon: Activity },
    { label: 'Active Scans', value: '8', status: 'operational', icon: Server },
    { label: 'Database', value: 'Connected', status: 'operational', icon: Database },
    { label: 'Alerts', value: '0', status: 'operational', icon: AlertCircle },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational': return 'text-emerald-400';
      case 'warning': return 'text-yellow-400';
      case 'critical': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  return (
    <div className="h-20 border-b border-slate-800/50 px-8 flex items-center justify-between bg-slate-950/50">
      <div className="flex flex-col">
        <div className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-1">
          Security Operations Dashboard
        </div>
        <h1 className="text-xl font-semibold text-slate-100 tracking-tight">
          Real-time Monitoring
        </h1>
      </div>

      <div className="flex gap-8 items-center">
        {metrics.map((metric, index) => {
          const Icon = metric.icon;
          return (
            <div key={metric.label} className="flex items-center gap-3">
              {index > 0 && <div className="w-px h-8 bg-slate-800" />}
              <div className="flex items-center gap-2">
                <Icon className={`w-4 h-4 ${getStatusColor(metric.status)}`} />
                <div className="flex flex-col">
                  <div className="text-xs text-slate-500 font-medium">
                    {metric.label}
                  </div>
                  <div className={`text-sm font-semibold ${getStatusColor(metric.status)}`}>
                    {metric.value}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
