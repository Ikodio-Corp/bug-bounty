"use client";

import { useEffect, useRef } from "react";
import gsap from 'gsap';
import { Sidebar } from '@/components/dashboard/Sidebar';
import { AtmosphericBackground } from '@/components/dashboard/AtmosphericBackground';
import { TopStatsBar } from '@/components/dashboard/TopStatsBar';
import { RefinedMetricsGrid } from '@/components/dashboard/RefinedMetricsGrid';
import { RefinedActiveScans } from '@/components/dashboard/RefinedActiveScans';
import { PerformanceChart, VulnerabilityDistribution } from '@/components/dashboard/Charts';
import { RefinedLiveActivity } from '@/components/dashboard/RefinedLiveActivity';
import { RefinedQuickActions } from '@/components/dashboard/RefinedQuickActions';

export default function DashboardPage() {
  const mainRef = useRef<HTMLDivElement>(null);
  const statsRef = useRef<HTMLDivElement>(null);
  const metricsRef = useRef<HTMLDivElement>(null);
  const scansRef = useRef<HTMLDivElement>(null);
  const chartsRef = useRef<HTMLDivElement>(null);
  const activityRef = useRef<HTMLDivElement>(null);
  const actionsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Create GSAP timeline for orchestrated page load animation
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

      // Phase 1: Stats bar slides down
      tl.from(statsRef.current, {
        y: -100,
        opacity: 0,
        duration: 0.8,
      });

      // Phase 2: Metric cards stagger in
      tl.from(
        '.metric-card',
        {
          y: 60,
          opacity: 0,
          stagger: 0.08,
          duration: 0.6,
        },
        '-=0.4'
      );

      // Phase 3: Scans section from left
      tl.from(
        scansRef.current,
        {
          x: -40,
          opacity: 0,
          duration: 0.6,
        },
        '-=0.3'
      );

      // Phase 4: Charts section from right
      tl.from(
        chartsRef.current,
        {
          x: 40,
          opacity: 0,
          duration: 0.6,
        },
        '-=0.5'
      );

      // Phase 5: Activity and actions cascade
      tl.from(
        [activityRef.current, actionsRef.current],
        {
          y: 40,
          opacity: 0,
          stagger: 0.15,
          duration: 0.6,
        },
        '-=0.4'
      );
    }, mainRef);

    return () => ctx.revert();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      <AtmosphericBackground />
      <Sidebar />
      
      <div className="lg:ml-64 min-h-screen">
        <div ref={mainRef} className="relative z-10 min-h-screen">
          <div ref={statsRef}>
            <TopStatsBar />
          </div>
          
          <main className="py-6 px-6">
            <div ref={metricsRef} className="mb-6">
              <RefinedMetricsGrid />
            </div>
            
            <div ref={scansRef} className="mb-6">
              <RefinedActiveScans />
            </div>
            
            <div ref={chartsRef} className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
              <PerformanceChart />
              <VulnerabilityDistribution />
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-[1fr_400px] gap-4 pb-6">
              <div ref={activityRef}>
                <RefinedLiveActivity />
              </div>
              <div ref={actionsRef}>
                <RefinedQuickActions />
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
