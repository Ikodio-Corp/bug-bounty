"use client";

import { motion } from 'framer-motion';
import { Activity, FileText, ShoppingCart, Users, BookOpen, Terminal } from 'lucide-react';

interface Action {
  id: string;
  label: string;
  icon: typeof Activity;
  href: string;
  description: string;
}

function ActionButton({ action }: { action: Action }) {
  const Icon = action.icon;

  return (
    <motion.a
      href={action.href}
      className="flex items-center gap-3 p-3 rounded-lg border border-slate-800/80 bg-slate-900/40 hover:border-slate-700/80 hover:bg-slate-800/60 transition-all duration-200"
      whileHover={{ x: 2 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
    >
      <div className="flex-shrink-0 w-9 h-9 rounded-md bg-slate-800/80 flex items-center justify-center">
        <Icon size={16} className="text-slate-300" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium text-slate-200">
          {action.label}
        </div>
        <div className="text-xs text-slate-500">
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
    },
    {
      id: '4',
      label: 'Guilds',
      description: 'Join security teams',
      icon: Users,
      href: '/guilds',
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
    },
  ];

  return (
    <div className="mb-6">
      <div className="flex items-center gap-2 mb-4">
        <Terminal size={18} className="text-slate-400" />
        <h2 className="text-base font-semibold text-slate-200 uppercase tracking-wide">Quick Actions</h2>
      </div>
      
      <div className="grid grid-cols-2 gap-2">
        {actions.map((action) => (
          <ActionButton key={action.id} action={action} />
        ))}
      </div>
    </div>
  );
}
