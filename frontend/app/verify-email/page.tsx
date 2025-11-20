'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Mail, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';

export default function VerifyEmailPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'pending' | 'verifying' | 'success' | 'error'>('pending');
  const [message, setMessage] = useState('');
  const [resending, setResending] = useState(false);

  useEffect(() => {
    const token = searchParams.get('token');
    if (token) {
      verifyEmail(token);
    }
  }, [searchParams]);

  const verifyEmail = async (token: string) => {
    setStatus('verifying');
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://192.168.100.6:8002/api';
      const response = await fetch(`${API_URL}/auth/verify-email?token=${token}`, {
        method: 'GET',
      });

      const data = await response.json();

      if (response.ok) {
        setStatus('success');
        setMessage('Your email has been verified successfully!');
        setTimeout(() => {
          router.push('/login');
        }, 3000);
      } else {
        setStatus('error');
        setMessage(data.detail || 'Verification failed. The link may have expired.');
      }
    } catch (error) {
      setStatus('error');
      setMessage('Verification failed. Please try again.');
    }
  };

  const resendVerification = async () => {
    setResending(true);
    const tempToken = localStorage.getItem('temp_token');
    const email = localStorage.getItem('temp_email');

    try {
      const response = await fetch('http://192.168.100.6:8002/api/auth/resend-verification', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(tempToken && { 'Authorization': `Bearer ${tempToken}` })
        },
        body: JSON.stringify({ email }),
      });

      if (response.ok) {
        setMessage('Verification email sent! Please check your inbox.');
      } else {
        setMessage('Failed to resend verification email.');
      }
    } catch (error) {
      setMessage('Failed to resend verification email.');
    } finally {
      setResending(false);
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

          {/* Verification Card */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 text-center">
            {status === 'pending' && (
              <>
                <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-white/10 flex items-center justify-center">
                  <Mail className="w-10 h-10 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">Check Your Email</h2>
                <p className="text-white/60 mb-6">
                  We've sent a verification link to your email address. Please click the link to verify your account.
                </p>
                <div className="space-y-3">
                  <p className="text-sm text-white/40">
                    Didn't receive the email?
                  </p>
                  <Button 
                    onClick={resendVerification}
                    disabled={resending}
                    variant="outline"
                    className="w-full border-white/20 text-white hover:bg-white/10"
                  >
                    <RefreshCw className={`mr-2 ${resending ? 'animate-spin' : ''}`} size={16} />
                    {resending ? 'Sending...' : 'Resend Verification Email'}
                  </Button>
                </div>
              </>
            )}

            {status === 'verifying' && (
              <>
                <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-white/10 flex items-center justify-center">
                  <RefreshCw className="w-10 h-10 text-white animate-spin" />
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">Verifying...</h2>
                <p className="text-white/60">Please wait while we verify your email.</p>
              </>
            )}

            {status === 'success' && (
              <>
                <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-green-500/20 flex items-center justify-center">
                  <CheckCircle className="w-10 h-10 text-green-500" />
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">Email Verified!</h2>
                <p className="text-white/60 mb-6">{message}</p>
                <p className="text-sm text-white/40">Redirecting to login page...</p>
              </>
            )}

            {status === 'error' && (
              <>
                <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-red-500/20 flex items-center justify-center">
                  <AlertCircle className="w-10 h-10 text-red-500" />
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">Verification Failed</h2>
                <p className="text-white/60 mb-6">{message}</p>
                <div className="space-y-3">
                  <Button 
                    onClick={resendVerification}
                    disabled={resending}
                    className="w-full bg-white hover:bg-gray-200 text-black"
                  >
                    <RefreshCw className={`mr-2 ${resending ? 'animate-spin' : ''}`} size={16} />
                    {resending ? 'Sending...' : 'Resend Verification Email'}
                  </Button>
                  <Link href="/login" className="block">
                    <Button variant="outline" className="w-full border-white/20 text-white hover:bg-white/10">
                      Back to Login
                    </Button>
                  </Link>
                </div>
              </>
            )}

            {message && status === 'pending' && (
              <div className="mt-4 p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
                <p className="text-green-400 text-sm">{message}</p>
              </div>
            )}
          </div>

          <p className="mt-8 text-center text-sm text-white/40">
            Need help? <Link href="/contact" className="text-white/60 hover:text-white underline">Contact Support</Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
