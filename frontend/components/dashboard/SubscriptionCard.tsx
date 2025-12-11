'use client';

import { motion } from 'framer-motion';
import { Crown, Zap, TrendingUp, ArrowRight, Target, AlertCircle } from 'lucide-react';
import { useSubscription } from '@/contexts/SubscriptionContext';
import { useRouter } from 'next/navigation';

export function SubscriptionCard() {
  const { user, tier, features } = useSubscription();
  const router = useRouter();

  if (!user) return null;

  const getTierColor = (tier: string) => {
    const colors: Record<string, string> = {
      free: 'from-gray-700 to-gray-700',
      starter: 'from-gray-600 to-gray-600',
      professional: 'from-gray-500 to-gray-500',
      enterprise: 'from-white to-white',
    };
    return colors[tier] || 'from-gray-700 to-gray-700';
  };

  const getTierIcon = (tier: string) => {
    if (tier === 'free') return Zap;
    if (tier === 'enterprise') return Crown;
    return TrendingUp;
  };

  const tierPrices: Record<string, string> = {
    free: 'Rp 0',
    starter: 'Rp 199.000',
    professional: 'Rp 450.000',
    enterprise: 'Custom',
  };

  const TierIcon = getTierIcon(tier);

  const getUsagePercentage = (used: number, limit: number | string) => {
    if (limit === 'unlimited') return 0;
    return Math.min((used / Number(limit)) * 100, 100);
  };

  const isNearLimit = (used: number, limit: number | string) => {
    if (limit === 'unlimited') return false;
    return used / Number(limit) >= 0.8;
  };

  const scanPercentage = getUsagePercentage(user.scansUsedThisMonth, features.maxScansPerMonth);
  const domainPercentage = getUsagePercentage(user.targetDomainsCount, features.maxTargetDomains);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-black backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl overflow-hidden relative"
    >
      <div className={`absolute inset-0 bg-gradient-to-br ${getTierColor(tier)} opacity-5`} />
      
      <div className="relative z-10">
        <div className="flex items-start justify-between mb-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className={`p-2 rounded-lg bg-gradient-to-br ${getTierColor(tier)}`}>
                <TierIcon className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold capitalize text-white">
                  {tier} Plan
                </h3>
                <p className="text-sm text-gray-400">{tierPrices[tier]}/bulan</p>
              </div>
            </div>
          </div>
          {tier !== 'enterprise' && (
            <button 
              onClick={() => router.push('/')}
              className="px-4 py-2 bg-white text-black text-sm font-medium rounded-lg hover:bg-gray-300 transition-all flex items-center gap-2"
            >
              Upgrade
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>

        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-400">Scans</span>
              </div>
              <span className="text-sm font-medium text-white">
                {features.maxScansPerMonth === 'unlimited' 
                  ? `${user.scansUsedThisMonth} used` 
                  : `${user.scansUsedThisMonth} / ${features.maxScansPerMonth}`
                }
              </span>
            </div>
            {features.maxScansPerMonth !== 'unlimited' && (
              <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${scanPercentage}%` }}
                  transition={{ duration: 1, ease: 'easeOut' }}
                  className={`h-full rounded-full ${
                    isNearLimit(user.scansUsedThisMonth, features.maxScansPerMonth)
                      ? 'bg-gray-600'
                      : 'bg-white'
                  }`}
                />
              </div>
            )}
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">Target Domains</span>
              <span className="text-sm font-medium text-white">
                {features.maxTargetDomains === 'unlimited' 
                  ? `${user.targetDomainsCount} active` 
                  : `${user.targetDomainsCount} / ${features.maxTargetDomains}`
                }
              </span>
            </div>
            {features.maxTargetDomains !== 'unlimited' && (
              <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${domainPercentage}%` }}
                  transition={{ duration: 1, ease: 'easeOut', delay: 0.2 }}
                  className={`h-full rounded-full ${
                    isNearLimit(user.targetDomainsCount, features.maxTargetDomains)
                      ? 'bg-gray-600'
                      : 'bg-white'
                  }`}
                />
              </div>
            )}
          </div>

          <div className="pt-4 border-t border-gray-700">
            <h4 className="text-xs font-semibold text-gray-400 mb-3 uppercase tracking-wider">Active Features</h4>
            <div className="space-y-2">
              {features.apiAccess && (
                <div className="flex items-center gap-2 text-sm text-gray-300">
                  <div className="w-1.5 h-1.5 bg-white rounded-full" />
                  <span>API Access</span>
                </div>
              )}
              {features.aiScanner && (
                <div className="flex items-center gap-2 text-sm text-gray-300">
                  <div className="w-1.5 h-1.5 bg-white rounded-full" />
                  <span>AI Scanner</span>
                </div>
              )}
              {features.marketplaceAccess && (
                <div className="flex items-center gap-2 text-sm text-gray-300">
                  <div className="w-1.5 h-1.5 bg-white rounded-full" />
                  <span>Marketplace</span>
                </div>
              )}
              {features.guildAccess && (
                <div className="flex items-center gap-2 text-sm text-gray-300">
                  <div className="w-1.5 h-1.5 bg-white rounded-full" />
                  <span>Guild Access</span>
                </div>
              )}
            </div>
          </div>

          {(isNearLimit(user.scansUsedThisMonth, features.maxScansPerMonth) || 
            isNearLimit(user.targetDomainsCount, features.maxTargetDomains)) && (
            <div className="flex items-start gap-2 p-3 bg-gray-800 border border-gray-700 rounded-lg mt-4">
              <AlertCircle className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" />
              <p className="text-xs text-gray-300">
                You are approaching your plan limits. Consider upgrading for more resources.
              </p>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
