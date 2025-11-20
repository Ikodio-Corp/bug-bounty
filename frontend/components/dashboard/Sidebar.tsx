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
} from 'lucide-react';

interface NavItem {
  icon: any;
  label: string;
  href: string;
  badge?: string | number;
  badgeColor?: string;
}

const mainMenu: NavItem[] = [
  { icon: Home, label: 'Dashboard', href: '/dashboard' },
  { icon: Search, label: 'Scan Management', href: '/scans', badge: 3, badgeColor: 'blue' },
  { icon: Shield, label: 'Vulnerabilities', href: '/bugs', badge: 12, badgeColor: 'red' },
  { icon: ShoppingBag, label: 'Marketplace', href: '/marketplace' },
  { icon: Users, label: 'Guild Center', href: '/guilds' },
  { icon: BarChart, label: 'Analytics', href: '/analytics' },
  { icon: Trophy, label: 'Rewards', href: '/rewards' },
];

const toolsMenu: NavItem[] = [
  { icon: Zap, label: 'AI Scanner', href: '/ai-scanner' },
  { icon: Code, label: 'API Documentation', href: '/api-docs' },
  { icon: Workflow, label: 'Integrations', href: '/integrations' },
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

  return (
    <motion.aside
      initial={{ x: -280 }}
      animate={{ 
        x: 0,
        width: isCollapsed ? 80 : 280 
      }}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      className="fixed left-0 top-0 h-screen z-50 bg-gradient-to-b from-slate-900 to-slate-800 flex flex-col"
      style={{
        backdropFilter: 'blur(20px)',
        borderRight: '1px solid rgba(255, 255, 255, 0.06)',
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
        className="absolute top-6 -right-3 w-6 h-6 bg-slate-800 rounded-full border border-white/10 flex items-center justify-center hover:scale-110 hover:border-blue-500/50 hover:shadow-lg hover:shadow-blue-500/30 transition-all z-10"
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
          <div className="w-10 h-10 rounded-full border-2 border-blue-500/50 shadow-lg shadow-blue-500/30 bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
            <span className="text-white font-semibold text-sm">H</span>
          </div>
          <AnimatePresence>
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                className="flex-1 min-w-0"
              >
                <p className="text-sm font-semibold text-white truncate">Hylmii</p>
                <p className="text-xs text-white/50">Pro Member</p>
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
  
  return (
    <Link href={item.href} onClick={onClick}>
      <motion.div
        whileHover={{ x: isActive ? 0 : 4 }}
        className={`
          relative flex items-center gap-3 px-4 py-2.5 mx-2 rounded-lg transition-all cursor-pointer
          ${isActive 
            ? 'bg-gradient-to-r from-blue-500/15 to-transparent border-l-3 border-blue-500 text-white font-semibold' 
            : 'text-white/60 hover:bg-white/5 hover:text-white/90'
          }
        `}
        style={isActive ? { borderLeftWidth: '3px', borderLeftColor: '#3b82f6' } : {}}
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
                ? 'bg-gradient-to-r from-red-500 to-red-600 text-white shadow-lg shadow-red-500/30' 
                : 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-500/30'
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
