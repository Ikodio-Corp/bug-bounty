"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'

interface Resource {
  resource_id: number
  resource_type: string
  resource_name: string
  cloud_provider: string
  region: string
  monthly_cost: number
  auto_scaling_enabled: boolean
  created_at: string
}

interface Job {
  job_id: number
  job_type: string
  status: string
  target_environment: string
  estimated_duration_minutes: number
  actual_duration_minutes: number
  triggered_by_ai: boolean
  created_at: string
  completed_at: string
}

interface HealingEvent {
  event_id: number
  incident_type: string
  severity: string
  healing_action_taken: string
  healing_status: string
  resolution_time_seconds: number
  ai_confidence_score: number
  detected_at: string
  resolved_at: string
}

export default function DevOpsPage() {
  const [activeTab, setActiveTab] = useState<'resources' | 'jobs' | 'healing'>('resources')
  const [resources, setResources] = useState<Resource[]>([])
  const [jobs, setJobs] = useState<Job[]>([])
  const [healingEvents, setHealingEvents] = useState<HealingEvent[]>([])
  const [loading, setLoading] = useState(false)

  const loadResources = async () => {
    try {
      const response = await fetch('/api/devops/resources', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      const data = await response.json()
      setResources(data.data || [])
    } catch (error) {
      console.error('Error loading resources:', error)
    }
  }

  const loadJobs = async () => {
    try {
      const response = await fetch('/api/devops/jobs', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      const data = await response.json()
      setJobs(data.data || [])
    } catch (error) {
      console.error('Error loading jobs:', error)
    }
  }

  const loadHealingEvents = async () => {
    try {
      const response = await fetch('/api/devops/self-healing/events', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      const data = await response.json()
      setHealingEvents(data.data || [])
    } catch (error) {
      console.error('Error loading healing events:', error)
    }
  }

  const optimizeCosts = async () => {
    if (!confirm('Run AI cost optimization analysis?')) return

    setLoading(true)
    try {
      const response = await fetch('/api/devops/optimize-costs', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      const data = await response.json()
      if (data.success) {
        alert(`Found ${data.data.total_recommendations} optimizations! Potential savings: $${data.data.total_savings_monthly.toLocaleString()}/month (${data.data.savings_percentage.toFixed(1)}%)`)
      }
    } catch (error) {
      console.error('Error optimizing costs:', error)
    }
    setLoading(false)
  }

  useEffect(() => {
    loadResources()
    loadJobs()
    loadHealingEvents()
  }, [])

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold">DevOps Autopilot</h1>
        <Button onClick={optimizeCosts} disabled={loading} className="bg-green-600 hover:bg-green-700">
          Optimize Costs (AI)
        </Button>
      </div>

      <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 rounded-lg mb-8">
        <h2 className="text-xl font-semibold mb-2">Autonomous DevOps Operations</h2>
        <p className="text-sm text-gray-700">
          AI-powered infrastructure management that replaces 95% of traditional DevOps tasks.
          Autonomous provisioning, zero-downtime deployment, self-healing, and cost optimization (40-60% savings).
        </p>
      </div>

      <div className="flex gap-4 mb-6">
        <Button
          onClick={() => setActiveTab('resources')}
          variant={activeTab === 'resources' ? 'default' : 'outline'}
        >
          Infrastructure
        </Button>
        <Button
          onClick={() => setActiveTab('jobs')}
          variant={activeTab === 'jobs' ? 'default' : 'outline'}
        >
          Automation Jobs
        </Button>
        <Button
          onClick={() => setActiveTab('healing')}
          variant={activeTab === 'healing' ? 'default' : 'outline'}
        >
          Self-Healing Events
        </Button>
      </div>

      {activeTab === 'resources' && (
        <div>
          <h2 className="text-2xl font-semibold mb-4">Infrastructure Resources</h2>
          {resources.length === 0 ? (
            <p className="text-gray-500">No resources yet</p>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {resources.map((resource) => (
                <div key={resource.resource_id} className="bg-white p-6 rounded-lg shadow">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-semibold">{resource.resource_name}</h3>
                      <p className="text-sm text-gray-600">{resource.resource_type}</p>
                    </div>
                    {resource.auto_scaling_enabled && (
                      <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                        Auto-Scaling
                      </span>
                    )}
                  </div>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Provider:</span>
                      <span className="font-semibold">{resource.cloud_provider}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Region:</span>
                      <span className="font-semibold">{resource.region}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Cost:</span>
                      <span className="font-semibold">${resource.monthly_cost.toLocaleString()}/mo</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Created:</span>
                      <span className="text-xs">{new Date(resource.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'jobs' && (
        <div>
          <h2 className="text-2xl font-semibold mb-4">Automation Jobs</h2>
          {jobs.length === 0 ? (
            <p className="text-gray-500">No jobs yet</p>
          ) : (
            <div className="space-y-3">
              {jobs.map((job) => (
                <div key={job.job_id} className="bg-white p-4 rounded-lg shadow">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-semibold">{job.job_type.replace(/_/g, ' ').toUpperCase()}</h3>
                      <p className="text-sm text-gray-600">Environment: {job.target_environment}</p>
                    </div>
                    <div className="flex gap-2">
                      {job.triggered_by_ai && (
                        <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
                          AI Triggered
                        </span>
                      )}
                      <span className={`px-2 py-1 rounded text-xs ${
                        job.status === 'completed' ? 'bg-green-100 text-green-800' :
                        job.status === 'running' ? 'bg-blue-100 text-blue-800' :
                        job.status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {job.status}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-4 text-sm text-gray-600">
                    <span>Estimated: {job.estimated_duration_minutes}min</span>
                    {job.actual_duration_minutes && (
                      <span>Actual: {job.actual_duration_minutes}min</span>
                    )}
                    <span>Created: {new Date(job.created_at).toLocaleString()}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'healing' && (
        <div>
          <h2 className="text-2xl font-semibold mb-4">Self-Healing Events</h2>
          <div className="bg-blue-50 p-4 rounded-lg mb-4">
            <p className="text-sm">
              AI detects incidents and automatically heals them without human intervention.
              Average resolution time: 120 seconds.
            </p>
          </div>
          {healingEvents.length === 0 ? (
            <p className="text-gray-500">No healing events yet</p>
          ) : (
            <div className="space-y-3">
              {healingEvents.map((event) => (
                <div key={event.event_id} className="bg-white p-4 rounded-lg shadow">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-semibold">{event.incident_type.replace(/_/g, ' ').toUpperCase()}</h3>
                      <p className="text-sm text-gray-600">Detected: {new Date(event.detected_at).toLocaleString()}</p>
                    </div>
                    <div className="flex gap-2">
                      <span className={`px-2 py-1 rounded text-xs ${
                        event.severity === 'critical' ? 'bg-red-100 text-red-800' :
                        event.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                        event.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {event.severity}
                      </span>
                      <span className={`px-2 py-1 rounded text-xs ${
                        event.healing_status === 'resolved' ? 'bg-green-100 text-green-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {event.healing_status}
                      </span>
                    </div>
                  </div>
                  <div className="mb-3">
                    <p className="text-sm mb-1"><strong>Action Taken:</strong></p>
                    <p className="text-sm text-gray-700">{event.healing_action_taken}</p>
                  </div>
                  <div className="flex gap-4 text-sm">
                    <span className="text-gray-600">
                      Resolution Time: <strong>{event.resolution_time_seconds}s</strong>
                    </span>
                    <span className="text-gray-600">
                      AI Confidence: <strong>{(event.ai_confidence_score * 100).toFixed(0)}%</strong>
                    </span>
                    {event.resolved_at && (
                      <span className="text-gray-600">
                        Resolved: {new Date(event.resolved_at).toLocaleString()}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
