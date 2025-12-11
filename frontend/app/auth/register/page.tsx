'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowRight, Mail, Lock, User, Eye, EyeOff, AlertCircle, Shield, Zap, Globe } from 'lucide-react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import api from '@/lib/api'

export default function RegisterPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const tier = searchParams.get('tier') || 'free'
  const redirect = searchParams.get('redirect') || 'dashboard'

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isLoading, setIsLoading] = useState(false)

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.email) {
      newErrors.email = 'Email wajib diisi'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Format email tidak valid'
    }

    if (!formData.fullName) {
      newErrors.fullName = 'Nama lengkap wajib diisi'
    } else if (formData.fullName.length < 3) {
      newErrors.fullName = 'Nama minimal 3 karakter'
    }

    if (!formData.password) {
      newErrors.password = 'Password wajib diisi'
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password minimal 8 karakter'
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Password tidak cocok'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return

    setIsLoading(true)

    try {
      // Call backend API to register user
      const response = await api.post('/auth/register', {
        email: formData.email,
        password: formData.password,
        full_name: formData.fullName,
        username: formData.email.split('@')[0], // Use email prefix as username
        role: 'hunter',
        subscription_tier: tier === 'free' ? 'free' : tier
      })
      
      // Store authentication tokens
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token)
      }
      
      // Redirect to terms page
      router.push(`/auth/terms?tier=${tier}&redirect=${redirect}&email=${encodeURIComponent(formData.email)}&name=${encodeURIComponent(formData.fullName)}`)
    } catch (error: any) {
      const errorDetail = error.response?.data?.detail
      let errorMessage = 'Terjadi kesalahan. Silakan coba lagi.'
      
      if (typeof errorDetail === 'string') {
        errorMessage = errorDetail
      } else if (typeof errorDetail === 'object') {
        errorMessage = JSON.stringify(errorDetail)
      } else if (error.message) {
        errorMessage = error.message
      }
      
      setErrors({ submit: errorMessage })
    } finally {
      setIsLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  return (
    <div className="h-screen bg-black text-white flex overflow-hidden">
      {/* Left Side - Natural Interactive Animation */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-gradient-to-br from-gray-900/60 via-gray-900/50 to-black">
        {/* Subtle Grain Texture Overlay */}
        <div className="absolute inset-0 opacity-[0.03] bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMDAiIGhlaWdodD0iMzAwIj48ZmlsdGVyIGlkPSJhIj48ZmVUdXJidWxlbmNlIGJhc2VGcmVxdWVuY3k9Ii43NSIgc3RpdGNoVGlsZXM9InN0aXRjaCIgdHlwZT0iZnJhY3RhbE5vaXNlIi8+PGZlQ29sb3JNYXRyaXggdHlwZT0ic2F0dXJhdGUiIHZhbHVlcz0iMCIvPjwvZmlsdGVyPjxwYXRoIGQ9Ik0wIDBoMzAwdjMwMEgweiIgZmlsdGVyPSJ1cmwoI2EpIiBvcGFjaXR5PSIuMDUiLz48L3N2Zz4=')]" />
        
        {/* Animated Grid Background - Irregular */}
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#8b5cf608_1px,transparent_1px),linear-gradient(to_bottom,#8b5cf608_1px,transparent_1px)] bg-[size:4.2rem_3.8rem]" style={{ transform: 'rotate(0.5deg)' }} />
          <motion.div
            className="absolute inset-0 bg-[linear-gradient(to_right,#3b82f612_1px,transparent_1px),linear-gradient(to_bottom,#3b82f612_1px,transparent_1px)] bg-[size:3.9rem_4.1rem]"
            animate={{
              backgroundPosition: ['0px 0px', '67px 59px'],
            }}
            transition={{
              duration: 23,
              repeat: Infinity,
              ease: [0.45, 0.05, 0.55, 0.95],
            }}
          />
        </div>

        {/* Floating Orbs - Irregular movement & desaturated */}
        {[
          { color: 'from-gray-600/70 to-gray-500/60', size: 'w-64 h-64', blur: 'blur-3xl', x: '18%', y: '22%', duration: 11, path: [0, 45, -38, 0] },
          { color: 'from-gray-600/60 to-gray-500/50', size: 'w-80 h-80', blur: 'blur-3xl', x: '62%', y: '58%', duration: 13, path: [0, -52, 41, 0] },
          { color: 'from-teal-600/50 to-green-600/40', size: 'w-72 h-72', blur: 'blur-3xl', x: '68%', y: '32%', duration: 15, path: [0, 33, -47, 0] },
        ].map((orb, i) => (
          <motion.div
            key={i}
            className={`absolute ${orb.size} bg-gradient-to-br ${orb.color} rounded-full ${orb.blur} opacity-15`}
            style={{ left: orb.x, top: orb.y }}
            animate={{
              x: orb.path,
              y: [0, orb.path[1] * -0.8, orb.path[2] * 0.9, 0],
              scale: [1, 1.15, 0.88, 1.05, 1],
            }}
            transition={{
              duration: orb.duration,
              repeat: Infinity,
              ease: [0.42, 0, 0.58, 1],
              times: [0, 0.3, 0.6, 1],
            }}
          />
        ))}

        {/* Code Rain Effect - Less uniform */}
        <div className="absolute inset-0 overflow-hidden">
          {[...Array(12)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute font-mono text-xs"
              style={{
                left: `${(i * 8.5 + (i * 3.7) % 10) % 100}%`,
                color: i % 3 === 0 ? '#a78bfa' : i % 3 === 1 ? '#60a5fa' : '#4ade80',
                opacity: 0.6 + (i % 5) * 0.05,
              }}
              animate={{
                y: [-120, 1000],
                opacity: [0, 0.7, 0.4, 0],
              }}
              transition={{
                duration: 12 + (i % 6),
                repeat: Infinity,
                delay: (i % 8),
                ease: [0.33, 0, 0.67, 1],
              }}
            >
              {['01', '10', '11', '00', 'AI', 'BUG', 'SEC'][i % 7]}
            </motion.div>
          ))}
        </div>

        {/* Only background animations - no text or icons */}
        <div className="relative z-10 flex flex-col items-center justify-center w-full h-full" />
      </div>

      {/* Right Side - Register Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-black relative overflow-y-auto">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-gray-900 via-black to-black" />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:4rem_4rem]" />

      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6 }}
        className="relative z-10 w-full max-w-md"
      >
        <div className="mb-6">
          <Link href="/" className="text-sm text-gray-400 hover:text-white mb-6 inline-block">
            ← Kembali ke Beranda
          </Link>
          <h1 className="text-3xl font-bold mb-2">Sign up for IKODIO</h1>
          <p className="text-gray-400">
            Paket <span className="text-white font-semibold capitalize">{tier}</span>
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          {/* Email */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Email<span className="text-white">*</span>
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={`w-full px-4 py-2.5 bg-white/5 border ${errors.email ? 'border-white' : 'border-white/10'} rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30 transition-colors`}
              placeholder="Email"
            />
            {errors.email && (
              <p className="mt-2 text-sm text-white flex items-center gap-1">
                <AlertCircle className="w-4 h-4" />
                {errors.email}
              </p>
            )}
          </div>          {/* Password */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Password<span className="text-white">*</span>
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleChange}
                className={`w-full px-4 py-2.5 bg-white/5 border ${errors.password ? 'border-white' : 'border-white/10'} rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30 transition-colors`}
                placeholder="Password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
            {errors.password && (
              <p className="mt-2 text-sm text-white flex items-center gap-1">
                <AlertCircle className="w-4 h-4" />
                {errors.password}
              </p>
            )}
            <p className="mt-2 text-xs text-gray-500">
              Password minimal 8 karakter
            </p>
          </div>

          {/* Confirm Password */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Confirm Password<span className="text-white">*</span>
            </label>
            <div className="relative">
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                className={`w-full px-4 py-2.5 bg-white/5 border ${errors.confirmPassword ? 'border-white' : 'border-white/10'} rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30 transition-colors`}
                placeholder="Confirm Password"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
              >
                {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
            {errors.confirmPassword && (
              <p className="mt-2 text-sm text-white flex items-center gap-1">
                <AlertCircle className="w-4 h-4" />
                {errors.confirmPassword}
              </p>
            )}
          </div>

          {/* Username/Full Name */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Username<span className="text-white">*</span>
            </label>
            <input
              type="text"
              name="fullName"
              value={formData.fullName}
              onChange={handleChange}
                className={`w-full px-4 py-2.5 bg-white/5 border ${errors.fullName ? 'border-white' : 'border-white/10'} rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30 transition-colors`}
              placeholder="Username"
            />
            {errors.fullName && (
              <p className="mt-2 text-sm text-white flex items-center gap-1">
                <AlertCircle className="w-4 h-4" />
                {errors.fullName}
              </p>
            )}
          </div>

          {/* Email preferences */}
          <div className="flex items-start gap-3 pt-2">
            <input
              type="checkbox"
              id="emailPreferences"
              className="mt-1 w-4 h-4 bg-white/5 border border-white/10 rounded focus:ring-2 focus:ring-white/30"
            />
            <label htmlFor="emailPreferences" className="text-sm text-gray-400">
              Terima pembaruan produk dan pengumuman sesekali
            </label>
          </div>

          {errors.submit && (
            <div className="p-4 bg-white/10 border border-white/20 rounded-xl">
              <p className="text-sm text-white flex items-center gap-2">
                <AlertCircle className="w-5 h-5" />
                {errors.submit}
              </p>
            </div>
          )}

          <motion.button
            type="submit"
            disabled={isLoading}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="w-full py-2.5 bg-white hover:bg-gray-200 text-black font-semibold rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Memproses...</span>
              </>
            ) : (
              <>
                <span>Create account</span>
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </motion.button>
        </form>

        <div className="mt-6 text-center text-xs text-gray-400">
          Dengan membuat akun, Anda menyetujui{' '}
          <Link href="/terms" className="text-white hover:underline">
            Ketentuan Layanan
          </Link>
          . Untuk informasi lebih lanjut tentang praktik privasi IKODIO, lihat{' '}
          <Link href="/privacy" className="text-white hover:underline">
            Pernyataan Privasi IKODIO
          </Link>
          . Kami akan sesekali mengirimkan email terkait akun.
        </div>

        <div className="mt-8 text-center">
          <p className="text-gray-400 text-sm">
            Sudah punya akun?{' '}
            <Link href={`/auth/login?tier=${tier}&redirect=${redirect}`} className="text-white font-semibold hover:underline">
              Sign in →
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
    </div>
  )
}
