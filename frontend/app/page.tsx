'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, useScroll, useInView } from 'framer-motion';
import { 
  Shield, Zap, Users, TrendingUp, DollarSign, 
  ArrowRight, ChevronDown, Star, Award, Target,
  Code, Brain, Sparkles, Lock, Globe, Rocket,
  BarChart3, Headphones, ShoppingCart, Menu, X,
  Github, Twitter, Linkedin, Play, Check, Upload,
  FileText, RefreshCw, Trophy
} from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

// Animated background particles
function ParticleBackground() {
  const [particles, setParticles] = useState<Array<{x: number; y: number; opacity: number}>>([]);

  useEffect(() => {
    const newParticles = Array.from({ length: 50 }, () => ({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      opacity: Math.random() * 0.5,
    }));
    setParticles(newParticles);
  }, []);

  if (particles.length === 0) return null;

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map((particle, i) => (
        <motion.div
          key={i}
          className="absolute w-1 h-1 bg-white rounded-full"
          initial={particle}
          animate={{
            y: [particle.y, Math.random() * (typeof window !== 'undefined' ? window.innerHeight : 1000)],
            opacity: [particle.opacity, Math.random() * 0.5, 0],
          }}
          transition={{
            duration: Math.random() * 10 + 10,
            repeat: Infinity,
            ease: 'linear',
          }}
        />
      ))}
    </div>
  );
}

// Floating elements
function FloatingElements() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      <motion.div
        className="absolute top-20 left-10 w-20 h-20 border border-white/10 rounded-full"
        animate={{ y: [0, 30, 0], rotate: 360 }}
        transition={{ duration: 20, repeat: Infinity }}
      />
      <motion.div
        className="absolute top-40 right-20 w-32 h-32 border border-white/10 rounded-lg"
        animate={{ y: [0, -40, 0], rotate: -360 }}
        transition={{ duration: 25, repeat: Infinity }}
      />
      <motion.div
        className="absolute bottom-20 left-1/4 w-16 h-16 border border-white/10 rounded-full"
        animate={{ y: [0, 20, 0], x: [0, 20, 0] }}
        transition={{ duration: 15, repeat: Infinity }}
      />
    </div>
  );
}

// Code Terminal Animation
function CodeTerminal() {
  const [currentLine, setCurrentLine] = useState(0);
  const codeLines = [
    '$ ikodio scan --target example.com',
    '✓ AI agents initialized',
    '✓ Scanning for vulnerabilities...',
    '✓ Found 3 critical bugs in 90 seconds!',
    '$ Reward: $5,000',
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentLine((prev) => (prev + 1) % codeLines.length);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-black/50 backdrop-blur-xl rounded-lg border border-gray-700 p-6 font-mono text-sm">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-3 h-3 rounded-full bg-red-500" />
        <div className="w-3 h-3 rounded-full bg-yellow-500" />
        <div className="w-3 h-3 rounded-full bg-green-500" />
      </div>
      {codeLines.slice(0, currentLine + 1).map((line, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className={line.includes('$') ? 'text-green-400' : 'text-gray-300'}
        >
          {line}
        </motion.div>
      ))}
      <motion.div
        animate={{ opacity: [1, 0] }}
        transition={{ duration: 0.8, repeat: Infinity }}
        className="inline-block w-2 h-4 bg-white ml-1 mt-2"
      />
    </div>
  );
}

// Pricing Modal
function PricingModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={onClose}>
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-gradient-to-br from-gray-900 to-black border border-gray-700 rounded-2xl max-w-4xl w-full p-8"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-start mb-6">
          <h2 className="text-3xl font-bold text-white">Pricing Plans</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={24} />
          </button>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {[
            { 
              name: 'Starter', 
              price: 'Gratis', 
              features: [
                '10 scan per bulan', 
                'Scanner dasar (Nuclei, ZAP)', 
                'Report PDF standar',
                'Community support',
                'Max 3 target domain'
              ] 
            },
            { 
              name: 'Professional', 
              price: 'Rp 450.000', 
              features: [
                '100 scan per bulan', 
                'AI Scanner + semua tools',
                'Priority support 24/7',
                'API access & webhooks', 
                'Custom report template',
                'Guild & marketplace access',
                'Advanced analytics',
                'Unlimited target domain'
              ], 
              highlight: true 
            },
            { 
              name: 'Enterprise', 
              price: 'Rp 2.500.000', 
              features: [
                'Unlimited scans', 
                'Dedicated security expert',
                'Custom AI model training',
                'White-label solution',
                'SLA 99.9% uptime',
                'On-premise deployment',
                'Team collaboration (unlimited)',
                'Compliance reports (ISO, PCI-DSS)'
              ] 
            }
          ].map((plan, i) => (
            <motion.div
              key={i}
              whileHover={{ y: -10 }}
              className={`p-6 rounded-xl border ${plan.highlight ? 'border-white bg-white/5' : 'border-gray-700'}`}
            >
              <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
              <div className="text-3xl font-bold text-white mb-6">
                {plan.price}
                {plan.price !== 'Gratis' && plan.name !== 'Enterprise' && <span className="text-lg text-gray-400">/bulan</span>}
                {plan.name === 'Enterprise' && <span className="text-lg text-gray-400">/bulan</span>}
              </div>
              <ul className="space-y-3 mb-6">
                {plan.features.map((feature, j) => (
                  <li key={j} className="flex items-start gap-2 text-gray-300 text-sm">
                    <Check size={16} className="text-green-400 mt-0.5 flex-shrink-0" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
              <Button className={plan.highlight ? 'w-full bg-white text-black hover:bg-gray-200' : 'w-full'}>
                {plan.name === 'Enterprise' ? 'Hubungi Sales' : 'Mulai Sekarang'}
              </Button>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

// Video Modal
function VideoModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={onClose}>
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-gradient-to-br from-gray-900 to-black border border-gray-700 rounded-2xl max-w-4xl w-full p-8"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-start mb-6">
          <h2 className="text-3xl font-bold text-white">Platform Demo</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={24} />
          </button>
        </div>
        <div className="aspect-video bg-black rounded-lg flex items-center justify-center">
          <Play size={64} className="text-white" />
        </div>
      </motion.div>
    </div>
  );
}

// Counter animation
function Counter({ end, duration = 2 }: { end: number; duration?: number }) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true });

  useEffect(() => {
    if (!isInView) return;
    
    let startTime: number;
    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / (duration * 1000), 1);
      setCount(Math.floor(progress * end));
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
  }, [isInView, end, duration]);

  return <div ref={ref}>{count.toLocaleString()}+</div>;
}

export default function Home() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [pricingModalOpen, setPricingModalOpen] = useState(false);
  const [videoModalOpen, setVideoModalOpen] = useState(false);
  const { scrollYProgress } = useScroll();
  
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
      setMobileMenuOpen(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white">
      {/* Scroll Progress Bar */}
      <motion.div
        style={{ scaleX: scrollYProgress }}
        className="fixed top-0 left-0 right-0 h-1 bg-white origin-left z-50"
      />

      {/* HEADER */}
      <motion.nav
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.6 }}
        className={`fixed top-0 left-0 right-0 z-40 transition-all duration-300 ${
          isScrolled ? 'bg-black/90 backdrop-blur-xl shadow-lg' : 'bg-transparent'
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <motion.div 
              className="text-2xl font-bold text-white"
              whileHover={{ scale: 1.05 }}
            >
              Ikodio
            </motion.div>

            <div className="hidden md:flex items-center space-x-8">
              {['Home', 'Features', 'How It Works', 'Pricing'].map((item) => (
                <motion.button
                  key={item}
                  onClick={() => item === 'Pricing' ? setPricingModalOpen(true) : scrollToSection(item.toLowerCase().replace(' ', '-'))}
                  className="text-gray-300 hover:text-white transition-colors relative group"
                  whileHover={{ scale: 1.05 }}
                >
                  {item}
                  <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-white group-hover:w-full transition-all duration-300" />
                </motion.button>
              ))}
              <Link href="/marketplace" className="text-gray-300 hover:text-white transition-colors">
                Marketplace
              </Link>
            </div>

            <div className="hidden md:flex items-center space-x-4">
              <Link href="/login">
                <Button variant="outline" className="border-gray-600 text-white hover:bg-gray-800">
                  Login
                </Button>
              </Link>
              <Link href="/dashboard">
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button className="bg-white hover:bg-gray-200 text-black">
                    Dashboard
                  </Button>
                </motion.div>
              </Link>
            </div>

            <button className="md:hidden" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
              {mobileMenuOpen ? <X /> : <Menu />}
            </button>
          </div>
        </div>

        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="md:hidden bg-black/95 backdrop-blur-xl border-t border-gray-800"
          >
            <div className="px-4 py-4 space-y-3">
              {['Home', 'Features', 'How It Works', 'Pricing'].map((item) => (
                <button
                  key={item}
                  onClick={() => {
                    if (item === 'Pricing') {
                      setPricingModalOpen(true);
                      setMobileMenuOpen(false);
                    } else {
                      scrollToSection(item.toLowerCase().replace(' ', '-'));
                    }
                  }}
                  className="block w-full text-left py-2 text-gray-300 hover:text-white"
                >
                  {item}
                </button>
              ))}
              <Link href="/marketplace" className="block w-full text-left py-2 text-gray-300 hover:text-white">
                Marketplace
              </Link>
              <Link href="/login" className="block w-full text-left py-2 text-gray-300 hover:text-white">
                Login
              </Link>
              <Link href="/dashboard" className="block w-full text-left py-2 text-white font-semibold">
                Dashboard
              </Link>
            </div>
          </motion.div>
        )}
      </motion.nav>

      {/* HERO SECTION */}
      <section id="home" className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
        <ParticleBackground />
        <FloatingElements />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 z-10">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
              >
                <motion.h1 
                  className="text-5xl md:text-7xl font-extrabold mb-6 leading-tight text-white"
                  initial={{ opacity: 0, y: 50 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2, duration: 0.8 }}
                >
                  Ikodio Bug Bounty
                </motion.h1>

                <motion.h2 
                  className="text-2xl md:text-4xl font-bold mb-4 text-white"
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4, duration: 0.8 }}
                >
                  AI-Powered Bug Discovery in 90 Seconds
                </motion.h2>

                <motion.p
                  className="text-lg md:text-xl text-gray-400 mb-8 max-w-xl"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.4 }}
                >
                  Discover vulnerabilities faster than ever with AI agents. Join 10,000+ security researchers earning rewards globally.
                </motion.p>

                <motion.div
                  className="flex flex-col sm:flex-row gap-4 mb-8"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.6 }}
                >
                  <Link href="/dashboard">
                    <motion.div whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(255, 255, 255, 0.3)" }} whileTap={{ scale: 0.95 }}>
                      <Button size="lg" className="bg-white hover:bg-gray-200 text-black px-8 py-6 text-lg group">
                        Get Started
                        <ArrowRight className="ml-2 group-hover:translate-x-1 transition-transform" />
                      </Button>
                    </motion.div>
                  </Link>
                  
                  <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    <Button 
                      size="lg" 
                      variant="outline" 
                      className="border-2 border-white text-white hover:bg-white/10 px-8 py-6 text-lg group"
                      onClick={() => setVideoModalOpen(true)}
                    >
                      <Play className="mr-2 group-hover:scale-110 transition-transform" />
                      Watch Demo
                    </Button>
                  </motion.div>
                </motion.div>

                <motion.div
                  className="flex flex-wrap gap-6 text-sm"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.8 }}
                >
                  <div className="flex items-center gap-2 text-gray-400">
                    <Zap className="text-white" size={20} />
                    <span>1,234 Bugs Found Today</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-400">
                    <DollarSign className="text-white" size={20} />
                    <span>$50K Paid This Week</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-400">
                    <Users className="text-white" size={20} />
                    <span>500+ Active Hunters</span>
                  </div>
                </motion.div>
              </motion.div>
            </div>

            <motion.div
              initial={{ opacity: 0, x: 100 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="relative"
            >
              <CodeTerminal />
            </motion.div>
          </div>
        </div>

        <motion.div
          className="absolute bottom-8 left-1/2 -translate-x-1/2"
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          <ChevronDown className="w-8 h-8 text-white" />
        </motion.div>
      </section>

      {/* FEATURES SECTION */}
      <section id="features" className="relative py-20 md:py-32 overflow-hidden">
        {/* Futuristic Background */}
        <div className="absolute inset-0">
          {/* Animated grid */}
          <div className="absolute inset-0 opacity-20">
            <div className="absolute inset-0" style={{
              backgroundImage: `
                linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)
              `,
              backgroundSize: '50px 50px',
              animation: 'gridMove 20s linear infinite'
            }} />
          </div>
          
          {/* Glowing orbs */}
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-white/5 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-white/5 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
          
          {/* Scan lines */}
          <div className="absolute inset-0 opacity-10" style={{
            backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.03) 2px, rgba(255,255,255,0.03) 4px)'
          }} />
        </div>

        <div className="max-w-7xl mx-auto px-4 relative z-10">
          {/* Futuristic Header */}
          <div className="text-center mb-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="inline-block mb-4"
            >
              <div className="relative">
                <div className="absolute inset-0 bg-white/10 blur-xl rounded-full" />
                <div className="relative px-6 py-2 border border-white/20 rounded-full backdrop-blur-sm">
                  <span className="text-sm font-mono text-white/70 tracking-wider">ADVANCED CAPABILITIES</span>
                </div>
              </div>
            </motion.div>
            
            <motion.h2
              className="text-4xl md:text-6xl font-bold text-white mb-4 tracking-tight relative"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              <span className="relative">
                Powerful Features
                <div className="absolute -inset-1 bg-white/5 blur-2xl -z-10" />
              </span>
            </motion.h2>
            
            <motion.p
              className="text-lg text-white/60 max-w-2xl mx-auto leading-relaxed font-light"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              Next-generation security platform with AI-powered automation
            </motion.p>
          </div>

          {/* Futuristic Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: Zap,
                title: '90-Second Discovery',
                description: 'Advanced AI agents automatically scan and identify vulnerabilities in record time',
                features: [
                  'Automated vulnerability detection',
                  'Real-time threat analysis',
                  'Comprehensive security reports',
                  'Zero false positives'
                ],
                glowColor: 'rgba(255, 255, 255, 0.1)'
              },
              {
                icon: ShoppingCart,
                title: 'Bug Marketplace',
                description: 'Trade discovered vulnerabilities as assets, with NFT support and futures trading',
                features: [
                  'Buy and sell verified bugs',
                  'NFT-based ownership proof',
                  'Real-time market pricing',
                  'Secure escrow system'
                ],
                glowColor: 'rgba(255, 255, 255, 0.1)'
              },
              {
                icon: Users,
                title: 'Guild System',
                description: 'Join or create elite hunter guilds, collaborate on bounties, and compete globally',
                features: [
                  'Team-based hunting',
                  'Shared bounty rewards',
                  'Global ranking system',
                  'Exclusive guild benefits'
                ],
                glowColor: 'rgba(255, 255, 255, 0.1)'
              },
              {
                icon: BarChart3,
                title: 'Advanced Analytics',
                description: 'Track your performance, earnings, and success rates with detailed dashboards',
                features: [
                  'Real-time earning statistics',
                  'Vulnerability trend analysis',
                  'Performance benchmarking',
                  'Export detailed reports'
                ],
                glowColor: 'rgba(255, 255, 255, 0.1)'
              },
              {
                icon: Code,
                title: 'Developer-First API',
                description: 'Integrate Ikodio directly into your workflow with comprehensive API and webhooks',
                features: [
                  'RESTful API access',
                  'Webhook notifications',
                  'Multiple SDK support',
                  'Detailed documentation'
                ],
                glowColor: 'rgba(255, 255, 255, 0.1)'
              },
              {
                icon: Headphones,
                title: 'Enterprise Support',
                description: 'Dedicated security experts and round-the-clock support for critical issues',
                features: [
                  '24/7 technical support',
                  'Priority bug validation',
                  'Custom integration help',
                  'Security consultation'
                ],
                glowColor: 'rgba(255, 255, 255, 0.1)'
              }
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.08 }}
                whileHover={{ y: -8, scale: 1.02 }}
                className="group relative"
              >
                {/* Holographic border effect */}
                <div className="absolute -inset-0.5 bg-gradient-to-r from-white/0 via-white/20 to-white/0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-sm" />
                
                {/* Glow effect */}
                <div className="absolute -inset-4 opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-2xl" style={{ background: feature.glowColor }} />
                
                {/* Card */}
                <div className="relative h-full bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-8 transition-all duration-500 group-hover:bg-black/60 group-hover:border-white/30 overflow-hidden">
                  {/* Corner accents */}
                  <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-white/20 group-hover:border-white/40 transition-colors" />
                  <div className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-white/20 group-hover:border-white/40 transition-colors" />
                  <div className="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-white/20 group-hover:border-white/40 transition-colors" />
                  <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-white/20 group-hover:border-white/40 transition-colors" />
                  
                  {/* Scan line effect */}
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-b from-transparent via-white/5 to-transparent opacity-0 group-hover:opacity-100"
                    animate={{ y: ['-100%', '200%'] }}
                    transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                  />

                  {/* Icon with holographic effect */}
                  <div className="relative mb-6">
                    <div className="absolute inset-0 bg-white/20 blur-xl rounded-xl transform group-hover:scale-150 transition-transform duration-500" />
                    <div className="relative inline-flex items-center justify-center w-16 h-16 rounded-xl bg-white/90 shadow-lg backdrop-blur-sm group-hover:bg-white transition-all duration-300 group-hover:shadow-2xl group-hover:shadow-white/20">
                      <feature.icon className="w-8 h-8 text-black" strokeWidth={2} />
                    </div>
                    {/* Orbiting particles */}
                    <motion.div
                      className="absolute top-0 right-0 w-2 h-2 bg-white rounded-full opacity-0 group-hover:opacity-100"
                      animate={{ 
                        rotate: 360,
                        scale: [1, 1.5, 1]
                      }}
                      transition={{ 
                        rotate: { duration: 3, repeat: Infinity, ease: 'linear' },
                        scale: { duration: 1.5, repeat: Infinity }
                      }}
                    />
                  </div>

                  {/* Title with glitch effect on hover */}
                  <h3 className="text-2xl font-bold text-white mb-3 tracking-tight font-mono relative">
                    {feature.title}
                    <div className="absolute inset-0 opacity-0 group-hover:opacity-20 transition-opacity duration-300 text-white blur-sm transform translate-x-0.5">
                      {feature.title}
                    </div>
                  </h3>

                  {/* Description */}
                  <p className="text-base text-white/60 leading-relaxed mb-6 font-light">
                    {feature.description}
                  </p>

                  {/* Feature List with animated checkmarks */}
                  <ul className="space-y-2.5">
                    {feature.features.map((item, i) => (
                      <motion.li 
                        key={i} 
                        className="flex items-start gap-2.5 text-sm text-white/70"
                        initial={{ opacity: 0, x: -10 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: index * 0.08 + i * 0.05 }}
                      >
                        <div className="relative mt-0.5">
                          <Check className="w-4 h-4 text-white flex-shrink-0 relative z-10" strokeWidth={3} />
                          <div className="absolute inset-0 bg-white/30 blur-md" />
                        </div>
                        <span className="font-light">{item}</span>
                      </motion.li>
                    ))}
                  </ul>

                  {/* Data stream effect at bottom */}
                  <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent transform scale-x-0 group-hover:scale-x-100 transition-transform duration-500" />
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        <style jsx>{`
          @keyframes gridMove {
            0% { transform: translateY(0); }
            100% { transform: translateY(50px); }
          }
        `}</style>
      </section>

      {/* HOW IT WORKS SECTION */}
      <section id="how-it-works" className="py-20 px-4 bg-gradient-to-b from-gray-900 to-black">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-white">
              How Ikodio Works
            </h2>
            <p className="text-gray-400 text-lg">Your journey from scan to reward in 5 simple steps</p>
          </motion.div>

          <div className="space-y-12">
            {[
              { icon: Upload, title: 'Submit Your Target', description: 'Upload URL or API endpoint for security analysis', delay: 0 },
              { icon: Brain, title: 'AI Analysis', description: 'AI agents scan your target in just 90 seconds', delay: 0.2 },
              { icon: FileText, title: 'Get Results', description: 'Receive comprehensive vulnerability reports instantly', delay: 0.4 },
              { icon: RefreshCw, title: 'Trade or Report', description: 'Sell bugs in marketplace or report directly to companies', delay: 0.6 },
              { icon: Trophy, title: 'Earn Rewards', description: 'Get paid bounties and profit from your discoveries', delay: 0.8 }
            ].map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: step.delay }}
                className="flex flex-col md:flex-row items-center gap-8 group"
              >
                <div className="flex-shrink-0 w-16 h-16 rounded-full bg-white flex items-center justify-center text-2xl font-bold shadow-lg shadow-white/30 group-hover:scale-110 transition-transform text-black">
                  {index + 1}
                </div>
                
                <motion.div 
                  className="flex-1 bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-xl p-6 rounded-xl border border-gray-700 group-hover:border-white/50 transition-all"
                  whileHover={{ scale: 1.02 }}
                >
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-lg bg-white/20 flex items-center justify-center">
                      <step.icon className="text-white" size={24} />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-2xl font-bold mb-2 text-white">{step.title}</h3>
                      <p className="text-gray-400">{step.description}</p>
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* STATISTICS SECTION */}
      <section className="py-20 px-4 bg-gradient-to-br from-gray-900 via-black to-gray-900 relative overflow-hidden">

        <div className="max-w-7xl mx-auto relative z-10">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {/* Bugs Found */}
            <motion.div
              initial={{ opacity: 0, scale: 0.5 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0 }}
              className="text-center group"
            >
              <motion.div 
                className="inline-block mb-4 p-4 rounded-full bg-white/20"
                whileHover={{ scale: 1.1, rotate: 360 }}
                transition={{ duration: 0.5 }}
              >
                <TrendingUp className="text-white" size={32} />
              </motion.div>
              <div className="text-4xl md:text-5xl font-bold mb-2 text-white">
                <Counter end={10000} />
              </div>
              <div className="text-gray-400 text-lg">Bugs Found</div>
            </motion.div>

            {/* Active Hunters */}
            <motion.div
              initial={{ opacity: 0, scale: 0.5 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="text-center group"
            >
              <motion.div 
                className="inline-block mb-4 p-4 rounded-full bg-white/20"
                whileHover={{ scale: 1.1, rotate: 360 }}
                transition={{ duration: 0.5 }}
              >
                <Users className="text-white" size={32} />
              </motion.div>
              <div className="text-4xl md:text-5xl font-bold mb-2 text-white">
                <Counter end={500} />
              </div>
              <div className="text-gray-400 text-lg">Active Hunters</div>
            </motion.div>

            {/* Success Rate */}
            <motion.div
              initial={{ opacity: 0, scale: 0.5 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="text-center group"
            >
              <motion.div 
                className="inline-block mb-4 p-4 rounded-full bg-white/20"
                whileHover={{ scale: 1.1, rotate: 360 }}
                transition={{ duration: 0.5 }}
              >
                <Shield className="text-white" size={32} />
              </motion.div>
              <div className="text-4xl md:text-5xl font-bold mb-2 text-white">
                <Counter end={95} />%
              </div>
              <div className="text-gray-400 text-lg">Success Rate</div>
            </motion.div>

            {/* Paid in Bounties */}
            <motion.div
              initial={{ opacity: 0, scale: 0.5 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="text-center group"
            >
              <motion.div 
                className="inline-block mb-4 p-4 rounded-full bg-white/20"
                whileHover={{ scale: 1.1, rotate: 360 }}
                transition={{ duration: 0.5 }}
              >
                <DollarSign className="text-white" size={32} />
              </motion.div>
              <div className="text-4xl md:text-5xl font-bold mb-2 text-white">
                $<Counter end={2000000} />
              </div>
              <div className="text-gray-400 text-lg">Paid in Bounties</div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA SECTION */}
      <section className="py-24 px-4 relative overflow-hidden">
        <ParticleBackground />
        
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white">
              Ready to Start Bug Hunting?
            </h2>
            <p className="text-xl text-gray-300 mb-8">Join thousands of security researchers earning rewards</p>
            
            <Link href="/dashboard">
              <motion.div 
                whileHover={{ scale: 1.05, boxShadow: '0 0 50px rgba(255, 255, 255, 0.3)' }} 
                whileTap={{ scale: 0.95 }}
                className="inline-block"
              >
                <Button size="lg" className="bg-white hover:bg-gray-200 text-black px-12 py-6 text-lg font-semibold group">
                  Get Started Now
                  <ArrowRight className="ml-2 group-hover:translate-x-2 transition-transform" />
                </Button>
              </motion.div>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="bg-black border-t border-gray-800 py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
            <div>
              <div className="text-2xl font-bold mb-4 text-white">
                Ikodio
              </div>
              <p className="text-gray-400 mb-4">AI-powered bug bounty platform revolutionizing security research.</p>
              <div className="flex space-x-4">
                {[Github, Twitter, Linkedin].map((Icon, i) => (
                  <motion.a
                    key={i}
                    href="#"
                    whileHover={{ scale: 1.2, y: -5 }}
                    className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center hover:bg-white hover:text-black transition-all"
                  >
                    <Icon size={20} />
                  </motion.a>
                ))}
              </div>
            </div>

            {[
              {
                title: 'Product',
                links: [
                  { name: 'Features', action: () => scrollToSection('features') },
                  { name: 'Marketplace', href: '/marketplace' },
                  { name: 'Guilds', href: '/guilds' },
                  { name: 'Pricing', action: () => setPricingModalOpen(true) },
                  { name: 'Documentation', href: '/documentation' }
                ]
              },
              {
                title: 'Resources',
                links: [
                  { name: 'Blog', href: '/dashboard' },
                  { name: 'Help Center', href: '/dashboard' },
                  { name: 'API Docs', href: '/documentation' },
                  { name: 'Security', href: '/dashboard' },
                  { name: 'Status', href: '/dashboard' }
                ]
              },
              {
                title: 'Company',
                links: [
                  { name: 'About Us', href: '/about' },
                  { name: 'Careers', href: '/dashboard' },
                  { name: 'Contact', href: '/contact' },
                  { name: 'Terms', href: '/dashboard' },
                  { name: 'Privacy', href: '/dashboard' }
                ]
              }
            ].map((column, index) => (
              <div key={index}>
                <h3 className="text-white font-semibold mb-4">{column.title}</h3>
                <ul className="space-y-2">
                  {column.links.map((link) => (
                    <li key={link.name}>
                      {link.href ? (
                        <Link href={link.href}>
                          <motion.span
                            whileHover={{ x: 5 }}
                            className="text-gray-400 hover:text-white transition-colors inline-block cursor-pointer"
                          >
                            {link.name}
                          </motion.span>
                        </Link>
                      ) : (
                        <motion.button
                          onClick={link.action}
                          whileHover={{ x: 5 }}
                          className="text-gray-400 hover:text-white transition-colors inline-block text-left"
                        >
                          {link.name}
                        </motion.button>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="pt-8 border-t border-gray-800 text-center text-gray-400">
            <p>© 2025 Ikodio. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Modals */}
      <PricingModal isOpen={pricingModalOpen} onClose={() => setPricingModalOpen(false)} />
      <VideoModal isOpen={videoModalOpen} onClose={() => setVideoModalOpen(false)} />
    </div>
  );
}
