"use client";

import { motion } from 'framer-motion';
import { Activity, FileText, ShoppingCart, Users, BookOpen, Terminal, Lock } from 'lucide-react';
import { useSubscription } from '@/contexts/SubscriptionContext';
import { InlineFeatureLocked } from '@/components/FeatureLocked';

interface Action {
  id: string;
  label: string;
  icon: typeof Activity;
  href: string;
  description: string;
  requiresFeature?: keyof ReturnType<typeof useSubscription>['features'];
  requiredTier?: 'free' | 'starter' | 'professional' | 'enterprise';
}

function ActionButton({ action }: { action: Action }) {
  const Icon = action.icon;
  const { features, canUseScan } = useSubscription();

  const isLocked = action.requiresFeature && !features[action.requiresFeature];
  const canStartScan = action.id === '1' && !canUseScan();

  if (isLocked && action.requiredTier) {
    return (
      <div className="flex items-center gap-3 p-3 rounded-lg border border-gray-700 bg-gray-900/40 relative overflow-hidden">
        <div className="flex-shrink-0 w-9 h-9 rounded-md bg-gray-800 flex items-center justify-center">
          <Lock size={16} className="text-gray-400" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium text-gray-300">
            {action.label}
          </div>
          <div className="text-xs text-gray-400">
            Requires {action.requiredTier}
          </div>
        </div>
      </div>
    );
  }

  if (canStartScan) {
    return (
      <div className="flex items-center gap-3 p-3 rounded-lg border border-gray-700 bg-gray-900/60 relative overflow-hidden">
        <div className="flex-shrink-0 w-9 h-9 rounded-md bg-gray-800 flex items-center justify-center">
          <Lock size={16} className="text-gray-400" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium text-gray-300">
            {action.label}
          </div>
          <div className="text-xs text-gray-400">
            Scan limit reached
          </div>
        </div>
      </div>
    );
  }

  return (
    <motion.a
      href={action.href}
      className="flex items-center gap-3 p-3 rounded-lg border border-gray-700 bg-gray-900/40 hover:border-white hover:bg-gray-800 transition-all duration-200"
      whileHover={{ x: 2 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
    >
      <div className="flex-shrink-0 w-9 h-9 rounded-md bg-gray-800 flex items-center justify-center">
        <Icon size={16} className="text-white" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium text-white">
          {action.label}
        </div>
        <div className="text-xs text-gray-400">
          {action.description}
        </div>
      </div>
    </motion.a>
  );
}

export function RefinedQuickActions() {
  const actions: Action[] = [
    {
      id: '1',
      label: 'New Scan',
      description: 'Start security assessment',
      icon: Activity,
      href: '/scans/new',
    },
    {
      id: '2',
      label: 'Reports',
      description: 'View scan results',
      icon: FileText,
      href: '/reports',
    },
    {
      id: '3',
      label: 'Marketplace',
      description: 'Browse tools & services',
      icon: ShoppingCart,
      href: '/marketplace',
      requiresFeature: 'marketplaceAccess',
      requiredTier: 'professional',
    },
    {
      id: '4',
      label: 'Guilds',
      description: 'Join security teams',
      icon: Users,
      href: '/guilds',
      requiresFeature: 'guildAccess',
      requiredTier: 'professional',
    },
    {
      id: '5',
      label: 'Knowledge Base',
      description: 'Learning resources',
      icon: BookOpen,
      href: '/learn',
    },
    {
      id: '6',
      label: 'API Docs',
      description: 'Developer documentation',
      icon: Terminal,
      href: '/docs/api',
      requiresFeature: 'apiAccess',
      requiredTier: 'professional',
    },
  ];

  return (
    <div className="mb-6">
      <div className="flex items-center gap-2 mb-4">
        <Terminal size={18} className="text-gray-400" />
        <h2 className="text-base font-semibold text-white uppercase tracking-wide">Quick Actions</h2>
      </div>
      
      <div className="grid grid-cols-2 gap-2">
        {actions.map((action) => (
          <ActionButton key={action.id} action={action} />
        ))}
      </div>
    </div>
  );
}
