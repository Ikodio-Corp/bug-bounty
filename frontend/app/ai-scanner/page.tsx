"use client";

import { Sidebar } from '@/components/dashboard/Sidebar';
import { AtmosphericBackground } from '@/components/dashboard/AtmosphericBackground';

export default function AIScannerPage() {
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
          
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
            <p className="text-white/60">AI Scanner coming soon. Automated vulnerability detection with machine learning.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
