'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { SimpleCard, SimpleCardHeader, SimpleCardTitle, SimpleCardContent } from '@/components/ui/simple-card'
import { SimpleBadge } from '@/components/ui/simple-badge'
import api from '@/lib/api'

interface Tool {
  id: number
  name: string
  category: string
  description: string
  version: string
  language: string
  stars: number
  downloads: number
  author: string
  license: string
  githubUrl: string
  documentationUrl?: string
  price: number
}

export default function ToolsPage() {
  const [tools, setTools] = useState<Tool[]>([])
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTools()
  }, [])

  const loadTools = async () => {
    try {
      const response = await api.get('/marketplace/tools')
      setTools(response.data)
    } catch (error) {
      console.error('Failed to load tools:', error)
      // Mock data
      setTools([
        {
          id: 1,
          name: 'IKODIO Scanner CLI',
          category: 'Scanner',
          description: 'Command-line interface for IKODIO automated security scanning',
          version: '2.1.0',
          language: 'Python',
          stars: 1250,
          downloads: 15600,
          author: 'IKODIO Team',
          license: 'MIT',
          githubUrl: 'https://github.com/ikodio/scanner-cli',
          documentationUrl: 'https://docs.ikodio.com/scanner-cli',
          price: 0
        },
        {
          id: 2,
          name: 'BurpSuite Integration',
          category: 'Integration',
          description: 'Seamless integration with Burp Suite for enhanced vulnerability detection',
          version: '1.5.2',
          language: 'Java',
          stars: 890,
          downloads: 7800,
          author: 'Community',
          license: 'Apache 2.0',
          githubUrl: 'https://github.com/ikodio/burp-integration',
          price: 0
        },
        {
          id: 3,
          name: 'XSS Hunter Pro',
          category: 'Exploitation',
          description: 'Advanced XSS detection and exploitation toolkit with payload library',
          version: '3.0.1',
          language: 'JavaScript',
          stars: 2100,
          downloads: 23400,
          author: 'security_researcher',
          license: 'GPL-3.0',
          githubUrl: 'https://github.com/security/xss-hunter-pro',
          documentationUrl: 'https://xsshunter.pro/docs',
          price: 49.99
        },
        {
          id: 4,
          name: 'SQLMap Extended',
          category: 'Exploitation',
          description: 'Enhanced SQLMap with custom payloads and detection techniques',
          version: '1.8.4',
          language: 'Python',
          stars: 3500,
          downloads: 45000,
          author: 'sql_ninja',
          license: 'GPL-2.0',
          githubUrl: 'https://github.com/sqlninja/sqlmap-extended',
          price: 0
        },
        {
          id: 5,
          name: 'ReportGen AI',
          category: 'Reporting',
          description: 'AI-powered bug report generator with professional templates',
          version: '2.3.0',
          language: 'Python',
          stars: 780,
          downloads: 5600,
          author: 'IKODIO Labs',
          license: 'Commercial',
          githubUrl: 'https://github.com/ikodio/reportgen-ai',
          documentationUrl: 'https://docs.ikodio.com/reportgen',
          price: 29.99
        },
        {
          id: 6,
          name: 'API Fuzzer',
          category: 'Testing',
          description: 'Intelligent API fuzzing tool for REST and GraphQL endpoints',
          version: '1.2.5',
          language: 'Go',
          stars: 1450,
          downloads: 12300,
          author: 'api_security',
          license: 'MIT',
          githubUrl: 'https://github.com/apisec/api-fuzzer',
          price: 0
        },
        {
          id: 7,
          name: 'Subdomain Hunter',
          category: 'Reconnaissance',
          description: 'Fast subdomain enumeration with multiple data sources',
          version: '4.1.0',
          language: 'Go',
          stars: 5200,
          downloads: 67000,
          author: 'recon_master',
          license: 'MIT',
          githubUrl: 'https://github.com/recon/subdomain-hunter',
          price: 0
        },
        {
          id: 8,
          name: 'Vulnerability Scanner Pro',
          category: 'Scanner',
          description: 'Enterprise-grade vulnerability scanner with custom rule engine',
          version: '5.0.2',
          language: 'Python',
          stars: 4100,
          downloads: 38900,
          author: 'IKODIO Enterprise',
          license: 'Commercial',
          githubUrl: 'https://github.com/ikodio/vuln-scanner-pro',
          documentationUrl: 'https://docs.ikodio.com/scanner-pro',
          price: 199.99
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const categories = ['all', ...Array.from(new Set(tools.map(t => t.category)))]

  const filteredTools = tools.filter(tool => {
    const categoryMatch = selectedCategory === 'all' || tool.category === selectedCategory
    const searchMatch = tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                       tool.description.toLowerCase().includes(searchQuery.toLowerCase())
    return categoryMatch && searchMatch
  })

  const installTool = async (toolId: number) => {
    try {
      await api.post(`/marketplace/tools/${toolId}/install`)
      alert('Tool installation started')
    } catch (error) {
      console.error('Failed to install tool:', error)
      alert('Failed to install tool')
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
          <h1 className="text-4xl font-bold text-white mb-2">Security Tools</h1>
          <p className="text-slate-400">Discover and use powerful security testing tools</p>
        </div>

        <div className="mb-8">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search tools..."
            className="w-full px-6 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="bg-slate-800 rounded-xl p-6 mb-8">
          <div className="flex flex-wrap gap-3">
            {categories.map(category => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-6 py-2 rounded-lg font-semibold transition-colors capitalize ${
                  selectedCategory === category
                    ? 'bg-cyan-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredTools.map(tool => (
            <SimpleCard key={tool.id} className="hover:border-cyan-500 transition-colors">
              <SimpleCardHeader>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-bold text-white">{tool.name}</h3>
                      {tool.price === 0 ? (
                        <SimpleBadge variant="success">Free</SimpleBadge>
                      ) : (
                        <SimpleBadge variant="warning">${tool.price}</SimpleBadge>
                      )}
                    </div>
                    <p className="text-slate-400 text-sm mb-3">{tool.description}</p>
                    <div className="flex flex-wrap gap-2">
                      <SimpleBadge variant="info">{tool.category}</SimpleBadge>
                      <SimpleBadge variant="default">{tool.language}</SimpleBadge>
                      <SimpleBadge variant="default">v{tool.version}</SimpleBadge>
                    </div>
                  </div>
                </div>
              </SimpleCardHeader>
              <SimpleCardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <div className="text-slate-400">Stars</div>
                      <div className="text-yellow-400 font-semibold">⭐ {tool.stars.toLocaleString()}</div>
                    </div>
                    <div>
                      <div className="text-slate-400">Downloads</div>
                      <div className="text-green-400 font-semibold">↓ {tool.downloads.toLocaleString()}</div>
                    </div>
                    <div>
                      <div className="text-slate-400">License</div>
                      <div className="text-white font-semibold">{tool.license}</div>
                    </div>
                  </div>

                  <div className="text-sm">
                    <div className="text-slate-400">Author</div>
                    <div className="text-white font-semibold">{tool.author}</div>
                  </div>

                  <div className="flex gap-3 pt-4 border-t border-slate-700">
                    <button
                      onClick={() => installTool(tool.id)}
                      className="flex-1 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white font-semibold transition-colors"
                    >
                      {tool.price === 0 ? 'Install' : 'Purchase'}
                    </button>
                    <a
                      href={tool.githubUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white font-semibold transition-colors"
                    >
                      GitHub
                    </a>
                    {tool.documentationUrl && (
                      <a
                        href={tool.documentationUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-semibold transition-colors"
                      >
                        Docs
                      </a>
                    )}
                  </div>
                </div>
              </SimpleCardContent>
            </SimpleCard>
          ))}
        </div>

        {filteredTools.length === 0 && (
          <SimpleCard>
            <SimpleCardContent className="py-12 text-center">
              <div className="text-6xl mb-4">🔧</div>
              <h3 className="text-xl font-semibold text-white mb-2">No Tools Found</h3>
              <p className="text-slate-400">Try adjusting your search or filters</p>
            </SimpleCardContent>
          </SimpleCard>
        )}

        <div className="mt-12 bg-slate-800 rounded-xl p-8">
          <h2 className="text-2xl font-bold text-white mb-4">Submit Your Tool</h2>
          <p className="text-slate-300 mb-6">
            Have you developed a security tool? Share it with the IKODIO community and earn rewards!
          </p>
          <button className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white font-semibold transition-colors">
            Submit Tool
          </button>
        </div>
      </div>
    </div>
  )
}
