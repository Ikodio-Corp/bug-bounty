"use client";

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  ChevronRight, 
  Search, 
  Bell, 
  ChevronDown,
  TrendingUp,
  TrendingDown
} from 'lucide-react';

interface QuickStat {
  label: string;
  value: number;
  trend: 'up' | 'down';
}

export function Header() {
  const [quickStats] = useState<QuickStat[]>([
    { label: 'Active Scans', value: 8, trend: 'up' },
    { label: 'Pending Reviews', value: 12, trend: 'up' },
    { label: "Today's Earnings", value: 247, trend: 'up' },
  ]);

  const [displayValues, setDisplayValues] = useState<number[]>([0, 0, 0]);

  useEffect(() => {
    // Animate counter on mount
    const timers = quickStats.map((stat, index) => {
      let current = 0;
      const increment = stat.value / 30;
      const timer = setInterval(() => {
        current += increment;
        if (current >= stat.value) {
          current = stat.value;
          clearInterval(timer);
        }
        setDisplayValues(prev => {
          const newValues = [...prev];
          newValues[index] = Math.round(current);
          return newValues;
        });
      }, 30);
      return timer;
    });

    return () => timers.forEach(clearInterval);
  }, []);

  return (
    <motion.header
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1], delay: 0.2 }}
      className="sticky top-0 h-20 z-40 flex items-center justify-between px-8 bg-slate-900/80 border-b"
      style={{
        backdropFilter: 'blur(20px)',
        borderColor: 'rgba(255, 255, 255, 0.06)',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
      }}
    >
      {/* Left Section - Breadcrumb & Welcome */}
      <div>
        <div className="flex items-center gap-2 text-xs text-white/50 mb-2">
          <span>Home</span>
          <ChevronRight className="w-3.5 h-3.5 text-white/30" />
          <span className="text-white font-semibold">Dashboard</span>
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight mb-1">
          Welcome back, Hylmii
        </h1>
        <p className="text-sm text-white/50">
          Here is your security research overview for today
        </p>
      </div>

      {/* Right Section - Quick Stats & Actions */}
      <div className="flex items-center gap-6">
        {/* Quick Stats Inline */}
        <div className="flex items-center gap-6">
          {quickStats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + index * 0.1 }}
              className="text-right"
            >
              <div className="text-xs uppercase tracking-wider text-white/50 font-semibold mb-1">
                {stat.label}
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-lg font-bold text-white">
                  {stat.label.includes('Earnings') ? '$' : ''}{displayValues[index]}
                </span>
                {stat.trend === 'up' ? (
                  <TrendingUp className="w-3.5 h-3.5 text-emerald-500" />
                ) : (
                  <TrendingDown className="w-3.5 h-3.5 text-red-500" />
                )}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Divider */}
        <div className="w-px h-10 bg-white/10" />

        {/* Search Button */}
        <button className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center hover:bg-white/10 transition-colors">
          <Search className="w-4.5 h-4.5 text-white/70" />
        </button>

        {/* Notifications */}
        <button className="relative w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center hover:bg-white/10 transition-colors">
          <Bell className="w-4.5 h-4.5 text-white/70" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full shadow-lg shadow-red-500/50" />
          <span className="absolute top-0 right-0 px-1.5 py-0.5 bg-red-500 text-white text-xs font-bold rounded-full -translate-y-1 translate-x-1">
            5
          </span>
        </button>

        {/* Profile Dropdown */}
        <button className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">
          <div className="w-8 h-8 rounded-full border-2 border-white/50 bg-white/10 flex items-center justify-center">
            <span className="text-white font-semibold text-xs">H</span>
          </div>
          <span className="text-sm font-semibold text-white">Hylmii</span>
          <ChevronDown className="w-3.5 h-3.5 text-white/40" />
        </button>
      </div>
    </motion.header>
  );
}
