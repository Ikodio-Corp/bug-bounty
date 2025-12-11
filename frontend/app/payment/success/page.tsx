'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle, ArrowRight, Sparkles } from 'lucide-react'
import { useRouter, useSearchParams } from 'next/navigation'
import { api } from '@/lib/api'

export default function PaymentSuccessPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const invoice = searchParams.get('invoice')
  
  const [status, setStatus] = useState<'checking' | 'success' | 'error'>('checking')
  const [message, setMessage] = useState('Verifying your payment...')

  useEffect(() => {
    if (invoice) {
      verifyPayment(invoice)
    } else {
      // If no invoice, assume success from Midtrans redirect
      setStatus('success')
      setMessage('Payment successful! Your subscription has been activated.')
    }
  }, [invoice])

  const verifyPayment = async (invoiceNumber: string) => {
    try {
      const response = await api.get(`/payments/status/${invoiceNumber}`)
      const transactionStatus = response.data.transaction_status || response.data.status
      
      if (transactionStatus === 'settlement' || transactionStatus === 'capture' || transactionStatus === 'SUCCESS') {
        setStatus('success')
        setMessage('Payment successful! Your subscription has been activated.')
        
        // Redirect to dashboard after 3 seconds
        setTimeout(() => {
          router.push('/dashboard')
        }, 3000)
      } else {
        setStatus('checking')
        setMessage('Payment is being processed. This may take a few moments...')
        
        // Retry after 5 seconds
        setTimeout(() => verifyPayment(invoiceNumber), 5000)
      }
    } catch (error) {
      setStatus('error')
      setMessage('Unable to verify payment status. Please contact support.')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-900 to-gray-900 flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-md w-full"
      >
        {status === 'checking' && (
          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 text-center">
            <div className="w-16 h-16 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-6" />
            <h1 className="text-2xl font-bold text-white mb-4">Processing Payment</h1>
            <p className="text-gray-300">{message}</p>
          </div>
        )}

        {status === 'success' && (
          <div className="bg-gradient-to-br from-green-600 to-emerald-600 rounded-2xl p-8 text-center text-white">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', bounce: 0.5 }}
              className="inline-block mb-6"
            >
              <CheckCircle className="w-24 h-24" />
            </motion.div>
            
            <h1 className="text-3xl font-bold mb-4">Payment Successful!</h1>
            <p className="text-green-100 mb-8">{message}</p>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 mb-6">
              <div className="flex items-center justify-center gap-2 text-sm mb-2">
                <Sparkles className="w-4 h-4" />
                <span>Your subscription is now active</span>
              </div>
              {invoice && (
                <div className="text-xs text-green-200 mt-2">
                  Invoice: {invoice}
                </div>
              )}
            </div>

            <button
              onClick={() => router.push('/dashboard')}
              className="w-full bg-white text-green-600 py-3 rounded-xl font-semibold hover:bg-green-50 transition-all flex items-center justify-center gap-2"
            >
              Go to Dashboard
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        )}

        {status === 'error' && (
          <div className="bg-gray-800/50 backdrop-blur-sm border border-red-500/50 rounded-2xl p-8 text-center">
            <div className="text-red-500 text-6xl mb-6">!</div>
            <h1 className="text-2xl font-bold text-white mb-4">Verification Issue</h1>
            <p className="text-gray-300 mb-6">{message}</p>
            <button
              onClick={() => router.push('/dashboard')}
              className="w-full bg-white text-white py-3 rounded-xl font-semibold hover:bg-gray-200 transition-all"
            >
              Go to Dashboard
            </button>
          </div>
        )}
      </motion.div>
    </div>
  )
}
