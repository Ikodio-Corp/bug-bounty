"use client";

import { useState } from 'react';
import { Sidebar } from '@/components/dashboard/Sidebar';
import { AtmosphericBackground } from '@/components/dashboard/AtmosphericBackground';
import { Bell, Shield, Palette, Globe, Save } from 'lucide-react';

export default function PreferencesPage() {
  const [notifications, setNotifications] = useState({ email: true, push: true, sms: false });
  const [theme, setTheme] = useState('dark');

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      <AtmosphericBackground />
      <Sidebar />
      
      <div className="lg:ml-64 min-h-screen">
        <div className="relative z-10 p-10">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Preferences</h1>
            <p className="text-slate-400">Customize your Ikodio experience</p>
          </div>

          {/* Notifications */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 mb-6">
            <div className="flex items-center gap-3 mb-4">
              <Bell className="text-gray-400" size={24} />
              <h2 className="text-xl font-bold text-white">Notifications</h2>
            </div>
            <div className="space-y-4">
              {[
                { key: 'email', label: 'Email Notifications', desc: 'Receive updates via email' },
                { key: 'push', label: 'Push Notifications', desc: 'Browser push notifications' },
                { key: 'sms', label: 'SMS Notifications', desc: 'Text message alerts' }
              ].map((item) => (
                <div key={item.key} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                  <div>
                    <div className="text-white font-medium">{item.label}</div>
                    <div className="text-slate-400 text-sm">{item.desc}</div>
                  </div>
                  <button onClick={() => setNotifications({...notifications, [item.key]: !notifications[item.key as keyof typeof notifications]})} className={`w-12 h-6 rounded-full transition ${notifications[item.key as keyof typeof notifications] ? 'bg-white' : 'bg-slate-600'}`}>
                    <div className={`w-5 h-5 bg-white rounded-full transition-transform ${notifications[item.key as keyof typeof notifications] ? 'translate-x-6' : 'translate-x-1'}`} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Appearance */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 mb-6">
            <div className="flex items-center gap-3 mb-4">
              <Palette className="text-gray-400" size={24} />
              <h2 className="text-xl font-bold text-white">Appearance</h2>
            </div>
            <div className="grid md:grid-cols-3 gap-4">
              {['dark', 'light', 'auto'].map((t) => (
                <button key={t} onClick={() => setTheme(t)} className={`p-4 rounded-lg border-2 transition ${theme === t ? 'border-white bg-white/20' : 'border-white/10 bg-white/5'}`}>
                  <div className="text-white font-medium capitalize">{t}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Security */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 mb-6">
            <div className="flex items-center gap-3 mb-4">
              <Shield className="text-green-400" size={24} />
              <h2 className="text-xl font-bold text-white">Security</h2>
            </div>
            <div className="space-y-3">
              <button className="w-full p-4 bg-white/5 hover:bg-white/10 rounded-lg text-left transition">
                <div className="text-white font-medium">Change Password</div>
                <div className="text-slate-400 text-sm">Update your password</div>
              </button>
              <button className="w-full p-4 bg-white/5 hover:bg-white/10 rounded-lg text-left transition">
                <div className="text-white font-medium">Two-Factor Authentication</div>
                <div className="text-slate-400 text-sm">Add extra security layer</div>
              </button>
            </div>
          </div>

          {/* Language */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 mb-6">
            <div className="flex items-center gap-3 mb-4">
              <Globe className="text-gray-400" size={24} />
              <h2 className="text-xl font-bold text-white">Language & Region</h2>
            </div>
            <select className="w-full p-4 bg-white/5 border border-white/10 rounded-lg text-white">
              <option>English (US)</option>
              <option>Español</option>
              <option>Français</option>
            </select>
          </div>

          {/* Save Button */}
          <button className="flex items-center gap-2 px-6 py-3 bg-white hover:bg-gray-200 text-white rounded-lg transition">
            <Save size={20} />
            Save Preferences
          </button>
        </div>
      </div>
    </div>
  );
}
