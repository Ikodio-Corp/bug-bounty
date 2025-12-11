'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import api from '@/lib/api'

interface Overview {
  users: {
    total: number
    active: number
    inactive: number
  }
  bugs: {
    total: number
    pending: number
    validated: number
    rejected: number
  }
  scans: {
    total: number
    active: number
    completed: number
  }
  revenue: {
    total: number
    this_month: number
  }
}

export default function AdminDashboardPage() {
  const router = useRouter()
  const [overview, setOverview] = useState<Overview | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchOverview()
  }, [])

  const fetchOverview = async () => {
    try {
      const response = await api.get('/admin/overview')
      setOverview(response.data)
    } catch (error: any) {
      console.error('Failed to fetch overview:', error)
      if (error.response?.status === 403) {
        router.push('/dashboard')
      }
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center text-slate-400">Loading admin dashboard...</div>
        </div>
      </div>
    )
  }

  if (!overview) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center text-red-400">Failed to load admin dashboard</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Admin Dashboard</h1>
            <p className="text-slate-400">Platform management and oversight</p>
          </div>
          <Link href="/dashboard">
            <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white transition-colors">
              Back to Dashboard
            </button>
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-slate-800 rounded-xl p-6 border border-cyan-500/20">
            <div className="flex items-center justify-between mb-4">
              <div className="text-4xl"></div>
              <div className="text-sm text-slate-400">Users</div>
            </div>
            <div className="text-3xl font-bold text-white mb-2">
              {overview.users.total.toLocaleString()}
            </div>
            <div className="flex gap-4 text-sm">
              <div className="text-green-400">{overview.users.active} active</div>
              <div className="text-slate-400">{overview.users.inactive} inactive</div>
            </div>
          </div>

          <div className="bg-slate-800 rounded-xl p-6 border border-white/20">
            <div className="flex items-center justify-between mb-4">
              <div className="text-4xl"></div>
              <div className="text-sm text-slate-400">Bugs</div>
            </div>
            <div className="text-3xl font-bold text-white mb-2">
              {overview.bugs.total.toLocaleString()}
            </div>
            <div className="flex gap-4 text-sm">
              <div className="text-yellow-400">{overview.bugs.pending} pending</div>
              <div className="text-green-400">{overview.bugs.validated} validated</div>
            </div>
          </div>

          <div className="bg-slate-800 rounded-xl p-6 border border-white/20">
            <div className="flex items-center justify-between mb-4">
              <div className="text-4xl"></div>
              <div className="text-sm text-slate-400">Scans</div>
            </div>
            <div className="text-3xl font-bold text-white mb-2">
              {overview.scans.total.toLocaleString()}
            </div>
            <div className="flex gap-4 text-sm">
              <div className="text-gray-400">{overview.scans.active} active</div>
              <div className="text-slate-400">{overview.scans.completed} completed</div>
            </div>
          </div>

          <div className="bg-slate-800 rounded-xl p-6 border border-green-500/20">
            <div className="flex items-center justify-between mb-4">
              <div className="text-4xl"></div>
              <div className="text-sm text-slate-400">Revenue</div>
            </div>
            <div className="text-3xl font-bold text-white mb-2">
              ${overview.revenue.total.toLocaleString()}
            </div>
            <div className="text-sm text-green-400">
              ${overview.revenue.this_month.toLocaleString()} this month
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Link href="/admin/users">
            <div className="bg-slate-800 rounded-xl p-6 hover:bg-slate-700 transition-colors cursor-pointer border border-slate-700 hover:border-cyan-500">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white">User Management</h3>
                <div className="text-3xl"></div>
              </div>
              <p className="text-slate-400 mb-4">
                Manage user accounts, roles, and permissions
              </p>
              <div className="flex items-center text-cyan-400">
                <span>View all users</span>
                <svg
                  className="w-5 h-5 ml-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </div>
            </div>
          </Link>

          <Link href="/admin/bugs">
            <div className="bg-slate-800 rounded-xl p-6 hover:bg-slate-700 transition-colors cursor-pointer border border-slate-700 hover:border-white">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white">Bug Moderation</h3>
                <div className="text-3xl"></div>
              </div>
              <p className="text-slate-400 mb-4">
                Review, validate, and manage bug reports
              </p>
              <div className="flex items-center text-gray-400">
                <span>View all bugs</span>
                <svg
                  className="w-5 h-5 ml-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </div>
            </div>
          </Link>

          <Link href="/admin/scans">
            <div className="bg-slate-800 rounded-xl p-6 hover:bg-slate-700 transition-colors cursor-pointer border border-slate-700 hover:border-white">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white">Scan Monitoring</h3>
                <div className="text-3xl"></div>
              </div>
              <p className="text-slate-400 mb-4">
                Monitor security scans and performance
              </p>
              <div className="flex items-center text-gray-400">
                <span>View all scans</span>
                <svg
                  className="w-5 h-5 ml-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </div>
            </div>
          </Link>

          <Link href="/admin/analytics">
            <div className="bg-slate-800 rounded-xl p-6 hover:bg-slate-700 transition-colors cursor-pointer border border-slate-700 hover:border-green-500">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white">Analytics</h3>
                <div className="text-3xl"></div>
              </div>
              <p className="text-slate-400 mb-4">
                View platform analytics and insights
              </p>
              <div className="flex items-center text-green-400">
                <span>View analytics</span>
                <svg
                  className="w-5 h-5 ml-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </div>
            </div>
          </Link>
        </div>

        <div className="bg-slate-800 rounded-xl p-6">
          <h3 className="text-xl font-bold text-white mb-4">Quick Actions</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button className="px-4 py-3 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white transition-colors">
              Create User
            </button>
            <button className="px-4 py-3 bg-gray-700 hover:bg-gray-700 rounded-lg text-white transition-colors">
              Export Data
            </button>
            <button className="px-4 py-3 bg-white hover:bg-gray-200 rounded-lg text-white transition-colors">
              System Settings
            </button>
            <button className="px-4 py-3 bg-slate-700 hover:bg-slate-600 rounded-lg text-white transition-colors">
              View Logs
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
