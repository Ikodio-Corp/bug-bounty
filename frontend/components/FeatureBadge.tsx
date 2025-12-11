'use client';

import { motion } from 'framer-motion';
import { Lock, Zap, Crown } from 'lucide-react';
import { useState } from 'react';

interface FeatureBadgeProps {
  feature: string;
  requiredTier: 'PROFESSIONAL' | 'BUSINESS' | 'ENTERPRISE' | 'GOVERNMENT';
  currentTier: string;
  disabled?: boolean;
  children?: React.ReactNode;
  onUpgradeClick?: () => void;
}

const TIER_DETAILS: Record<string, { name: string; color: string; icon: any }> = {
  PROFESSIONAL: { name: 'Professional', color: 'blue-500', icon: Zap },
  BUSINESS: { name: 'Business', color: 'purple-500', icon: Crown },
  ENTERPRISE: { name: 'Enterprise', color: 'orange-500', icon: Crown },
  GOVERNMENT: { name: 'Government', color: 'green-500', icon: Crown },
};

export default function FeatureBadge({
  feature,
  requiredTier,
  currentTier,
  disabled = false,
  children,
  onUpgradeClick,
}: FeatureBadgeProps) {
  const [showTooltip, setShowTooltip] = useState(false);
  
  const tierDetails = TIER_DETAILS[requiredTier];
  const TierIcon = tierDetails?.icon || Lock;
  
  // Check if user has access
  const tierHierarchy = ['FREE', 'PROFESSIONAL', 'BUSINESS', 'ENTERPRISE', 'GOVERNMENT'];
  const currentTierIndex = tierHierarchy.indexOf(currentTier);
  const requiredTierIndex = tierHierarchy.indexOf(requiredTier);
  const hasAccess = currentTierIndex >= requiredTierIndex;

  if (hasAccess) {
    return <>{children}</>;
  }

  return (
    <div className="relative inline-block">
      {/* Disabled content wrapper */}
      <div
        className={`relative ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        {children}
        
        {disabled && (
          <div className="absolute inset-0 bg-gray-900/20 backdrop-blur-[1px] rounded-lg flex items-center justify-center">
            <Lock className="w-6 h-6 text-gray-400" />
          </div>
        )}
      </div>

      {/* Tooltip */}
      {showTooltip && (
        <motion.div
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 5 }}
          className="absolute z-50 bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-64"
        >
          <div className="bg-gray-800 border border-gray-700 rounded-lg shadow-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className={`w-8 h-8 bg-${tierDetails.color}/20 rounded-full flex items-center justify-center`}>
                <TierIcon className={`w-4 h-4 text-${tierDetails.color}`} />
              </div>
              <div>
                <p className="text-white font-semibold text-sm">{feature}</p>
                <p className="text-gray-400 text-xs">Requires {tierDetails.name}</p>
              </div>
            </div>
            
            <p className="text-gray-300 text-xs mb-3">
              Upgrade ke {tierDetails.name} untuk mengakses fitur ini
            </p>

            {onUpgradeClick && (
              <button
                onClick={onUpgradeClick}
                className={`w-full py-2 bg-${tierDetails.color} text-white text-sm font-semibold rounded-lg hover:opacity-90 transition-opacity flex items-center justify-center gap-2`}
              >
                <Zap className="w-4 h-4" />
                <span>Upgrade Sekarang</span>
              </button>
            )}
          </div>
          
          {/* Arrow */}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-px">
            <div className="border-8 border-transparent border-t-gray-800"></div>
          </div>
        </motion.div>
      )}
    </div>
  );
}

// Badge variant for feature lists
export function FeatureRequiredBadge({ 
  requiredTier 
}: { 
  requiredTier: 'PROFESSIONAL' | 'BUSINESS' | 'ENTERPRISE' | 'GOVERNMENT' 
}) {
  const tierDetails = TIER_DETAILS[requiredTier];
  const TierIcon = tierDetails?.icon || Lock;

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 bg-${tierDetails.color}/20 border border-${tierDetails.color}/30 rounded-full text-xs font-semibold text-${tierDetails.color}`}>
      <TierIcon className="w-3 h-3" />
      <span>{tierDetails.name}</span>
    </span>
  );
}
