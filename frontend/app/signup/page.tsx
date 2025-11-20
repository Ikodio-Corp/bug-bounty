'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Mail, Lock, User, ArrowRight, AlertCircle, CheckCircle } from 'lucide-react';

export default function SignUpPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [verificationSent, setVerificationSent] = useState(false);

  const validateEmail = (email: string) => {
    // Check temporary email domains
    const tempDomains = [
      'tempmail.com', 'guerrillamail.com', '10minutemail.com',
      'throwaway.email', 'mailinator.com', 'maildrop.cc',
      'temp-mail.org', 'yopmail.com', 'getairmail.com'
    ];
    const domain = email.split('@')[1]?.toLowerCase();
    if (tempDomains.includes(domain)) {
      return 'Temporary email addresses are not allowed';
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match!');
      return;
    }

    // Validate email
    const emailError = validateEmail(formData.email);
    if (emailError) {
      setError(emailError);
      return;
    }

    // Validate password strength (must match backend requirements)
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }
    if (!/[A-Z]/.test(formData.password)) {
      setError('Password must contain at least one uppercase letter');
      return;
    }
    if (!/[a-z]/.test(formData.password)) {
      setError('Password must contain at least one lowercase letter');
      return;
    }
    if (!/[0-9]/.test(formData.password)) {
      setError('Password must contain at least one digit');
      return;
    }

    setLoading(true);

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://192.168.100.6:8002/api';
      const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          username: formData.username || formData.email.split('@')[0],
          password: formData.password,
          full_name: formData.name
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Registration failed');
      }

      // Auto-verification enabled - store token and redirect to dashboard
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      setSuccess('Registration successful! Redirecting to dashboard...');
      
      // Force redirect to dashboard
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 1500);

    } catch (err: any) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Logo */}
          <Link href="/" className="block text-center mb-8">
            <h1 className="text-4xl font-bold text-white">Ikodio</h1>
            <p className="text-white/60 mt-2">Bug Bounty Platform</p>
          </Link>

          {/* Sign Up Form */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-white mb-2">Create Account</h2>
            <p className="text-white/60 mb-6">Join thousands of security researchers</p>

            {error && (
              <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg flex items-start gap-2">
                <AlertCircle className="text-red-500 mt-0.5" size={20} />
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            {success && (
              <div className="mb-4 p-3 bg-green-500/10 border border-green-500/20 rounded-lg flex items-start gap-2">
                <CheckCircle className="text-green-500 mt-0.5" size={20} />
                <p className="text-green-400 text-sm">{success}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" size={20} />
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-3 text-white placeholder:text-white/40 focus:outline-none focus:border-white/30 transition-colors"
                    placeholder="John Doe"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" size={20} />
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value, username: e.target.value.split('@')[0] })}
                    className="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-3 text-white placeholder:text-white/40 focus:outline-none focus:border-white/30 transition-colors"
                    placeholder="you@example.com"
                    required
                  />
                </div>
                <p className="text-xs text-white/40 mt-1">Use a valid email. Temporary emails are not allowed.</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" size={20} />
                  <input
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-3 text-white placeholder:text-white/40 focus:outline-none focus:border-white/30 transition-colors"
                    placeholder="••••••••"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" size={20} />
                  <input
                    type="password"
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                    className="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-3 text-white placeholder:text-white/40 focus:outline-none focus:border-white/30 transition-colors"
                    placeholder="••••••••"
                    required
                  />
                </div>
              </div>

              <Button 
                type="submit" 
                disabled={loading || verificationSent}
                className="w-full bg-white hover:bg-gray-200 text-black py-6 text-lg font-semibold group disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Creating Account...' : verificationSent ? 'Verification Sent!' : 'Create Account'}
                {!loading && <ArrowRight className="ml-2 group-hover:translate-x-1 transition-transform" size={20} />}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-white/60">
                Already have an account?{' '}
                <Link href="/login" className="text-white hover:underline font-semibold">
                  Sign In
                </Link>
              </p>
            </div>

            <div className="mt-6 relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-white/10"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-black/50 text-white/60">Or continue with</span>
              </div>
            </div>

            <div className="mt-6 grid grid-cols-2 gap-4">
              <button 
                onClick={() => {
                  setError('OAuth login will be available soon. Please use email registration.');
                }}
                type="button"
                className="flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg py-3 text-white transition-colors"
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Google
              </button>
              <button 
                onClick={() => {
                  setError('OAuth login will be available soon. Please use email registration.');
                }}
                type="button"
                className="flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg py-3 text-white transition-colors"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                GitHub
              </button>
            </div>
          </div>

          <p className="mt-8 text-center text-sm text-white/40">
            By signing up, you agree to our{' '}
            <Link href="/dashboard" className="text-white/60 hover:text-white underline">
              Terms of Service
            </Link>
            {' '}and{' '}
            <Link href="/dashboard" className="text-white/60 hover:text-white underline">
              Privacy Policy
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
