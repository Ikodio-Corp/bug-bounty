'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Check, X, CreditCard, Shield, Clock } from 'lucide-react'
import { api } from '@/lib/api'
import { useRouter, useSearchParams } from 'next/navigation'

interface PricingTier {
  name: string
  monthly: {
    price: number
    price_formatted: string
    features: string[]
  }
  yearly: {
    price: number
    price_formatted: string
    save: number
    features: string[]
  }
}

interface PricingData {
  currency: string
  tiers: {
    [key: string]: PricingTier
  }
}

export default function PaymentPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const selectedTier = searchParams.get('tier') || 'professional'
  
  const [pricingData, setPricingData] = useState<PricingData | null>(null)
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchPricing()
  }, [])

  const fetchPricing = async () => {
    try {
      console.log('Fetching pricing data...')
      const response = await api.get('/payments/pricing')
      console.log('Pricing data:', response.data)
      setPricingData(response.data)
    } catch (err: any) {
      console.error('Error fetching pricing:', err)
      console.error('Error details:', err.response?.data)
      const errorDetail = err.response?.data?.detail
      const errorMessage = typeof errorDetail === 'string' 
        ? errorDetail 
        : (typeof errorDetail === 'object' ? JSON.stringify(errorDetail) : err.message)
      setError('Failed to load pricing: ' + errorMessage)
    }
  }

  const handlePayment = async (tier: string) => {
    // Check if user is logged in
    const token = localStorage.getItem('access_token')
    if (!token) {
      // Redirect to login with return URL
      router.push(`/login?redirect=/payment&tier=${tier}`)
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await api.post('/payments/create', {
        tier,
        billing_cycle: billingCycle
      })

      // Redirect to Doku payment page
      if (response.data.payment_url) {
        window.location.href = response.data.payment_url
      } else {
        throw new Error('No payment URL received')
      }
    } catch (err: any) {
      const errorDetail = err.response?.data?.detail
      const errorMessage = typeof errorDetail === 'string' 
        ? errorDetail 
        : (typeof errorDetail === 'object' ? JSON.stringify(errorDetail) : 'Payment failed. Please try again.')
      setError(errorMessage)
      setLoading(false)
    }
  }

  if (!pricingData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-900 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-white text-xl mb-4">Loading pricing...</div>
          {error && (
            <div className="text-red-400 text-sm max-w-md mx-auto">
              {error}
              <button 
                onClick={fetchPricing}
                className="block mt-4 mx-auto px-4 py-2 bg-white hover:bg-gray-200 rounded-lg transition-colors"
              >
                Retry
              </button>
            </div>
          )}
        </div>
      </div>
    )
  }

  const currentTierData = pricingData.tiers[selectedTier]
  if (!currentTierData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-900 to-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Invalid tier selected</div>
      </div>
    )
  }
  
  const currentPrice = currentTierData[billingCycle]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-900 to-gray-900 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Complete Your Purchase
          </h1>
          <p className="text-xl text-gray-300">
            Upgrade to {currentTierData.name} Plan
          </p>
        </motion.div>

        {/* Billing Cycle Toggle */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="flex justify-center mb-8"
        >
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-1 inline-flex">
            <button
              onClick={() => setBillingCycle('monthly')}
              className={`px-6 py-2 rounded-md transition-all ${
                billingCycle === 'monthly'
                  ? 'bg-white text-white'
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle('yearly')}
              className={`px-6 py-2 rounded-md transition-all ${
                billingCycle === 'yearly'
                  ? 'bg-white text-white'
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              Yearly
              {currentPrice.save && (
                <span className="ml-2 text-xs bg-green-500 px-2 py-1 rounded">
                  Save Rp {(currentPrice.save / 1000).toFixed(0)}k
                </span>
              )}
            </button>
          </div>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Plan Details */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8"
          >
            <h2 className="text-2xl font-bold text-white mb-6">Plan Details</h2>
            
            <div className="mb-6">
              <div className="text-gray-400 text-sm mb-2">Selected Plan</div>
              <div className="text-3xl font-bold text-white">{currentTierData.name}</div>
            </div>

            <div className="mb-6">
              <div className="text-gray-400 text-sm mb-2">Billing</div>
              <div className="text-xl text-white capitalize">{billingCycle}</div>
            </div>

            <div className="mb-8">
              <div className="text-gray-400 text-sm mb-2">Features Included</div>
              <div className="space-y-3">
                {currentPrice.features.map((feature, idx) => (
                  <div key={idx} className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-300">{feature}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Security Badges */}
            <div className="border-t border-gray-700 pt-6 space-y-3">
              <div className="flex items-center gap-3 text-sm text-gray-400">
                <Shield className="w-5 h-5 text-gray-400" />
                <span>Secured by Doku Payment Gateway</span>
              </div>
              <div className="flex items-center gap-3 text-sm text-gray-400">
                <Clock className="w-5 h-5 text-gray-400" />
                <span>Instant activation after payment</span>
              </div>
              <div className="flex items-center gap-3 text-sm text-gray-400">
                <CreditCard className="w-5 h-5 text-gray-400" />
                <span>Multiple payment methods available</span>
              </div>
            </div>
          </motion.div>

          {/* Payment Summary */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-gradient-to-br from-gray-600 to-gray-700 rounded-2xl p-8 text-white"
          >
            <h2 className="text-2xl font-bold mb-8">Payment Summary</h2>

            <div className="space-y-4 mb-8">
              <div className="flex justify-between text-lg">
                <span>Plan</span>
                <span className="font-semibold">{currentTierData.name}</span>
              </div>
              <div className="flex justify-between text-lg">
                <span>Billing Cycle</span>
                <span className="font-semibold capitalize">{billingCycle}</span>
              </div>
              {currentPrice.save && (
                <div className="flex justify-between text-green-300 font-medium">
                  <span>You Save</span>
                  <span>Rp {(currentPrice.save / 1000).toFixed(0)}.000</span>
                </div>
              )}
              <div className="border-t border-white/20 pt-4 mt-4">
                <div className="flex justify-between items-center">
                  <span className="text-2xl font-bold">Total</span>
                  <div className="text-right">
                    <div className="text-3xl font-bold">{currentPrice.price_formatted}</div>
                    <div className="text-sm text-gray-300">
                      {billingCycle === 'yearly' ? 'per year' : 'per month'}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {error && (
              <div className="mb-4 p-4 bg-red-500/20 border border-red-500/50 rounded-lg flex items-start gap-3">
                <X className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <p className="text-sm">{error}</p>
              </div>
            )}

            <button
              onClick={() => handlePayment(selectedTier)}
              disabled={loading}
              className="w-full bg-white text-white py-4 rounded-xl font-bold text-lg hover:bg-gray-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <CreditCard className="w-5 h-5" />
                  Proceed to Payment
                </>
              )}
            </button>

            <p className="text-center text-sm text-gray-400 mt-4">
              You will be redirected to Doku secure payment page
            </p>

            <button
              onClick={() => router.push('/pricing')}
              className="w-full mt-4 text-white/80 hover:text-white py-2 text-sm transition-colors"
            >
              Change Plan
            </button>
          </motion.div>
        </div>

        {/* Trust Indicators */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mt-12 text-center"
        >
          <div className="flex flex-wrap justify-center gap-8 items-center text-gray-400 text-sm">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4" />
              <span>256-bit SSL Encryption</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4" />
              <span>PCI DSS Compliant</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              <span>Cancel Anytime</span>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
