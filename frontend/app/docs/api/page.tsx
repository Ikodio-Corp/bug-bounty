"use client";

import { Sidebar } from '@/components/dashboard/Sidebar';
import { AtmosphericBackground } from '@/components/dashboard/AtmosphericBackground';
import { Code2, Lock, Webhook, Database } from 'lucide-react';

export default function DocsAPIPage() {
  const sections = [
    { title: 'Authentication', desc: 'JWT tokens, OAuth2, API keys', icon: Lock, color: 'blue' },
    { title: 'REST API', desc: 'RESTful endpoints and requests', icon: Code2, color: 'purple' },
    { title: 'Webhooks', desc: 'Real-time event notifications', icon: Webhook, color: 'green' },
    { title: 'Database', desc: 'Data models and schemas', icon: Database, color: 'yellow' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      <AtmosphericBackground />
      <Sidebar />
      
      <div className="lg:ml-64 min-h-screen">
        <div className="relative z-10 p-10">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">API Documentation</h1>
            <p className="text-slate-400">Complete API reference and integration guides</p>
          </div>

          {/* Quick Links */}
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            {sections.map((section) => (
              <button key={section.title} className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:border-white/50 transition text-left">
                <section.icon className={`text-${section.color}-400 mb-3`} size={28} />
                <div className="text-white font-bold mb-1">{section.title}</div>
                <div className="text-slate-400 text-sm">{section.desc}</div>
              </button>
            ))}
          </div>

          {/* Example Endpoints */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 mb-6">
            <h2 className="text-xl font-bold text-white mb-4">Common Endpoints</h2>
            <div className="space-y-3">
              {[
                { method: 'POST', path: '/api/auth/login', desc: 'Authenticate user' },
                { method: 'GET', path: '/api/scans', desc: 'List all scans' },
                { method: 'POST', path: '/api/scans', desc: 'Create new scan' },
                { method: 'GET', path: '/api/bugs', desc: 'Get bug reports' },
                { method: 'GET', path: '/api/profile', desc: 'Get user profile' },
              ].map((endpoint, i) => (
                <div key={i} className="flex items-center gap-4 p-4 bg-white/5 rounded-lg">
                  <span className={`px-3 py-1 rounded font-mono text-sm ${
                    endpoint.method === 'GET' ? 'bg-green-600/20 text-green-400' : 'bg-white/20 text-gray-400'
                  }`}>{endpoint.method}</span>
                  <code className="text-gray-400 font-mono">{endpoint.path}</code>
                  <span className="text-slate-400 ml-auto">{endpoint.desc}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Code Example */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <h2 className="text-xl font-bold text-white mb-4">Example Request</h2>
            <pre className="bg-slate-900 rounded-lg p-4 overflow-x-auto">
              <code className="text-green-400 text-sm">
{`curl -X GET https://api.ikodio.com/v1/scans \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json"`}
              </code>
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
