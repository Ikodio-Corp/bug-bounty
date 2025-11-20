"use client";

import { motion } from 'framer-motion';
import { 
  Search, 
  FileText, 
  ShoppingBag, 
  Users, 
  Trophy, 
  Code, 
  ArrowRight,
  Calendar,
  Clock
} from 'lucide-react';
import Link from 'next/link';

interface QuickAction {
  icon: any;
  label: string;
  href: string;
  gradient: string;
}

interface Event {
  date: { day: string; month: string };
  title: string;
  description: string;
  time: string;
}

const quickActions: QuickAction[] = [
  { icon: Search, label: 'Start New Scan', href: '/scans/new', gradient: 'from-blue-500 to-blue-600' },
  { icon: FileText, label: 'View Reports', href: '/reports', gradient: 'from-cyan-500 to-cyan-600' },
  { icon: ShoppingBag, label: 'Browse Marketplace', href: '/marketplace', gradient: 'from-purple-500 to-purple-600' },
  { icon: Users, label: 'Join Guild', href: '/guilds', gradient: 'from-emerald-500 to-emerald-600' },
  { icon: Trophy, label: 'View Leaderboard', href: '/leaderboard', gradient: 'from-orange-500 to-orange-600' },
  { icon: Code, label: 'API Docs', href: '/api-docs', gradient: 'from-red-500 to-red-600' },
];

const upcomingEvents: Event[] = [
  {
    date: { day: '24', month: 'JAN' },
    title: 'Monthly Bounty Payout',
    description: 'Receive your earnings from verified bugs',
    time: '12:00 PM UTC',
  },
  {
    date: { day: '25', month: 'JAN' },
    title: 'Guild Championship Finals',
    description: 'Top guilds compete for grand prize',
    time: '3:00 PM UTC',
  },
  {
    date: { day: '28', month: 'JAN' },
    title: 'Security Webinar',
    description: 'Advanced XSS exploitation techniques',
    time: '2:00 PM UTC',
  },
];

export function QuickActions() {
  return (
    <motion.div
      initial={{ opacity: 0, x: 30 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, delay: 1.2 }}
      className="p-6 rounded-2xl border border-white/8 backdrop-blur-md mb-6"
      style={{
        background: 'rgba(30, 41, 59, 0.5)',
      }}
    >
      <h3 className="text-lg font-bold text-white mb-1">Quick Actions</h3>
      <p className="text-xs text-white/50 mb-4">Common tasks and shortcuts</p>

      <div className="grid grid-cols-2 gap-3">
        {quickActions.map((action, index) => (
          <Link key={action.label} href={action.href}>
            <motion.button
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.2, delay: 1.3 + index * 0.05 }}
              whileHover={{ 
                y: -2,
                boxShadow: '0 8px 16px rgba(0, 0, 0, 0.2)',
              }}
              className="relative w-full p-4 bg-white/3 border border-white/8 rounded-xl flex flex-col items-start gap-2 hover:bg-white/6 hover:border-white/15 transition-all group text-left"
            >
              <motion.div
                whileHover={{ scale: 1.1, rotate: 5 }}
                transition={{ type: "spring", stiffness: 400 }}
                className={`w-10 h-10 rounded-lg bg-gradient-to-br ${action.gradient} flex items-center justify-center shadow-lg`}
                style={{
                  boxShadow: `0 4px 12px ${action.gradient.includes('blue') ? 'rgba(59, 130, 246, 0.3)' :
                             action.gradient.includes('cyan') ? 'rgba(6, 182, 212, 0.3)' :
                             action.gradient.includes('purple') ? 'rgba(139, 92, 246, 0.3)' :
                             action.gradient.includes('emerald') ? 'rgba(16, 185, 129, 0.3)' :
                             action.gradient.includes('orange') ? 'rgba(249, 115, 22, 0.3)' :
                             'rgba(239, 68, 68, 0.3)'}`
                }}
              >
                <action.icon className="w-5 h-5 text-white" strokeWidth={2} />
              </motion.div>

              <span className="text-sm font-semibold text-white leading-tight">
                {action.label}
              </span>

              <ArrowRight className="absolute top-4 right-3 w-3.5 h-3.5 text-white/30 group-hover:text-white/60 group-hover:translate-x-1 transition-all" />
            </motion.button>
          </Link>
        ))}
      </div>
    </motion.div>
  );
}

export function UpcomingEvents() {
  return (
    <motion.div
      initial={{ opacity: 0, x: 30 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, delay: 1.3 }}
      className="p-6 rounded-2xl border border-white/8 backdrop-blur-md"
      style={{
        background: 'rgba(30, 41, 59, 0.5)',
      }}
    >
      <div className="flex items-center gap-2 mb-4">
        <Calendar className="w-5 h-5 text-blue-400" />
        <div>
          <h3 className="text-lg font-bold text-white">Upcoming Events</h3>
          <p className="text-xs text-white/50">Important dates and deadlines</p>
        </div>
      </div>

      <div className="space-y-3.5">
        {upcomingEvents.map((event, index) => (
          <motion.div
            key={event.title}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, delay: 1.4 + index * 0.1 }}
            className="flex gap-3.5 pb-3.5 border-b border-white/5 last:border-0 last:pb-0"
          >
            {/* Date Box */}
            <div className="w-14 h-14 flex-shrink-0 rounded-lg bg-blue-500/15 border border-blue-500/30 flex flex-col items-center justify-center">
              <span className="text-xl font-bold text-blue-400 leading-none">
                {event.date.day}
              </span>
              <span className="text-[10px] font-semibold text-blue-400/70 uppercase tracking-wide mt-0.5">
                {event.date.month}
              </span>
            </div>

            {/* Event Details */}
            <div className="flex-1 min-w-0">
              <h4 className="text-sm font-semibold text-white mb-1">
                {event.title}
              </h4>
              <p className="text-xs text-white/50 leading-relaxed mb-1.5">
                {event.description}
              </p>
              <div className="flex items-center gap-1 text-xs text-white/40">
                <Clock className="w-3 h-3" />
                <span>{event.time}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* View All Link */}
      <button className="w-full mt-4 py-2 text-xs font-semibold text-blue-400 hover:text-blue-300 transition-colors flex items-center justify-center gap-1 group">
        <span>View All Events</span>
        <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
      </button>
    </motion.div>
  );
}
