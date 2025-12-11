'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import api from '@/lib/api'

interface Bug {
  id: number
  title: string
  severity: string
  vulnerability_type: string
  validated: boolean
  paid_out: boolean
  bounty_amount: number
  hunter_id: number
  target_url: string
  created_at: string
}

interface Pagination {
  page: number
  per_page: number
  total: number
  pages: number
}

export default function AdminBugsPage() {
  const [bugs, setBugs] = useState<Bug[]>([])
  const [pagination, setPagination] = useState<Pagination | null>(null)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [severityFilter, setSeverityFilter] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [selectedBug, setSelectedBug] = useState<Bug | null>(null)
  const [showValidateModal, setShowValidateModal] = useState(false)
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [bountyAmount, setBountyAmount] = useState('')
  const [rejectionReason, setRejectionReason] = useState('')

  useEffect(() => {
    fetchBugs()
  }, [currentPage, search, statusFilter, severityFilter])

  const fetchBugs = async () => {
    try {
      setLoading(true)
      const response = await api.get('/admin/bugs', {
        params: {
          page: currentPage,
          per_page: 20,
          search: search || undefined,
          status: statusFilter || undefined,
          severity: severityFilter || undefined
        }
      })
      setBugs(response.data.bugs)
      setPagination(response.data.pagination)
    } catch (error) {
      console.error('Failed to fetch bugs:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleValidate = async () => {
    if (!selectedBug || !bountyAmount) return

    try {
      await api.post(`/admin/bugs/${selectedBug.id}/validate`, {
        bounty_amount: parseFloat(bountyAmount)
      })
      setShowValidateModal(false)
      setBountyAmount('')
      setSelectedBug(null)
      await fetchBugs()
    } catch (error) {
      console.error('Failed to validate bug:', error)
    }
  }

  const handleReject = async () => {
    if (!selectedBug || !rejectionReason) return

    try {
      await api.post(`/admin/bugs/${selectedBug.id}/reject`, {
        reason: rejectionReason
      })
      setShowRejectModal(false)
      setRejectionReason('')
      setSelectedBug(null)
      await fetchBugs()
    } catch (error) {
      console.error('Failed to reject bug:', error)
    }
  }

  const getSeverityColor = (severity: string) => {
    const colors: { [key: string]: string } = {
      critical: 'bg-red-500/20 text-red-400',
      high: 'bg-orange-500/20 text-orange-400',
      medium: 'bg-yellow-500/20 text-yellow-400',
      low: 'bg-green-500/20 text-green-400',
      info: 'bg-white/20 text-gray-400'
    }
    return colors[severity] || 'bg-slate-500/20 text-slate-400'
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
            <h1 className="text-4xl font-bold text-white mb-2">Bug Moderation</h1>
            <p className="text-slate-400">Review and validate bug reports</p>
          </div>
        </div>

        <div className="bg-slate-800 rounded-xl p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <input
              type="text"
              placeholder="Search bugs..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:ring-2 focus:ring-white/50 focus:border-transparent"
            />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-white/50 focus:border-transparent"
            >
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="validated">Validated</option>
              <option value="paid">Paid</option>
            </select>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-white/50 focus:border-transparent"
            >
              <option value="">All Severity</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
              <option value="info">Info</option>
            </select>
            <button
              onClick={fetchBugs}
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white transition-colors"
            >
              Search
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center text-slate-400 py-12">Loading bugs...</div>
        ) : (
          <>
            <div className="bg-slate-800 rounded-xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-700">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Bug</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Severity</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Type</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Status</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Bounty</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Submitted</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700">
                    {bugs.map((bug) => (
                      <tr key={bug.id} className="hover:bg-slate-700/50 transition-colors">
                        <td className="px-6 py-4">
                          <div>
                            <div className="text-white font-semibold">{bug.title}</div>
                            <div className="text-slate-400 text-sm">{bug.target_url}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-3 py-1 rounded-full text-sm ${getSeverityColor(bug.severity)}`}>
                            {bug.severity}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-slate-300 text-sm">{bug.vulnerability_type}</div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="space-y-1">
                            {bug.validated ? (
                              <div className="text-green-400 text-sm">Validated</div>
                            ) : (
                              <div className="text-yellow-400 text-sm">Pending</div>
                            )}
                            {bug.paid_out && (
                              <div className="text-gray-400 text-sm">Paid</div>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-green-400 font-semibold">
                            ${bug.bounty_amount.toLocaleString()}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-slate-400">
                            {new Date(bug.created_at).toLocaleDateString()}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          {!bug.validated && (
                            <div className="flex gap-2">
                              <button
                                onClick={() => {
                                  setSelectedBug(bug)
                                  setShowValidateModal(true)
                                }}
                                className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded-lg text-white text-sm transition-colors"
                              >
                                Validate
                              </button>
                              <button
                                onClick={() => {
                                  setSelectedBug(bug)
                                  setShowRejectModal(true)
                                }}
                                className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded-lg text-white text-sm transition-colors"
                              >
                                Reject
                              </button>
                            </div>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {pagination && pagination.pages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-6">
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Previous
                </button>
                <span className="text-white">
                  Page {pagination.page} of {pagination.pages}
                </span>
                <button
                  onClick={() => setCurrentPage(Math.min(pagination.pages, currentPage + 1))}
                  disabled={currentPage === pagination.pages}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {showValidateModal && selectedBug && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-xl p-8 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold text-white mb-4">Validate Bug</h2>
            <p className="text-slate-400 mb-6">Set bounty amount for: {selectedBug.title}</p>
            <input
              type="number"
              placeholder="Bounty amount ($)"
              value={bountyAmount}
              onChange={(e) => setBountyAmount(e.target.value)}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:ring-2 focus:ring-white/50 focus:border-transparent mb-6"
            />
            <div className="flex gap-4">
              <button
                onClick={handleValidate}
                className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-white transition-colors"
              >
                Validate
              </button>
              <button
                onClick={() => {
                  setShowValidateModal(false)
                  setBountyAmount('')
                  setSelectedBug(null)
                }}
                className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {showRejectModal && selectedBug && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-xl p-8 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold text-white mb-4">Reject Bug</h2>
            <p className="text-slate-400 mb-6">Provide rejection reason for: {selectedBug.title}</p>
            <textarea
              placeholder="Rejection reason..."
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              rows={4}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:ring-2 focus:ring-white/50 focus:border-transparent mb-6"
            />
            <div className="flex gap-4">
              <button
                onClick={handleReject}
                className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-white transition-colors"
              >
                Reject
              </button>
              <button
                onClick={() => {
                  setShowRejectModal(false)
                  setRejectionReason('')
                  setSelectedBug(null)
                }}
                className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
