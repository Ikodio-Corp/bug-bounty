"use client";

import { motion } from 'framer-motion';
import { Shield, Activity, ShoppingBag, Users } from 'lucide-react';

interface ActivityLog {
  id: string;
  type: 'vulnerability' | 'scan' | 'marketplace' | 'guild';
  user: {
    name: string;
    avatar: string;
  };
  action: string;
  target: string;
  reward?: string;
  time: string;
}

const activityIcons = {
  vulnerability: Shield,
  scan: Activity,
  marketplace: ShoppingBag,
  guild: Users,
};

const activityColors = {
  vulnerability: 'text-red-400 bg-red-400/10',
  scan: 'text-blue-400 bg-blue-400/10',
  marketplace: 'text-purple-400 bg-purple-400/10',
  guild: 'text-emerald-400 bg-emerald-400/10',
};

function ActivityItem({ activity, isLast }: { activity: ActivityLog; isLast: boolean }) {
  const Icon = activityIcons[activity.type];
  const colorClass = activityColors[activity.type];

  return (
    <motion.div
      className={`relative pl-6 ${!isLast ? 'pb-4' : ''}`}
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
    >
      {!isLast && (
        <div className="absolute left-0 top-0 bottom-0 w-px bg-slate-800/60" />
      )}

      <div className="absolute left-0 top-2 -translate-x-[5px]">
        <div className={`w-2.5 h-2.5 rounded-full border-2 border-slate-900 ${colorClass.split(' ')[1]}`} />
      </div>

      <motion.div
        className="group"
        whileHover={{ x: 2 }}
        transition={{ duration: 0.15 }}
      >
        <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-slate-800/40 transition-colors">
          <div className={`flex-shrink-0 w-8 h-8 rounded-md ${colorClass} flex items-center justify-center`}>
            <Icon size={14} />
          </div>

          <div className="flex-1 min-w-0">
            <p className="text-xs text-slate-300 leading-relaxed mb-1">
              <span className="font-medium text-slate-200">
                {activity.user.name}
              </span>{' '}
              <span className="text-slate-400">
                {activity.action}
              </span>{' '}
              <span className="font-mono text-slate-500">
                {activity.target}
              </span>
            </p>

            <div className="flex items-center gap-2 text-[10px]">
              <span className="text-slate-500 tabular-nums">
                {activity.time}
              </span>
              {activity.reward && (
                <>
                  <span className="text-slate-700">|</span>
                  <span className="text-emerald-400 font-semibold">
                    {activity.reward}
                  </span>
                </>
              )}
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}

export function RefinedLiveActivity() {
  const activities: ActivityLog[] = [
    {
      id: '1',
      type: 'vulnerability',
      user: {
        name: 'Sarah Chen',
        avatar: 'https://i.pravatar.cc/150?img=1',
      },
      action: 'discovered SQL injection in',
      target: 'api.shop.com',
      reward: '$500',
      time: '2m ago',
    },
    {
      id: '2',
      type: 'scan',
      user: {
        name: 'Marcus Rodriguez',
        avatar: 'https://i.pravatar.cc/150?img=12',
      },
      action: 'completed security scan on',
      target: 'banking.acme.io',
      time: '8m ago',
    },
    {
      id: '3',
      type: 'marketplace',
      user: {
        name: 'Aisha Patel',
        avatar: 'https://i.pravatar.cc/150?img=5',
      },
      action: 'purchased scanner bundle',
      target: '@sectools',
      time: '15m ago',
    },
    {
      id: '4',
      type: 'guild',
      user: {
        name: 'James Wilson',
        avatar: 'https://i.pravatar.cc/150?img=8',
      },
      action: 'joined guild',
      target: 'Elite Hunters',
      time: '23m ago',
    },
    {
      id: '5',
      type: 'vulnerability',
      user: {
        name: 'Emma Thompson',
        avatar: 'https://i.pravatar.cc/150?img=9',
      },
      action: 'found XSS vulnerability in',
      target: 'dashboard.startup.io',
      reward: '$250',
      time: '1h ago',
    },
    {
      id: '6',
      type: 'scan',
      user: {
        name: 'David Kim',
        avatar: 'https://i.pravatar.cc/150?img=13',
      },
      action: 'initiated deep scan on',
      target: 'api.fintech.com',
      time: '1h ago',
    },
  ];

  return (
    <div className="mb-6">
      <div className="flex items-center gap-2 mb-4">
        <Activity size={18} className="text-slate-400" />
        <h2 className="text-base font-semibold text-slate-200 uppercase tracking-wide">System Activity Log</h2>
        <span className="text-xs text-slate-500 ml-auto">Real-time</span>
      </div>

      <div className="rounded-lg border border-slate-800/80 bg-slate-900/40 p-4">
        {activities.map((activity, index) => (
          <ActivityItem 
            key={activity.id} 
            activity={activity} 
            isLast={index === activities.length - 1}
          />
        ))}
      </div>
    </div>
  );
}
