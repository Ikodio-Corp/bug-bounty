'use client'

import { useState } from 'react'
import Link from 'next/link'
import { SimpleCard, SimpleCardHeader, SimpleCardTitle, SimpleCardContent } from '@/components/ui/simple-card'
import { SimpleBadge } from '@/components/ui/simple-badge'

interface Proposal {
  id: number
  title: string
  description: string
  status: 'active' | 'passed' | 'rejected' | 'pending'
  votesFor: number
  votesAgainst: number
  endDate: string
  proposer: string
}

export default function DAOPage() {
  const [activeTab, setActiveTab] = useState('proposals')

  const proposals: Proposal[] = [
    {
      id: 1,
      title: 'Increase Bug Bounty Rewards by 20%',
      description: 'Proposal to increase all bug bounty rewards by 20% to attract more security researchers.',
      status: 'active',
      votesFor: 1250,
      votesAgainst: 340,
      endDate: '2025-12-01',
      proposer: 'hunter_elite'
    },
    {
      id: 2,
      title: 'Add Support for Ethereum Smart Contract Audits',
      description: 'Expand platform capabilities to include smart contract vulnerability detection and auditing.',
      status: 'active',
      votesFor: 980,
      votesAgainst: 120,
      endDate: '2025-11-28',
      proposer: 'crypto_researcher'
    },
    {
      id: 3,
      title: 'Implement Weekly Community Challenges',
      description: 'Create weekly security challenges with special rewards for top performers.',
      status: 'passed',
      votesFor: 2100,
      votesAgainst: 450,
      endDate: '2025-11-15',
      proposer: 'community_mod'
    }
  ]

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: any } = {
      active: 'info',
      passed: 'success',
      rejected: 'error',
      pending: 'warning'
    }
    return colors[status]
  }

  const calculateVotePercentage = (votesFor: number, votesAgainst: number) => {
    const total = votesFor + votesAgainst
    return total > 0 ? Math.round((votesFor / total) * 100) : 0
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
          <h1 className="text-4xl font-bold text-white mb-2">DAO Governance</h1>
          <p className="text-slate-400">Decentralized decision making for platform direction</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <SimpleCard>
            <SimpleCardHeader>
              <SimpleCardTitle className="text-lg">Total Proposals</SimpleCardTitle>
            </SimpleCardHeader>
            <SimpleCardContent>
              <div className="text-4xl font-bold text-cyan-400">28</div>
              <p className="text-slate-400 text-sm mt-2">12 active, 16 completed</p>
            </SimpleCardContent>
          </SimpleCard>

          <SimpleCard>
            <SimpleCardHeader>
              <SimpleCardTitle className="text-lg">Your Voting Power</SimpleCardTitle>
            </SimpleCardHeader>
            <SimpleCardContent>
              <div className="text-4xl font-bold text-purple-400">1,250</div>
              <p className="text-slate-400 text-sm mt-2">Based on reputation score</p>
            </SimpleCardContent>
          </SimpleCard>

          <SimpleCard>
            <SimpleCardHeader>
              <SimpleCardTitle className="text-lg">Active Voters</SimpleCardTitle>
            </SimpleCardHeader>
            <SimpleCardContent>
              <div className="text-4xl font-bold text-green-400">3,421</div>
              <p className="text-slate-400 text-sm mt-2">Participated this month</p>
            </SimpleCardContent>
          </SimpleCard>
        </div>

        <div className="bg-slate-800 rounded-xl p-6 mb-8">
          <div className="flex gap-4">
            <button
              onClick={() => setActiveTab('proposals')}
              className={`px-6 py-2 rounded-lg font-semibold transition-colors ${
                activeTab === 'proposals'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Active Proposals
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`px-6 py-2 rounded-lg font-semibold transition-colors ${
                activeTab === 'history'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              History
            </button>
            <button className="ml-auto px-6 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-white font-semibold transition-colors">
              Create Proposal
            </button>
          </div>
        </div>

        <div className="space-y-6">
          {proposals.map(proposal => (
            <SimpleCard key={proposal.id} className="hover:border-cyan-500 transition-colors">
              <SimpleCardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <SimpleCardTitle className="text-2xl">{proposal.title}</SimpleCardTitle>
                      <SimpleBadge variant={getStatusColor(proposal.status)}>
                        {proposal.status}
                      </SimpleBadge>
                    </div>
                    <p className="text-slate-400 mb-4">{proposal.description}</p>
                    <div className="flex items-center gap-4 text-sm text-slate-500">
                      <span>Proposed by: {proposal.proposer}</span>
                      <span>Ends: {new Date(proposal.endDate).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
              </SimpleCardHeader>
              <SimpleCardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-slate-400">Voting Progress</span>
                      <span className="text-sm font-semibold text-white">
                        {calculateVotePercentage(proposal.votesFor, proposal.votesAgainst)}% in favor
                      </span>
                    </div>
                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-green-500 to-cyan-500"
                        style={{
                          width: `${calculateVotePercentage(proposal.votesFor, proposal.votesAgainst)}%`
                        }}
                      />
                    </div>
                    <div className="flex items-center justify-between mt-2 text-sm">
                      <span className="text-green-400">
                        For: {proposal.votesFor.toLocaleString()}
                      </span>
                      <span className="text-red-400">
                        Against: {proposal.votesAgainst.toLocaleString()}
                      </span>
                    </div>
                  </div>

                  {proposal.status === 'active' && (
                    <div className="flex gap-4 pt-4 border-t border-slate-700">
                      <button className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-white font-semibold transition-colors">
                        Vote For
                      </button>
                      <button className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-white font-semibold transition-colors">
                        Vote Against
                      </button>
                      <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white font-semibold transition-colors">
                        Details
                      </button>
                    </div>
                  )}
                </div>
              </SimpleCardContent>
            </SimpleCard>
          ))}
        </div>

        <div className="mt-12 bg-slate-800 rounded-xl p-8">
          <h2 className="text-2xl font-bold text-white mb-4">How DAO Governance Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div className="text-4xl mb-3">📝</div>
              <h3 className="text-xl font-semibold text-white mb-2">1. Create Proposal</h3>
              <p className="text-slate-400">
                Any member with 500+ reputation can create proposals for platform improvements.
              </p>
            </div>
            <div>
              <div className="text-4xl mb-3">🗳️</div>
              <h3 className="text-xl font-semibold text-white mb-2">2. Community Vote</h3>
              <p className="text-slate-400">
                Members vote using their reputation-based voting power during the 7-day period.
              </p>
            </div>
            <div>
              <div className="text-4xl mb-3">✅</div>
              <h3 className="text-xl font-semibold text-white mb-2">3. Execute Decision</h3>
              <p className="text-slate-400">
                Proposals with 60%+ approval are automatically implemented by smart contracts.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
