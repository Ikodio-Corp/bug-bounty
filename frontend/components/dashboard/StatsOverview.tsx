"use client";

import { motion } from 'framer-motion';
import { Shield, Search, DollarSign, Target, Trophy, TrendingUp, TrendingDown } from 'lucide-react';
import { useEffect, useState } from 'react';

interface StatCard {
  icon: any;
  gradient: string;
  value: number;
  label: string;
  trend: string;
  trendDirection: 'up' | 'down';
}

const statsData: StatCard[] = [
  {
    icon: Shield,
    gradient: 'from-gray-500 to-gray-600',
    value: 1247,
    label: 'Total Vulnerabilities',
    trend: '+23%',
    trendDirection: 'up',
  },
  {
    icon: Search,
    gradient: 'from-cyan-500 to-cyan-600',
    value: 8,
    label: 'Active Scans',
    trend: '+12%',
    trendDirection: 'up',
  },
  {
    icon: DollarSign,
    gradient: 'from-emerald-500 to-emerald-600',
    value: 45280,
    label: 'Total Earnings',
    trend: '+18.5%',
    trendDirection: 'up',
  },
  {
    icon: Target,
    gradient: 'from-gray-400 to-gray-500',
    value: 94.8,
    label: 'Success Rate',
    trend: '+2.1%',
    trendDirection: 'up',
  },
  {
    icon: Trophy,
    gradient: 'from-orange-500 to-red-500',
    value: 47,
    label: 'Global Rank',
    trend: 'Up 8',
    trendDirection: 'up',
  },
];

export function StatsOverview() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.4 }}
      className="flex gap-4 px-8 py-6 overflow-x-auto"
    >
      {statsData.map((stat, index) => (
        <motion.div
          key={stat.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.4 + index * 0.05 }}
          whileHover={{ 
            y: -2, 
            boxShadow: '0 8px 16px rgba(0, 0, 0, 0.2)',
          }}
          className="min-w-[200px] flex-1 flex items-center justify-between px-5 py-4 bg-slate-800/40 backdrop-blur-sm border border-white/5 rounded-xl hover:bg-slate-800/60 hover:border-white/10 transition-all cursor-pointer"
        >
          <div>
            <div className="text-xs text-white/50 font-medium mb-2">
              {stat.label}
            </div>
            <div className="text-3xl font-bold text-white mb-1">
              <CountUpAnimation 
                end={stat.value} 
                duration={2000}
                prefix={stat.label === 'Total Earnings' ? '$' : ''}
                suffix={stat.label === 'Success Rate' ? '%' : stat.label === 'Global Rank' ? '' : ''}
                decimals={stat.label === 'Success Rate' ? 1 : 0}
              />
            </div>
            <div className={`flex items-center gap-1 text-xs font-medium ${stat.trendDirection === 'up' ? 'text-emerald-500' : 'text-red-500'}`}>
              {stat.trendDirection === 'up' ? (
                <TrendingUp className="w-3 h-3" />
              ) : (
                <TrendingDown className="w-3 h-3" />
              )}
              <span>{stat.trend}</span>
            </div>
          </div>

          <motion.div
            whileHover={{ scale: 1.1, rotate: 5 }}
            className={`w-12 h-12 rounded-lg bg-gradient-to-br ${stat.gradient} flex items-center justify-center shadow-lg`}
            style={{
              boxShadow: `0 4px 12px ${stat.gradient.includes('blue') ? 'rgba(59, 130, 246, 0.3)' : 
                         stat.gradient.includes('cyan') ? 'rgba(6, 182, 212, 0.3)' :
                         stat.gradient.includes('emerald') ? 'rgba(16, 185, 129, 0.3)' :
                         stat.gradient.includes('purple') ? 'rgba(139, 92, 246, 0.3)' :
                         'rgba(249, 115, 22, 0.3)'}`
            }}
          >
            <stat.icon className="w-6 h-6 text-white" strokeWidth={2} />
          </motion.div>
        </motion.div>
      ))}
    </motion.div>
  );
}

function CountUpAnimation({ 
  end, 
  duration = 2000, 
  prefix = '', 
  suffix = '',
  decimals = 0 
}: { 
  end: number; 
  duration?: number; 
  prefix?: string;
  suffix?: string;
  decimals?: number;
}) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTime: number;
    let animationFrame: number;

    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      
      // Easing function
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      setCount(end * easeOutQuart);

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    animationFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrame);
  }, [end, duration]);

  return (
    <span>
      {prefix}
      {decimals > 0 ? count.toFixed(decimals) : Math.round(count).toLocaleString()}
      {suffix}
    </span>
  );
}
