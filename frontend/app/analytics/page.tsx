"use client";

import { Sidebar } from '@/components/dashboard/Sidebar';
import { AtmosphericBackground } from '@/components/dashboard/AtmosphericBackground';
import { TrendingUp, BarChart3, Activity, Target } from 'lucide-react';

export default function AnalyticsPage() {
  const stats = [
    { label: 'Total Scans', value: '1,234', change: '+12%', icon: Activity, color: 'blue' },
    { label: 'Bugs Found', value: '856', change: '+8%', icon: Target, color: 'red' },
    { label: 'Success Rate', value: '92%', change: '+5%', icon: TrendingUp, color: 'green' },
    { label: 'Avg Response', value: '2.4h', change: '-15%', icon: BarChart3, color: 'purple' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      <AtmosphericBackground />
      <Sidebar />
      
      <div className="lg:ml-64 min-h-screen">
        <div className="relative z-10 p-10">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Analytics</h1>
            <p className="text-slate-400">Track your performance and bug discovery metrics</p>
          </div>

          {/* Stats Grid */}
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            {stats.map((stat) => (
              <div key={stat.label} className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <stat.icon className={`text-${stat.color}-400`} size={24} />
                  <span className={`text-${stat.change.startsWith('+') ? 'green' : 'red'}-400 text-sm font-medium`}>{stat.change}</span>
                </div>
                <div className="text-3xl font-bold text-white mb-1">{stat.value}</div>
                <div className="text-slate-400 text-sm">{stat.label}</div>
              </div>
            ))}
          </div>

          {/* Chart Placeholder */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 mb-8">
            <h2 className="text-xl font-bold text-white mb-6">Activity Over Time</h2>
            <div className="h-64 flex items-end justify-between gap-2">
              {[40, 60, 45, 75, 55, 80, 65, 90, 70, 85, 75, 95].map((h, i) => (
                <div key={i} className="flex-1 bg-gradient-to-t from-blue-600 to-purple-600 rounded-t" style={{height: `${h}%`}} />
              ))}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <h2 className="text-xl font-bold text-white mb-4">Recent Activity</h2>
            <div className="space-y-3">
              {['Scan completed: example.com', 'New bug found: SQL Injection', 'Report submitted: XSS vulnerability', 'Payment received: $500'].map((activity, i) => (
                <div key={i} className="p-4 bg-white/5 rounded-lg text-slate-300">{activity}</div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
