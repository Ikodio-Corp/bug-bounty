'use client'

import { ReactNode, useState } from 'react'
import { Lock, Crown, TrendingUp, ArrowRight, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { useSubscription, SubscriptionTier } from '@/contexts/SubscriptionContext'

interface FeatureLockedProps {
  feature: string
  requiredTier: SubscriptionTier
  children: ReactNode
  showUpgrade?: boolean
  blur?: boolean
}

export function FeatureLocked({ 
  feature, 
  requiredTier, 
  children, 
  showUpgrade = true,
  blur = true 
}: FeatureLockedProps) {
  const { tier, hasFeature } = useSubscription()
  const [showModal, setShowModal] = useState(false)
  const router = useRouter()

  const tierNames: Record<SubscriptionTier, string> = {
    free: 'Free',
    starter: 'Starter',
    professional: 'Professional',
    enterprise: 'Enterprise'
  }

  const tierPrices: Record<SubscriptionTier, string> = {
    free: 'Rp 0',
    starter: 'Rp 199.000',
    professional: 'Rp 450.000',
    enterprise: 'Custom'
  }

  const tierOrder: SubscriptionTier[] = ['free', 'starter', 'professional', 'enterprise']
  const currentIndex = tierOrder.indexOf(tier)
  const requiredIndex = tierOrder.indexOf(requiredTier)
  const isLocked = currentIndex < requiredIndex

  if (!isLocked) {
    return <>{children}</>
  }

  return (
    <>
      <div className="relative group">
        <div className={blur ? 'filter blur-sm pointer-events-none select-none' : 'pointer-events-none select-none opacity-50'}>
          {children}
        </div>
        
        {showUpgrade && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/60 backdrop-blur-sm rounded-xl">
            <motion.button
              onClick={() => setShowModal(true)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-amber-500 to-orange-600 text-white rounded-xl font-semibold shadow-lg shadow-amber-500/25"
            >
              <Crown className="w-5 h-5" />
              <span>Upgrade to {tierNames[requiredTier]}</span>
            </motion.button>
          </div>
        )}
      </div>

      <AnimatePresence>
        {showModal && (
          <UpgradeModal
            feature={feature}
            currentTier={tier}
            requiredTier={requiredTier}
            onClose={() => setShowModal(false)}
          />
        )}
      </AnimatePresence>
    </>
  )
}

interface UpgradeModalProps {
  feature: string
  currentTier: SubscriptionTier
  requiredTier: SubscriptionTier
  onClose: () => void
}

function UpgradeModal({ feature, currentTier, requiredTier, onClose }: UpgradeModalProps) {
  const router = useRouter()

  const tierInfo: Record<SubscriptionTier, { name: string; price: string; color: string; features: string[] }> = {
    free: {
      name: 'Free',
      price: 'Rp 0/bulan',
      color: 'from-gray-500 to-gray-600',
      features: ['5 scan/bulan', 'Basic scanner', 'PDF reports', 'Community support']
    },
    starter: {
      name: 'Starter',
      price: 'Rp 199.000/bulan',
      color: 'from-gray-500 to-gray-600',
      features: ['25 scan/bulan', 'Advanced scanners', 'HTML reports', 'Email support']
    },
    professional: {
      name: 'Professional',
      price: 'Rp 450.000/bulan',
      color: 'from-amber-500 to-orange-600',
      features: ['100 scan/bulan', 'AI Scanner', 'API access', 'Priority support', 'Guild & Marketplace']
    },
    enterprise: {
      name: 'Enterprise',
      price: 'Custom',
      color: 'from-gray-400 to-gray-500',
      features: ['Unlimited scans', 'Custom AI', 'White-label', 'Dedicated expert', 'SLA 99.9%']
    }
  }

  const handleUpgrade = () => {
    router.push(`/payment?tier=${requiredTier}&upgrade=true`)
  }

  const requiredInfo = tierInfo[requiredTier]

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.9, y: 20 }}
        onClick={(e) => e.stopPropagation()}
        className="bg-slate-900 border border-white/10 rounded-2xl p-8 max-w-lg w-full relative"
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
        >
          <X className="w-6 h-6" />
        </button>

        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-amber-500/20 to-orange-600/20 rounded-full mb-4">
            <Lock className="w-8 h-8 text-amber-500" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Feature Locked</h2>
          <p className="text-gray-400">
            <span className="text-white font-semibold">{feature}</span> is available in {requiredInfo.name} plan
          </p>
        </div>

        <div className={`bg-gradient-to-br ${requiredInfo.color} rounded-xl p-6 mb-6`}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-2xl font-bold text-white">{requiredInfo.name}</h3>
            <div className="text-right">
              <div className="text-2xl font-bold text-white">{requiredInfo.price}</div>
            </div>
          </div>
          
          <ul className="space-y-2">
            {requiredInfo.features.map((feat, index) => (
              <li key={index} className="flex items-center gap-2 text-white/90">
                <div className="w-1.5 h-1.5 bg-white rounded-full" />
                <span>{feat}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-6 py-3 bg-white/5 border border-white/10 text-white rounded-xl hover:bg-white/10 transition-colors"
          >
            Cancel
          </button>
          <motion.button
            onClick={handleUpgrade}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className={`flex-1 px-6 py-3 bg-gradient-to-r ${requiredInfo.color} text-white rounded-xl font-semibold flex items-center justify-center gap-2`}
          >
            <TrendingUp className="w-5 h-5" />
            <span>Upgrade Now</span>
            <ArrowRight className="w-5 h-5" />
          </motion.button>
        </div>
      </motion.div>
    </motion.div>
  )
}

interface InlineFeatureLockedProps {
  feature: string
  requiredTier: SubscriptionTier
  compact?: boolean
}

export function InlineFeatureLocked({ feature, requiredTier, compact = false }: InlineFeatureLockedProps) {
  const [showModal, setShowModal] = useState(false)
  const router = useRouter()

  const tierNames: Record<SubscriptionTier, string> = {
    free: 'Free',
    starter: 'Starter',
    professional: 'Professional',
    enterprise: 'Enterprise'
  }

  if (compact) {
    return (
      <>
        <motion.button
          onClick={() => setShowModal(true)}
          whileHover={{ scale: 1.02 }}
          className="inline-flex items-center gap-2 px-3 py-1.5 bg-amber-500/10 border border-amber-500/20 text-amber-400 rounded-lg text-sm hover:bg-amber-500/20 transition-colors"
        >
          <Lock className="w-4 h-4" />
          <span>{tierNames[requiredTier]}</span>
        </motion.button>

        <AnimatePresence>
          {showModal && (
            <UpgradeModal
              feature={feature}
              currentTier="free"
              requiredTier={requiredTier}
              onClose={() => setShowModal(false)}
            />
          )}
        </AnimatePresence>
      </>
    )
  }

  return (
    <>
      <motion.button
        onClick={() => setShowModal(true)}
        whileHover={{ scale: 1.02 }}
        className="flex items-center gap-3 px-4 py-3 bg-gradient-to-r from-amber-500/10 to-orange-600/10 border border-amber-500/20 rounded-xl hover:border-amber-500/40 transition-all"
      >
        <Lock className="w-5 h-5 text-amber-500" />
        <div className="text-left flex-1">
          <div className="text-sm font-semibold text-white">{feature}</div>
          <div className="text-xs text-gray-400">Requires {tierNames[requiredTier]} plan</div>
        </div>
        <Crown className="w-5 h-5 text-amber-500" />
      </motion.button>

      <AnimatePresence>
        {showModal && (
          <UpgradeModal
            feature={feature}
            currentTier="free"
            requiredTier={requiredTier}
            onClose={() => setShowModal(false)}
          />
        )}
      </AnimatePresence>
    </>
  )
}

interface ScanLimitIndicatorProps {
  className?: string
}

export function ScanLimitIndicator({ className = '' }: ScanLimitIndicatorProps) {
  const { user, features, canUseScan } = useSubscription()
  
  if (!user) return null

  const maxScans = features.maxScansPerMonth
  const usedScans = user.scansUsedThisMonth
  const isUnlimited = maxScans === 'unlimited'
  const percentage = isUnlimited ? 100 : (usedScans / (maxScans as number)) * 100
  const remaining = isUnlimited ? 'Unlimited' : `${(maxScans as number) - usedScans} left`

  return (
    <div className={`bg-white/5 border border-white/10 rounded-xl p-4 ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="text-sm font-medium text-gray-300">Scan Usage</div>
        <div className="text-sm font-bold text-white">{remaining}</div>
      </div>
      
      {!isUnlimited && (
        <>
          <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden mb-2">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${percentage}%` }}
              className={`h-full ${percentage > 80 ? 'bg-red-500' : percentage > 50 ? 'bg-amber-500' : 'bg-green-500'}`}
            />
          </div>
          <div className="text-xs text-gray-400">
            {usedScans} / {maxScans} scans used this month
          </div>
        </>
      )}
      
      {isUnlimited && (
        <div className="text-xs text-green-400 flex items-center gap-1">
          <Crown className="w-3 h-3" />
          <span>Unlimited scans available</span>
        </div>
      )}

      {!canUseScan() && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-3 p-2 bg-red-500/10 border border-red-500/20 rounded-lg"
        >
          <p className="text-xs text-red-400">Scan limit reached. Upgrade to continue scanning.</p>
        </motion.div>
      )}
    </div>
  )
}
