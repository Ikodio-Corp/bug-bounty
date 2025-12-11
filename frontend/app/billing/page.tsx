"use client";

import { Sidebar } from '@/components/dashboard/Sidebar';
import { AtmosphericBackground } from '@/components/dashboard/AtmosphericBackground';
import { CreditCard, Download, Check } from 'lucide-react';

export default function BillingPage() {
  const invoices = [
    { id: 'INV-001', date: '01 Nov 2024', amount: 450000, status: 'Lunas', plan: 'Professional Bulanan' },
    { id: 'INV-002', date: '01 Okt 2024', amount: 450000, status: 'Lunas', plan: 'Professional Bulanan' },
    { id: 'INV-003', date: '01 Sep 2024', amount: 450000, status: 'Lunas', plan: 'Professional Bulanan' },
  ];

  const plans = [
    { 
      name: 'Starter', 
      price: 0, 
      features: ['10 scan per bulan', '3 target domain', 'Scanner dasar', 'Community support', 'Report PDF'] 
    },
    { 
      name: 'Professional', 
      price: 450000, 
      features: ['100 scan per bulan', 'Unlimited domain', 'AI Scanner + semua tools', 'Priority support 24/7', 'API access', 'Guild & marketplace'], 
      current: true 
    },
    { 
      name: 'Enterprise', 
      price: 2500000, 
      features: ['Unlimited scans', 'Dedicated expert', 'Custom AI training', 'White-label', 'SLA 99.9%', 'On-premise', 'Team unlimited'] 
    },
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
          <div className="bg-gradient-to-r from-white/10 to-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-white mb-2">Paket Saat Ini: Professional Bulanan</h2>
                <p className="text-slate-300">Rp 450.000/bulan • Billing berikutnya: 1 Des 2024</p>
              </div>
              <button className="px-6 py-3 bg-white/10 hover:bg-white/20 text-white rounded-lg transition">Upgrade Paket</button>
            </div>
          </div>

          {/* Plans */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            {plans.map((plan) => (
              <div key={plan.name} className={`bg-white/5 backdrop-blur-xl border rounded-2xl p-6 ${plan.current ? 'border-white' : 'border-white/10'}`}>
                {plan.current && <span className="inline-block px-3 py-1 bg-white text-white text-xs rounded-full mb-3">Aktif</span>}
                <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                <div className="text-2xl font-bold text-white mb-4">
                  {plan.price === 0 ? 'Gratis' : `Rp ${plan.price.toLocaleString('id-ID')}`}
                  {plan.price > 0 && <span className="text-sm text-slate-400">/bulan</span>}
                </div>
                <ul className="space-y-2 mb-6">
                  {plan.features.map((f) => <li key={f} className="flex items-start gap-2 text-slate-300 text-sm"><Check size={16} className="text-green-400 mt-0.5 flex-shrink-0" />{f}</li>)}
                </ul>
                <button className="w-full py-3 bg-white/10 hover:bg-white/20 text-white rounded-lg transition">
                  {plan.current ? 'Paket Aktif' : plan.name === 'Enterprise' ? 'Hubungi Sales' : 'Pilih Paket'}
                </button>
              </div>
            ))}
          </div>

          {/* Payment Method */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 mb-8">
            <h2 className="text-xl font-bold text-white mb-4">Metode Pembayaran</h2>
            <div className="flex items-center gap-4 p-4 bg-white/5 rounded-lg">
              <CreditCard className="text-gray-400" size={32} />
              <div className="flex-1">
                <div className="text-white font-medium">BCA •••• •••• 8899</div>
                <div className="text-slate-400 text-sm">Virtual Account</div>
              </div>
              <button className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition">Ubah</button>
            </div>
          </div>

          {/* Invoice History */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <h2 className="text-xl font-bold text-white mb-4">Riwayat Invoice</h2>
            <div className="space-y-3">
              {invoices.map((inv) => (
                <div key={inv.id} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                  <div>
                    <div className="text-white font-medium">{inv.id}</div>
                    <div className="text-slate-400 text-sm">{inv.date} • {inv.plan}</div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-white font-bold">Rp {inv.amount.toLocaleString('id-ID')}</span>
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
