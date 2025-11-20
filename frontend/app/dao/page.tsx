"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'

interface Proposal {
  proposal_id: number
  proposal_number: string
  title: string
  status: string
  votes_for: number
  votes_against: number
  votes_abstain: number
  voting_ends_at: string
}

interface TokenBalance {
  token_balance: number
  staked_balance: number
  voting_power: number
  earned_from_bug_bounties: number
  earned_from_marketplace: number
  earned_from_governance: number
}

export default function DAOPage() {
  const [proposals, setProposals] = useState<Proposal[]>([])
  const [tokenBalance, setTokenBalance] = useState<TokenBalance | null>(null)
  const [loading, setLoading] = useState(false)
  const [showCreateForm, setShowCreateForm] = useState(false)

  const [newProposal, setNewProposal] = useState({
    title: '',
    description: '',
    proposal_type: 'parameter_change'
  })

  const loadProposals = async () => {
    try {
      const response = await fetch('/api/dao/proposals?status=active', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      const data = await response.json()
      setProposals(data.data || [])
    } catch (error) {
      console.error('Error loading proposals:', error)
    }
  }

  const loadTokenBalance = async () => {
    try {
      const response = await fetch('/api/dao/tokens/balance', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      const data = await response.json()
      setTokenBalance(data.data)
    } catch (error) {
      console.error('Error loading balance:', error)
    }
  }

  const createProposal = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/dao/proposals', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(newProposal)
      })
      const data = await response.json()
      if (data.success) {
        alert('Proposal created successfully!')
        setShowCreateForm(false)
        loadProposals()
        setNewProposal({ title: '', description: '', proposal_type: 'parameter_change' })
      }
    } catch (error) {
      console.error('Error creating proposal:', error)
      alert('Error: ' + error)
    }
    setLoading(false)
  }

  const vote = async (proposalId: number, choice: string) => {
    setLoading(true)
    try {
      const response = await fetch(`/api/dao/proposals/${proposalId}/vote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ vote_choice: choice })
      })
      const data = await response.json()
      if (data.success) {
        alert('Vote cast successfully!')
        loadProposals()
      }
    } catch (error) {
      console.error('Error voting:', error)
      alert('Error: ' + error)
    }
    setLoading(false)
  }

  const stakeTokens = async () => {
    const amount = prompt('Enter amount to stake:')
    if (!amount) return

    setLoading(true)
    try {
      const response = await fetch('/api/dao/tokens/stake', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ amount: parseFloat(amount) })
      })
      const data = await response.json()
      if (data.success) {
        alert('Tokens staked successfully!')
        loadTokenBalance()
      }
    } catch (error) {
      console.error('Error staking:', error)
    }
    setLoading(false)
  }

  useEffect(() => {
    loadProposals()
    loadTokenBalance()
  }, [])

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">DAO Governance</h1>

      {tokenBalance && (
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-sm text-gray-600 mb-1">IKOD Balance</h3>
            <div className="text-2xl font-bold">{tokenBalance.token_balance.toLocaleString()}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-sm text-gray-600 mb-1">Staked</h3>
            <div className="text-2xl font-bold">{tokenBalance.staked_balance.toLocaleString()}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-sm text-gray-600 mb-1">Voting Power</h3>
            <div className="text-2xl font-bold text-blue-600">{tokenBalance.voting_power.toLocaleString()}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow flex items-center">
            <Button onClick={stakeTokens} disabled={loading} className="w-full">
              Stake Tokens
            </Button>
          </div>
        </div>
      )}

      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold">Active Proposals</h2>
        <Button onClick={() => setShowCreateForm(!showCreateForm)}>
          {showCreateForm ? 'Cancel' : 'Create Proposal'}
        </Button>
      </div>

      {showCreateForm && (
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <h3 className="text-lg font-semibold mb-4">Create New Proposal</h3>
          <div className="space-y-4">
            <div>
              <label className="block mb-2 text-sm">Title</label>
              <input
                type="text"
                value={newProposal.title}
                onChange={(e) => setNewProposal({ ...newProposal, title: e.target.value })}
                className="w-full p-2 border rounded"
                placeholder="Proposal title"
              />
            </div>
            <div>
              <label className="block mb-2 text-sm">Description</label>
              <textarea
                value={newProposal.description}
                onChange={(e) => setNewProposal({ ...newProposal, description: e.target.value })}
                className="w-full p-2 border rounded h-32"
                placeholder="Detailed description"
              />
            </div>
            <div>
              <label className="block mb-2 text-sm">Type</label>
              <select
                value={newProposal.proposal_type}
                onChange={(e) => setNewProposal({ ...newProposal, proposal_type: e.target.value })}
                className="w-full p-2 border rounded"
              >
                <option value="parameter_change">Parameter Change</option>
                <option value="treasury_spend">Treasury Spend</option>
                <option value="feature_request">Feature Request</option>
                <option value="other">Other</option>
              </select>
            </div>
            <Button onClick={createProposal} disabled={loading} className="w-full">
              Submit Proposal
            </Button>
          </div>
        </div>
      )}

      {proposals.length === 0 ? (
        <p className="text-gray-500">No active proposals</p>
      ) : (
        <div className="space-y-4">
          {proposals.map((proposal) => (
            <div key={proposal.proposal_id} className="bg-white p-6 rounded-lg shadow">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold">{proposal.title}</h3>
                  <p className="text-sm text-gray-600">{proposal.proposal_number}</p>
                </div>
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                  {proposal.status}
                </span>
              </div>

              <div className="mb-4">
                <div className="flex justify-between text-sm mb-2">
                  <span>Voting Progress</span>
                  <span>Ends: {new Date(proposal.voting_ends_at).toLocaleDateString()}</span>
                </div>
                <div className="space-y-2">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>For</span>
                      <span className="font-semibold text-green-600">{proposal.votes_for.toLocaleString()}</span>
                    </div>
                    <div className="bg-gray-200 h-2 rounded">
                      <div 
                        className="bg-green-600 h-2 rounded" 
                        style={{ width: `${(proposal.votes_for / (proposal.votes_for + proposal.votes_against + proposal.votes_abstain) * 100) || 0}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Against</span>
                      <span className="font-semibold text-red-600">{proposal.votes_against.toLocaleString()}</span>
                    </div>
                    <div className="bg-gray-200 h-2 rounded">
                      <div 
                        className="bg-red-600 h-2 rounded" 
                        style={{ width: `${(proposal.votes_against / (proposal.votes_for + proposal.votes_against + proposal.votes_abstain) * 100) || 0}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex gap-2">
                <Button
                  onClick={() => vote(proposal.proposal_id, 'for')}
                  disabled={loading}
                  className="flex-1 bg-green-600 hover:bg-green-700"
                >
                  Vote For
                </Button>
                <Button
                  onClick={() => vote(proposal.proposal_id, 'against')}
                  disabled={loading}
                  className="flex-1 bg-red-600 hover:bg-red-700"
                >
                  Vote Against
                </Button>
                <Button
                  onClick={() => vote(proposal.proposal_id, 'abstain')}
                  disabled={loading}
                  variant="outline"
                  className="flex-1"
                >
                  Abstain
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-8 bg-purple-50 p-6 rounded-lg">
        <h2 className="text-xl font-semibold mb-4">About DAO Governance</h2>
        <ul className="space-y-2 text-sm">
          <li>IKOD token holders can create and vote on proposals</li>
          <li>Voting power = token balance + staked balance</li>
          <li>Quorum requirement: 10% of circulating supply</li>
          <li>Voting period: 7 days per proposal</li>
          <li>Earn IKOD through bug bounties, marketplace, and governance participation</li>
        </ul>
      </div>
    </div>
  )
}
