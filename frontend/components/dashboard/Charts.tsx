"use client";

import { motion } from 'framer-motion';
import { useState } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from 'recharts';

// Performance data
const performanceData = [
  { date: 'Jan 12', scans: 12, vulnerabilities: 45 },
  { date: 'Jan 13', scans: 15, vulnerabilities: 52 },
  { date: 'Jan 14', scans: 10, vulnerabilities: 38 },
  { date: 'Jan 15', scans: 18, vulnerabilities: 67 },
  { date: 'Jan 16', scans: 22, vulnerabilities: 81 },
  { date: 'Jan 17', scans: 25, vulnerabilities: 95 },
  { date: 'Jan 18', scans: 20, vulnerabilities: 74 },
];

// Severity data
const severityData = [
  { name: 'Critical', count: 23, color: '#ef4444', percentage: 18 },
  { name: 'High', count: 45, color: '#f97316', percentage: 36 },
  { name: 'Medium', count: 38, color: '#f59e0b', percentage: 30 },
  { name: 'Low', count: 20, color: '#3b82f6', percentage: 16 },
];

// Type data
const typeData = [
  { type: 'SQL Injection', count: 38, color: '#ef4444' },
  { type: 'XSS', count: 32, color: '#f97316' },
  { type: 'CSRF', count: 18, color: '#f59e0b' },
  { type: 'Auth Issues', count: 15, color: '#3b82f6' },
  { type: 'Info Disclosure', count: 12, color: '#8b5cf6' },
  { type: 'Other', count: 11, color: '#6b7280' },
];

export function PerformanceChart() {
  const [activeTab, setActiveTab] = useState('7D');

  return (
    <motion.section
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.9 }}
      className="dashboard-section mb-6 p-7 rounded-2xl border border-white/8 backdrop-blur-md"
      style={{
        background: 'rgba(30, 41, 59, 0.5)',
      }}
    >
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-bold text-white mb-1">Scan Performance</h2>
          <p className="text-sm text-white/50">
            Vulnerability discovery trends over time
          </p>
        </div>
        <div className="flex gap-2">
          {['7D', '30D', '90D', '1Y'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
                activeTab === tab
                  ? 'bg-white/15 border border-white/30 text-white'
                  : 'bg-transparent border border-white/10 text-white/60 hover:bg-white/5'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Chart */}
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={performanceData}>
            <defs>
              <linearGradient id="scansGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="vulnsGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
              </linearGradient>
            </defs>
            
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke="rgba(255, 255, 255, 0.05)" 
              vertical={false}
            />
            
            <XAxis 
              dataKey="date" 
              stroke="rgba(255, 255, 255, 0.3)"
              tick={{ fill: 'rgba(255, 255, 255, 0.5)', fontSize: 12 }}
              tickLine={{ stroke: 'rgba(255, 255, 255, 0.1)' }}
            />
            
            <YAxis 
              stroke="rgba(255, 255, 255, 0.3)"
              tick={{ fill: 'rgba(255, 255, 255, 0.5)', fontSize: 12 }}
              tickLine={{ stroke: 'rgba(255, 255, 255, 0.1)' }}
            />
            
            <Tooltip 
              contentStyle={{
                background: 'rgba(15, 23, 42, 0.95)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                backdropFilter: 'blur(10px)',
              }}
              labelStyle={{ color: 'white', fontWeight: 600 }}
              itemStyle={{ color: 'white' }}
            />
            
            <Legend 
              wrapperStyle={{
                paddingTop: '20px',
                fontSize: '13px',
                fontWeight: 600,
              }}
            />
            
            <Area
              type="monotone"
              dataKey="scans"
              name="Scans Completed"
              stroke="#3b82f6"
              strokeWidth={2}
              fill="url(#scansGradient)"
              animationDuration={1500}
              dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, strokeWidth: 0 }}
            />
            
            <Area
              type="monotone"
              dataKey="vulnerabilities"
              name="Vulnerabilities Found"
              stroke="#8b5cf6"
              strokeWidth={2}
              fill="url(#vulnsGradient)"
              animationDuration={1500}
              dot={{ fill: '#8b5cf6', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, strokeWidth: 0 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.section>
  );
}

export function VulnerabilityDistribution() {
  const total = severityData.reduce((sum, item) => sum + item.count, 0);

  return (
    <motion.section
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 1.0 }}
      className="dashboard-section mb-6 p-7 rounded-2xl border border-white/8 backdrop-blur-md"
      style={{
        background: 'rgba(30, 41, 59, 0.5)',
      }}
    >
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-xl font-bold text-white mb-1">Vulnerability Distribution</h2>
        <p className="text-sm text-white/50">
          Breakdown by severity and type
        </p>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Severity Donut Chart */}
        <div className="relative">
          <h3 className="text-sm font-semibold text-white mb-4">By Severity</h3>
          <div className="h-64 relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="count"
                  animationDuration={1000}
                >
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{
                    background: 'rgba(15, 23, 42, 0.95)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '8px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            
            {/* Center Text */}
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center pointer-events-none">
              <div className="text-3xl font-bold text-white">{total}</div>
              <div className="text-sm text-white/50 font-medium">Total</div>
            </div>
          </div>
          
          {/* Legend */}
          <div className="grid grid-cols-2 gap-3 mt-4">
            {severityData.map((item) => (
              <div key={item.name} className="flex items-center gap-2">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: item.color }}
                />
                <span className="text-xs text-white/70">
                  {item.name}: <strong className="text-white">{item.count}</strong>
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Type Bar Chart */}
        <div>
          <h3 className="text-sm font-semibold text-white mb-4">By Type</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={typeData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" />
                <XAxis 
                  type="number" 
                  stroke="rgba(255, 255, 255, 0.3)"
                  tick={{ fill: 'rgba(255, 255, 255, 0.5)', fontSize: 11 }}
                />
                <YAxis 
                  type="category" 
                  dataKey="type" 
                  stroke="rgba(255, 255, 255, 0.3)"
                  width={110}
                  tick={{ fill: 'rgba(255, 255, 255, 0.5)', fontSize: 11 }}
                />
                <Tooltip 
                  contentStyle={{
                    background: 'rgba(15, 23, 42, 0.95)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '8px',
                  }}
                  cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }}
                />
                <Bar 
                  dataKey="count" 
                  radius={[0, 8, 8, 0]}
                  animationDuration={1000}
                >
                  {typeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </motion.section>
  );
}
