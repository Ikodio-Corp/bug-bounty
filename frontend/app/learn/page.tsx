"use client";

import { Sidebar } from '@/components/dashboard/Sidebar';
import { AtmosphericBackground } from '@/components/dashboard/AtmosphericBackground';

export default function LearnPage() {
  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      <AtmosphericBackground />
      <Sidebar />
      
      <div className="lg:ml-64 min-h-screen">
        <div className="relative z-10 p-10">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Learning Hub</h1>
            <p className="text-slate-400">Educational resources and tutorials</p>
          </div>
          
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
            <p className="text-white/60">Learning hub coming soon. Access tutorials, courses, and security guides.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
