"use client";

import { useState } from 'react';
import { Sidebar } from '@/components/dashboard/Sidebar';
import { AtmosphericBackground } from '@/components/dashboard/AtmosphericBackground';
import { Search, MessageCircle, FileText, HelpCircle, Mail, Phone, Book } from 'lucide-react';

export default function HelpPage() {
  const [searchQuery, setSearchQuery] = useState('');

  const faqs = [
    { q: 'How do I start bug hunting?', a: 'Create an account, complete your profile, and browse available programs.' },
    { q: 'When do I get paid?', a: 'Payments are processed within 7-14 days after bug verification.' },
    { q: 'What tools do I need?', a: 'Basic tools include Burp Suite, OWASP ZAP, Nmap, and our built-in AI scanner.' },
    { q: 'How many scans can I run?', a: 'Free tier: 5/month, Pro: 50/month, Enterprise: Unlimited.' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      <AtmosphericBackground />
      <Sidebar />
      
      <div className="lg:ml-64 min-h-screen">
        <div className="relative z-10 p-10">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Help Center</h1>
            <p className="text-slate-400">Find answers and get support</p>
          </div>

          {/* Search */}
          <div className="mb-8">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
              <input
                type="text"
                placeholder="Search for help..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          {/* Quick Actions */}
          <div className="grid md:grid-cols-3 gap-4 mb-8">
            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6 hover:bg-white/10 transition cursor-pointer">
              <Book className="text-blue-400 mb-3" size={32} />
              <h3 className="text-white font-semibold mb-2">Documentation</h3>
              <p className="text-slate-400 text-sm">Complete guides and API reference</p>
            </div>
            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6 hover:bg-white/10 transition cursor-pointer">
              <MessageCircle className="text-green-400 mb-3" size={32} />
              <h3 className="text-white font-semibold mb-2">Live Chat</h3>
              <p className="text-slate-400 text-sm">Chat with support team</p>
            </div>
            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6 hover:bg-white/10 transition cursor-pointer">
              <FileText className="text-purple-400 mb-3" size={32} />
              <h3 className="text-white font-semibold mb-2">Submit Ticket</h3>
              <p className="text-slate-400 text-sm">Get help from our team</p>
            </div>
          </div>

          {/* FAQs */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 mb-8">
            <h2 className="text-xl font-bold text-white mb-4">Frequently Asked Questions</h2>
            <div className="space-y-3">
              {faqs.map((faq, idx) => (
                <details key={idx} className="group">
                  <summary className="flex items-center justify-between cursor-pointer p-4 bg-white/5 rounded-lg hover:bg-white/10 transition">
                    <span className="text-white font-medium">{faq.q}</span>
                    <HelpCircle className="text-slate-400" size={20} />
                  </summary>
                  <div className="mt-2 p-4 text-slate-300">{faq.a}</div>
                </details>
              ))}
            </div>
          </div>

          {/* Contact */}
          <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-white mb-4">Still need help?</h2>
            <p className="text-slate-300 mb-6">Our support team is available 24/7</p>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="flex items-center gap-3 p-4 bg-white/5 rounded-lg">
                <Mail className="text-blue-400" size={24} />
                <div>
                  <div className="text-white font-medium">Email</div>
                  <div className="text-slate-400 text-sm">support@ikodio.com</div>
                </div>
              </div>
              <div className="flex items-center gap-3 p-4 bg-white/5 rounded-lg">
                <Phone className="text-green-400" size={24} />
                <div>
                  <div className="text-white font-medium">Phone</div>
                  <div className="text-slate-400 text-sm">+1 (234) 567-890</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
