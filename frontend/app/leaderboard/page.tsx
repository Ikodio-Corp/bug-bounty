'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import api from '@/lib/api'

export default function LeaderboardPage() {
  const router = useRouter()
  const [leaderboard, setLeaderboard] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [timeframe, setTimeframe] = useState<'all' | 'month' | 'week'>('all')
  const [category, setCategory] = useState<'bounties' | 'bugs' | 'reputation'>('reputation')

  useEffect(() => {
    fetchLeaderboard()
  }, [timeframe, category])

  const fetchLeaderboard = async () => {
    try {
      setLoading(true)
      const response = await api.get('/users/leaderboard', {
        params: {
          timeframe,
          category,
          limit: 50
        }
      })
      setLeaderboard(response.data.leaderboard)
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRankColor = (position: number) => {
    if (position === 1) return 'text-yellow-400'
    if (position === 2) return 'text-slate-300'
    if (position === 3) return 'text-orange-400'
    return 'text-slate-400'
  }

  const getRankIcon = (position: number) => {
    if (position === 1) return '🥇'
    if (position === 2) return '🥈'
    if (position === 3) return '🥉'
    return `#${position}`
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Leaderboard</h1>
            <p className="text-slate-400">Top security researchers and bug hunters</p>
          </div>
          <Link href="/dashboard">
            <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white transition-colors">
              Back to Dashboard
            </button>
          </Link>
        </div>

        <div className="flex flex-wrap gap-4 mb-6">
          <div className="flex gap-2">
            <button
              onClick={() => setTimeframe('all')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                timeframe === 'all'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              All Time
            </button>
            <button
              onClick={() => setTimeframe('month')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                timeframe === 'month'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              This Month
            </button>
            <button
              onClick={() => setTimeframe('week')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                timeframe === 'week'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              This Week
            </button>
          </div>

          <div className="flex gap-2 ml-auto">
            <button
              onClick={() => setCategory('reputation')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                category === 'reputation'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Reputation
            </button>
            <button
              onClick={() => setCategory('bounties')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                category === 'bounties'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Earnings
            </button>
            <button
              onClick={() => setCategory('bugs')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                category === 'bugs'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Bugs Found
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center text-slate-400 py-12">Loading leaderboard...</div>
        ) : (
          <div className="bg-slate-800 rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-700">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                      Rank
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                      Hunter
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                      Reputation
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                      Total Earnings
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                      Bugs Found
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                      Hunter Rank
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {leaderboard.map((hunter, index) => (
                    <tr
                      key={hunter.id}
                      className="hover:bg-slate-700/50 transition-colors cursor-pointer"
                      onClick={() => router.push(`/profile/${hunter.username}`)}
                    >
                      <td className="px-6 py-4">
                        <div className={`text-2xl font-bold ${getRankColor(index + 1)}`}>
                          {getRankIcon(index + 1)}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                            {hunter.avatar_url ? (
                              <img
                                src={hunter.avatar_url}
                                alt={hunter.username}
                                className="w-full h-full rounded-full object-cover"
                              />
                            ) : (
                              hunter.username[0].toUpperCase()
                            )}
                          </div>
                          <div>
                            <div className="text-white font-semibold">{hunter.username}</div>
                            {hunter.location && (
                              <div className="text-slate-400 text-sm">{hunter.location}</div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-cyan-400 font-bold text-lg">
                          {hunter.reputation_score}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-green-400 font-semibold">
                          ${hunter.total_bounties_earned.toLocaleString()}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-white font-semibold">{hunter.total_bugs_found}</div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-3 py-1 bg-slate-700 text-slate-300 rounded-full text-sm">
                          {hunter.hunter_rank}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {leaderboard.length === 0 && (
              <div className="text-center py-12 text-slate-400">No data available</div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
