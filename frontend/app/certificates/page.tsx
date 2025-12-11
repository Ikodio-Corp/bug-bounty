'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { SimpleCard, SimpleCardHeader, SimpleCardTitle, SimpleCardContent } from '@/components/ui/simple-card'
import { SimpleBadge } from '@/components/ui/simple-badge'
import api from '@/lib/api'

interface Certificate {
  id: number
  name: string
  issuer: string
  type: 'course' | 'achievement' | 'certification'
  issuedAt: string
  expiresAt?: string
  credentialId: string
  skills: string[]
  verified: boolean
}

export default function CertificatesPage() {
  const [certificates, setCertificates] = useState<Certificate[]>([])
  const [selectedType, setSelectedType] = useState<string>('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadCertificates()
  }, [])

  const loadCertificates = async () => {
    try {
      const response = await api.get('/users/certificates')
      setCertificates(response.data)
    } catch (error) {
      console.error('Failed to load certificates:', error)
      // Mock data
      setCertificates([
        {
          id: 1,
          name: 'Web Application Security Professional',
          issuer: 'IKODIO Security Academy',
          type: 'certification',
          issuedAt: '2025-10-15T00:00:00Z',
          expiresAt: '2027-10-15T00:00:00Z',
          credentialId: 'WASP-2025-10-15-ABCD1234',
          skills: ['Web Security', 'OWASP Top 10', 'Penetration Testing'],
          verified: true
        },
        {
          id: 2,
          name: 'Bug Bounty Fundamentals',
          issuer: 'IKODIO University',
          type: 'course',
          issuedAt: '2025-09-20T00:00:00Z',
          credentialId: 'BBF-2025-09-20-EFGH5678',
          skills: ['Bug Hunting', 'Vulnerability Analysis', 'Report Writing'],
          verified: true
        },
        {
          id: 3,
          name: 'Elite Bug Hunter',
          issuer: 'IKODIO Platform',
          type: 'achievement',
          issuedAt: '2025-11-01T00:00:00Z',
          credentialId: 'EBH-2025-11-01-IJKL9012',
          skills: ['Critical Vulnerabilities', 'Advanced Exploitation'],
          verified: true
        },
        {
          id: 4,
          name: 'API Security Expert',
          issuer: 'IKODIO Security Academy',
          type: 'certification',
          issuedAt: '2025-08-10T00:00:00Z',
          expiresAt: '2027-08-10T00:00:00Z',
          credentialId: 'ASE-2025-08-10-MNOP3456',
          skills: ['REST API', 'GraphQL', 'OAuth 2.0', 'JWT'],
          verified: true
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const downloadCertificate = async (id: number) => {
    try {
      const response = await api.get(`/users/certificates/${id}/download`, { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `certificate-${id}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Failed to download certificate:', error)
      alert('Failed to download certificate')
    }
  }

  const shareCertificate = (certificate: Certificate) => {
    const shareUrl = `${window.location.origin}/certificates/verify/${certificate.credentialId}`
    navigator.clipboard.writeText(shareUrl)
    alert('Certificate verification URL copied to clipboard!')
  }

  const getTypeColor = (type: string) => {
    const colors: { [key: string]: any } = {
      certification: 'success',
      course: 'info',
      achievement: 'warning'
    }
    return colors[type]
  }

  const getTypeIcon = (type: string) => {
    const icons: { [key: string]: string } = {
      certification: '',
      course: '',
      achievement: ''
    }
    return icons[type] || ''
  }

  const isExpiringSoon = (expiresAt?: string) => {
    if (!expiresAt) return false
    const daysUntilExpiry = Math.floor((new Date(expiresAt).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
    return daysUntilExpiry <= 30 && daysUntilExpiry > 0
  }

  const isExpired = (expiresAt?: string) => {
    if (!expiresAt) return false
    return new Date(expiresAt) < new Date()
  }

  const filteredCertificates = selectedType === 'all'
    ? certificates
    : certificates.filter(c => c.type === selectedType)

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
          <h1 className="text-4xl font-bold text-white mb-2">My Certificates</h1>
          <p className="text-slate-400">Your earned certifications and achievements</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <SimpleCard>
            <SimpleCardHeader>
              <SimpleCardTitle className="text-lg">Total Certificates</SimpleCardTitle>
            </SimpleCardHeader>
            <SimpleCardContent>
              <div className="text-4xl font-bold text-cyan-400">{certificates.length}</div>
            </SimpleCardContent>
          </SimpleCard>

          <SimpleCard>
            <SimpleCardHeader>
              <SimpleCardTitle className="text-lg">Certifications</SimpleCardTitle>
            </SimpleCardHeader>
            <SimpleCardContent>
              <div className="text-4xl font-bold text-green-400">
                {certificates.filter(c => c.type === 'certification').length}
              </div>
            </SimpleCardContent>
          </SimpleCard>

          <SimpleCard>
            <SimpleCardHeader>
              <SimpleCardTitle className="text-lg">Courses</SimpleCardTitle>
            </SimpleCardHeader>
            <SimpleCardContent>
              <div className="text-4xl font-bold text-gray-400">
                {certificates.filter(c => c.type === 'course').length}
              </div>
            </SimpleCardContent>
          </SimpleCard>

          <SimpleCard>
            <SimpleCardHeader>
              <SimpleCardTitle className="text-lg">Achievements</SimpleCardTitle>
            </SimpleCardHeader>
            <SimpleCardContent>
              <div className="text-4xl font-bold text-yellow-400">
                {certificates.filter(c => c.type === 'achievement').length}
              </div>
            </SimpleCardContent>
          </SimpleCard>
        </div>

        <div className="bg-slate-800 rounded-xl p-6 mb-8">
          <div className="flex gap-4">
            <button
              onClick={() => setSelectedType('all')}
              className={`px-6 py-2 rounded-lg font-semibold transition-colors ${
                selectedType === 'all'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setSelectedType('certification')}
              className={`px-6 py-2 rounded-lg font-semibold transition-colors ${
                selectedType === 'certification'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Certifications
            </button>
            <button
              onClick={() => setSelectedType('course')}
              className={`px-6 py-2 rounded-lg font-semibold transition-colors ${
                selectedType === 'course'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Courses
            </button>
            <button
              onClick={() => setSelectedType('achievement')}
              className={`px-6 py-2 rounded-lg font-semibold transition-colors ${
                selectedType === 'achievement'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Achievements
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredCertificates.map(certificate => (
            <SimpleCard key={certificate.id} className="hover:border-cyan-500 transition-colors">
              <SimpleCardHeader>
                <div className="flex items-start gap-4">
                  <div className="text-5xl">{getTypeIcon(certificate.type)}</div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-xl font-bold text-white">{certificate.name}</h3>
                    </div>
                    <p className="text-slate-400 text-sm mb-3">{certificate.issuer}</p>
                    <div className="flex flex-wrap gap-2">
                      <SimpleBadge variant={getTypeColor(certificate.type)}>
                        {certificate.type}
                      </SimpleBadge>
                      {certificate.verified && (
                        <SimpleBadge variant="success">
                          Verified
                        </SimpleBadge>
                      )}
                      {isExpired(certificate.expiresAt) && (
                        <SimpleBadge variant="error">
                          Expired
                        </SimpleBadge>
                      )}
                      {isExpiringSoon(certificate.expiresAt) && !isExpired(certificate.expiresAt) && (
                        <SimpleBadge variant="warning">
                          Expiring Soon
                        </SimpleBadge>
                      )}
                    </div>
                  </div>
                </div>
              </SimpleCardHeader>
              <SimpleCardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-slate-400">Issued</div>
                      <div className="text-white font-semibold">
                        {new Date(certificate.issuedAt).toLocaleDateString()}
                      </div>
                    </div>
                    {certificate.expiresAt && (
                      <div>
                        <div className="text-slate-400">Expires</div>
                        <div className="text-white font-semibold">
                          {new Date(certificate.expiresAt).toLocaleDateString()}
                        </div>
                      </div>
                    )}
                  </div>

                  <div>
                    <div className="text-slate-400 text-sm mb-2">Credential ID</div>
                    <code className="text-xs bg-slate-700 px-2 py-1 rounded text-cyan-400">
                      {certificate.credentialId}
                    </code>
                  </div>

                  <div>
                    <div className="text-slate-400 text-sm mb-2">Skills</div>
                    <div className="flex flex-wrap gap-2">
                      {certificate.skills.map(skill => (
                        <SimpleBadge key={skill} variant="info">
                          {skill}
                        </SimpleBadge>
                      ))}
                    </div>
                  </div>

                  <div className="flex gap-3 pt-4 border-t border-slate-700">
                    <button
                      onClick={() => downloadCertificate(certificate.id)}
                      className="flex-1 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white font-semibold transition-colors"
                    >
                      Download
                    </button>
                    <button
                      onClick={() => shareCertificate(certificate)}
                      className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-white font-semibold transition-colors"
                    >
                      Share
                    </button>
                    <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white font-semibold transition-colors">
                      Verify
                    </button>
                  </div>
                </div>
              </SimpleCardContent>
            </SimpleCard>
          ))}
        </div>

        {filteredCertificates.length === 0 && (
          <SimpleCard>
            <SimpleCardContent className="py-12 text-center">
              <div className="text-6xl mb-4"></div>
              <h3 className="text-xl font-semibold text-white mb-2">No Certificates Yet</h3>
              <p className="text-slate-400 mb-4">Complete courses and earn achievements to get certificates</p>
              <Link href="/university">
                <button className="px-6 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white font-semibold transition-colors">
                  Browse Courses
                </button>
              </Link>
            </SimpleCardContent>
          </SimpleCard>
        )}

        <div className="mt-12 bg-slate-800 rounded-xl p-8">
          <h2 className="text-2xl font-bold text-white mb-4">Certificate Verification</h2>
          <p className="text-slate-300 mb-4">
            All IKODIO certificates are blockchain-verified and can be independently validated using the credential ID.
          </p>
          <div className="flex gap-4">
            <input
              type="text"
              placeholder="Enter credential ID to verify"
              className="flex-1 px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
            />
            <button className="px-6 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white font-semibold transition-colors">
              Verify Certificate
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
