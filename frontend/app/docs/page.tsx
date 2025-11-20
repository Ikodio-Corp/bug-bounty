'use client'

import { useState } from 'react'
import Link from 'next/link'

interface DocSection {
  id: string
  title: string
  content: string[]
}

export default function DocsPage() {
  const [activeSection, setActiveSection] = useState('getting-started')

  const sections: DocSection[] = [
    {
      id: 'getting-started',
      title: 'Getting Started',
      content: [
        'Welcome to IKODIO BugBounty documentation. This guide will help you get started with the platform.',
        'IKODIO is an AI-powered vulnerability detection and bug bounty platform that combines automated security scanning with a comprehensive marketplace for bug bounties.',
        'Key Features:',
        '- AI-powered vulnerability detection',
        '- Multiple scanner integrations',
        '- Real-time notifications',
        '- Bug marketplace',
        '- Guild collaboration system',
        '- NFT tokenization'
      ]
    },
    {
      id: 'authentication',
      title: 'Authentication',
      content: [
        'IKODIO supports multiple authentication methods:',
        '1. Email and Password - Traditional authentication',
        '2. OAuth2 - Login with Google, GitHub, or GitLab',
        '3. Two-Factor Authentication - Enhanced security with TOTP',
        '4. SAML 2.0 - Enterprise SSO integration',
        'To enable 2FA, go to Settings > Security and scan the QR code with your authenticator app.'
      ]
    },
    {
      id: 'scanning',
      title: 'Security Scanning',
      content: [
        'IKODIO provides multiple scanning options:',
        'Quick Scan - Fast vulnerability detection (5-10 minutes)',
        'Full Scan - Comprehensive security analysis (30-60 minutes)',
        'Custom Scan - Configure specific tests',
        'Supported Scanners:',
        '- Nuclei - Template-based vulnerability scanner',
        '- OWASP ZAP - Dynamic application security testing',
        '- Burp Suite - Professional security scanner',
        'To start a scan, navigate to Scans > New Scan and enter your target URL.'
      ]
    },
    {
      id: 'bug-submission',
      title: 'Bug Submission',
      content: [
        'When submitting a bug report, include:',
        '1. Clear Title - Descriptive summary of the vulnerability',
        '2. Detailed Description - Full explanation of the issue',
        '3. Steps to Reproduce - Clear instructions to replicate',
        '4. Proof of Concept - Code or screenshots demonstrating the vulnerability',
        '5. Impact Assessment - Potential consequences',
        '6. Remediation Suggestions - How to fix the issue',
        'Severity Levels:',
        '- Critical - Complete system compromise',
        '- High - Significant security impact',
        '- Medium - Moderate security issue',
        '- Low - Minor security concern',
        '- Info - General security information'
      ]
    },
    {
      id: 'marketplace',
      title: 'Bug Marketplace',
      content: [
        'The IKODIO marketplace allows you to:',
        '- List bugs for sale',
        '- Purchase validated vulnerabilities',
        '- Set custom pricing',
        '- Make private offers',
        '- Track transaction history',
        'Marketplace Rules:',
        '1. Only validated bugs can be listed',
        '2. Private information must be disclosed after purchase',
        '3. All transactions are recorded on blockchain',
        '4. Platform takes 10% commission'
      ]
    },
    {
      id: 'guilds',
      title: 'Guild System',
      content: [
        'Guilds allow security researchers to collaborate:',
        'Create a Guild - Build your security research team',
        'Join Existing Guilds - Apply to established groups',
        'Guild Chat - Real-time communication',
        'Shared Discoveries - Collaborate on bug reports',
        'Guild Benefits:',
        '- Pooled resources',
        '- Knowledge sharing',
        '- Reputation boost',
        '- Exclusive programs'
      ]
    },
    {
      id: 'api-reference',
      title: 'API Reference',
      content: [
        'IKODIO provides a comprehensive REST API:',
        'Base URL: https://api.ikodio.com',
        'Authentication: Bearer token in Authorization header',
        'Common Endpoints:',
        'POST /api/auth/login - User authentication',
        'GET /api/scans - List scans',
        'POST /api/scans - Create new scan',
        'GET /api/bugs - List bug reports',
        'POST /api/bugs - Submit bug report',
        'For complete API documentation, visit: https://docs.ikodio.com/api'
      ]
    },
    {
      id: 'integrations',
      title: 'Integrations',
      content: [
        'IKODIO integrates with popular tools:',
        'Issue Tracking:',
        '- Jira - Sync bugs to Jira issues',
        '- Linear - Create Linear tasks',
        '- Asana - Track in Asana',
        'Bug Bounty Platforms:',
        '- HackerOne - Submit to HackerOne programs',
        '- Bugcrowd - Report to Bugcrowd',
        'Cloud Providers:',
        '- AWS Security Hub - Export findings',
        '- Azure Sentinel - Send alerts',
        '- GCP Security Command Center - Sync vulnerabilities',
        'To configure integrations, go to Settings > Integrations.'
      ]
    },
    {
      id: 'webhooks',
      title: 'Webhooks',
      content: [
        'Configure webhooks to receive real-time notifications:',
        'Supported Events:',
        '- scan.completed - Scan finished',
        '- bug.validated - Bug approved',
        '- bug.rejected - Bug rejected',
        '- payment.received - Bounty paid',
        'Webhook Payload Format:',
        '{ "event": "scan.completed", "data": {...}, "timestamp": "..." }',
        'Configure webhooks in Settings > Webhooks.'
      ]
    },
    {
      id: 'pricing',
      title: 'Pricing',
      content: [
        'IKODIO offers flexible pricing plans:',
        'Free Tier:',
        '- 5 scans per month',
        '- Basic vulnerability detection',
        '- Community support',
        'Professional ($49/month):',
        '- 50 scans per month',
        '- Advanced scanners',
        '- Priority support',
        '- API access',
        'Enterprise ($199/month):',
        '- Unlimited scans',
        '- Custom integrations',
        '- Dedicated support',
        '- SLA guarantees',
        '- White-label options'
      ]
    }
  ]

  const activeContent = sections.find(s => s.id === activeSection)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <Link href="/dashboard">
            <button className="text-slate-400 hover:text-white mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Dashboard
            </button>
          </Link>
          <h1 className="text-4xl font-bold text-white mb-2">Documentation</h1>
          <p className="text-slate-400">Comprehensive guide to using IKODIO BugBounty</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <aside className="lg:col-span-1">
            <div className="bg-slate-800 rounded-xl p-6 sticky top-8">
              <h2 className="text-lg font-semibold text-white mb-4">Table of Contents</h2>
              <nav className="space-y-2">
                {sections.map(section => (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                      activeSection === section.id
                        ? 'bg-cyan-600 text-white'
                        : 'text-slate-400 hover:text-white hover:bg-slate-700'
                    }`}
                  >
                    {section.title}
                  </button>
                ))}
              </nav>
            </div>
          </aside>

          <main className="lg:col-span-3">
            <div className="bg-slate-800 rounded-xl p-8">
              {activeContent && (
                <>
                  <h2 className="text-3xl font-bold text-white mb-6">{activeContent.title}</h2>
                  <div className="prose prose-invert max-w-none">
                    {activeContent.content.map((paragraph, index) => (
                      <p key={index} className="text-slate-300 mb-4 leading-relaxed">
                        {paragraph}
                      </p>
                    ))}
                  </div>
                </>
              )}

              <div className="mt-8 pt-8 border-t border-slate-700">
                <h3 className="text-xl font-semibold text-white mb-4">Need More Help?</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-slate-700 rounded-lg p-4">
                    <h4 className="text-white font-semibold mb-2">Contact Support</h4>
                    <p className="text-slate-400 text-sm mb-3">
                      Get help from our support team
                    </p>
                    <a
                      href="mailto:support@ikodio.com"
                      className="text-cyan-400 hover:text-cyan-300 text-sm"
                    >
                      support@ikodio.com
                    </a>
                  </div>
                  <div className="bg-slate-700 rounded-lg p-4">
                    <h4 className="text-white font-semibold mb-2">Community Forum</h4>
                    <p className="text-slate-400 text-sm mb-3">
                      Join our community discussions
                    </p>
                    <a
                      href="https://community.ikodio.com"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-cyan-400 hover:text-cyan-300 text-sm"
                    >
                      Visit Forum
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
