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
import { useRouter } from 'next/navigation';
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
    { text: '$ ikodio scan --target example.com', color: 'text-gray-300' },
    { text: 'AI agents initialized', color: 'text-green-400' },
    { text: 'Scanning for vulnerabilities...', color: 'text-yellow-400' },
    { text: 'Found 3 critical bugs in 90 seconds!', color: 'text-green-400' },
    { text: '$ Reward: $5,000', color: 'text-gray-300' },
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
          className={line.color}
        >
          {line.text}
        </motion.div>
      ))})
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
  const router = useRouter();
  
  if (!isOpen) return null;

  const handleSelectPlan = (planName: string) => {
    if (planName === 'Enterprise') {
      router.push('/enterprise-inquiry');
    } else {
      const tier = planName.toLowerCase();
      router.push(`/auth/register?tier=${tier}&redirect=payment`);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex items-center justify-center p-8" onClick={onClose}>
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-black border border-white/20 rounded-2xl w-full max-w-7xl h-[90vh] flex flex-col overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header - Fixed */}
        <div className="flex justify-between items-center px-8 py-5 border-b border-white/10 flex-shrink-0">
          <div>
            <h2 className="text-3xl font-bold text-white">Pricing Plans</h2>
            <p className="text-gray-400 text-sm mt-1">Pilih paket yang sesuai dengan kebutuhan Anda</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
            <X size={28} />
          </button>
        </div>

        {/* Pricing Cards - Scrollable if needed */}
        <div className="flex-1 grid grid-cols-4 divide-x divide-white/10 min-h-0">
          {[
            { 
              name: 'Free', 
              price: 'Rp 0',
              period: '/bulan',
              features: [
                '5 scan per bulan', 
                'Scanner dasar (Nuclei)', 
                'Report PDF standar',
                'Community support',
                'Max 2 target domain',
                'Basic vulnerability detection'
              ] 
            },
            { 
              name: 'Starter', 
              price: 'Rp 199K',
              period: '/bulan',
              features: [
                '25 scan per bulan', 
                'Scanner: Nuclei + ZAP', 
                'Report PDF + HTML',
                'Email support (24h response)',
                'Max 5 target domain',
                'Basic vulnerability detection',
                'Email notifications',
                'Scan history (30 hari)'
              ] 
            },
            { 
              name: 'Professional', 
              price: 'Rp 450K',
              period: '/bulan',
              features: [
                '100 scan per bulan', 
                'AI Scanner + semua tools',
                'Priority support 24/7',
                'API access & webhooks', 
                'Custom report template',
                'Guild & marketplace access',
                'Advanced analytics dashboard',
                'Unlimited target domain',
                'Scheduled scans',
                'Real-time alerts',
                'Integration Slack/Discord',
                'Export data (JSON, CSV, XML)',
                'Scan history (unlimited)',
                'Team collaboration (5 users)'
              ], 
              highlight: true 
            },
            { 
              name: 'Enterprise', 
              price: 'Custom',
              period: '',
              features: [
                'Unlimited scans', 
                'Dedicated security expert',
                'Custom AI model training',
                'White-label solution',
                'SLA 99.9% uptime',
                'On-premise deployment option',
                'Team collaboration (unlimited)',
                'Compliance reports (ISO, PCI-DSS)',
                'Custom integrations',
                'Dedicated account manager',
                'Training & onboarding',
                'Custom security policies',
                'Advanced threat intelligence',
                'Multi-region deployment',
                'SSO & LDAP integration',
                'Custom contract & billing'
              ] 
            }
          ].map((plan, i) => (
            <div
              key={i}
              className={`flex flex-col p-6 min-h-0 ${
                plan.highlight ? 'bg-gradient-to-b from-white/5 to-black' : 'bg-black'
              }`}
            >
              <div className="flex-1 overflow-y-auto min-h-0 pr-2">
                {plan.highlight && (
                  <div className="inline-block self-start px-3 py-1 bg-white text-black text-xs font-bold rounded-full mb-4">
                    POPULAR
                  </div>
                )}
                
                <h3 className="text-2xl font-bold text-white mb-6">{plan.name}</h3>
                
                <div className="mb-6">
                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-bold text-white">{plan.price}</span>
                    {plan.period && <span className="text-gray-500 text-xs">{plan.period}</span>}
                  </div>
                </div>
                
                <ul className="space-y-2.5 pb-4">
                  {plan.features.map((feature, j) => (
                    <li key={j} className="flex items-start gap-2 text-gray-400 text-xs">
                      <span className="text-white mt-0.5 text-sm"></span>
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className="flex-shrink-0 pt-4 border-t border-white/10">
                <button 
                  onClick={() => handleSelectPlan(plan.name)}
                  className={`w-full py-3 text-sm font-semibold transition-all rounded-lg ${
                    plan.highlight 
                      ? 'bg-white text-black hover:bg-gray-200' 
                      : 'bg-white/10 text-white hover:bg-white/20 border border-white/20'
                  }`}
                >
                  {plan.name === 'Enterprise' ? 'Hubungi Sales' : 'Mulai Sekarang'}
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Footer - Fixed */}
        <div className="px-8 py-4 border-t border-white/10 text-center flex-shrink-0">
          <p className="text-gray-500 text-xs">
            Semua paket termasuk SSL gratis & backup harian • <a href="mailto:support@ikodio.com" className="text-white underline">Hubungi kami</a>
          </p>
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
                  <motion.div whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(255, 255, 255, 0.3)" }} whileTap={{ scale: 0.95 }}>
                    <Button size="lg" className="bg-white hover:bg-gray-200 text-black px-8 py-6 text-lg group" onClick={() => setPricingModalOpen(true)}>
                      Get Started
                      <ArrowRight className="ml-2 group-hover:translate-x-1 transition-transform" />
                    </Button>
                  </motion.div>
                  
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
      <section id="features" className="relative py-20 md:py-32 bg-gradient-to-b from-black via-gray-900 to-black overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {/* Grid Pattern */}
          <div className="absolute inset-0 opacity-20">
            <div className="absolute inset-0" style={{
              backgroundImage: 'linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)',
              backgroundSize: '50px 50px',
            }} />
          </div>
          
          {/* Moving Code Lines - More visible and abundant */}
          {[
            'SELECT * FROM vulnerabilities WHERE severity="critical"',
            'const scanTarget = await AI.analyze(url)',
            'if (threat.level > 8) { alert("High Risk Detected") }',
            'POST /api/scan {target: "example.com", deep: true}',
            'function detectXSS(input) { return sanitize(input) }',
            'query { bugs { id severity status bounty } }',
            'npm install @ikodio/security-scanner',
            'docker run -p 8080:8080 ikodio/scanner',
            'git commit -m "Fix: SQL injection vulnerability"',
            'axios.post("/validate", {token, signature})',
            'async function verifyAuth() { return jwt.verify(token) }',
            'UPDATE reports SET status="fixed" WHERE id=123',
            'const risk = calculateScore(cve, cvss)',
            'import { Scanner } from "@ikodio/core"',
            'while(scanning) { progress.update(percent) }',
            'app.get("/api/bugs", authenticate, getBugs)',
            'const payload = jwt.sign({id: user.id}, SECRET)',
            'db.query("INSERT INTO scans VALUES (?, ?)")',
            'for(let bug of criticalBugs) { notify(bug) }',
            'response.json({ success: true, data: results })',
            'const encrypted = crypto.encrypt(password, key)',
            'if(validated) { await processPayment(amount) }',
            'fetch("/api/analyze", {method: "POST", body})',
            'class VulnerabilityScanner extends BaseScanner',
            'return vulnerabilities.filter(v => v.cvss > 7)',
            'mongoose.model("Bug", bugSchema)',
            'redis.set("scan:123", JSON.stringify(data))',
            'const result = await validateInput(req.body)',
            'socket.emit("scan-complete", {id, findings})',
            'Authorization: Bearer eyJhbGciOiJIUzI1NiIs...',
          ].map((code, i) => (
            <motion.div
              key={`code-${i}`}
              className="absolute font-mono text-xs text-green-400/20 whitespace-nowrap"
              initial={{ x: -500, opacity: 0 }}
              animate={{
                x: ['-100%', '100vw'],
                opacity: [0, 0.5, 0.5, 0],
              }}
              transition={{
                duration: 20 + (i % 5) * 3,
                repeat: Infinity,
                delay: i * 0.8,
                ease: "linear",
              }}
              style={{
                top: `${5 + (i * 3.2) % 90}%`,
              }}
            >
              {code}
            </motion.div>
          ))}
          
          {/* Additional code snippets with different colors */}
          {[
            'ERROR: Connection timeout to target server',
            'SUCCESS: 15 vulnerabilities found in 87 seconds',
            'WARNING: Potential SQL injection detected',
            'INFO: Starting deep scan on 47 endpoints',
            'CRITICAL: Remote code execution vulnerability',
            'DEBUG: Checking CORS policy configuration',
            'ALERT: Suspicious activity detected in logs',
            'COMPLETE: Report generated successfully',
          ].map((log, i) => (
            <motion.div
              key={`log-${i}`}
              className={`absolute font-mono text-xs whitespace-nowrap ${
                log.includes('ERROR') || log.includes('CRITICAL') ? 'text-red-400/20' :
                log.includes('SUCCESS') || log.includes('COMPLETE') ? 'text-green-400/20' :
                log.includes('WARNING') || log.includes('ALERT') ? 'text-yellow-400/20' :
                'text-gray-400/20'
              }`}
              initial={{ x: '100vw', opacity: 0 }}
              animate={{
                x: ['100vw', '-100%'],
                opacity: [0, 0.6, 0.6, 0],
              }}
              transition={{
                duration: 18 + (i % 4) * 2,
                repeat: Infinity,
                delay: i * 1.2,
                ease: "linear",
              }}
              style={{
                top: `${10 + (i * 11) % 80}%`,
              }}
            >
              {log}
            </motion.div>
          ))}
          
          {/* Moving Lines */}
          <motion.div
            className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white to-transparent"
            animate={{
              y: [0, 800],
              opacity: [0, 0.3, 0],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "linear",
            }}
          />
          <motion.div
            className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white to-transparent"
            animate={{
              y: [0, 800],
              opacity: [0, 0.3, 0],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "linear",
              delay: 1.5,
            }}
          />
          
          {/* Floating Particles */}
          {[...Array(30)].map((_, i) => (
            <motion.div
              key={`particle-${i}`}
              className="absolute w-1 h-1 bg-white rounded-full"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
              }}
              animate={{
                y: [0, -30, 0],
                opacity: [0.1, 0.4, 0.1],
              }}
              transition={{
                duration: 3 + Math.random() * 2,
                repeat: Infinity,
                delay: Math.random() * 2,
              }}
            />
          ))}
          
          {/* Pulse Circles */}
          <motion.div
            className="absolute top-1/4 left-1/4 w-64 h-64 rounded-full bg-white"
            animate={{
              scale: [1, 2, 1],
              opacity: [0.05, 0, 0.05],
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
          <motion.div
            className="absolute bottom-1/4 right-1/4 w-64 h-64 rounded-full bg-white"
            animate={{
              scale: [1, 2, 1],
              opacity: [0.05, 0, 0.05],
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 2,
            }}
          />
        </div>

        <div className="max-w-7xl mx-auto px-4 relative z-10">
          {/* Header */}
          <div className="text-center mb-16">
            <div className="inline-block mb-4 px-3 py-1 border border-white/10 rounded-md bg-white/5 backdrop-blur-sm">
              <span className="text-xs font-medium text-white/60 tracking-wider uppercase">Advanced Capabilities</span>
            </div>
            
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Powerful Features
            </h2>
            
            <p className="text-lg text-gray-400 max-w-2xl mx-auto">
              Next-generation security platform with AI-powered automation
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-px bg-white/5">
            {[
              {
                title: '90-Second Discovery',
                description: 'Advanced AI agents automatically scan and identify vulnerabilities in record time',
                features: [
                  'Automated vulnerability detection',
                  'Real-time threat analysis',
                  'Comprehensive security reports',
                  'Zero false positives'
                ]
              },
              {
                title: 'Bug Marketplace',
                description: 'Trade discovered vulnerabilities as assets, with NFT support and futures trading',
                features: [
                  'Buy and sell verified bugs',
                  'NFT-based ownership proof',
                  'Real-time market pricing',
                  'Secure escrow system'
                ]
              },
              {
                title: 'Guild System',
                description: 'Join or create elite hunter guilds, collaborate on bounties, and compete globally',
                features: [
                  'Team-based hunting',
                  'Shared bounty rewards',
                  'Global ranking system',
                  'Exclusive guild benefits'
                ]
              },
              {
                title: 'Advanced Analytics',
                description: 'Track your performance, earnings, and success rates with detailed dashboards',
                features: [
                  'Real-time earning statistics',
                  'Vulnerability trend analysis',
                  'Performance benchmarking',
                  'Export detailed reports'
                ]
              },
              {
                title: 'Developer-First API',
                description: 'Integrate Ikodio directly into your workflow with comprehensive API and webhooks',
                features: [
                  'RESTful API access',
                  'Webhook notifications',
                  'Multiple SDK support',
                  'Detailed documentation'
                ]
              },
              {
                title: 'Enterprise Support',
                description: 'Dedicated security experts and round-the-clock support for critical issues',
                features: [
                  '24/7 technical support',
                  'Priority bug validation',
                  'Custom integration help',
                  'Security consultation'
                ]
              }
            ].map((feature, index) => (
              <div
                key={index}
                className="bg-black p-8 hover:bg-white/[0.02] transition-colors duration-200"
              >
                {/* Title */}
                <h3 className="text-xl font-semibold text-white mb-3">
                  {feature.title}
                </h3>

                {/* Description */}
                <p className="text-sm text-gray-400 leading-relaxed mb-6">
                  {feature.description}
                </p>

                {/* Feature List */}
                <ul className="space-y-2.5">
                  {feature.features.map((item, i) => (
                    <li 
                      key={i} 
                      className="flex items-start gap-2.5 text-sm text-gray-500"
                    >
                      <span className="text-white mt-0.5"></span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* HOW IT WORKS SECTION */}
      <section id="how-it-works" className="relative py-20 px-4 bg-gradient-to-b from-black via-gray-900 to-black border-t border-white/5 overflow-hidden">
        {/* Animated Background - Workflow Theme */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {/* Flowchart Lines */}
          <svg className="absolute inset-0 w-full h-full opacity-10" style={{ strokeDasharray: '10 5' }}>
            <motion.path
              d="M 100 50 L 300 50 L 300 150 L 500 150"
              stroke="white"
              strokeWidth="2"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
            />
            <motion.path
              d="M 600 100 L 800 100 L 800 200 L 1000 200"
              stroke="white"
              strokeWidth="2"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 3, repeat: Infinity, delay: 0.5, ease: "linear" }}
            />
            <motion.path
              d="M 200 300 L 400 300 L 400 400 L 600 400"
              stroke="white"
              strokeWidth="2"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 3, repeat: Infinity, delay: 1, ease: "linear" }}
            />
          </svg>
          
          {/* Moving Step Numbers */}
          {[1, 2, 3, 4, 5].map((num, i) => (
            <motion.div
              key={`step-${num}`}
              className="absolute w-12 h-12 rounded-full bg-white/5 border-2 border-white/20 flex items-center justify-center text-white font-bold text-lg"
              style={{
                left: `${10 + i * 18}%`,
                top: `${20 + (i % 2) * 30}%`,
              }}
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.3, 0.6, 0.3],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: i * 0.4,
              }}
            >
              {num}
            </motion.div>
          ))}
          
          {/* Floating Arrows */}
          {[...Array(12)].map((_, i) => (
            <motion.div
              key={`arrow-${i}`}
              className="absolute text-white/10 text-2xl"
              style={{
                left: `${5 + (i * 8) % 90}%`,
                top: `${15 + (i * 7) % 70}%`,
              }}
              animate={{
                x: [0, 20, 0],
                opacity: [0.1, 0.3, 0.1],
              }}
              transition={{
                duration: 3 + (i % 3),
                repeat: Infinity,
                delay: i * 0.3,
              }}
            >
              →
            </motion.div>
          ))}
          
          {/* Journey Path Text */}
          {[
            'SCAN',
            'ANALYZE',
            'REPORT',
            'TRADE',
            'REWARD',
          ].map((text, i) => (
            <motion.div
              key={`journey-${text}`}
              className="absolute font-bold text-sm text-white/10 tracking-wider"
              style={{
                left: `${15 + i * 17}%`,
                top: `${60 + (i % 2) * 10}%`,
              }}
              animate={{
                opacity: [0.1, 0.25, 0.1],
                y: [0, -10, 0],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                delay: i * 0.6,
              }}
            >
              {text}
            </motion.div>
          ))}
          
          {/* Progress Lines */}
          {[...Array(5)].map((_, i) => (
            <motion.div
              key={`progress-${i}`}
              className="absolute h-0.5 bg-gradient-to-r from-transparent via-white to-transparent"
              style={{
                left: 0,
                right: 0,
                top: `${20 + i * 15}%`,
              }}
              animate={{
                scaleX: [0, 1, 0],
                opacity: [0, 0.2, 0],
              }}
              transition={{
                duration: 4,
                repeat: Infinity,
                delay: i * 0.8,
                ease: "easeInOut",
              }}
            />
          ))}
          
          {/* Circular Progress Indicators */}
          {[...Array(8)].map((_, i) => (
            <motion.div
              key={`circle-${i}`}
              className="absolute w-3 h-3 rounded-full border-2 border-white/20"
              style={{
                left: `${10 + (i * 12) % 80}%`,
                top: `${30 + (i * 8) % 50}%`,
              }}
              animate={{
                scale: [1, 1.5, 1],
                opacity: [0.2, 0.4, 0.2],
                borderColor: ['rgba(255,255,255,0.2)', 'rgba(255,255,255,0.4)', 'rgba(255,255,255,0.2)'],
              }}
              transition={{
                duration: 2.5,
                repeat: Infinity,
                delay: i * 0.3,
              }}
            />
          ))}
          
          {/* Animated Dots Trail */}
          {[...Array(15)].map((_, i) => (
            <motion.div
              key={`dot-${i}`}
              className="absolute w-1.5 h-1.5 rounded-full bg-white"
              initial={{ x: 0, opacity: 0 }}
              animate={{
                x: [0, 1200],
                opacity: [0, 0.4, 0],
              }}
              transition={{
                duration: 5,
                repeat: Infinity,
                delay: i * 0.3,
                ease: "linear",
              }}
              style={{
                left: '-10px',
                top: `${10 + (i * 6) % 80}%`,
              }}
            />
          ))}
        </div>

        <div className="max-w-6xl mx-auto relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-white">
              How Ikodio Works
            </h2>
            <p className="text-gray-400 text-lg">Your journey from scan to reward in 5 simple steps</p>
          </div>

          <div className="space-y-0 border border-white/5">
            {[
              { title: 'Submit Your Target', description: 'Upload URL or API endpoint for security analysis' },
              { title: 'AI Analysis', description: 'AI agents scan your target in just 90 seconds' },
              { title: 'Get Results', description: 'Receive comprehensive vulnerability reports instantly' },
              { title: 'Trade or Report', description: 'Sell bugs in marketplace or report directly to companies' },
              { title: 'Earn Rewards', description: 'Get paid bounties and profit from your discoveries' }
            ].map((step, index) => (
              <div
                key={index}
                className="flex items-start gap-6 p-8 border-b border-white/5 last:border-b-0 hover:bg-white/[0.02] transition-colors"
              >
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white flex items-center justify-center text-sm font-semibold text-black">
                  {index + 1}
                </div>
                
                <div className="flex-1">
                  <h3 className="text-xl font-semibold mb-2 text-white">{step.title}</h3>
                  <p className="text-sm text-gray-500">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* STATISTICS SECTION */}
      <section className="py-20 px-4 bg-gradient-to-br from-gray-900 via-black to-gray-900 relative overflow-hidden">

        <div className="max-w-7xl mx-auto relative z-10">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {/* Bugs Found */}
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold mb-2 text-white">
                <Counter end={10000} />
              </div>
              <div className="text-gray-400 text-lg">Bugs Found</div>
            </div>

            {/* Active Hunters */}
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold mb-2 text-white">
                <Counter end={500} />
              </div>
              <div className="text-gray-400 text-lg">Active Hunters</div>
            </div>

            {/* Success Rate */}
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold mb-2 text-white">
                <Counter end={95} />%
              </div>
              <div className="text-gray-400 text-lg">Success Rate</div>
            </div>

            {/* Paid in Bounties */}
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold mb-2 text-white">
                $<Counter end={2000000} />
              </div>
              <div className="text-gray-400 text-lg">Paid in Bounties</div>
            </div>
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
            
            <motion.div 
              whileHover={{ scale: 1.05, boxShadow: '0 0 50px rgba(255, 255, 255, 0.3)' }} 
              whileTap={{ scale: 0.95 }}
              className="inline-block"
            >
              <Button size="lg" className="bg-white hover:bg-gray-200 text-black px-12 py-6 text-lg font-semibold group" onClick={() => setPricingModalOpen(true)}>
                Get Started Now
                <ArrowRight className="ml-2 group-hover:translate-x-2 transition-transform" />
              </Button>
            </motion.div>
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
