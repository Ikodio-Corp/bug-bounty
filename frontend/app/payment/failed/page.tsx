'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { XCircle, ArrowLeft, RefreshCw, Mail } from 'lucide-react'
import { useRouter, useSearchParams } from 'next/navigation'

export default function PaymentFailedPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const invoice = searchParams.get('invoice')
  const reason = searchParams.get('reason') || 'Payment was not completed'

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-red-900 to-gray-900 flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-md w-full"
      >
        <div className="bg-gray-800/50 backdrop-blur-sm border border-red-500/50 rounded-2xl p-8 text-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', bounce: 0.5 }}
            className="inline-block mb-6"
          >
            <XCircle className="w-24 h-24 text-red-500" />
          </motion.div>
          
          <h1 className="text-3xl font-bold text-white mb-4">Payment Failed</h1>
          <p className="text-gray-300 mb-8">{reason}</p>
          
          {invoice && (
            <div className="bg-gray-900/50 rounded-xl p-4 mb-6">
              <div className="text-xs text-gray-400 mb-1">Invoice Number</div>
              <div className="text-sm text-gray-200 font-mono">{invoice}</div>
            </div>
          )}

          <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 mb-6 text-left">
            <h3 className="text-white font-semibold mb-2">Common Issues:</h3>
            <ul className="text-sm text-gray-300 space-y-1">
              <li>• Insufficient funds in your account</li>
              <li>• Payment method expired or invalid</li>
              <li>• Bank declined the transaction</li>
              <li>• Payment was cancelled by user</li>
            </ul>
          </div>

          <div className="space-y-3">
            <button
              onClick={() => router.push('/payment?tier=' + (searchParams.get('tier') || 'professional'))}
              className="w-full bg-white text-white py-3 rounded-xl font-semibold hover:bg-gray-200 transition-all flex items-center justify-center gap-2"
            >
              <RefreshCw className="w-5 h-5" />
              Try Again
            </button>
            
            <button
              onClick={() => router.push('/dashboard')}
              className="w-full bg-gray-700 text-white py-3 rounded-xl font-semibold hover:bg-gray-600 transition-all flex items-center justify-center gap-2"
            >
              <ArrowLeft className="w-5 h-5" />
              Back to Dashboard
            </button>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-700">
            <div className="flex items-center justify-center gap-2 text-sm text-gray-400">
              <Mail className="w-4 h-4" />
              <span>Need help? Contact support@ikodio.com</span>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
