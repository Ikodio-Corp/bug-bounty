"use client";

import { Sidebar } from '@/components/dashboard/Sidebar';
import { AtmosphericBackground } from '@/components/dashboard/AtmosphericBackground';
import { DollarSign, TrendingUp, Award, Download } from 'lucide-react';

export default function RewardsPage() {
  const payments = [
    { date: '2024-11-20', amount: 5000, bug: 'SQL Injection', status: 'Paid' },
    { date: '2024-11-15', amount: 2500, bug: 'XSS Vulnerability', status: 'Paid' },
    { date: '2024-11-10', amount: 1000, bug: 'CSRF Token Bypass', status: 'Pending' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      <AtmosphericBackground />
      <Sidebar />
      
      <div className="lg:ml-64 min-h-screen">
        <div className="relative z-10 p-10">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Rewards</h1>
            <p className="text-slate-400">Track your earnings and claim bounties</p>
          </div>

          {/* Summary Cards */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="bg-gradient-to-br from-green-600/20 to-emerald-600/20 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
              <DollarSign className="text-green-400 mb-3" size={32} />
              <div className="text-3xl font-bold text-white mb-1">$15,000</div>
              <div className="text-slate-300">Total Earned</div>
            </div>
            <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
              <TrendingUp className="text-gray-400 mb-3" size={32} />
              <div className="text-3xl font-bold text-white mb-1">$2,500</div>
              <div className="text-slate-300">Pending</div>
            </div>
            <div className="bg-gradient-to-br from-white/10 to-gray-500/20 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
              <Award className="text-gray-400 mb-3" size={32} />
              <div className="text-3xl font-bold text-white mb-1">42</div>
              <div className="text-slate-300">Bugs Rewarded</div>
            </div>
          </div>

          {/* Payment History */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <h2 className="text-xl font-bold text-white mb-4">Payment History</h2>
            <div className="space-y-3">
              {payments.map((payment, i) => (
                <div key={i} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                  <div>
                    <div className="text-white font-medium">{payment.bug}</div>
                    <div className="text-slate-400 text-sm">{payment.date}</div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-white font-bold text-xl">${payment.amount.toLocaleString()}</span>
                    <span className={`px-3 py-1 rounded-full text-sm ${payment.status === 'Paid' ? 'bg-green-600/20 text-green-400' : 'bg-yellow-600/20 text-yellow-400'}`}>{payment.status}</span>
                    {payment.status === 'Paid' && <button className="p-2 hover:bg-white/10 rounded-lg transition"><Download size={18} className="text-slate-400" /></button>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
