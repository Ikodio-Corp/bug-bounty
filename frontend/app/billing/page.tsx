"use client";

import { Sidebar } from '@/components/dashboard/Sidebar';
import { AtmosphericBackground } from '@/components/dashboard/AtmosphericBackground';
import { CreditCard, Download, Check } from 'lucide-react';

export default function BillingPage() {
  const invoices = [
    { id: 'INV-001', date: '2024-11-01', amount: 99, status: 'Paid', plan: 'Pro Monthly' },
    { id: 'INV-002', date: '2024-10-01', amount: 99, status: 'Paid', plan: 'Pro Monthly' },
    { id: 'INV-003', date: '2024-09-01', amount: 99, status: 'Paid', plan: 'Pro Monthly' },
  ];

  const plans = [
    { name: 'Free', price: 0, features: ['5 scans/month', 'Basic support', 'Community access'] },
    { name: 'Pro', price: 99, features: ['50 scans/month', 'Priority support', 'Advanced tools', 'API access'], current: true },
    { name: 'Enterprise', price: 499, features: ['Unlimited scans', '24/7 support', 'Custom integrations', 'Dedicated manager'] },
  ];

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      <AtmosphericBackground />
      <Sidebar />
      
      <div className="lg:ml-64 min-h-screen">
        <div className="relative z-10 p-10">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Billing</h1>
            <p className="text-slate-400">Manage your subscription and payment methods</p>
          </div>

          {/* Current Plan */}
          <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 backdrop-blur-xl border border-white/10 rounded-2xl p-6 mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-white mb-2">Current Plan: Pro Monthly</h2>
                <p className="text-slate-300">$99/month • Next billing: Dec 1, 2024</p>
              </div>
              <button className="px-6 py-3 bg-white/10 hover:bg-white/20 text-white rounded-lg transition">Upgrade Plan</button>
            </div>
          </div>

          {/* Plans */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            {plans.map((plan) => (
              <div key={plan.name} className={`bg-white/5 backdrop-blur-xl border rounded-2xl p-6 ${plan.current ? 'border-blue-500' : 'border-white/10'}`}>
                {plan.current && <span className="inline-block px-3 py-1 bg-blue-600 text-white text-xs rounded-full mb-3">Current</span>}
                <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                <div className="text-3xl font-bold text-white mb-4">${plan.price}<span className="text-lg text-slate-400">/mo</span></div>
                <ul className="space-y-2 mb-6">
                  {plan.features.map((f) => <li key={f} className="flex items-center gap-2 text-slate-300"><Check size={16} className="text-green-400" />{f}</li>)}
                </ul>
                <button className="w-full py-3 bg-white/10 hover:bg-white/20 text-white rounded-lg transition">{plan.current ? 'Current Plan' : 'Select Plan'}</button>
              </div>
            ))}
          </div>

          {/* Payment Method */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 mb-8">
            <h2 className="text-xl font-bold text-white mb-4">Payment Method</h2>
            <div className="flex items-center gap-4 p-4 bg-white/5 rounded-lg">
              <CreditCard className="text-blue-400" size={32} />
              <div className="flex-1">
                <div className="text-white font-medium">•••• •••• •••• 4242</div>
                <div className="text-slate-400 text-sm">Expires 12/2025</div>
              </div>
              <button className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition">Update</button>
            </div>
          </div>

          {/* Invoice History */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <h2 className="text-xl font-bold text-white mb-4">Invoice History</h2>
            <div className="space-y-3">
              {invoices.map((inv) => (
                <div key={inv.id} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                  <div>
                    <div className="text-white font-medium">{inv.id}</div>
                    <div className="text-slate-400 text-sm">{inv.date} • {inv.plan}</div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-white font-bold">${inv.amount}</span>
                    <span className="px-3 py-1 bg-green-600/20 text-green-400 rounded-full text-sm">{inv.status}</span>
                    <button className="p-2 hover:bg-white/10 rounded-lg transition"><Download size={18} className="text-slate-400" /></button>
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
