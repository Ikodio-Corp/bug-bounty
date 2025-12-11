"use client";

import { motion } from 'framer-motion';
import { Shield, DollarSign, Target, Trophy, TrendingUp } from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer } from 'recharts';

interface MetricCard {
  icon: any;
  gradient: string;
  value: string;
  label: string;
  badge: string;
  details: { label: string; value: string }[];
  sparklineData: { value: number }[];
}

const metricsData: MetricCard[] = [
  {
    icon: Shield,
    gradient: 'from-gray-500 to-gray-600',
    value: '1,247',
    label: 'Total Vulnerabilities Discovered',
    badge: '+23%',
    details: [
      { label: 'This Month', value: '+156' },
      { label: 'Average per Day', value: '5.2' },
    ],
    sparklineData: Array.from({ length: 30 }, (_, i) => ({
      value: Math.floor(Math.random() * 50) + 100 + i * 2,
    })),
  },
  {
    icon: DollarSign,
    gradient: 'from-emerald-500 to-emerald-600',
    value: '$45,280',
    label: 'Lifetime Earnings from Bounties',
    badge: '+18.5%',
    details: [
      { label: 'This Month', value: '$5,240' },
      { label: 'Average Bounty', value: '$287' },
    ],
    sparklineData: Array.from({ length: 30 }, (_, i) => ({
      value: Math.floor(Math.random() * 200) + 300 + i * 5,
    })),
  },
  {
    icon: Target,
    gradient: 'from-gray-400 to-gray-500',
    value: '94.8%',
    label: 'Vulnerability Validation Rate',
    badge: '+2.1%',
    details: [
      { label: 'Accepted', value: '1,182' },
      { label: 'Rejected', value: '65' },
    ],
    sparklineData: Array.from({ length: 30 }, (_, i) => ({
      value: Math.floor(Math.random() * 5) + 92,
    })),
  },
  {
    icon: Trophy,
    gradient: 'from-orange-500 to-red-500',
    value: '#47',
    label: 'Global Leaderboard Position',
    badge: 'Up 8 positions',
    details: [
      { label: 'Top 1% of', value: '10,000+' },
      { label: 'Points', value: '45,280' },
    ],
    sparklineData: Array.from({ length: 30 }, (_, i) => ({
      value: 200 - i * 3 - Math.floor(Math.random() * 10),
    })),
  },
];

export function MetricsGrid() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5, delay: 0.6 }}
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 px-8 mb-8"
    >
      {metricsData.map((metric, index) => (
        <motion.div
          key={metric.label}
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ 
            duration: 0.5, 
            delay: 0.6 + index * 0.08,
            ease: [0.4, 0, 0.2, 1]
          }}
          whileHover={{ 
            y: -6,
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
          }}
          className="relative min-h-[240px] p-7 rounded-2xl border border-white/8 backdrop-blur-md overflow-hidden transition-all group cursor-pointer"
          style={{
            background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.5), rgba(30, 41, 59, 0.3))',
          }}
        >
          {/* Background Decoration */}
          <div 
            className="absolute top-0 right-0 w-32 h-32 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
            style={{
              background: `radial-gradient(circle, ${metric.gradient.includes('blue') ? 'rgba(59, 130, 246, 0.15)' : 
                                                      metric.gradient.includes('emerald') ? 'rgba(16, 185, 129, 0.15)' :
                                                      metric.gradient.includes('purple') ? 'rgba(139, 92, 246, 0.15)' :
                                                      'rgba(249, 115, 22, 0.15)'}, transparent)`,
              transform: 'translate(20px, -20px)',
            }}
          />

          {/* Header */}
          <div className="flex justify-between items-start mb-6 relative z-10">
            <motion.div
              whileHover={{ scale: 1.1, rotate: 5 }}
              transition={{ type: "spring", stiffness: 400 }}
              className={`w-14 h-14 rounded-xl bg-gradient-to-br ${metric.gradient} flex items-center justify-center shadow-lg`}
              style={{
                boxShadow: `0 8px 20px ${metric.gradient.includes('blue') ? 'rgba(59, 130, 246, 0.4)' : 
                           metric.gradient.includes('emerald') ? 'rgba(16, 185, 129, 0.4)' :
                           metric.gradient.includes('purple') ? 'rgba(139, 92, 246, 0.4)' :
                           'rgba(249, 115, 22, 0.4)'}`
              }}
            >
              <metric.icon className="w-7 h-7 text-white" strokeWidth={2} />
            </motion.div>

            <div className="px-3 py-1.5 bg-emerald-500/15 border border-emerald-500/30 rounded-lg flex items-center gap-1.5">
              <TrendingUp className="w-3 h-3 text-emerald-500" />
              <span className="text-xs font-semibold text-emerald-500">
                {metric.badge}
              </span>
            </div>
          </div>

          {/* Value */}
          <div className="mb-4 relative z-10">
            <div className="text-4xl font-extrabold text-white mb-2 tracking-tight">
              {metric.value}
            </div>
            <div className="text-sm text-white/60 font-medium leading-tight">
              {metric.label}
            </div>
          </div>

          {/* Details */}
          <div className="space-y-2 mb-4 relative z-10">
            {metric.details.map((detail, i) => (
              <div 
                key={i}
                className="flex justify-between items-center py-2 border-t border-white/5"
              >
                <span className="text-xs text-white/50 font-medium">
                  {detail.label}
                </span>
                <span className="text-sm text-white font-semibold">
                  {detail.value}
                </span>
              </div>
            ))}
          </div>

          {/* Sparkline */}
          <div className="h-12 pt-4 border-t border-white/5 relative z-10">
            <ResponsiveContainer width="100%" height={48}>
              <AreaChart data={metric.sparklineData}>
                <defs>
                  <linearGradient id={`gradient-${index}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={metric.gradient.includes('blue') ? '#3b82f6' : 
                                                   metric.gradient.includes('emerald') ? '#10b981' :
                                                   metric.gradient.includes('purple') ? '#8b5cf6' :
                                                   '#f97316'} stopOpacity={0.4}/>
                    <stop offset="95%" stopColor={metric.gradient.includes('blue') ? '#3b82f6' : 
                                                    metric.gradient.includes('emerald') ? '#10b981' :
                                                    metric.gradient.includes('purple') ? '#8b5cf6' :
                                                    '#f97316'} stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke={metric.gradient.includes('blue') ? '#3b82f6' : 
                          metric.gradient.includes('emerald') ? '#10b981' :
                          metric.gradient.includes('purple') ? '#8b5cf6' :
                          '#f97316'}
                  strokeWidth={2}
                  fill={`url(#gradient-${index})`}
                  animationDuration={1500}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      ))}
    </motion.div>
  );
}
