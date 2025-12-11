"use client";

import { Sidebar } from '@/components/dashboard/Sidebar';
import { AtmosphericBackground } from '@/components/dashboard/AtmosphericBackground';
import { Check } from 'lucide-react';

export default function IntegrationsPage() {
  const integrations = [
    { name: 'Slack', desc: 'Get instant notifications', status: 'connected', icon: '' },
    { name: 'GitHub', desc: 'Auto-create issues from bugs', status: 'connected', icon: '' },
    { name: 'Jira', desc: 'Sync bugs with Jira tickets', status: 'available', icon: '' },
    { name: 'Discord', desc: 'Team notifications', status: 'available', icon: '' },
    { name: 'Telegram', desc: 'Mobile alerts', status: 'available', icon: 'TG' },
    { name: 'Burp Suite', desc: 'Import scan results', status: 'connected', icon: '' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      <AtmosphericBackground />
      <Sidebar />
      
      <div className="lg:ml-64 min-h-screen">
        <div className="relative z-10 p-10">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Integrations</h1>
            <p className="text-slate-400">Connect Ikodio with your favorite tools</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {integrations.map((int) => (
              <div key={int.name} className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-4xl">{int.icon}</span>
                  {int.status === 'connected' && <span className="flex items-center gap-1 px-3 py-1 bg-green-600/20 text-green-400 rounded-full text-sm"><Check size={14} />Connected</span>}
                </div>
                <h3 className="text-xl font-bold text-white mb-2">{int.name}</h3>
                <p className="text-slate-400 mb-4">{int.desc}</p>
                <button className={`w-full py-2 rounded-lg transition ${int.status === 'connected' ? 'bg-white/10 hover:bg-white/20 text-white' : 'bg-white hover:bg-gray-200 text-white'}`}>
                  {int.status === 'connected' ? 'Configure' : 'Connect'}
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
