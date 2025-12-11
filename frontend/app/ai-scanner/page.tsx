"use client";

import { useState } from 'react';
import { Sidebar } from '@/components/dashboard/Sidebar';
import { AtmosphericBackground } from '@/components/dashboard/AtmosphericBackground';
import { Zap, Target, Brain, Play } from 'lucide-react';

export default function AIScannerPage() {
  const [target, setTarget] = useState('');
  const [scanType, setScanType] = useState('quick');
  const [isScanning, setIsScanning] = useState(false);

  const handleScan = () => {
    setIsScanning(true);
    setTimeout(() => setIsScanning(false), 3000);
  };

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      <AtmosphericBackground />
      <Sidebar />
      
      <div className="lg:ml-64 min-h-screen">
        <div className="relative z-10 p-10">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">AI Scanner</h1>
            <p className="text-slate-400">Advanced AI-powered vulnerability scanning</p>
          </div>

          {/* Scan Configuration */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 mb-8">
            <div className="flex items-center gap-3 mb-6">
              <Brain className="text-gray-400" size={28} />
              <h2 className="text-xl font-bold text-white">Configure Scan</h2>
            </div>

            <div className="space-y-6">
              <div>
                <label className="block text-slate-300 mb-2">Target URL</label>
                <input
                  type="text"
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                  placeholder="https://example.com"
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-white/50"
                />
              </div>

              <div>
                <label className="block text-slate-300 mb-2">Scan Type</label>
                <div className="grid grid-cols-3 gap-4">
                  {[
                    { id: 'quick', label: 'Quick Scan', desc: '5-10 mins', icon: Zap },
                    { id: 'deep', label: 'Deep Scan', desc: '30-60 mins', icon: Target },
                    { id: 'full', label: 'Full Audit', desc: '2-4 hours', icon: Brain },
                  ].map((type) => (
                    <button
                      key={type.id}
                      onClick={() => setScanType(type.id)}
                      className={`p-4 rounded-lg border transition ${
                        scanType === type.id
                          ? 'bg-gray-700/20 border-white'
                          : 'bg-white/5 border-white/10 hover:border-white/20'
                      }`}
                    >
                      <type.icon className={scanType === type.id ? 'text-gray-400' : 'text-slate-400'} size={24} />
                      <div className="text-white font-medium mt-2">{type.label}</div>
                      <div className="text-slate-400 text-sm">{type.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              <button
                onClick={handleScan}
                disabled={!target || isScanning}
                className="w-full py-3 bg-gradient-to-r from-gray-500 to-gray-600 rounded-lg text-white font-medium flex items-center justify-center gap-2 hover:opacity-90 transition disabled:opacity-50"
              >
                <Play size={20} />
                {isScanning ? 'Scanning...' : 'Start Scan'}
              </button>
            </div>
          </div>

          {/* Recent Scans */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <h2 className="text-xl font-bold text-white mb-4">Recent AI Scans</h2>
            <div className="space-y-3">
              {[
                { url: 'example.com', type: 'Deep', findings: 12, status: 'Completed' },
                { url: 'test.io', type: 'Quick', findings: 3, status: 'Completed' },
                { url: 'demo.app', type: 'Full', findings: 8, status: 'In Progress' },
              ].map((scan, i) => (
                <div key={i} className="p-4 bg-white/5 rounded-lg flex items-center justify-between">
                  <div>
                    <div className="text-white font-medium">{scan.url}</div>
                    <div className="text-slate-400 text-sm">{scan.type} Scan • {scan.findings} findings</div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm ${scan.status === 'Completed' ? 'bg-green-600/20 text-green-400' : 'bg-white/20 text-gray-400'}`}>
                    {scan.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
