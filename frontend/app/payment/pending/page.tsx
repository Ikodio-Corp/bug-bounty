'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import api from '@/lib/api'

export default function PaymentPending() {
  const searchParams = useSearchParams()
  const orderId = searchParams.get('order_id')
  const [status, setStatus] = useState<'pending' | 'success' | 'failed'>('pending')
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    if (!orderId) return

    const checkStatus = async () => {
      try {
        const token = localStorage.getItem('access_token')
        if (!token) return

        const response = await api.get(`/payments/status/${orderId}`, {
          headers: { Authorization: `Bearer ${token}` }
        })

        const paymentStatus = response.data.status
        if (paymentStatus === 'settlement' || paymentStatus === 'capture') {
          setStatus('success')
          setTimeout(() => {
            window.location.href = '/payment/success?order_id=' + orderId
          }, 2000)
        } else if (paymentStatus === 'deny' || paymentStatus === 'cancel' || paymentStatus === 'expire') {
          setStatus('failed')
        } else {
          setStatus('pending')
        }
      } catch (error) {
        console.error('Error checking payment status:', error)
      } finally {
        setChecking(false)
      }
    }

    // Check immediately
    checkStatus()

    // Then check every 5 seconds
    const interval = setInterval(checkStatus, 5000)

    return () => clearInterval(interval)
  }, [orderId])

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 via-white to-orange-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
        {/* Pending Icon */}
        <div className="mx-auto w-20 h-20 bg-yellow-100 rounded-full flex items-center justify-center mb-6">
          {checking ? (
            <svg
              className="w-10 h-10 text-yellow-600 animate-spin"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          ) : (
            <svg
              className="w-10 h-10 text-yellow-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          )}
        </div>

        {/* Status Message */}
        {status === 'success' ? (
          <>
            <h1 className="text-3xl font-bold text-gray-900 mb-3">
              Pembayaran Berhasil! 
            </h1>
            <p className="text-gray-600 mb-6">
              Mengalihkan ke halaman sukses...
            </p>
          </>
        ) : status === 'failed' ? (
          <>
            <h1 className="text-3xl font-bold text-gray-900 mb-3">
              Pembayaran Gagal 
            </h1>
            <p className="text-gray-600 mb-6">
              Silakan coba lagi atau hubungi support.
            </p>
          </>
        ) : (
          <>
            <h1 className="text-3xl font-bold text-gray-900 mb-3">
              Pembayaran Pending ⏳
            </h1>
            <p className="text-gray-600 mb-6">
              {checking
                ? 'Memeriksa status pembayaran...'
                : 'Pembayaran Anda sedang diproses. Mohon selesaikan pembayaran.'}
            </p>
          </>
        )}

        {/* Order Details */}
        {orderId && (
          <div className="bg-gray-50 rounded-lg p-4 mb-6 text-left">
            <div className="text-sm text-gray-500 mb-1">Order ID</div>
            <div className="font-mono text-sm text-gray-900">{orderId}</div>
          </div>
        )}

        {/* Instructions */}
        {status === 'pending' && !checking && (
          <div className="bg-yellow-50 rounded-lg p-4 mb-6 text-left">
            <h3 className="font-semibold text-gray-900 mb-3">
              Langkah Selanjutnya:
            </h3>
            <ol className="space-y-2 text-sm text-gray-700">
              <li className="flex items-start">
                <span className="font-semibold mr-2">1.</span>
                <span>Kembali ke halaman pembayaran Midtrans</span>
              </li>
              <li className="flex items-start">
                <span className="font-semibold mr-2">2.</span>
                <span>Selesaikan pembayaran sesuai metode yang dipilih</span>
              </li>
              <li className="flex items-start">
                <span className="font-semibold mr-2">3.</span>
                <span>Halaman ini akan otomatis update setelah pembayaran berhasil</span>
              </li>
            </ol>
          </div>
        )}

        {/* Auto Refresh Info */}
        {status === 'pending' && !checking && (
          <div className="text-sm text-gray-500 mb-6">
             Memeriksa status setiap 5 detik...
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col gap-3">
          {status === 'pending' && (
            <button
              onClick={() => window.location.reload()}
              className="w-full bg-white text-white py-3 px-6 rounded-lg font-medium hover:bg-gray-200 transition"
            >
              Refresh Status
            </button>
          )}
          
          <Link
            href="/dashboard"
            className="w-full border border-gray-300 text-gray-700 py-3 px-6 rounded-lg font-medium hover:bg-gray-50 transition text-center"
          >
            Kembali ke Dashboard
          </Link>

          {status === 'failed' && (
            <Link
              href="/pricing"
              className="w-full bg-white text-white py-3 px-6 rounded-lg font-medium hover:bg-gray-200 transition text-center"
            >
              Coba Lagi
            </Link>
          )}
        </div>

        {/* Support Link */}
        <div className="mt-6 text-sm text-gray-500">
          Butuh bantuan?{' '}
          <a href="mailto:support@ikodio.com" className="text-white hover:underline">
            Hubungi Support
          </a>
        </div>
      </div>
    </div>
  )
}
