'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import api from '@/lib/api'

interface Notification {
  type: string
  title: string
  message: string
  data: any
  read: boolean
  timestamp: string
}

export default function NotificationsPage() {
  const router = useRouter()
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'unread'>('all')
  const [unreadCount, setUnreadCount] = useState(0)

  const fetchNotifications = async () => {
    try {
      const response = await api.get('/notifications', {
        params: {
          limit: 100,
          unread_only: filter === 'unread'
        }
      })
      setNotifications(response.data.notifications)
    } catch (error) {
      console.error('Failed to fetch notifications:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchUnreadCount = async () => {
    try {
      const response = await api.get('/notifications/unread-count')
      setUnreadCount(response.data.count)
    } catch (error) {
      console.error('Failed to fetch unread count:', error)
    }
  }

  useEffect(() => {
    fetchNotifications()
    fetchUnreadCount()
  }, [filter])

  const markAsRead = async (index: number) => {
    try {
      await api.post(`/notifications/${index}/read`)
      await fetchNotifications()
      await fetchUnreadCount()
    } catch (error) {
      console.error('Failed to mark as read:', error)
    }
  }

  const markAllAsRead = async () => {
    try {
      await api.post('/notifications/read-all')
      await fetchNotifications()
      await fetchUnreadCount()
    } catch (error) {
      console.error('Failed to mark all as read:', error)
    }
  }

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'scan_complete':
        return ''
      case 'bug_validated':
        return '[OK]'
      case 'payment_received':
        return ''
      case 'guild_invitation':
        return ''
      default:
        return ''
    }
  }

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'scan_complete':
        return 'border-l-white'
      case 'bug_validated':
        return 'border-l-green-500'
      case 'payment_received':
        return 'border-l-yellow-500'
      case 'guild_invitation':
        return 'border-l-white'
      default:
        return 'border-l-slate-500'
    }
  }

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(minutes / 60)
    const days = Math.floor(hours / 24)

    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    if (days < 7) return `${days}d ago`
    return date.toLocaleDateString()
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center text-slate-400">Loading notifications...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Notifications</h1>
            <p className="text-slate-400">
              {unreadCount > 0 ? `You have ${unreadCount} unread notifications` : 'All caught up!'}
            </p>
          </div>
          <Link href="/dashboard">
            <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white transition-colors">
              Back to Dashboard
            </button>
          </Link>
        </div>

        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setFilter('all')}
            className={`px-6 py-2 rounded-lg transition-colors ${
              filter === 'all'
                ? 'bg-cyan-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('unread')}
            className={`px-6 py-2 rounded-lg transition-colors ${
              filter === 'unread'
                ? 'bg-cyan-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            Unread ({unreadCount})
          </button>
          {unreadCount > 0 && (
            <button
              onClick={markAllAsRead}
              className="ml-auto px-6 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white transition-colors"
            >
              Mark all as read
            </button>
          )}
        </div>

        {notifications.length === 0 ? (
          <div className="bg-slate-800 rounded-xl p-12 text-center">
            <div className="text-6xl mb-4"></div>
            <h3 className="text-xl font-semibold text-white mb-2">No notifications</h3>
            <p className="text-slate-400">
              {filter === 'unread' ? 'No unread notifications' : 'You have no notifications yet'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {notifications.map((notification, index) => (
              <div
                key={index}
                className={`bg-slate-800 rounded-xl p-6 border-l-4 ${getNotificationColor(
                  notification.type
                )} ${!notification.read ? 'ring-2 ring-cyan-500/20' : ''}`}
              >
                <div className="flex items-start gap-4">
                  <div className="text-4xl">{getNotificationIcon(notification.type)}</div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-lg font-semibold text-white">{notification.title}</h3>
                      <span className="text-sm text-slate-400">
                        {formatTime(notification.timestamp)}
                      </span>
                    </div>
                    <p className="text-slate-300 mb-3">{notification.message}</p>
                    <div className="flex gap-3">
                      {!notification.read && (
                        <button
                          onClick={() => markAsRead(index)}
                          className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white text-sm transition-colors"
                        >
                          Mark as read
                        </button>
                      )}
                      {notification.type === 'scan_complete' && notification.data.scan_id && (
                        <Link href={`/scans/${notification.data.scan_id}`}>
                          <button className="px-4 py-1.5 bg-slate-700 hover:bg-slate-600 rounded-lg text-white text-sm transition-colors">
                            View Scan
                          </button>
                        </Link>
                      )}
                      {notification.type === 'bug_validated' && notification.data.bug_id && (
                        <Link href={`/bugs/${notification.data.bug_id}`}>
                          <button className="px-4 py-1.5 bg-slate-700 hover:bg-slate-600 rounded-lg text-white text-sm transition-colors">
                            View Bug
                          </button>
                        </Link>
                      )}
                      {notification.type === 'guild_invitation' && notification.data.guild_id && (
                        <Link href={`/guilds/${notification.data.guild_id}`}>
                          <button className="px-4 py-1.5 bg-slate-700 hover:bg-slate-600 rounded-lg text-white text-sm transition-colors">
                            View Guild
                          </button>
                        </Link>
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
