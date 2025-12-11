'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import api from '@/lib/api'

interface Profile {
  user: {
    id: number
    username: string
    email: string
    full_name: string
    bio: string
    avatar_url: string
    location: string
    website: string
    github_username: string
    twitter_username: string
    linkedin_url: string
    discord_username: string
    total_bounties_earned: number
    total_bugs_found: number
    reputation_score: number
    hunter_rank: string
    specializations: string
    skills: string
    subscription_tier: string
    created_at: string
  }
  profile: {
    about_me: string
    experience_years: number
    total_scans: number
    successful_reports: number
    acceptance_rate: number
    avg_severity: number
    preferred_platforms: string
    preferred_vulnerabilities: string
    certifications: string
    portfolio_url: string
    blog_url: string
  }
}

export default function ProfilePage() {
  const router = useRouter()
  const [profile, setProfile] = useState<Profile | null>(null)
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [formData, setFormData] = useState({
    full_name: '',
    bio: '',
    location: '',
    website: '',
    github_username: '',
    twitter_username: '',
    linkedin_url: '',
    discord_username: '',
    specializations: '',
    skills: ''
  })

  useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    try {
      const response = await api.get('/profile')
      setProfile(response.data)
      setFormData({
        full_name: response.data.user.full_name || '',
        bio: response.data.user.bio || '',
        location: response.data.user.location || '',
        website: response.data.user.website || '',
        github_username: response.data.user.github_username || '',
        twitter_username: response.data.user.twitter_username || '',
        linkedin_url: response.data.user.linkedin_url || '',
        discord_username: response.data.user.discord_username || '',
        specializations: response.data.user.specializations || '',
        skills: response.data.user.skills || ''
      })
    } catch (error) {
      console.error('Failed to fetch profile:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.put('/profile', formData)
      await fetchProfile()
      setEditing(false)
    } catch (error) {
      console.error('Failed to update profile:', error)
    }
  }

  const getRankColor = (rank: string) => {
    const colors: { [key: string]: string } = {
      bronze: 'text-orange-400',
      silver: 'text-slate-300',
      gold: 'text-yellow-400',
      platinum: 'text-cyan-400',
      diamond: 'text-gray-400'
    }
    return colors[rank.toLowerCase()] || 'text-slate-400'
  }

  const getRankIcon = (rank: string) => {
    const icons: { [key: string]: string } = {
      bronze: '',
      silver: '',
      gold: '',
      platinum: '',
      diamond: ''
    }
    return icons[rank.toLowerCase()] || ''
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center text-slate-400">Loading profile...</div>
        </div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center text-red-400">Failed to load profile</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-bold text-white">My Profile</h1>
          <div className="flex gap-3">
            <Link href="/dashboard">
              <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white transition-colors">
                Back to Dashboard
              </button>
            </Link>
            {!editing && (
              <button
                onClick={() => setEditing(true)}
                className="px-6 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white transition-colors"
              >
                Edit Profile
              </button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <div className="bg-slate-800 rounded-xl p-6 text-center">
              <div className="w-32 h-32 bg-gradient-to-br from-gray-400 to-gray-500 rounded-full mx-auto mb-4 flex items-center justify-center text-5xl">
                {profile.user.avatar_url ? (
                  <img
                    src={profile.user.avatar_url}
                    alt={profile.user.username}
                    className="w-full h-full rounded-full object-cover"
                  />
                ) : (
                  profile.user.username[0].toUpperCase()
                )}
              </div>
              <h2 className="text-2xl font-bold text-white mb-1">{profile.user.username}</h2>
              <p className="text-slate-400 mb-4">{profile.user.email}</p>
              <div className="flex items-center justify-center gap-2 mb-4">
                <span className="text-3xl">{getRankIcon(profile.user.hunter_rank)}</span>
                <span className={`text-lg font-semibold ${getRankColor(profile.user.hunter_rank)}`}>
                  {profile.user.hunter_rank}
                </span>
              </div>
              <div className="bg-slate-700 rounded-lg p-4 mb-4">
                <div className="text-3xl font-bold text-cyan-400 mb-1">
                  {profile.user.reputation_score}
                </div>
                <div className="text-sm text-slate-400">Reputation Score</div>
              </div>
              <div className="space-y-3">
                <div className="bg-slate-700 rounded-lg p-3">
                  <div className="text-2xl font-bold text-white">
                    ${profile.user.total_bounties_earned.toLocaleString()}
                  </div>
                  <div className="text-sm text-slate-400">Total Earned</div>
                </div>
                <div className="bg-slate-700 rounded-lg p-3">
                  <div className="text-2xl font-bold text-white">{profile.user.total_bugs_found}</div>
                  <div className="text-sm text-slate-400">Bugs Found</div>
                </div>
              </div>
            </div>

            {profile.user.location && (
              <div className="bg-slate-800 rounded-xl p-4 mt-4">
                <div className="text-slate-400 text-sm mb-2"> Location</div>
                <div className="text-white">{profile.user.location}</div>
              </div>
            )}

            <div className="bg-slate-800 rounded-xl p-4 mt-4">
              <div className="text-slate-400 text-sm mb-3">Connect</div>
              <div className="space-y-2">
                {profile.user.website && (
                  <a
                    href={profile.user.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-cyan-400 hover:text-cyan-300"
                  >
                     Website
                  </a>
                )}
                {profile.user.github_username && (
                  <a
                    href={`https://github.com/${profile.user.github_username}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-cyan-400 hover:text-cyan-300"
                  >
                     GitHub
                  </a>
                )}
                {profile.user.twitter_username && (
                  <a
                    href={`https://twitter.com/${profile.user.twitter_username}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-cyan-400 hover:text-cyan-300"
                  >
                     Twitter
                  </a>
                )}
                {profile.user.linkedin_url && (
                  <a
                    href={profile.user.linkedin_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-cyan-400 hover:text-cyan-300"
                  >
                     LinkedIn
                  </a>
                )}
              </div>
            </div>
          </div>

          <div className="lg:col-span-2">
            {editing ? (
              <form onSubmit={handleUpdate} className="bg-slate-800 rounded-xl p-6">
                <h3 className="text-2xl font-bold text-white mb-6">Edit Profile</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-slate-400 text-sm mb-2">Full Name</label>
                    <input
                      type="text"
                      value={formData.full_name}
                      onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                      className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-white/50 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 text-sm mb-2">Bio</label>
                    <textarea
                      value={formData.bio}
                      onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                      rows={4}
                      className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-white/50 focus:border-transparent"
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-slate-400 text-sm mb-2">Location</label>
                      <input
                        type="text"
                        value={formData.location}
                        onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                        className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-white/50 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-400 text-sm mb-2">Website</label>
                      <input
                        type="url"
                        value={formData.website}
                        onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                        className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-white/50 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-slate-400 text-sm mb-2">GitHub Username</label>
                      <input
                        type="text"
                        value={formData.github_username}
                        onChange={(e) =>
                          setFormData({ ...formData, github_username: e.target.value })
                        }
                        className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-white/50 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-400 text-sm mb-2">Twitter Username</label>
                      <input
                        type="text"
                        value={formData.twitter_username}
                        onChange={(e) =>
                          setFormData({ ...formData, twitter_username: e.target.value })
                        }
                        className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-white/50 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-slate-400 text-sm mb-2">Specializations</label>
                    <input
                      type="text"
                      value={formData.specializations}
                      onChange={(e) =>
                        setFormData({ ...formData, specializations: e.target.value })
                      }
                      placeholder="e.g., Web Security, Mobile Security"
                      className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-white/50 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 text-sm mb-2">Skills</label>
                    <input
                      type="text"
                      value={formData.skills}
                      onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
                      placeholder="e.g., Penetration Testing, Code Review"
                      className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-white/50 focus:border-transparent"
                    />
                  </div>
                  <div className="flex gap-3 pt-4">
                    <button
                      type="submit"
                      className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white font-semibold transition-colors"
                    >
                      Save Changes
                    </button>
                    <button
                      type="button"
                      onClick={() => setEditing(false)}
                      className="px-6 py-3 bg-slate-700 hover:bg-slate-600 rounded-lg text-white transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </form>
            ) : (
              <>
                <div className="bg-slate-800 rounded-xl p-6 mb-6">
                  <h3 className="text-2xl font-bold text-white mb-4">About</h3>
                  {profile.user.bio ? (
                    <p className="text-slate-300 leading-relaxed">{profile.user.bio}</p>
                  ) : (
                    <p className="text-slate-500 italic">No bio added yet</p>
                  )}
                </div>

                {profile.profile && (
                  <div className="bg-slate-800 rounded-xl p-6 mb-6">
                    <h3 className="text-2xl font-bold text-white mb-4">Statistics</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="bg-slate-700 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-cyan-400">
                          {profile.profile.total_scans}
                        </div>
                        <div className="text-sm text-slate-400">Total Scans</div>
                      </div>
                      <div className="bg-slate-700 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-green-400">
                          {profile.profile.successful_reports}
                        </div>
                        <div className="text-sm text-slate-400">Successful Reports</div>
                      </div>
                      <div className="bg-slate-700 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-yellow-400">
                          {profile.profile.acceptance_rate.toFixed(1)}%
                        </div>
                        <div className="text-sm text-slate-400">Acceptance Rate</div>
                      </div>
                      <div className="bg-slate-700 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-gray-400">
                          {profile.profile.experience_years}
                        </div>
                        <div className="text-sm text-slate-400">Years Experience</div>
                      </div>
                    </div>
                  </div>
                )}

                {profile.user.specializations && (
                  <div className="bg-slate-800 rounded-xl p-6 mb-6">
                    <h3 className="text-2xl font-bold text-white mb-4">Specializations</h3>
                    <div className="flex flex-wrap gap-2">
                      {profile.user.specializations.split(',').map((spec, index) => (
                        <span
                          key={index}
                          className="px-4 py-2 bg-cyan-600/20 text-cyan-400 rounded-lg text-sm"
                        >
                          {spec.trim()}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {profile.user.skills && (
                  <div className="bg-slate-800 rounded-xl p-6">
                    <h3 className="text-2xl font-bold text-white mb-4">Skills</h3>
                    <div className="flex flex-wrap gap-2">
                      {profile.user.skills.split(',').map((skill, index) => (
                        <span
                          key={index}
                          className="px-4 py-2 bg-slate-700 text-slate-300 rounded-lg text-sm"
                        >
                          {skill.trim()}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
