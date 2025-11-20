"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'

interface Policy {
  policy_id: number
  policy_number: string
  coverage_amount: number
  premium_amount: number
  status: string
  start_date: string
  end_date: string
}

interface PremiumData {
  coverage_amount: number
  final_premium: number
  monthly_premium: number
  pre_audit_score: number
  risk_level: string
  risk_multiplier: number
}

export default function InsurancePage() {
  const [policies, setPolicies] = useState<Policy[]>([])
  const [coverageAmount, setCoverageAmount] = useState('1000000')
  const [premiumData, setPremiumData] = useState<PremiumData | null>(null)
  const [loading, setLoading] = useState(false)

  const calculatePremium = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/insurance/calculate-premium', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ coverage_amount: parseFloat(coverageAmount) })
      })
      const data = await response.json()
      setPremiumData(data.data)
    } catch (error) {
      console.error('Error calculating premium:', error)
    }
    setLoading(false)
  }

  const createPolicy = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/insurance/policies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          coverage_amount: parseFloat(coverageAmount),
          covered_assets: [
            { type: 'web_app', url: 'https://example.com' }
          ]
        })
      })
      const data = await response.json()
      if (data.success) {
        alert('Policy created successfully!')
        loadPolicies()
      }
    } catch (error) {
      console.error('Error creating policy:', error)
    }
    setLoading(false)
  }

  const loadPolicies = async () => {
    try {
      const response = await fetch('/api/insurance/policies', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      const data = await response.json()
      setPolicies(data.data || [])
    } catch (error) {
      console.error('Error loading policies:', error)
    }
  }

  useEffect(() => {
    loadPolicies()
  }, [])

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Bug Bounty Insurance</h1>

      <div className="grid md:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-2xl font-semibold mb-4">Calculate Premium</h2>
          
          <div className="mb-4">
            <label className="block mb-2">Coverage Amount ($)</label>
            <input
              type="number"
              value={coverageAmount}
              onChange={(e) => setCoverageAmount(e.target.value)}
              className="w-full p-2 border rounded"
              placeholder="1000000"
            />
          </div>

          <Button onClick={calculatePremium} disabled={loading} className="w-full mb-4">
            Calculate Premium
          </Button>

          {premiumData && (
            <div className="bg-gray-50 p-4 rounded">
              <h3 className="font-semibold mb-2">Premium Details</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Coverage:</span>
                  <span className="font-semibold">${premiumData.coverage_amount.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span>Annual Premium:</span>
                  <span className="font-semibold">${premiumData.final_premium.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span>Monthly Premium:</span>
                  <span className="font-semibold">${premiumData.monthly_premium.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span>Security Score:</span>
                  <span className="font-semibold">{premiumData.pre_audit_score}/100</span>
                </div>
                <div className="flex justify-between">
                  <span>Risk Level:</span>
                  <span className={`font-semibold ${
                    premiumData.risk_level === 'low' ? 'text-green-600' :
                    premiumData.risk_level === 'medium' ? 'text-yellow-600' :
                    'text-red-600'
                  }`}>{premiumData.risk_level.toUpperCase()}</span>
                </div>
              </div>
              
              <Button onClick={createPolicy} disabled={loading} className="w-full mt-4">
                Purchase Policy
              </Button>
            </div>
          )}
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-2xl font-semibold mb-4">Your Policies</h2>
          
          {policies.length === 0 ? (
            <p className="text-gray-500">No policies yet</p>
          ) : (
            <div className="space-y-4">
              {policies.map((policy) => (
                <div key={policy.policy_id} className="border p-4 rounded">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-semibold">{policy.policy_number}</h3>
                      <p className="text-sm text-gray-600">
                        Coverage: ${policy.coverage_amount.toLocaleString()}
                      </p>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs ${
                      policy.status === 'active' ? 'bg-green-100 text-green-800' :
                      policy.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {policy.status}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600">
                    <p>Premium: ${policy.premium_amount.toLocaleString()}/year</p>
                    <p>Valid: {new Date(policy.start_date).toLocaleDateString()} - {new Date(policy.end_date).toLocaleDateString()}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="mt-8 bg-blue-50 p-6 rounded-lg">
        <h2 className="text-xl font-semibold mb-4">How It Works</h2>
        <ul className="space-y-2 text-sm">
          <li>1. Calculate premium based on your coverage needs</li>
          <li>2. Premium is 2-5% of coverage with risk multiplier (0.5x - 2.5x)</li>
          <li>3. Pre-audit security assessment determines your risk level</li>
          <li>4. Purchase policy and get instant coverage</li>
          <li>5. Submit claims for bug-related incidents up to coverage amount</li>
        </ul>
      </div>
    </div>
  )
}
