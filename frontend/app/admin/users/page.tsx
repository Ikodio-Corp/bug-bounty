'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import api from '@/lib/api'

interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  is_verified: boolean
  subscription_tier: string
  reputation_score: number
  total_bugs_found: number
  total_bounties_earned: number
  created_at: string
  last_login: string | null
}

interface Pagination {
  page: number
  per_page: number
  total: number
  pages: number
}

export default function AdminUsersPage() {
  const router = useRouter()
  const [users, setUsers] = useState<User[]>([])
  const [pagination, setPagination] = useState<Pagination | null>(null)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [currentPage, setCurrentPage] = useState(1)

  useEffect(() => {
    fetchUsers()
  }, [currentPage, search, roleFilter, statusFilter])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      const response = await api.get('/admin/users', {
        params: {
          page: currentPage,
          per_page: 20,
          search: search || undefined,
          role: roleFilter || undefined,
          status: statusFilter || undefined
        }
      })
      setUsers(response.data.users)
      setPagination(response.data.pagination)
    } catch (error) {
      console.error('Failed to fetch users:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleUserStatus = async (userId: number, currentStatus: boolean) => {
    try {
      await api.put(`/admin/users/${userId}/status`, {
        is_active: !currentStatus
      })
      await fetchUsers()
    } catch (error) {
      console.error('Failed to update user status:', error)
    }
  }

  const deleteUser = async (userId: number) => {
    if (!confirm('Are you sure you want to delete this user?')) {
      return
    }

    try {
      await api.delete(`/admin/users/${userId}`)
      await fetchUsers()
    } catch (error) {
      console.error('Failed to delete user:', error)
    }
  }

  const getRoleColor = (role: string) => {
    const colors: { [key: string]: string } = {
      admin: 'bg-red-500/20 text-red-400',
      hunter: 'bg-cyan-500/20 text-cyan-400',
      developer: 'bg-white/20 text-gray-400',
      company: 'bg-white/20 text-gray-400'
    }
    return colors[role] || 'bg-slate-500/20 text-slate-400'
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
            <h1 className="text-4xl font-bold text-white mb-2">User Management</h1>
            <p className="text-slate-400">Manage user accounts and permissions</p>
          </div>
        </div>

        <div className="bg-slate-800 rounded-xl p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <input
              type="text"
              placeholder="Search users..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:ring-2 focus:ring-white/50 focus:border-transparent"
            />
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-white/50 focus:border-transparent"
            >
              <option value="">All Roles</option>
              <option value="admin">Admin</option>
              <option value="hunter">Hunter</option>
              <option value="developer">Developer</option>
              <option value="company">Company</option>
            </select>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-white/50 focus:border-transparent"
            >
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="verified">Verified</option>
              <option value="unverified">Unverified</option>
            </select>
            <button
              onClick={fetchUsers}
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white transition-colors"
            >
              Search
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center text-slate-400 py-12">Loading users...</div>
        ) : (
          <>
            <div className="bg-slate-800 rounded-xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-700">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">User</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Role</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Status</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Stats</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Joined</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700">
                    {users.map((user) => (
                      <tr key={user.id} className="hover:bg-slate-700/50 transition-colors">
                        <td className="px-6 py-4">
                          <div>
                            <div className="text-white font-semibold">{user.username}</div>
                            <div className="text-slate-400 text-sm">{user.email}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-3 py-1 rounded-full text-sm ${getRoleColor(user.role)}`}>
                            {user.role}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="space-y-1">
                            <div className={`text-sm ${user.is_active ? 'text-green-400' : 'text-red-400'}`}>
                              {user.is_active ? 'Active' : 'Inactive'}
                            </div>
                            <div className={`text-sm ${user.is_verified ? 'text-gray-400' : 'text-slate-400'}`}>
                              {user.is_verified ? 'Verified' : 'Unverified'}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm">
                            <div className="text-slate-300">{user.total_bugs_found} bugs</div>
                            <div className="text-green-400">${user.total_bounties_earned.toLocaleString()}</div>
                            <div className="text-cyan-400">{user.reputation_score} rep</div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-slate-400">
                            {new Date(user.created_at).toLocaleDateString()}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex gap-2">
                            <button
                              onClick={() => toggleUserStatus(user.id, user.is_active)}
                              className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                                user.is_active
                                  ? 'bg-red-600 hover:bg-red-700 text-white'
                                  : 'bg-green-600 hover:bg-green-700 text-white'
                              }`}
                            >
                              {user.is_active ? 'Deactivate' : 'Activate'}
                            </button>
                            <button
                              onClick={() => deleteUser(user.id)}
                              className="px-3 py-1 bg-slate-700 hover:bg-slate-600 rounded-lg text-white text-sm transition-colors"
                            >
                              Delete
                            </button>
                          </div>
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
    </div>
  )
}
