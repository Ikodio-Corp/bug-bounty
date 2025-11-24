"use client";

import { Sidebar } from '@/components/dashboard/Sidebar';
import { AtmosphericBackground } from '@/components/dashboard/AtmosphericBackground';
import { Code, Key, Book } from 'lucide-react';

export default function APIDocsPage() {
  const endpoints = [
    { method: 'GET', path: '/api/scans', desc: 'List all scans' },
    { method: 'POST', path: '/api/scans', desc: 'Create new scan' },
    { method: 'GET', path: '/api/bugs', desc: 'List bugs' },
    { method: 'GET', path: '/api/profile', desc: 'Get profile' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      <AtmosphericBackground />
      <Sidebar />
      
      <div className="lg:ml-64 min-h-screen">
        <div className="relative z-10 p-10">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">API Documentation</h1>
            <p className="text-slate-400">Complete reference for Ikodio API integration</p>
          </div>

          {/* API Key */}
          <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 backdrop-blur-xl border border-white/10 rounded-2xl p-6 mb-8">
            <div className="flex items-center gap-3 mb-3">
              <Key className="text-yellow-400" size={24} />
              <h2 className="text-xl font-bold text-white">Your API Key</h2>
            </div>
            <code className="block p-3 bg-black/30 rounded-lg text-green-400 font-mono text-sm">sk_live_xxxxxxxxxxxxxxxxxxxx</code>
          </div>

          {/* Base URL */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 mb-8">
            <h3 className="text-white font-semibold mb-2">Base URL</h3>
            <code className="block p-3 bg-black/30 rounded-lg text-blue-400 font-mono">https://api.ikodio.com/v1</code>
          </div>

          {/* Endpoints */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 mb-8">
            <div className="flex items-center gap-3 mb-4">
              <Book className="text-blue-400" size={24} />
              <h2 className="text-xl font-bold text-white">Endpoints</h2>
            </div>
            <div className="space-y-3">
              {endpoints.map((ep, idx) => (
                <div key={idx} className="p-4 bg-white/5 rounded-lg">
                  <div className="flex items-center gap-4 mb-2">
                    <span className={`px-3 py-1 rounded text-xs font-bold ${ep.method === 'GET' ? 'bg-green-600/20 text-green-400' : 'bg-blue-600/20 text-blue-400'}`}>{ep.method}</span>
                    <code className="text-slate-300 font-mono text-sm">{ep.path}</code>
                  </div>
                  <p className="text-slate-400 text-sm">{ep.desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Example */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <Code className="text-purple-400" size={24} />
              <h2 className="text-xl font-bold text-white">Example Request</h2>
            </div>
            <pre className="p-4 bg-black/50 rounded-lg text-green-400 font-mono text-sm overflow-x-auto">
{`curl -X GET https://api.ikodio.com/v1/scans \\
  -H "Authorization: Bearer YOUR_API_KEY"`}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
}
