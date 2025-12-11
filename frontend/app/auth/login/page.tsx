'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowRight, Eye, EyeOff, AlertCircle, Chrome, Github, Shield, Key, CheckCircle2, Lock } from 'lucide-react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'

export default function LoginPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const tier = searchParams.get('tier') || 'free'
  const redirect = searchParams.get('redirect') || 'dashboard'

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      await new Promise(resolve => setTimeout(resolve, 1500))
      router.push(`/auth/terms?tier=${tier}&redirect=${redirect}&email=${encodeURIComponent(email)}&name=User`)
    } catch (err) {
      setError('Email atau password salah. Silakan coba lagi.')
    } finally {
      setLoading(false)
    }
  }

  const handleOAuthLogin = (provider: string) => {
    window.location.href = `http://localhost:8002/api/oauth/${provider}`
  }

  return (
    <div className="h-screen bg-black text-white flex overflow-hidden">
      {/* Left Side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-black relative overflow-y-auto">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-gray-900 via-black to-black" />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:4rem_4rem]" />

        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="relative z-10 w-full max-w-md"
        >
          <div className="mb-6">
            <Link href="/" className="text-sm text-gray-400 hover:text-white mb-6 inline-block">
              ← Kembali ke Beranda
            </Link>
            <h1 className="text-3xl font-bold mb-2">Masuk ke Akun</h1>
            <p className="text-gray-400">
              Lanjutkan ke paket <span className="text-white font-semibold capitalize">{tier}</span>
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 p-3 bg-white/5 border border-white/10 rounded-xl flex items-start gap-3"
            >
              <AlertCircle className="w-5 h-5 text-white flex-shrink-0 mt-0.5" />
              <p className="text-sm text-gray-300">{error}</p>
            </motion.div>
          )}

          {/* Login Form */}
          <form onSubmit={handleLogin} className="space-y-4">
            {/* Email Field */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Email<span className="text-white">*</span>
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30 transition-colors"
                placeholder="nama@email.com"
                required
              />
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Password<span className="text-white">*</span>
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30 transition-colors"
                  placeholder="Masukkan password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Remember & Forgot */}
            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 text-gray-300 cursor-pointer">
                <input type="checkbox" className="w-4 h-4 rounded border-white/10 bg-white/5" />
                <span>Remember me</span>
              </label>
              <Link href="/forgot-password" className="text-gray-300 hover:text-white transition-colors">
                Lupa password?
              </Link>
            </div>

            {/* Login Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-white text-black font-semibold rounded-xl hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-black border-t-transparent rounded-full animate-spin" />
                  <span>Memproses...</span>
                </>
              ) : (
                <>
                  <span>Masuk</span>
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </motion.button>
          </form>

          {/* Divider */}
          <div className="relative my-5">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-white/10"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-black text-gray-400">Or continue with</span>
            </div>
          </div>

          {/* OAuth Buttons */}
          <div className="grid grid-cols-2 gap-3 mb-5">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleOAuthLogin('google')}
              className="flex items-center justify-center gap-2 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white hover:bg-white/10 transition-all"
            >
              <Chrome className="w-5 h-5" />
              <span>Google</span>
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleOAuthLogin('github')}
              className="flex items-center justify-center gap-2 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white hover:bg-white/10 transition-all"
            >
              <Github className="w-5 h-5" />
              <span>GitHub</span>
            </motion.button>
          </div>

          {/* Register Link */}
          <div className="text-center">
            <p className="text-gray-400 text-sm">
              Belum punya akun?{' '}
              <Link href={`/auth/register?tier=${tier}&redirect=${redirect}`} className="text-white font-semibold hover:underline">
                Daftar sekarang →
              </Link>
            </p>
          </div>
        </motion.div>
      </div>

      {/* Right Side - Natural Interactive Animation */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-gradient-to-br from-gray-900/55 via-gray-900/45 to-black">
        {/* Subtle Grain Texture */}
        <div className="absolute inset-0 opacity-[0.03] bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMDAiIGhlaWdodD0iMzAwIj48ZmlsdGVyIGlkPSJhIj48ZmVUdXJidWxlbmNlIGJhc2VGcmVxdWVuY3k9Ii43NSIgc3RpdGNoVGlsZXM9InN0aXRjaCIgdHlwZT0iZnJhY3RhbE5vaXNlIi8+PGZlQ29sb3JNYXRyaXggdHlwZT0ic2F0dXJhdGUiIHZhbHVlcz0iMCIvPjwvZmlsdGVyPjxwYXRoIGQ9Ik0wIDBoMzAwdjMwMEgweiIgZmlsdGVyPSJ1cmwoI2EpIiBvcGFjaXR5PSIuMDUiLz48L3N2Zz4=')]" />
        
        {/* Animated Grid - Slightly rotated */}
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#6366f108_1px,transparent_1px),linear-gradient(to_bottom,#6366f108_1px,transparent_1px)] bg-[size:4.1rem_3.9rem]" style={{ transform: 'rotate(-0.5deg)' }} />
          <motion.div
            className="absolute inset-0 bg-[linear-gradient(to_right,#8b5cf612_1px,transparent_1px),linear-gradient(to_bottom,#8b5cf612_1px,transparent_1px)] bg-[size:3.8rem_4.2rem]"
            animate={{
              backgroundPosition: ['0px 0px', '63px 71px'],
            }}
            transition={{
              duration: 25,
              repeat: Infinity,
              ease: [0.45, 0.05, 0.55, 0.95],
            }}
          />
        </div>

        {/* Floating Orbs - Irregular paths & desaturated */}
        {[
          { color: 'from-gray-600/65 to-gray-700/55', size: 'w-64 h-64', blur: 'blur-3xl', x: '15%', y: '18%', duration: 12, path: [0, 52, -44, 0] },
          { color: 'from-gray-500/55 to-gray-600/45', size: 'w-80 h-80', blur: 'blur-3xl', x: '65%', y: '62%', duration: 14, path: [0, -39, 48, 0] },
          { color: 'from-gray-500/50 to-gray-600/40', size: 'w-72 h-72', blur: 'blur-3xl', x: '72%', y: '28%', duration: 16, path: [0, 41, -36, 0] },
        ].map((orb, i) => (
          <motion.div
            key={i}
            className={`absolute ${orb.size} bg-gradient-to-br ${orb.color} rounded-full ${orb.blur} opacity-15`}
            style={{ left: orb.x, top: orb.y }}
            animate={{
              x: orb.path,
              y: [0, orb.path[1] * -0.7, orb.path[2] * 0.95, 0],
              scale: [1, 1.18, 0.92, 1.06, 1],
            }}
            transition={{
              duration: orb.duration,
              repeat: Infinity,
              ease: [0.42, 0, 0.58, 1],
              times: [0, 0.35, 0.65, 1],
            }}
          />
        ))}

        {/* Binary Rain - Less uniform */}
        <div className="absolute inset-0 overflow-hidden">
          {[...Array(12)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute font-mono text-xs"
              style={{
                left: `${(i * 8.5 + (i * 4) % 10) % 100}%`,
                color: i % 3 === 0 ? '#818cf8' : i % 3 === 1 ? '#a78bfa' : '#c084fc',
                opacity: 0.55 + (i % 5) * 0.05,
              }}
              animate={{
                y: [-100, 1000],
                opacity: [0, 0.7, 0.45, 0],
              }}
              transition={{
                duration: 13 + (i % 6),
                repeat: Infinity,
                delay: (i % 7),
                ease: [0.33, 0, 0.67, 1],
              }}
            >
              {['SECURE', 'LOGIN', '', '', 'AUTH'][i % 5]}
            </motion.div>
          ))}
        </div>

        {/* Only background animations - no text or icons */}
        <div className="relative z-10 flex flex-col items-center justify-center w-full h-full" />
      </div>
    </div>
  )
}
