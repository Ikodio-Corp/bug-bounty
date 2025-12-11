'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { X, Zap, Check, ArrowRight, TrendingUp, Shield, Sparkles } from 'lucide-react';
import Link from 'next/link';

interface UpgradePromptProps {
  isOpen: boolean;
  onClose: () => void;
  reason: string;
  currentTier: string;
  suggestedTier: string;
  limitType: 'scans' | 'autofixes' | 'api' | 'storage' | 'team' | 'marketplace';
  currentUsage?: number;
  limit?: number;
}

const TIER_DETAILS: Record<string, {
  name: string;
  price: string;
  color: string;
  gradient: string;
  icon: any;
  features: string[];
  limits: {
    scans: string;
    autofixes: string;
    api: string;
    storage: string;
  };
}> = {
  FREE: {
    name: 'Free',
    price: 'Rp 0',
    color: 'gray',
    gradient: 'from-gray-500 to-gray-600',
    icon: Sparkles,
    features: ['10 scans/bulan', 'Tanpa auto-fix', 'Community support'],
    limits: { scans: '10', autofixes: '0', api: '0', storage: '100 MB' },
  },
  PROFESSIONAL: {
    name: 'Professional',
    price: 'Rp 450.000',
    color: 'blue',
    gradient: 'from-gray-500 to-white',
    icon: Zap,
    features: [
      '100 scans/bulan',
      '10 auto-fixes/bulan',
      '10,000 API requests',
      '10 GB storage',
      'Priority support',
      'AI-powered insights',
    ],
    limits: { scans: '100', autofixes: '10', api: '10,000', storage: '10 GB' },
  },
  BUSINESS: {
    name: 'Business',
    price: 'Rp 1.500.000',
    color: 'purple',
    gradient: 'from-gray-400 to-gray-500',
    icon: TrendingUp,
    features: [
      '300 scans/bulan',
      'Unlimited auto-fixes',
      '100,000 API requests',
      '100 GB storage',
      '24/7 support',
      'Team collaboration (10 members)',
      'Custom integrations',
      'White-label reports',
    ],
    limits: { scans: '300', autofixes: 'Unlimited', api: '100,000', storage: '100 GB' },
  },
  ENTERPRISE: {
    name: 'Enterprise',
    price: 'Rp 10.000.000',
    color: 'orange',
    gradient: 'from-yellow-500 to-orange-600',
    icon: Shield,
    features: [
      'Unlimited scans',
      'Unlimited auto-fixes',
      'Unlimited API requests',
      '1 TB storage',
      'Dedicated support',
      'Unlimited team members',
      'On-premise deployment',
      'SLA guarantees',
      'Custom training',
    ],
    limits: { scans: 'Unlimited', autofixes: 'Unlimited', api: 'Unlimited', storage: '1 TB' },
  },
};

const LIMIT_MESSAGES: Record<string, string> = {
  scans: 'Anda telah mencapai limit scan bulanan',
  autofixes: 'Auto-fix tidak tersedia di plan Anda',
  api: 'API request limit tercapai',
  storage: 'Storage limit tercapai',
  team: 'Team member limit tercapai',
  marketplace: 'Marketplace access tidak tersedia',
};

export default function UpgradePrompt({
  isOpen,
  onClose,
  reason,
  currentTier,
  suggestedTier,
  limitType,
  currentUsage,
  limit,
}: UpgradePromptProps) {
  const currentDetails = TIER_DETAILS[currentTier] || TIER_DETAILS.FREE;
  const suggestedDetails = TIER_DETAILS[suggestedTier] || TIER_DETAILS.PROFESSIONAL;
  const SuggestedIcon = suggestedDetails.icon;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div className="bg-gray-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-gray-700">
              {/* Header */}
              <div className={`relative bg-gradient-to-r ${suggestedDetails.gradient} p-6 rounded-t-2xl`}>
                <button
                  onClick={onClose}
                  className="absolute top-4 right-4 text-white/80 hover:text-white transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>

                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
                    <SuggestedIcon className="w-8 h-8 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-white mb-1">Upgrade to {suggestedDetails.name}</h2>
                    <p className="text-white/80">{LIMIT_MESSAGES[limitType]}</p>
                  </div>
                </div>
              </div>

              {/* Content */}
              <div className="p-6 space-y-6">
                {/* Usage Info */}
                {currentUsage !== undefined && limit !== undefined && (
                  <div className="bg-gray-700/50 rounded-lg p-4 border border-gray-600">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-gray-300">Current Usage</span>
                      <span className="text-white font-semibold">
                        {currentUsage} / {limit}
                      </span>
                    </div>
                    <div className="w-full bg-gray-600 rounded-full h-2">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min((currentUsage / limit) * 100, 100)}%` }}
                        className={`h-2 rounded-full bg-gradient-to-r ${suggestedDetails.gradient}`}
                      />
                    </div>
                  </div>
                )}

                {/* Reason Message */}
                <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
                  <p className="text-yellow-200 text-sm">{reason}</p>
                </div>

                {/* Comparison */}
                <div className="grid grid-cols-2 gap-4">
                  {/* Current Tier */}
                  <div className="bg-gray-700/30 rounded-lg p-4 border border-gray-600">
                    <h3 className="text-white font-semibold mb-2">{currentDetails.name}</h3>
                    <p className="text-gray-400 text-2xl font-bold mb-3">{currentDetails.price}/mo</p>
                    <div className="space-y-2">
                      {Object.entries(currentDetails.limits).map(([key, value]) => (
                        <div key={key} className="text-sm text-gray-400">
                          <span className="capitalize">{key}:</span> {value}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Suggested Tier */}
                  <div className={`bg-gradient-to-br ${suggestedDetails.gradient} rounded-lg p-4 border-2 border-white/20 relative overflow-hidden`}>
                    <div className="absolute top-2 right-2 bg-white/20 backdrop-blur-sm px-2 py-1 rounded text-xs font-semibold text-white">
                      RECOMMENDED
                    </div>
                    <h3 className="text-white font-semibold mb-2">{suggestedDetails.name}</h3>
                    <p className="text-white text-2xl font-bold mb-3">{suggestedDetails.price}/mo</p>
                    <div className="space-y-2">
                      {Object.entries(suggestedDetails.limits).map(([key, value]) => (
                        <div key={key} className="text-sm text-white/90">
                          <span className="capitalize">{key}:</span> <strong>{value}</strong>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Features */}
                <div>
                  <h3 className="text-white font-semibold mb-3">What you'll get with {suggestedDetails.name}:</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {suggestedDetails.features.map((feature, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="flex items-center gap-2 text-gray-300"
                      >
                        <Check className="w-5 h-5 text-green-400 flex-shrink-0" />
                        <span className="text-sm">{feature}</span>
                      </motion.div>
                    ))}
                  </div>
                </div>

                {/* ROI Banner */}
                {suggestedTier === 'PROFESSIONAL' && (
                  <div className="bg-gradient-to-r from-white/10 to-white/5 border border-green-500/30 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                      <TrendingUp className="w-6 h-6 text-green-400" />
                      <div>
                        <p className="text-white font-semibold">ROI hingga 789%</p>
                        <p className="text-gray-300 text-sm">Temukan 1 critical bug = ROI tercapai!</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* CTA Buttons */}
                <div className="flex gap-3">
                  <Link
                    href={`/pricing?highlight=${suggestedTier.toLowerCase()}`}
                    className="flex-1"
                  >
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className={`w-full py-3 bg-gradient-to-r ${suggestedDetails.gradient} text-white font-semibold rounded-lg hover:shadow-lg transition-all duration-300 flex items-center justify-center gap-2`}
                    >
                      <span>Upgrade Sekarang</span>
                      <ArrowRight className="w-5 h-5" />
                    </motion.button>
                  </Link>
                  <button
                    onClick={onClose}
                    className="px-6 py-3 bg-gray-700 text-gray-300 font-semibold rounded-lg hover:bg-gray-600 transition-colors"
                  >
                    Nanti
                  </button>
                </div>

                {/* Trial Banner */}
                {suggestedTier === 'PROFESSIONAL' && (
                  <div className="text-center">
                    <p className="text-gray-400 text-sm">
                       Trial GRATIS 14 hari - Tanpa kartu kredit
                    </p>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
