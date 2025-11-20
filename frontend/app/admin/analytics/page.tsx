'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import api from '@/lib/api'

interface AnalyticsData {
  period: string
  new_users: number
  new_bugs: number
  new_scans: number
  daily_stats: Array<{
    date: string
    users: number
    bugs: number
    scans: number
  }>
}

export default function AdminAnalyticsPage() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [days, setDays] = useState(30)

  useEffect(() => {
    fetchAnalytics()
  }, [days])

  const fetchAnalytics = async () => {
    try {
      setLoading(true)
      const response = await api.get('/admin/analytics', {
        params: { days }
      })
      setAnalytics(response.data)
    } catch (error) {
      console.error('Failed to fetch analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <Link href="/admin">
              <button className="text-slate-400 hover:text-white mb-2 flex items-center">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Back to Admin Dashboard
              </button>
            </Link>
            <h1 className="text-4xl font-bold text-white mb-2">Platform Analytics</h1>
            <p className="text-slate-400">Insights and trends</p>
          </div>
        </div>

        <div className="bg-slate-800 rounded-xl p-6 mb-6">
          <div className="flex items-center gap-4">
            <label className="text-white">Time Period:</label>
            <select
              value={days}
              onChange={(e) => setDays(parseInt(e.target.value))}
              className="px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
              <option value={365}>Last year</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div className="text-center text-slate-400 py-12">Loading analytics...</div>
        ) : analytics ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-slate-800 rounded-xl p-6 border border-cyan-500/20">
                <div className="flex items-center justify-between mb-4">
                  <div className="text-3xl">👥</div>
                  <div className="text-sm text-slate-400">New Users</div>
                </div>
                <div className="text-4xl font-bold text-white mb-2">
                  {analytics.new_users.toLocaleString()}
                </div>
                <div className="text-sm text-cyan-400">{analytics.period}</div>
              </div>

              <div className="bg-slate-800 rounded-xl p-6 border border-purple-500/20">
                <div className="flex items-center justify-between mb-4">
                  <div className="text-3xl">🐛</div>
                  <div className="text-sm text-slate-400">New Bugs</div>
                </div>
                <div className="text-4xl font-bold text-white mb-2">
                  {analytics.new_bugs.toLocaleString()}
                </div>
                <div className="text-sm text-purple-400">{analytics.period}</div>
              </div>

              <div className="bg-slate-800 rounded-xl p-6 border border-blue-500/20">
                <div className="flex items-center justify-between mb-4">
                  <div className="text-3xl">🔍</div>
                  <div className="text-sm text-slate-400">New Scans</div>
                </div>
                <div className="text-4xl font-bold text-white mb-2">
                  {analytics.new_scans.toLocaleString()}
                </div>
                <div className="text-sm text-blue-400">{analytics.period}</div>
              </div>
            </div>

            <div className="bg-slate-800 rounded-xl p-6">
              <h3 className="text-xl font-bold text-white mb-6">Daily Statistics</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-700">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Date</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Users</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Bugs</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Scans</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700">
                    {analytics.daily_stats.map((stat) => (
                      <tr key={stat.date} className="hover:bg-slate-700/50 transition-colors">
                        <td className="px-6 py-4">
                          <div className="text-white">{stat.date}</div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-cyan-400 font-semibold">{stat.users}</div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-purple-400 font-semibold">{stat.bugs}</div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-blue-400 font-semibold">{stat.scans}</div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        ) : (
          <div className="text-center text-red-400">Failed to load analytics</div>
        )}
      </div>
    </div>
  )
}
