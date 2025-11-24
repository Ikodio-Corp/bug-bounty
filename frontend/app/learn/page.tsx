"use client";

import { Sidebar } from '@/components/dashboard/Sidebar';
import { AtmosphericBackground } from '@/components/dashboard/AtmosphericBackground';
import { BookOpen, Video, FileText, Award, Clock } from 'lucide-react';

export default function LearnPage() {
  const courses = [
    { title: 'Web Application Security Fundamentals', lessons: 12, duration: '4h', level: 'Beginner', icon: '🔐' },
    { title: 'Advanced XSS Exploitation', lessons: 8, duration: '2.5h', level: 'Advanced', icon: '⚡' },
    { title: 'SQL Injection Mastery', lessons: 10, duration: '3h', level: 'Intermediate', icon: '💉' },
    { title: 'API Security Testing', lessons: 15, duration: '5h', level: 'Intermediate', icon: '🔌' },
    { title: 'Mobile App Penetration Testing', lessons: 14, duration: '6h', level: 'Advanced', icon: '📱' },
    { title: 'Bug Bounty Methodology', lessons: 9, duration: '3.5h', level: 'Beginner', icon: '🎯' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      <AtmosphericBackground />
      <Sidebar />
      
      <div className="lg:ml-64 min-h-screen">
        <div className="relative z-10 p-10">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Learning Hub</h1>
            <p className="text-slate-400">Educational resources and tutorials</p>
          </div>

          {/* Stats */}
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            {[
              { icon: BookOpen, label: 'Courses', value: '24', color: 'blue' },
              { icon: Video, label: 'Videos', value: '156', color: 'purple' },
              { icon: FileText, label: 'Articles', value: '89', color: 'green' },
              { icon: Award, label: 'Certificates', value: '12', color: 'yellow' },
            ].map((stat) => (
              <div key={stat.label} className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
                <stat.icon className={`text-${stat.color}-400 mb-3`} size={28} />
                <div className="text-3xl font-bold text-white mb-1">{stat.value}</div>
                <div className="text-slate-400 text-sm">{stat.label}</div>
              </div>
            ))}
          </div>

          {/* Courses Grid */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <h2 className="text-xl font-bold text-white mb-6">Popular Courses</h2>
            <div className="grid md:grid-cols-2 gap-6">
              {courses.map((course, i) => (
                <div key={i} className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6 hover:border-purple-500/50 transition">
                  <div className="flex items-start gap-4 mb-4">
                    <div className="text-4xl">{course.icon}</div>
                    <div className="flex-1">
                      <h3 className="text-white font-bold mb-2">{course.title}</h3>
                      <div className="flex items-center gap-4 text-sm text-slate-400">
                        <span className="flex items-center gap-1">
                          <BookOpen size={14} />
                          {course.lessons} lessons
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock size={14} />
                          {course.duration}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className={`px-3 py-1 rounded-full text-sm ${
                      course.level === 'Beginner' ? 'bg-green-600/20 text-green-400' :
                      course.level === 'Intermediate' ? 'bg-blue-600/20 text-blue-400' :
                      'bg-purple-600/20 text-purple-400'
                    }`}>{course.level}</span>
                    <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-white text-sm font-medium transition">
                      Start Learning
                    </button>
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
