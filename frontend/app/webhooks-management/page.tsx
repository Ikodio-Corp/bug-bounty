'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { SimpleCard, SimpleCardHeader, SimpleCardTitle, SimpleCardContent } from '@/components/ui/simple-card'
import { SimpleBadge } from '@/components/ui/simple-badge'
import api from '@/lib/api'

interface Webhook {
  id: number
  name: string
  url: string
  events: string[]
  active: boolean
  secret: string
  lastTriggered?: string
  successCount: number
  failureCount: number
  createdAt: string
}

export default function WebhooksPage() {
  const [webhooks, setWebhooks] = useState<Webhook[]>([])
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newWebhook, setNewWebhook] = useState({
    name: '',
    url: '',
    events: [] as string[]
  })
  const [loading, setLoading] = useState(true)

  const availableEvents = [
    'scan.started',
    'scan.completed',
    'scan.failed',
    'bug.submitted',
    'bug.validated',
    'bug.rejected',
    'payment.sent',
    'guild.joined',
    'marketplace.purchase'
  ]

  useEffect(() => {
    loadWebhooks()
  }, [])

  const loadWebhooks = async () => {
    try {
      const response = await api.get('/webhooks')
      setWebhooks(response.data)
    } catch (error) {
      console.error('Failed to load webhooks:', error)
      // Mock data
      setWebhooks([
        {
          id: 1,
          name: 'Slack Notifications',
          url: 'https://hooks.slack.com/services/xxx/yyy/zzz',
          events: ['bug.validated', 'payment.sent'],
          active: true,
          secret: 'whsec_xxxxxxxxxxxxx',
          lastTriggered: '2025-11-20T10:30:00Z',
          successCount: 145,
          failureCount: 2,
          createdAt: '2025-10-15T08:00:00Z'
        },
        {
          id: 2,
          name: 'Discord Bot',
          url: 'https://discord.com/api/webhooks/xxx/yyy',
          events: ['scan.completed', 'bug.submitted'],
          active: true,
          secret: 'whsec_yyyyyyyyyyyyy',
          lastTriggered: '2025-11-19T18:45:00Z',
          successCount: 89,
          failureCount: 0,
          createdAt: '2025-10-20T12:30:00Z'
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const createWebhook = async () => {
    try {
      const response = await api.post('/webhooks', newWebhook)
      setWebhooks([...webhooks, response.data])
      setShowCreateModal(false)
      setNewWebhook({ name: '', url: '', events: [] })
    } catch (error) {
      console.error('Failed to create webhook:', error)
    }
  }

  const deleteWebhook = async (id: number) => {
    if (!confirm('Are you sure you want to delete this webhook?')) return
    
    try {
      await api.delete(`/webhooks/${id}`)
      setWebhooks(webhooks.filter(w => w.id !== id))
    } catch (error) {
      console.error('Failed to delete webhook:', error)
    }
  }

  const toggleWebhook = async (id: number, active: boolean) => {
    try {
      await api.put(`/webhooks/${id}`, { active })
      setWebhooks(webhooks.map(w => w.id === id ? { ...w, active } : w))
    } catch (error) {
      console.error('Failed to toggle webhook:', error)
    }
  }

  const testWebhook = async (id: number) => {
    try {
      await api.post(`/webhooks/${id}/test`)
      alert('Test webhook sent successfully')
    } catch (error) {
      console.error('Failed to test webhook:', error)
      alert('Failed to send test webhook')
    }
  }

  const toggleEvent = (event: string) => {
    if (newWebhook.events.includes(event)) {
      setNewWebhook({
        ...newWebhook,
        events: newWebhook.events.filter(e => e !== event)
      })
    } else {
      setNewWebhook({
        ...newWebhook,
        events: [...newWebhook.events, event]
      })
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <Link href="/dashboard">
            <button className="text-slate-400 hover:text-white mb-2 flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Dashboard
            </button>
          </Link>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">Webhooks</h1>
              <p className="text-slate-400">Integrate with external services</p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white font-semibold transition-colors"
            >
              Create Webhook
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <SimpleCard>
            <SimpleCardHeader>
              <SimpleCardTitle className="text-lg">Total Webhooks</SimpleCardTitle>
            </SimpleCardHeader>
            <SimpleCardContent>
              <div className="text-4xl font-bold text-cyan-400">{webhooks.length}</div>
              <p className="text-slate-400 text-sm mt-2">
                {webhooks.filter(w => w.active).length} active
              </p>
            </SimpleCardContent>
          </SimpleCard>

          <SimpleCard>
            <SimpleCardHeader>
              <SimpleCardTitle className="text-lg">Success Rate</SimpleCardTitle>
            </SimpleCardHeader>
            <SimpleCardContent>
              <div className="text-4xl font-bold text-green-400">
                {webhooks.length > 0
                  ? Math.round(
                      (webhooks.reduce((acc, w) => acc + w.successCount, 0) /
                        (webhooks.reduce((acc, w) => acc + w.successCount + w.failureCount, 0) || 1)) *
                        100
                    )
                  : 0}
                %
              </div>
              <p className="text-slate-400 text-sm mt-2">Last 30 days</p>
            </SimpleCardContent>
          </SimpleCard>

          <SimpleCard>
            <SimpleCardHeader>
              <SimpleCardTitle className="text-lg">Total Deliveries</SimpleCardTitle>
            </SimpleCardHeader>
            <SimpleCardContent>
              <div className="text-4xl font-bold text-purple-400">
                {webhooks.reduce((acc, w) => acc + w.successCount + w.failureCount, 0)}
              </div>
              <p className="text-slate-400 text-sm mt-2">
                {webhooks.reduce((acc, w) => acc + w.failureCount, 0)} failed
              </p>
            </SimpleCardContent>
          </SimpleCard>
        </div>

        <div className="space-y-6">
          {webhooks.map(webhook => (
            <SimpleCard key={webhook.id} className="hover:border-cyan-500 transition-colors">
              <SimpleCardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <SimpleCardTitle className="text-2xl">{webhook.name}</SimpleCardTitle>
                      <SimpleBadge variant={webhook.active ? 'success' : 'error'}>
                        {webhook.active ? 'Active' : 'Inactive'}
                      </SimpleBadge>
                    </div>
                    <div className="text-slate-400 mb-3">
                      <code className="text-sm bg-slate-700 px-2 py-1 rounded">{webhook.url}</code>
                    </div>
                    <div className="flex flex-wrap gap-2 mb-3">
                      {webhook.events.map(event => (
                        <SimpleBadge key={event} variant="info">
                          {event}
                        </SimpleBadge>
                      ))}
                    </div>
                  </div>
                </div>
              </SimpleCardHeader>
              <SimpleCardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-slate-400">Success</div>
                      <div className="text-green-400 font-semibold">{webhook.successCount}</div>
                    </div>
                    <div>
                      <div className="text-slate-400">Failures</div>
                      <div className="text-red-400 font-semibold">{webhook.failureCount}</div>
                    </div>
                    <div>
                      <div className="text-slate-400">Last Triggered</div>
                      <div className="text-white font-semibold">
                        {webhook.lastTriggered
                          ? new Date(webhook.lastTriggered).toLocaleDateString()
                          : 'Never'}
                      </div>
                    </div>
                    <div>
                      <div className="text-slate-400">Created</div>
                      <div className="text-white font-semibold">
                        {new Date(webhook.createdAt).toLocaleDateString()}
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-4 pt-4 border-t border-slate-700">
                    <button
                      onClick={() => testWebhook(webhook.id)}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-semibold transition-colors"
                    >
                      Test
                    </button>
                    <button
                      onClick={() => toggleWebhook(webhook.id, !webhook.active)}
                      className={`px-4 py-2 rounded-lg text-white font-semibold transition-colors ${
                        webhook.active
                          ? 'bg-yellow-600 hover:bg-yellow-700'
                          : 'bg-green-600 hover:bg-green-700'
                      }`}
                    >
                      {webhook.active ? 'Deactivate' : 'Activate'}
                    </button>
                    <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white font-semibold transition-colors">
                      Edit
                    </button>
                    <button
                      onClick={() => deleteWebhook(webhook.id)}
                      className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-white font-semibold transition-colors ml-auto"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </SimpleCardContent>
            </SimpleCard>
          ))}
        </div>

        {webhooks.length === 0 && (
          <SimpleCard>
            <SimpleCardContent className="py-12 text-center">
              <div className="text-6xl mb-4">🔗</div>
              <h3 className="text-xl font-semibold text-white mb-2">No Webhooks Yet</h3>
              <p className="text-slate-400 mb-4">Create your first webhook to start receiving events</p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-6 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white font-semibold transition-colors"
              >
                Create Webhook
              </button>
            </SimpleCardContent>
          </SimpleCard>
        )}

        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-slate-800 rounded-xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <h2 className="text-2xl font-bold text-white mb-6">Create New Webhook</h2>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-white font-semibold mb-2">Webhook Name</label>
                  <input
                    type="text"
                    value={newWebhook.name}
                    onChange={(e) => setNewWebhook({ ...newWebhook, name: e.target.value })}
                    className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                    placeholder="Slack Notifications"
                  />
                </div>

                <div>
                  <label className="block text-white font-semibold mb-2">Payload URL</label>
                  <input
                    type="url"
                    value={newWebhook.url}
                    onChange={(e) => setNewWebhook({ ...newWebhook, url: e.target.value })}
                    className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                    placeholder="https://your-service.com/webhook"
                  />
                </div>

                <div>
                  <label className="block text-white font-semibold mb-3">Events</label>
                  <div className="grid grid-cols-2 gap-3">
                    {availableEvents.map(event => (
                      <div
                        key={event}
                        onClick={() => toggleEvent(event)}
                        className={`p-3 rounded-lg cursor-pointer transition-colors ${
                          newWebhook.events.includes(event)
                            ? 'bg-cyan-600 border-2 border-cyan-400'
                            : 'bg-slate-700 border-2 border-slate-600 hover:border-slate-500'
                        }`}
                      >
                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            checked={newWebhook.events.includes(event)}
                            onChange={() => {}}
                            className="mr-2"
                          />
                          <span className="text-white text-sm">{event}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex gap-4 mt-8">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-6 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white font-semibold transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={createWebhook}
                  disabled={!newWebhook.name || !newWebhook.url || newWebhook.events.length === 0}
                  className="flex-1 px-6 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white font-semibold transition-colors disabled:opacity-50"
                >
                  Create Webhook
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="mt-12 bg-slate-800 rounded-xl p-8">
          <h2 className="text-2xl font-bold text-white mb-4">Webhook Security</h2>
          <div className="space-y-4 text-slate-300">
            <p>
              All webhook payloads are signed with a secret key. Verify the signature to ensure the webhook is from IKODIO.
            </p>
            <div className="bg-slate-900 rounded-lg p-4">
              <code className="text-sm text-cyan-400">
                X-IKODIO-Signature: sha256=xxxxxxxxxxxxxxxxxxxxx
              </code>
            </div>
            <p className="text-sm text-slate-400">
              Learn more in our <Link href="/docs" className="text-cyan-400 hover:underline">webhook documentation</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
