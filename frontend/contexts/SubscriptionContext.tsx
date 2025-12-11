'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

export type SubscriptionTier = 'free' | 'starter' | 'professional' | 'enterprise'

export interface SubscriptionFeatures {
  // Scanning limits
  maxScansPerMonth: number | 'unlimited'
  maxTargetDomains: number | 'unlimited'
  scheduledScans: boolean
  
  // Scanner access
  basicScanner: boolean // Nuclei
  advancedScanner: boolean // ZAP
  aiScanner: boolean // AI-powered
  customScanner: boolean
  
  // Reports
  pdfReports: boolean
  htmlReports: boolean
  customReportTemplate: boolean
  complianceReports: boolean // ISO, PCI-DSS
  exportData: boolean // JSON, CSV, XML
  
  // Features
  apiAccess: boolean
  webhooks: boolean
  realTimeAlerts: boolean
  emailNotifications: boolean
  
  // Community
  guildAccess: boolean
  marketplaceAccess: boolean
  
  // Analytics
  basicAnalytics: boolean
  advancedAnalytics: boolean
  threatIntelligence: boolean
  
  // Support
  communitySupport: boolean
  emailSupport: boolean
  prioritySupport: boolean
  dedicatedExpert: boolean
  
  // Team
  maxTeamMembers: number | 'unlimited'
  teamCollaboration: boolean
  
  // History
  scanHistoryDays: number | 'unlimited'
  
  // Integrations
  slackDiscordIntegration: boolean
  customIntegrations: boolean
  ssoLdap: boolean
  
  // Enterprise
  onPremise: boolean
  whiteLabel: boolean
  customAI: boolean
  multiRegion: boolean
  sla: boolean
}

interface User {
  id: string
  email: string
  fullName: string
  tier: SubscriptionTier
  subscriptionStartDate: string
  subscriptionEndDate?: string
  scansUsedThisMonth: number
  targetDomainsCount: number
}

interface SubscriptionContextType {
  user: User | null
  tier: SubscriptionTier
  features: SubscriptionFeatures
  isLoading: boolean
  hasFeature: (feature: keyof SubscriptionFeatures) => boolean
  canUseScan: () => boolean
  canAddDomain: () => boolean
  refreshUser: () => Promise<void>
}

const SubscriptionContext = createContext<SubscriptionContextType | undefined>(undefined)

const tierFeatures: Record<SubscriptionTier, SubscriptionFeatures> = {
  free: {
    maxScansPerMonth: 5,
    maxTargetDomains: 2,
    scheduledScans: false,
    basicScanner: true,
    advancedScanner: false,
    aiScanner: false,
    customScanner: false,
    pdfReports: true,
    htmlReports: false,
    customReportTemplate: false,
    complianceReports: false,
    exportData: false,
    apiAccess: false,
    webhooks: false,
    realTimeAlerts: false,
    emailNotifications: false,
    guildAccess: false,
    marketplaceAccess: false,
    basicAnalytics: true,
    advancedAnalytics: false,
    threatIntelligence: false,
    communitySupport: true,
    emailSupport: false,
    prioritySupport: false,
    dedicatedExpert: false,
    maxTeamMembers: 1,
    teamCollaboration: false,
    scanHistoryDays: 30,
    slackDiscordIntegration: false,
    customIntegrations: false,
    ssoLdap: false,
    onPremise: false,
    whiteLabel: false,
    customAI: false,
    multiRegion: false,
    sla: false
  },
  starter: {
    maxScansPerMonth: 25,
    maxTargetDomains: 5,
    scheduledScans: false,
    basicScanner: true,
    advancedScanner: true,
    aiScanner: false,
    customScanner: false,
    pdfReports: true,
    htmlReports: true,
    customReportTemplate: false,
    complianceReports: false,
    exportData: false,
    apiAccess: false,
    webhooks: false,
    realTimeAlerts: false,
    emailNotifications: true,
    guildAccess: false,
    marketplaceAccess: false,
    basicAnalytics: true,
    advancedAnalytics: false,
    threatIntelligence: false,
    communitySupport: true,
    emailSupport: true,
    prioritySupport: false,
    dedicatedExpert: false,
    maxTeamMembers: 1,
    teamCollaboration: false,
    scanHistoryDays: 30,
    slackDiscordIntegration: false,
    customIntegrations: false,
    ssoLdap: false,
    onPremise: false,
    whiteLabel: false,
    customAI: false,
    multiRegion: false,
    sla: false
  },
  professional: {
    maxScansPerMonth: 100,
    maxTargetDomains: 'unlimited',
    scheduledScans: true,
    basicScanner: true,
    advancedScanner: true,
    aiScanner: true,
    customScanner: false,
    pdfReports: true,
    htmlReports: true,
    customReportTemplate: true,
    complianceReports: false,
    exportData: true,
    apiAccess: true,
    webhooks: true,
    realTimeAlerts: true,
    emailNotifications: true,
    guildAccess: true,
    marketplaceAccess: true,
    basicAnalytics: true,
    advancedAnalytics: true,
    threatIntelligence: false,
    communitySupport: true,
    emailSupport: true,
    prioritySupport: true,
    dedicatedExpert: false,
    maxTeamMembers: 5,
    teamCollaboration: true,
    scanHistoryDays: 'unlimited',
    slackDiscordIntegration: true,
    customIntegrations: false,
    ssoLdap: false,
    onPremise: false,
    whiteLabel: false,
    customAI: false,
    multiRegion: false,
    sla: false
  },
  enterprise: {
    maxScansPerMonth: 'unlimited',
    maxTargetDomains: 'unlimited',
    scheduledScans: true,
    basicScanner: true,
    advancedScanner: true,
    aiScanner: true,
    customScanner: true,
    pdfReports: true,
    htmlReports: true,
    customReportTemplate: true,
    complianceReports: true,
    exportData: true,
    apiAccess: true,
    webhooks: true,
    realTimeAlerts: true,
    emailNotifications: true,
    guildAccess: true,
    marketplaceAccess: true,
    basicAnalytics: true,
    advancedAnalytics: true,
    threatIntelligence: true,
    communitySupport: true,
    emailSupport: true,
    prioritySupport: true,
    dedicatedExpert: true,
    maxTeamMembers: 'unlimited',
    teamCollaboration: true,
    scanHistoryDays: 'unlimited',
    slackDiscordIntegration: true,
    customIntegrations: true,
    ssoLdap: true,
    onPremise: true,
    whiteLabel: true,
    customAI: true,
    multiRegion: true,
    sla: true
  }
}

export function SubscriptionProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const loadUser = async () => {
    setIsLoading(true)
    try {
      // Simulate API call - replace with actual API
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Mock user data - replace with actual auth
      const mockUser: User = {
        id: '1',
        email: 'user@example.com',
        fullName: 'John Doe',
        tier: 'professional', // Change this to test different tiers
        subscriptionStartDate: '2025-01-01',
        subscriptionEndDate: '2026-01-01',
        scansUsedThisMonth: 15,
        targetDomainsCount: 3
      }
      
      setUser(mockUser)
    } catch (error) {
      console.error('Failed to load user:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadUser()
  }, [])

  const tier = user?.tier || 'free'
  const features = tierFeatures[tier]

  const hasFeature = (feature: keyof SubscriptionFeatures): boolean => {
    return features[feature] as boolean
  }

  const canUseScan = (): boolean => {
    if (!user) return false
    if (features.maxScansPerMonth === 'unlimited') return true
    return user.scansUsedThisMonth < (features.maxScansPerMonth as number)
  }

  const canAddDomain = (): boolean => {
    if (!user) return false
    if (features.maxTargetDomains === 'unlimited') return true
    return user.targetDomainsCount < (features.maxTargetDomains as number)
  }

  const refreshUser = async () => {
    await loadUser()
  }

  return (
    <SubscriptionContext.Provider
      value={{
        user,
        tier,
        features,
        isLoading,
        hasFeature,
        canUseScan,
        canAddDomain,
        refreshUser
      }}
    >
      {children}
    </SubscriptionContext.Provider>
  )
}

export function useSubscription() {
  const context = useContext(SubscriptionContext)
  if (context === undefined) {
    throw new Error('useSubscription must be used within a SubscriptionProvider')
  }
  return context
}
