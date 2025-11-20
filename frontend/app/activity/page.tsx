'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import api from '@/lib/api'

interface Activity {
  id: number
  type: string
  title: string
  description: string
  timestamp: string
  metadata: any
}

export default function ActivityPage() {
  const [activities, setActivities] = useState<Activity[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetchActivities()
  }, [filter])

  const fetchActivities = async () => {
    try {
      setLoading(true)
      const response = await api.get('/users/activity', {
        params: { type: filter !== 'all' ? filter : undefined }
      })
      setActivities(response.data)
    } catch (error) {
      console.error('Failed to fetch activities:', error)
    } finally {
      setLoading(false)
    }
  }

  const getActivityIcon = (type: string) => {
    const icons: { [key: string]: string } = {
      scan_started: '🔍',
      scan_completed: '✅',
      bug_submitted: '🐛',
      bug_validated: '✓',
      payment_received: '💰',
      guild_joined: '👥',
      marketplace_sale: '💵',
      profile_updated: '👤'
    }
    return icons[type] || '📝'
  }

  const getActivityColor = (type: string) => {
    const colors: { [key: string]: string } = {
      scan_started: 'border-blue-500/20',
      scan_completed: 'border-green-500/20',
      bug_submitted: 'border-purple-500/20',
      bug_validated: 'border-cyan-500/20',
      payment_received: 'border-green-500/20',
      guild_joined: 'border-yellow-500/20',
      marketplace_sale: 'border-green-500/20'
    }
    return colors[type] || 'border-slate-700'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <Link href="/dashboard">
            <button className="text-slate-400 hover:text-white mb-2 flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Dashboard
            </button>
          </Link>
          <h1 className="text-4xl font-bold text-white mb-2">Activity Feed</h1>
          <p className="text-slate-400">Track your recent actions and achievements</p>
        </div>

        <div className="bg-slate-800 rounded-xl p-6 mb-6">
          <div className="flex gap-2 overflow-x-auto">
            {['all', 'scans', 'bugs', 'payments', 'guilds', 'marketplace'].map(filterType => (
              <button
                key={filterType}
                onClick={() => setFilter(filterType)}
                className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                  filter === filterType
                    ? 'bg-cyan-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                {filterType.charAt(0).toUpperCase() + filterType.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="text-center text-slate-400 py-12">Loading activities...</div>
        ) : activities.length === 0 ? (
          <div className="bg-slate-800 rounded-xl p-12 text-center">
            <div className="text-6xl mb-4">📭</div>
            <h3 className="text-xl font-semibold text-white mb-2">No Activities Yet</h3>
            <p className="text-slate-400">Start scanning and hunting bugs to see your activity here</p>
          </div>
        ) : (
          <div className="space-y-4">
            {activities.map(activity => (
              <div
                key={activity.id}
                className={`bg-slate-800 rounded-xl p-6 border-l-4 ${getActivityColor(activity.type)}`}
              >
                <div className="flex items-start gap-4">
                  <div className="text-3xl">{getActivityIcon(activity.type)}</div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white mb-1">{activity.title}</h3>
                    <p className="text-slate-400 mb-2">{activity.description}</p>
                    <div className="flex items-center gap-4 text-sm text-slate-500">
                      <span>{new Date(activity.timestamp).toLocaleString()}</span>
                      {activity.metadata && (
                        <span className="px-2 py-1 bg-slate-700 rounded">
                          {activity.metadata.details}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
