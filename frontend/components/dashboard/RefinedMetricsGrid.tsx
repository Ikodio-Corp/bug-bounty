"use client";

import { motion } from 'framer-motion';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer } from 'recharts';
import { useState, useEffect } from 'react';

interface MetricCardProps {
  title: string;
  subtitle: string;
  value: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  trend: number;
  trendPeriod: string;
  contextLeft: string;
  contextRight: string;
  accentColor: 'blue' | 'emerald' | 'purple' | 'orange';
  sparklineData: { value: number }[];
}

const accentColors = {
  blue: {
    stroke: '#3b82f6',
    fill: 'url(#sparkGradBlue)',
  },
  emerald: {
    stroke: '#10b981',
    fill: 'url(#sparkGradEmerald)',
  },
  purple: {
    stroke: '#8b5cf6',
    fill: 'url(#sparkGradPurple)',
  },
  orange: {
    stroke: '#f97316',
    fill: 'url(#sparkGradOrange)',
  },
};

function CountUp({ end, duration = 2000, decimals = 0, prefix = '', suffix = '' }: { 
  end: number; 
  duration?: number; 
  decimals?: number;
  prefix?: string;
  suffix?: string;
}) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTime: number;
    let animationFrame: number;

    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      setCount(end * easeOutQuart);

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    animationFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrame);
  }, [end, duration]);

  const displayValue = decimals > 0 
    ? count.toFixed(decimals) 
    : Math.round(count).toLocaleString();

  return <span>{prefix}{displayValue}{suffix}</span>;
}

export function RefinedMetricCard(props: MetricCardProps) {
  const colors = accentColors[props.accentColor];
  const isPositive = props.trend >= 0;

  return (
    <motion.div
      className="metric-card relative rounded-lg p-6 border border-slate-800/80 bg-slate-900/40 hover:border-slate-700/80 transition-all duration-300"
      whileHover={{ 
        y: -2,
        boxShadow: '0 8px 24px -8px rgba(0, 0, 0, 0.4)',
      }}
      transition={{ 
        type: 'spring',
        stiffness: 300,
        damping: 20
      }}
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">
            {props.title}
          </h3>
          <p className="text-xs text-slate-500">
            {props.subtitle}
          </p>
        </div>
        <div className={`flex items-center gap-1 text-xs font-semibold ${isPositive ? 'text-emerald-400' : 'text-red-400'}`}>
          {isPositive ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
          {Math.abs(props.trend)}%
        </div>
      </div>

      <div className="mb-4">
        <div className="text-3xl font-bold text-slate-100 tracking-tight mb-1">
          <CountUp 
            end={props.value}
            duration={2000}
            decimals={props.decimals}
            prefix={props.prefix}
            suffix={props.suffix}
          />
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <span>{props.contextLeft}</span>
          <span>|</span>
          <span>{props.contextRight}</span>
        </div>
      </div>

      <div className="h-12 -mx-6 -mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={props.sparklineData}>
            <defs>
              <linearGradient id={`sparkGrad${props.accentColor.charAt(0).toUpperCase() + props.accentColor.slice(1)}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={colors.stroke} stopOpacity={0.15} />
                <stop offset="100%" stopColor={colors.stroke} stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="value"
              stroke={colors.stroke}
              strokeWidth={1.5}
              fill={colors.fill}
              animationDuration={1500}
              animationEasing="ease-out"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}

export function RefinedMetricsGrid() {
  const generateSparkline = (base: number, variance: number, points: number = 30) => {
    return Array.from({ length: points }, (_, i) => ({
      value: base + Math.random() * variance + i * (variance / points)
    }));
  };

  const metrics: MetricCardProps[] = [
    {
      title: 'Total Vulnerabilities',
      subtitle: 'All-time discoveries',
      value: 1247,
      trend: '23%',
      trendPeriod: 'vs last month',
      contextLeft: '156 this month',
      contextRight: '5.2 avg/day',
      accentColor: 'blue',
      sparklineData: generateSparkline(100, 50),
    },
    {
      title: 'Lifetime Earnings',
      subtitle: 'From bounties',
      value: 45280,
      prefix: '$',
      trend: '18.5%',
      trendPeriod: 'vs last month',
      contextLeft: '$5,240 this month',
      contextRight: '$287 avg',
      accentColor: 'emerald',
      sparklineData: generateSparkline(300, 200),
    },
    {
      title: 'Validation Rate',
      subtitle: 'Submission acceptance',
      value: 94.8,
      suffix: '%',
      decimals: 1,
      trend: 2.1,
      trendPeriod: 'vs last month',
      contextLeft: '1,182 accepted',
      contextRight: '65 rejected',
      accentColor: 'purple',
      sparklineData: generateSparkline(92, 5),
    },
    {
      title: 'Global Rank',
      subtitle: 'Leaderboard position',
      value: 47,
      prefix: '#',
      trend: -14.5,
      trendPeriod: 'vs last month',
      contextLeft: 'Top 1%',
      contextRight: '45,280 points',
      accentColor: 'orange',
      sparklineData: Array.from({ length: 30 }, (_, i) => ({
        value: 200 - i * 3 - Math.floor(Math.random() * 10)
      })),
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {metrics.map((metric, index) => (
        <RefinedMetricCard key={metric.title} {...metric} />
      ))}
    </div>
  );
}
