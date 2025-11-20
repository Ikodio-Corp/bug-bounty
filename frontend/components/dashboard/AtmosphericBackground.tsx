"use client";

import { useEffect, useRef } from 'react';
import gsap from 'gsap';

export function AtmosphericBackground() {
  const orb1Ref = useRef<HTMLDivElement>(null);
  const orb2Ref = useRef<HTMLDivElement>(null);
  const orb3Ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Animate gradient orbs slowly
    if (orb1Ref.current) {
      gsap.to(orb1Ref.current, {
        x: 100,
        y: 50,
        duration: 60,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut'
      });
    }

    if (orb2Ref.current) {
      gsap.to(orb2Ref.current, {
        x: -80,
        y: 80,
        duration: 45,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut'
      });
    }

    if (orb3Ref.current) {
      gsap.to(orb3Ref.current, {
        x: 60,
        y: -40,
        duration: 50,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut'
      });
    }

    // Parallax on scroll
    const handleScroll = () => {
      const scrollY = window.scrollY;
      if (orb1Ref.current) {
        gsap.to(orb1Ref.current, {
          y: scrollY * 0.1,
          duration: 0.5,
          ease: 'power2.out'
        });
      }
      if (orb2Ref.current) {
        gsap.to(orb2Ref.current, {
          y: scrollY * -0.08,
          duration: 0.5,
          ease: 'power2.out'
        });
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden">
      {/* Layer 1: Base Gradient */}
      <div 
        className="absolute inset-0"
        style={{
          background: 'radial-gradient(ellipse at top left, #0a0e27 0%, #020617 50%, #0f172a 100%)'
        }}
      />

      {/* Layer 2: Noise Texture */}
      <div 
        className="absolute inset-0 opacity-[0.02]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
          backgroundRepeat: 'repeat',
        }}
      />

      {/* Layer 3: Abstract Network Visualization */}
      <div className="absolute -top-[10%] -right-[5%] w-[800px] h-[800px] opacity-[0.03] blur-sm">
        <svg viewBox="0 0 800 800" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
          <defs>
            <radialGradient id="nodeGrad">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
            </radialGradient>
          </defs>
          {/* Abstract network nodes and connections */}
          <circle cx="200" cy="150" r="80" fill="url(#nodeGrad)" />
          <circle cx="600" cy="200" r="100" fill="url(#nodeGrad)" />
          <circle cx="400" cy="500" r="120" fill="url(#nodeGrad)" />
          <circle cx="650" cy="600" r="90" fill="url(#nodeGrad)" />
          <line x1="200" y1="150" x2="600" y2="200" stroke="#3b82f6" strokeWidth="1" opacity="0.1" />
          <line x1="600" y1="200" x2="400" y2="500" stroke="#8b5cf6" strokeWidth="1" opacity="0.1" />
          <line x1="400" y1="500" x2="650" y2="600" stroke="#0891b2" strokeWidth="1" opacity="0.1" />
          <line x1="200" y1="150" x2="400" y2="500" stroke="#3b82f6" strokeWidth="1" opacity="0.05" />
        </svg>
      </div>

      {/* Layer 4: Gradient Orbs */}
      <div
        ref={orb1Ref}
        className="orb absolute top-[10%] right-[15%] w-[400px] h-[400px] rounded-full opacity-[0.08]"
        style={{
          background: 'radial-gradient(circle, #1e40af, transparent)',
          filter: 'blur(120px)',
        }}
      />

      <div
        ref={orb2Ref}
        className="orb absolute bottom-[20%] left-[10%] w-[500px] h-[500px] rounded-full opacity-[0.08]"
        style={{
          background: 'radial-gradient(circle, #7c3aed, transparent)',
          filter: 'blur(120px)',
        }}
      />

      <div
        ref={orb3Ref}
        className="orb absolute top-[50%] left-[50%] w-[350px] h-[350px] rounded-full opacity-[0.08]"
        style={{
          background: 'radial-gradient(circle, #0891b2, transparent)',
          filter: 'blur(120px)',
        }}
      />

      {/* Layer 5: Scan Line Effect */}
      <div 
        className="absolute inset-0 opacity-[0.02]"
        style={{
          background: 'linear-gradient(to bottom, transparent 0%, rgba(59, 130, 246, 0.1) 50%, transparent 100%)',
          animation: 'scanline 8s linear infinite',
          pointerEvents: 'none',
        }}
      />

      <style jsx>{`
        @keyframes scanline {
          0% {
            transform: translateY(-100%);
          }
          100% {
            transform: translateY(100%);
          }
        }
      `}</style>
    </div>
  );
}
