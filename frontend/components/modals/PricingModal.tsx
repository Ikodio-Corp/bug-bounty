'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { X, Check, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface PricingModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function PricingModal({ isOpen, onClose }: PricingModalProps) {
  const plans = [
    {
      name: 'Free',
      price: '$0',
      period: '/month',
      description: 'Perfect for getting started',
      features: [
        'Up to 10 scans per month',
        'Basic vulnerability detection',
        'Community support',
        'Public bug reports',
        'Access to marketplace (view only)'
      ],
      cta: 'Get Started',
      popular: false
    },
    {
      name: 'Pro',
      price: '$49',
      period: '/month',
      description: 'For serious bug hunters',
      features: [
        'Unlimited scans',
        'Advanced AI detection',
        'Priority support',
        'Private bug reports',
        'Full marketplace access',
        'API access',
        'Custom integrations',
        'Performance analytics'
      ],
      cta: 'Start Free Trial',
      popular: true
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: '',
      description: 'For organizations',
      features: [
        'Everything in Pro',
        'Dedicated support team',
        'Custom SLA',
        'On-premise deployment',
        'Advanced security features',
        'Team management',
        'Custom training',
        'Compliance reports'
      ],
      cta: 'Contact Sales',
      popular: false
    }
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="relative w-full max-w-6xl max-h-[90vh] overflow-y-auto bg-black/95 backdrop-blur-xl border border-white/20 rounded-2xl pointer-events-auto"
            >
              {/* Close button */}
              <button
                onClick={onClose}
                className="absolute top-4 right-4 p-2 text-white/60 hover:text-white transition-colors"
              >
                <X size={24} />
              </button>

              <div className="p-8 md:p-12">
                {/* Header */}
                <div className="text-center mb-12">
                  <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                    Choose Your Plan
                  </h2>
                  <p className="text-lg text-white/60">
                    Start free, upgrade as you grow
                  </p>
                </div>

                {/* Pricing Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {plans.map((plan, index) => (
                    <motion.div
                      key={plan.name}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className={`relative p-8 rounded-xl border ${
                        plan.popular
                          ? 'border-white/40 bg-white/10'
                          : 'border-white/20 bg-white/5'
                      }`}
                    >
                      {plan.popular && (
                        <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                          <div className="bg-white text-black px-4 py-1 rounded-full text-sm font-semibold flex items-center gap-1">
                            <Zap size={14} />
                            Most Popular
                          </div>
                        </div>
                      )}

                      <div className="text-center mb-6">
                        <h3 className="text-2xl font-bold text-white mb-2">
                          {plan.name}
                        </h3>
                        <p className="text-white/60 text-sm mb-4">
                          {plan.description}
                        </p>
                        <div className="flex items-baseline justify-center gap-1">
                          <span className="text-4xl font-bold text-white">
                            {plan.price}
                          </span>
                          <span className="text-white/60">{plan.period}</span>
                        </div>
                      </div>

                      <ul className="space-y-3 mb-8">
                        {plan.features.map((feature, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-white/80">
                            <Check className="w-4 h-4 text-white flex-shrink-0 mt-0.5" strokeWidth={3} />
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>

                      <Button
                        className={`w-full ${
                          plan.popular
                            ? 'bg-white hover:bg-gray-200 text-black'
                            : 'bg-white/10 hover:bg-white/20 text-white border border-white/20'
                        }`}
                      >
                        {plan.cta}
                      </Button>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
