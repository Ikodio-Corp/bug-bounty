'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, X, Zap, Building, Crown, Shield, ChevronRight, Sparkles } from 'lucide-react';
import Link from 'next/link';

const pricingTiers = [
  {
    id: 'free',
    name: 'Free',
    icon: Sparkles,
    price: 'Rp 0',
    period: 'selamanya',
    description: 'Perfect for students & hobbyists',
    color: 'from-gray-500 to-gray-600',
    features: [
      { text: '10 scans per bulan', included: true },
      { text: '3 target domains maksimum', included: true },
      { text: 'Scanner dasar (Nuclei, ZAP)', included: true },
      { text: 'Report PDF standar', included: true },
      { text: 'Community support', included: true },
      { text: '1GB storage', included: true },
      { text: '1000 API calls per bulan', included: true },
      { text: 'No Auto-fix', included: false },
      { text: 'No Marketplace selling', included: false },
    ],
    cta: 'Mulai Gratis',
    ctaLink: '/register',
    popular: false,
  },
  {
    id: 'professional',
    name: 'Professional',
    icon: Zap,
    price: 'Rp 450K',
    period: '/bulan',
    priceAnnual: 'Rp 4.5 Juta/tahun',
    saveAnnual: 'Hemat 2 bulan',
    description: 'Best for freelance researchers',
    color: 'from-gray-400 to-gray-500',
    features: [
      { text: '50 scans per bulan', included: true },
      { text: 'Unlimited target domains', included: true },
      { text: 'AI Scanner + All tools', included: true },
      { text: '20 auto-fixes per bulan', included: true },
      { text: 'Priority support 24/7', included: true },
      { text: '10GB storage', included: true },
      { text: '5000 API calls per bulan', included: true },
      { text: 'Marketplace access (15% fee)', included: true },
      { text: '3 team members', included: true },
      { text: 'Advanced analytics', included: true },
    ],
    cta: 'Mulai Trial 14 Hari',
    ctaLink: '/register?tier=professional',
    popular: true,
    roi: '789% - 5,455% ROI',
  },
  {
    id: 'business',
    name: 'Business',
    icon: Building,
    price: 'Rp 1.5M',
    period: '/bulan',
    priceAnnual: 'Rp 15 Juta/tahun',
    saveAnnual: 'Hemat 3 Juta',
    description: 'For SMB & agencies',
    color: 'from-gray-300 to-gray-500',
    features: [
      { text: '200 scans per bulan', included: true },
      { text: 'Everything in Professional', included: true },
      { text: 'UNLIMITED auto-fixes', included: true, highlight: true },
      { text: '50GB storage', included: true },
      { text: '25000 API calls per bulan', included: true },
      { text: '10 team members', included: true },
      { text: 'SSO (Single Sign-On)', included: true },
      { text: 'CI/CD integration', included: true },
      { text: 'Marketplace (10% fee)', included: true },
      { text: 'Quarterly security review', included: true },
    ],
    cta: 'Request Demo',
    ctaLink: '/contact?demo=business',
    popular: false,
    roi: '1,233% - 1,900% ROI',
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    icon: Crown,
    price: 'Rp 10M',
    period: '/bulan',
    description: 'For large corporations',
    color: 'from-yellow-500 to-orange-600',
    features: [
      { text: 'Unlimited scans', included: true, highlight: true },
      { text: 'Everything in Business', included: true },
      { text: 'Unlimited auto-fixes', included: true },
      { text: '500GB storage', included: true },
      { text: 'Unlimited API calls', included: true },
      { text: 'Dedicated security expert', included: true },
      { text: 'White-label solution', included: true },
      { text: 'SLA 99.9% uptime', included: true },
      { text: 'On-premise deployment', included: true },
      { text: 'Custom AI model training', included: true },
      { text: 'Unlimited team members', included: true },
      { text: '24/7 dedicated support', included: true },
    ],
    cta: 'Contact Sales',
    ctaLink: '/contact?tier=enterprise',
    popular: false,
    roi: '250% ROI',
  },
  {
    id: 'government',
    name: 'Government',
    icon: Shield,
    price: 'Custom',
    period: '',
    description: 'For government agencies',
    color: 'from-green-500 to-teal-600',
    features: [
      { text: 'Everything in Enterprise', included: true },
      { text: 'Unlimited scans', included: true },
      { text: 'Unlimited auto-fixes', included: true },
      { text: '1000GB storage', included: true },
      { text: 'Unlimited API calls', included: true },
      { text: 'Air-gapped deployment', included: true, highlight: true },
      { text: 'Data sovereignty guarantee', included: true },
      { text: 'Government compliance', included: true },
      { text: 'Security clearance support', included: true },
      { text: 'Multi-year contracts', included: true },
      { text: 'Custom SLA terms', included: true },
      { text: 'Dedicated account team', included: true },
    ],
    cta: 'Contact Sales',
    ctaLink: '/contact?tier=government',
    popular: false,
  },
];

export default function PricingPage() {
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'annual'>('monthly');
  const [highlightTier, setHighlightTier] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-black text-white">
      {/* Header */}
      <div className="container mx-auto px-4 py-16 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-white via-gray-300 to-white bg-clip-text text-transparent">
            Pricing yang Fair, Value yang Maksimal
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            70% lebih murah dari kompetitor dengan 10x lebih banyak fitur. Pilih plan yang sesuai dengan kebutuhan Anda.
          </p>
        </motion.div>

        {/* Billing Toggle */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="flex items-center justify-center gap-4 mb-12"
        >
          <span className={billingPeriod === 'monthly' ? 'text-white font-semibold' : 'text-gray-400'}>
            Monthly
          </span>
          <button
            onClick={() => setBillingPeriod(billingPeriod === 'monthly' ? 'annual' : 'monthly')}
            className="relative w-16 h-8 bg-gray-700 rounded-full transition-all duration-300"
          >
            <motion.div
              className="absolute top-1 left-1 w-6 h-6 bg-white rounded-full"
              animate={{ x: billingPeriod === 'annual' ? 32 : 0 }}
              transition={{ type: 'spring', stiffness: 500, damping: 30 }}
            />
          </button>
          <span className={billingPeriod === 'annual' ? 'text-white font-semibold' : 'text-gray-400'}>
            Annual
            <span className="ml-2 text-green-400 text-sm">(Save 2 months)</span>
          </span>
        </motion.div>
      </div>

      {/* Pricing Cards */}
      <div className="container mx-auto px-4 pb-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {pricingTiers.map((tier, index) => {
            const Icon = tier.icon;
            const isHighlighted = highlightTier === tier.id;
            
            return (
              <motion.div
                key={tier.id}
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1, duration: 0.6 }}
                className={`relative bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border-2 transition-all duration-300 ${
                  tier.popular
                    ? 'border-white shadow-2xl shadow-white/10 scale-105'
                    : isHighlighted
                    ? 'border-white/40 shadow-xl shadow-white/10'
                    : 'border-gray-700 hover:border-gray-600'
                }`}
              >
                {/* Popular Badge */}
                {tier.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-white text-black px-4 py-1 rounded-full text-sm font-bold shadow-lg">
                       RECOMMENDED
                    </span>
                  </div>
                )}

                {/* Icon */}
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${tier.color} flex items-center justify-center mb-4`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>

                {/* Tier Name */}
                <h3 className="text-2xl font-bold mb-2">{tier.name}</h3>
                <p className="text-gray-400 text-sm mb-4">{tier.description}</p>

                {/* Price */}
                <div className="mb-6">
                  <div className="flex items-end gap-1">
                    <span className="text-4xl font-bold">{tier.price}</span>
                    {tier.period && <span className="text-gray-400 mb-1">{tier.period}</span>}
                  </div>
                  {billingPeriod === 'annual' && tier.priceAnnual && (
                    <div className="mt-2">
                      <p className="text-sm text-gray-300">{tier.priceAnnual}</p>
                      <p className="text-xs text-green-400">{tier.saveAnnual}</p>
                    </div>
                  )}
                  {tier.roi && (
                    <p className="text-sm text-green-400 mt-2 font-semibold">{tier.roi}</p>
                  )}
                </div>

                {/* Features */}
                <ul className="space-y-3 mb-6">
                  {tier.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      {feature.included ? (
                        <Check className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                      ) : (
                        <X className="w-5 h-5 text-gray-600 flex-shrink-0 mt-0.5" />
                      )}
                      <span
                        className={`text-sm ${
                          feature.included ? 'text-gray-300' : 'text-gray-600 line-through'
                        } ${feature.highlight ? 'font-bold text-yellow-400' : ''}`}
                      >
                        {feature.text}
                      </span>
                    </li>
                  ))}
                </ul>

                {/* CTA Button */}
                <Link href={tier.ctaLink}>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={`w-full py-3 rounded-lg font-semibold transition-all duration-300 flex items-center justify-center gap-2 ${
                      tier.popular
                        ? 'bg-white text-black shadow-lg hover:bg-gray-200'
                        : 'bg-gray-700 text-white hover:bg-gray-600'
                    }`}
                  >
                    {tier.cta}
                    <ChevronRight className="w-5 h-5" />
                  </motion.button>
                </Link>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Comparison Table CTA */}
      <div className="container mx-auto px-4 py-16 text-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8, duration: 0.6 }}
        >
          <h2 className="text-3xl font-bold mb-4">Need detailed comparison?</h2>
          <p className="text-gray-400 mb-6">View our comprehensive feature matrix</p>
          <Link href="#features">
            <button className="bg-white text-black px-8 py-3 rounded-lg font-semibold hover:bg-gray-200 transition-all duration-300">
              View Feature Matrix
            </button>
          </Link>
        </motion.div>
      </div>

      {/* FAQ Section */}
      <div className="container mx-auto px-4 py-16">
        <h2 className="text-4xl font-bold text-center mb-12">Frequently Asked Questions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          <FAQItem
            question="Can I upgrade or downgrade anytime?"
            answer="Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately for upgrades, or at the end of your billing period for downgrades."
          />
          <FAQItem
            question="What payment methods do you accept?"
            answer="We accept credit cards (Visa, Mastercard, Amex), bank transfers, and for Enterprise clients, we can arrange custom payment terms."
          />
          <FAQItem
            question="Is there a free trial?"
            answer="Yes! Professional plan comes with a 14-day free trial. No credit card required to start."
          />
          <FAQItem
            question="What happens if I exceed my limits?"
            answer="You'll receive notifications as you approach your limits. Once exceeded, you'll be prompted to upgrade or wait until the next billing cycle."
          />
        </div>
      </div>
    </div>
  );
}

function FAQItem({ question, answer }: { question: string; answer: string }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="bg-gray-800/50 backdrop-blur-lg rounded-lg p-6 border border-gray-700">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full text-left flex justify-between items-center gap-4"
      >
        <h3 className="text-lg font-semibold">{question}</h3>
        <ChevronRight
          className={`w-5 h-5 text-gray-400 transition-transform duration-300 ${
            isOpen ? 'rotate-90' : ''
          }`}
        />
      </button>
      {isOpen && (
        <motion.p
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="text-gray-400 mt-4"
        >
          {answer}
        </motion.p>
      )}
    </div>
  );
}
