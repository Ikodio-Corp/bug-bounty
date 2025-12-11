"use client";

import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Search, ShoppingBag, Users, Trophy, DollarSign, Clock } from 'lucide-react';
import { useState } from 'react';

interface Activity {
  id: string;
  user: {
    name: string;
    avatar: string;
  };
  action: string;
  target?: string;
  timeAgo: string;
  reward?: string;
  type: 'vulnerability' | 'scan' | 'marketplace' | 'guild' | 'achievement';
  icon: any;
  gradient: string;
}

const activitiesData: Activity[] = [
  {
    id: '1',
    user: { name: 'Sarah Chen', avatar: 'SC' },
    action: 'discovered a critical SQL injection',
    target: 'api.shop.com',
    timeAgo: '2 minutes ago',
    reward: '$500',
    type: 'vulnerability',
    icon: Shield,
    gradient: 'from-red-500 to-red-600',
  },
  {
    id: '2',
    user: { name: 'Marcus Liu', avatar: 'ML' },
    action: 'completed a security scan',
    target: 'bank.secure.com',
    timeAgo: '5 minutes ago',
    type: 'scan',
    icon: Search,
    gradient: 'from-gray-500 to-gray-600',
  },
  {
    id: '3',
    user: { name: 'Emma Johnson', avatar: 'EJ' },
    action: 'sold a vulnerability in marketplace',
    target: 'healthcare.net',
    timeAgo: '8 minutes ago',
    reward: '$1,250',
    type: 'marketplace',
    icon: ShoppingBag,
    gradient: 'from-gray-400 to-gray-500',
  },
  {
    id: '4',
    user: { name: 'David Park', avatar: 'DP' },
    action: 'joined the Elite Hunters guild',
    timeAgo: '12 minutes ago',
    type: 'guild',
    icon: Users,
    gradient: 'from-cyan-500 to-cyan-600',
  },
  {
    id: '5',
    user: { name: 'Lisa Anderson', avatar: 'LA' },
    action: 'earned an achievement badge',
    timeAgo: '15 minutes ago',
    type: 'achievement',
    icon: Trophy,
    gradient: 'from-orange-500 to-orange-600',
  },
];

const feedItemVariants = {
  hidden: { opacity: 0, x: 20, scale: 0.95 },
  visible: { opacity: 1, x: 0, scale: 1 },
  exit: { opacity: 0, x: -20, scale: 0.95 },
};

export function LiveActivityFeed() {
  const [activities] = useState(activitiesData);

  return (
    <motion.div
      initial={{ opacity: 0, x: 30 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, delay: 1.1 }}
      className="sticky top-24 p-6 rounded-2xl border border-white/8 backdrop-blur-md mb-6 overflow-hidden"
      style={{
        background: 'rgba(30, 41, 59, 0.5)',
        maxHeight: 'calc(100vh - 128px)',
      }}
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-bold text-white mb-1">Live Activity</h3>
          <p className="text-xs text-white/50">Platform-wide updates</p>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-1 bg-red-500/15 border border-red-500/30 rounded-md">
          <span className="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse" />
          <span className="text-xs font-bold text-red-400 uppercase tracking-wide">
            LIVE
          </span>
        </div>
      </div>

      {/* Feed Content */}
      <div 
        className="space-y-3 overflow-y-auto pr-2"
        style={{
          maxHeight: 'calc(100vh - 280px)',
        }}
      >
        <AnimatePresence>
          {activities.map((activity, index) => (
            <motion.div
              key={activity.id}
              variants={feedItemVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
              transition={{ duration: 0.3, delay: 1.2 + index * 0.05 }}
              layout
              className="flex gap-3 pb-3 border-b border-white/5 hover:bg-white/2 rounded-lg p-2 -mx-2 transition-colors"
            >
              {/* Avatar with Badge */}
              <div className="relative flex-shrink-0">
                <div className="w-9 h-9 rounded-full border-2 border-white/30 bg-white/10 flex items-center justify-center">
                  <span className="text-xs font-bold text-white">
                    {activity.user.avatar}
                  </span>
                </div>
                <div 
                  className={`absolute -bottom-0.5 -right-0.5 w-4.5 h-4.5 rounded-full bg-gradient-to-br ${activity.gradient} border-2 border-slate-900 flex items-center justify-center`}
                >
                  <activity.icon className="w-2.5 h-2.5 text-white" />
                </div>
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white/80 mb-1">
                  <strong className="font-semibold text-white">
                    {activity.user.name}
                  </strong>{' '}
                  {activity.action}
                </p>
                <div className="flex items-center gap-2 text-xs text-white/40">
                  {activity.target && (
                    <span className="px-1.5 py-0.5 bg-white/5 rounded font-mono text-[10px]">
                      {activity.target}
                    </span>
                  )}
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    <span>{activity.timeAgo}</span>
                  </div>
                </div>
                {activity.reward && (
                  <div className="mt-1.5 inline-flex items-center gap-1 px-2 py-1 bg-emerald-500/15 border border-emerald-500/30 rounded-md">
                    <DollarSign className="w-3 h-3 text-emerald-500" />
                    <span className="text-xs font-semibold text-emerald-500">
                      {activity.reward}
                    </span>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Load More */}
      <button className="w-full mt-3 py-2 text-xs font-semibold text-white/60 bg-white/3 border border-white/8 rounded-lg hover:bg-white/6 transition-colors">
        Load More Activity
      </button>

      {/* Custom Scrollbar Styles */}
      <style jsx>{`
        div::-webkit-scrollbar {
          width: 6px;
        }
        div::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 3px;
        }
        div::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.2);
          border-radius: 3px;
        }
        div::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.3);
        }
      `}</style>
    </motion.div>
  );
}
