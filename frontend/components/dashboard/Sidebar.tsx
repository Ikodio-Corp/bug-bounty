"use client";

import { useState } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Home,
  Search,
  Shield,
  ShoppingBag,
  Users,
  BarChart,
  Trophy,
  Zap,
  Code,
  Workflow,
  FileText,
  User,
  CreditCard,
  Settings,
  HelpCircle,
  ChevronLeft,
  ChevronRight,
  Lock,
  Crown,
} from 'lucide-react';
import { useSubscription, SubscriptionTier } from '@/contexts/SubscriptionContext';

interface NavItem {
  icon: any;
  label: string;
  href: string;
  badge?: string | number;
  badgeColor?: string;
  requiresFeature?: keyof ReturnType<typeof useSubscription>['features'];
  requiredTier?: SubscriptionTier;
}

const mainMenu: NavItem[] = [
  { icon: Home, label: 'Dashboard', href: '/dashboard' },
  { icon: Search, label: 'Scan Management', href: '/scans', badge: 3, badgeColor: 'blue' },
  { icon: Shield, label: 'Vulnerabilities', href: '/bugs', badge: 12, badgeColor: 'red' },
  { 
    icon: ShoppingBag, 
    label: 'Marketplace', 
    href: '/marketplace',
    requiresFeature: 'marketplaceAccess',
    requiredTier: 'professional'
  },
  { 
    icon: Users, 
    label: 'Guild Center', 
    href: '/guilds',
    requiresFeature: 'guildAccess',
    requiredTier: 'professional'
  },
  { 
    icon: BarChart, 
    label: 'Analytics', 
    href: '/analytics',
    requiresFeature: 'advancedAnalytics',
    requiredTier: 'professional'
  },
  { icon: Trophy, label: 'Rewards', href: '/rewards' },
];

const toolsMenu: NavItem[] = [
  { 
    icon: Zap, 
    label: 'AI Scanner', 
    href: '/ai-scanner',
    requiresFeature: 'aiScanner',
    requiredTier: 'professional'
  },
  { 
    icon: Code, 
    label: 'API Documentation', 
    href: '/api-docs',
    requiresFeature: 'apiAccess',
    requiredTier: 'professional'
  },
  { 
    icon: Workflow, 
    label: 'Integrations', 
    href: '/integrations',
    requiresFeature: 'slackDiscordIntegration',
    requiredTier: 'professional'
  },
  { icon: FileText, label: 'Reports', href: '/reports' },
];

const accountMenu: NavItem[] = [
  { icon: User, label: 'Profile Settings', href: '/profile' },
  { icon: CreditCard, label: 'Billing', href: '/billing' },
  { icon: Settings, label: 'Preferences', href: '/preferences' },
  { icon: HelpCircle, label: 'Help Center', href: '/help' },
];

export function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [activeItem, setActiveItem] = useState('/dashboard');
  const { user, tier, features } = useSubscription();

  const tierColors: Record<SubscriptionTier, string> = {
    free: 'from-gray-700 to-gray-700',
    starter: 'from-gray-600 to-gray-600',
    professional: 'from-gray-500 to-gray-500',
    enterprise: 'from-white to-white',
  };

  const tierNames: Record<SubscriptionTier, string> = {
    free: 'Free',
    starter: 'Starter',
    professional: 'Pro',
    enterprise: 'Enterprise',
  };

  return (
    <motion.aside
      initial={{ x: -280 }}
      animate={{ 
        x: 0,
        width: isCollapsed ? 80 : 280 
      }}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      className="fixed left-0 top-0 h-screen z-50 bg-black flex flex-col"
      style={{
        backdropFilter: 'blur(20px)',
        borderRight: '1px solid rgba(255, 255, 255, 0.1)',
      }}
    >
      {/* Logo Section */}
      <div 
        className="h-20 flex items-center px-6 border-b flex-shrink-0"
        style={{ borderColor: 'rgba(255, 255, 255, 0.06)' }}
      >
        <AnimatePresence mode="wait">
          {!isCollapsed ? (
            <motion.span
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.2 }}
              className="text-2xl font-bold text-white tracking-tight"
            >
              Ikodio
            </motion.span>
          ) : (
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="text-xl font-bold text-white tracking-tight"
            >
              I
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      {/* Collapse Toggle */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute top-6 -right-3 w-6 h-6 bg-gray-900 rounded-full border border-white/10 flex items-center justify-center hover:scale-110 hover:border-white/30 hover:shadow-lg hover:shadow-white/10 transition-all z-10"
      >
        {isCollapsed ? (
          <ChevronRight className="w-4 h-4 text-white/70" />
        ) : (
          <ChevronLeft className="w-4 h-4 text-white/70" />
        )}
      </button>

      {/* Navigation Sections - Scrollable */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden px-3 py-6 space-y-8" style={{ scrollbarWidth: 'thin', scrollbarColor: 'rgba(255, 255, 255, 0.2) transparent' }}>
        {/* Main Menu */}
        <nav className="space-y-1">
          {mainMenu.map((item) => (
            <NavMenuItem
              key={item.href}
              item={item}
              isCollapsed={isCollapsed}
              isActive={activeItem === item.href}
              onClick={() => setActiveItem(item.href)}
            />
          ))}
        </nav>

        {/* Tools Section */}
        <div>
          {!isCollapsed && (
            <h3 className="px-4 mb-2 text-xs font-semibold text-white/40 uppercase tracking-wider">
              Tools
            </h3>
          )}
          <nav className="space-y-1">
            {toolsMenu.map((item) => (
              <NavMenuItem
                key={item.href}
                item={item}
                isCollapsed={isCollapsed}
                isActive={activeItem === item.href}
                onClick={() => setActiveItem(item.href)}
              />
            ))}
          </nav>
        </div>

        {/* Account Section */}
        <div>
          {!isCollapsed && (
            <h3 className="px-4 mb-2 text-xs font-semibold text-white/40 uppercase tracking-wider">
              Account
            </h3>
          )}
          <nav className="space-y-1">
            {accountMenu.map((item) => (
              <NavMenuItem
                key={item.href}
                item={item}
                isCollapsed={isCollapsed}
                isActive={activeItem === item.href}
                onClick={() => setActiveItem(item.href)}
              />
            ))}
          </nav>
        </div>
      </div>

      {/* User Profile */}
      <div 
        className="flex-shrink-0 w-full p-4 border-t bg-white/5"
        style={{ borderColor: 'rgba(255, 255, 255, 0.06)' }}
      >
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-full border-2 shadow-lg bg-gradient-to-br ${tierColors[tier]} flex items-center justify-center`}>
            <span className="text-white font-semibold text-sm">{user?.fullName?.charAt(0) || 'U'}</span>
          </div>
          <AnimatePresence>
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                className="flex-1 min-w-0"
              >
                <p className="text-sm font-semibold text-white truncate">{user?.fullName || 'User'}</p>
                <div className="flex items-center gap-1">
                  {tier !== 'free' && <Crown className="w-3 h-3 text-white" />}
                  <p className="text-xs text-white/50 capitalize">{tierNames[tier]}</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          {!isCollapsed && (
            <ChevronRight className="w-4 h-4 text-white/40" />
          )}
        </div>
      </div>
    </motion.aside>
  );
}

function NavMenuItem({ 
  item, 
  isCollapsed, 
  isActive, 
  onClick 
}: { 
  item: NavItem; 
  isCollapsed: boolean; 
  isActive: boolean;
  onClick: () => void;
}) {
  const Icon = item.icon;
  const { features } = useSubscription();
  
  const isLocked = item.requiresFeature && !features[item.requiresFeature];
  
  if (isLocked) {
    return (
      <div>
        <motion.div
          className={`
            relative flex items-center gap-3 px-4 py-2.5 mx-2 rounded-lg cursor-not-allowed opacity-50
            text-white/40
          `}
        >
          <Lock className="w-5 h-5" strokeWidth={2} />
          
          <AnimatePresence>
            {!isCollapsed && (
              <motion.span
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                className="text-sm font-medium flex-1"
              >
                {item.label}
              </motion.span>
            )}
          </AnimatePresence>

          {!isCollapsed && (
            <Crown className="w-4 h-4 text-white" />
          )}
        </motion.div>
      </div>
    );
  }
  
  return (
    <Link href={item.href} onClick={onClick}>
      <motion.div
        whileHover={{ x: isActive ? 0 : 4 }}
        className={`
          relative flex items-center gap-3 px-4 py-2.5 mx-2 rounded-lg transition-all cursor-pointer
          ${isActive 
            ? 'bg-gray-800 border-l-3 border-white text-white font-semibold' 
            : 'text-white/60 hover:bg-gray-800 hover:text-white/90'
          }
        `}
        style={isActive ? { borderLeftWidth: '3px', borderLeftColor: '#ffffff' } : {}}
      >
        <motion.div
          whileHover={{ scale: 1.1, rotate: 5 }}
          transition={{ type: "spring", stiffness: 400 }}
        >
          <Icon className="w-5 h-5" strokeWidth={2} />
        </motion.div>
        
        <AnimatePresence>
          {!isCollapsed && (
            <motion.span
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              className="text-sm font-medium flex-1"
            >
              {item.label}
            </motion.span>
          )}
        </AnimatePresence>

        {!isCollapsed && item.badge && (
          <motion.span
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className={`
              px-2 py-0.5 rounded-full text-xs font-bold
              ${item.badgeColor === 'red' 
                ? 'bg-gray-700 text-white shadow-lg shadow-black/30' 
                : 'bg-gray-600 text-white shadow-lg shadow-black/30'
              }
            `}
          >
            {item.badge}
          </motion.span>
        )}
      </motion.div>
    </Link>
  );
}
