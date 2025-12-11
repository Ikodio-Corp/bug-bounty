'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import api from '@/lib/api'

export default function SettingsPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('account')
  const [preferences, setPreferences] = useState({
    email_notifications: true,
    push_notifications: true
  })
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  })
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetchPreferences()
  }, [])

  const fetchPreferences = async () => {
    try {
      const response = await api.get('/users/me')
      setPreferences({
        email_notifications: response.data.email_notifications,
        push_notifications: response.data.push_notifications
      })
    } catch (error) {
      console.error('Failed to fetch preferences:', error)
    } finally {
      setLoading(false)
    }
  }

  const updateNotificationPreferences = async () => {
    try {
      await api.put('/notifications/preferences', preferences)
      setMessage('Notification preferences updated successfully')
      setTimeout(() => setMessage(''), 3000)
    } catch (error) {
      console.error('Failed to update preferences:', error)
      setMessage('Failed to update preferences')
    }
  }

  const updatePassword = async (e: React.FormEvent) => {
    e.preventDefault()

    if (passwordData.new_password !== passwordData.confirm_password) {
      setMessage('Passwords do not match')
      return
    }

    try {
      await api.put('/auth/change-password', {
        old_password: passwordData.current_password,
        new_password: passwordData.new_password
      })
      setMessage('Password updated successfully')
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: ''
      })
      setTimeout(() => setMessage(''), 3000)
    } catch (error) {
      console.error('Failed to update password:', error)
      setMessage('Failed to update password')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center text-slate-400">Loading settings...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-bold text-white">Settings</h1>
          <Link href="/dashboard">
            <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white transition-colors">
              Back to Dashboard
            </button>
          </Link>
        </div>

        {message && (
          <div className="mb-6 p-4 bg-cyan-600/20 border border-cyan-500 rounded-lg text-cyan-400">
            {message}
          </div>
        )}

        <div className="bg-slate-800 rounded-xl overflow-hidden">
          <div className="flex border-b border-slate-700">
            <button
              onClick={() => setActiveTab('account')}
              className={`flex-1 px-6 py-4 font-semibold transition-colors ${
                activeTab === 'account'
                  ? 'bg-slate-700 text-white border-b-2 border-cyan-500'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Account
            </button>
            <button
              onClick={() => setActiveTab('notifications')}
              className={`flex-1 px-6 py-4 font-semibold transition-colors ${
                activeTab === 'notifications'
                  ? 'bg-slate-700 text-white border-b-2 border-cyan-500'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Notifications
            </button>
            <button
              onClick={() => setActiveTab('security')}
              className={`flex-1 px-6 py-4 font-semibold transition-colors ${
                activeTab === 'security'
                  ? 'bg-slate-700 text-white border-b-2 border-cyan-500'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Security
            </button>
            <button
              onClick={() => setActiveTab('privacy')}
              className={`flex-1 px-6 py-4 font-semibold transition-colors ${
                activeTab === 'privacy'
                  ? 'bg-slate-700 text-white border-b-2 border-cyan-500'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Privacy
            </button>
          </div>

          <div className="p-6">
            {activeTab === 'account' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-white mb-4">Account Settings</h2>
                <div>
                  <h3 className="text-lg font-semibold text-white mb-2">Change Password</h3>
                  <form onSubmit={updatePassword} className="space-y-4">
                    <div>
                      <label className="block text-slate-400 text-sm mb-2">
                        Current Password
                      </label>
                      <input
                        type="password"
                        value={passwordData.current_password}
                        onChange={(e) =>
                          setPasswordData({ ...passwordData, current_password: e.target.value })
                        }
                        className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-white/50 focus:border-transparent"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-slate-400 text-sm mb-2">New Password</label>
                      <input
                        type="password"
                        value={passwordData.new_password}
                        onChange={(e) =>
                          setPasswordData({ ...passwordData, new_password: e.target.value })
                        }
                        className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-white/50 focus:border-transparent"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-slate-400 text-sm mb-2">
                        Confirm New Password
                      </label>
                      <input
                        type="password"
                        value={passwordData.confirm_password}
                        onChange={(e) =>
                          setPasswordData({ ...passwordData, confirm_password: e.target.value })
                        }
                        className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-white/50 focus:border-transparent"
                        required
                      />
                    </div>
                    <button
                      type="submit"
                      className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white font-semibold transition-colors"
                    >
                      Update Password
                    </button>
                  </form>
                </div>
              </div>
            )}

            {activeTab === 'notifications' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-white mb-4">Notification Preferences</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-slate-700 rounded-lg">
                    <div>
                      <h3 className="text-white font-semibold">Email Notifications</h3>
                      <p className="text-slate-400 text-sm">
                        Receive email notifications for important updates
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={preferences.email_notifications}
                        onChange={(e) =>
                          setPreferences({
                            ...preferences,
                            email_notifications: e.target.checked
                          })
                        }
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-slate-600 peer-focus:ring-4 peer-focus:ring-cyan-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-600"></div>
                    </label>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-slate-700 rounded-lg">
                    <div>
                      <h3 className="text-white font-semibold">Push Notifications</h3>
                      <p className="text-slate-400 text-sm">
                        Receive push notifications in your browser
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={preferences.push_notifications}
                        onChange={(e) =>
                          setPreferences({
                            ...preferences,
                            push_notifications: e.target.checked
                          })
                        }
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-slate-600 peer-focus:ring-4 peer-focus:ring-cyan-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-600"></div>
                    </label>
                  </div>
                  <button
                    onClick={updateNotificationPreferences}
                    className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white font-semibold transition-colors"
                  >
                    Save Preferences
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-white mb-4">Security Settings</h2>
                <div className="space-y-4">
                  <div className="p-4 bg-slate-700 rounded-lg">
                    <h3 className="text-white font-semibold mb-2">Two-Factor Authentication</h3>
                    <p className="text-slate-400 text-sm mb-4">
                      Add an extra layer of security to your account
                    </p>
                    <button className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white transition-colors">
                      Enable 2FA
                    </button>
                  </div>
                  <div className="p-4 bg-slate-700 rounded-lg">
                    <h3 className="text-white font-semibold mb-2">Active Sessions</h3>
                    <p className="text-slate-400 text-sm mb-4">
                      Manage devices where you are currently logged in
                    </p>
                    <button className="px-4 py-2 bg-slate-600 hover:bg-slate-500 rounded-lg text-white transition-colors">
                      View Sessions
                    </button>
                  </div>
                  <div className="p-4 bg-slate-700 rounded-lg">
                    <h3 className="text-white font-semibold mb-2">API Keys</h3>
                    <p className="text-slate-400 text-sm mb-4">
                      Manage your API keys for programmatic access
                    </p>
                    <button className="px-4 py-2 bg-slate-600 hover:bg-slate-500 rounded-lg text-white transition-colors">
                      Manage API Keys
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'privacy' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-white mb-4">Privacy Settings</h2>
                <div className="space-y-4">
                  <div className="p-4 bg-slate-700 rounded-lg">
                    <h3 className="text-white font-semibold mb-2">Data Export</h3>
                    <p className="text-slate-400 text-sm mb-4">
                      Download a copy of your personal data
                    </p>
                    <Link href="/api/gdpr/users/me/data-export">
                      <button className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white transition-colors">
                        Export Data
                      </button>
                    </Link>
                  </div>
                  <div className="p-4 bg-slate-700 rounded-lg">
                    <h3 className="text-white font-semibold mb-2">Consent Management</h3>
                    <p className="text-slate-400 text-sm mb-4">
                      Manage your privacy and data processing consents
                    </p>
                    <button className="px-4 py-2 bg-slate-600 hover:bg-slate-500 rounded-lg text-white transition-colors">
                      Manage Consents
                    </button>
                  </div>
                  <div className="p-4 bg-red-900/20 border border-red-500 rounded-lg">
                    <h3 className="text-red-400 font-semibold mb-2">Delete Account</h3>
                    <p className="text-slate-400 text-sm mb-4">
                      Permanently delete your account and all associated data
                    </p>
                    <button className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-white transition-colors">
                      Delete Account
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
