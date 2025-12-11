'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { SimpleCard, SimpleCardHeader, SimpleCardTitle, SimpleCardDescription, SimpleCardContent } from '@/components/ui/simple-card'
import { SimpleBadge } from '@/components/ui/simple-badge'
import api from '@/lib/api'

interface Course {
  id: number
  title: string
  description: string
  level: string
  duration: string
  modules: number
  enrolled: number
  rating: number
}

export default function UniversityPage() {
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetchCourses()
  }, [filter])

  const fetchCourses = async () => {
    try {
      setLoading(true)
      const mockCourses: Course[] = [
        {
          id: 1,
          title: 'Web Application Security Fundamentals',
          description: 'Learn the basics of web application security, including OWASP Top 10 vulnerabilities and secure coding practices.',
          level: 'beginner',
          duration: '6 weeks',
          modules: 12,
          enrolled: 1250,
          rating: 4.8
        },
        {
          id: 2,
          title: 'Advanced SQL Injection Techniques',
          description: 'Master advanced SQL injection methods, bypass techniques, and automated exploitation tools.',
          level: 'advanced',
          duration: '4 weeks',
          modules: 8,
          enrolled: 680,
          rating: 4.9
        },
        {
          id: 3,
          title: 'API Security Testing',
          description: 'Comprehensive guide to testing REST and GraphQL APIs for security vulnerabilities.',
          level: 'intermediate',
          duration: '5 weeks',
          modules: 10,
          enrolled: 920,
          rating: 4.7
        },
        {
          id: 4,
          title: 'Bug Bounty Hunter Bootcamp',
          description: 'Complete bootcamp covering reconnaissance, exploitation, and reporting for bug bounty programs.',
          level: 'beginner',
          duration: '8 weeks',
          modules: 16,
          enrolled: 2100,
          rating: 4.9
        },
        {
          id: 5,
          title: 'Mobile Application Security',
          description: 'Learn to find and exploit vulnerabilities in iOS and Android applications.',
          level: 'intermediate',
          duration: '6 weeks',
          modules: 12,
          enrolled: 540,
          rating: 4.6
        },
        {
          id: 6,
          title: 'Cloud Security Assessment',
          description: 'Assess security of AWS, Azure, and GCP infrastructure and identify misconfigurations.',
          level: 'advanced',
          duration: '7 weeks',
          modules: 14,
          enrolled: 430,
          rating: 4.8
        }
      ]

      if (filter !== 'all') {
        setCourses(mockCourses.filter(c => c.level === filter))
      } else {
        setCourses(mockCourses)
      }
    } catch (error) {
      console.error('Failed to fetch courses:', error)
    } finally {
      setLoading(false)
    }
  }

  const getLevelColor = (level: string) => {
    const colors: { [key: string]: string } = {
      beginner: 'success',
      intermediate: 'warning',
      advanced: 'error'
    }
    return colors[level] || 'default'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <Link href="/dashboard">
            <button className="text-slate-400 hover:text-white mb-2 flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Dashboard
            </button>
          </Link>
          <h1 className="text-4xl font-bold text-white mb-2">Security University</h1>
          <p className="text-slate-400">Learn from industry experts and level up your skills</p>
        </div>

        <div className="bg-slate-800 rounded-xl p-6 mb-8">
          <div className="flex gap-4 overflow-x-auto">
            {['all', 'beginner', 'intermediate', 'advanced'].map(level => (
              <button
                key={level}
                onClick={() => setFilter(level)}
                className={`px-6 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                  filter === level
                    ? 'bg-cyan-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                {level.charAt(0).toUpperCase() + level.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="text-center text-slate-400 py-12">Loading courses...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.map(course => (
              <SimpleCard key={course.id} className="hover:border-cyan-500 transition-colors cursor-pointer">
                <SimpleCardHeader>
                  <div className="flex items-start justify-between mb-2">
                    <SimpleBadge variant={getLevelColor(course.level) as any}>
                      {course.level}
                    </SimpleBadge>
                    <div className="flex items-center text-yellow-400">
                      <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                      {course.rating}
                    </div>
                  </div>
                  <SimpleCardTitle className="text-xl">{course.title}</SimpleCardTitle>
                  <SimpleCardDescription>{course.description}</SimpleCardDescription>
                </SimpleCardHeader>
                <SimpleCardContent>
                  <div className="space-y-3">
                    <div className="flex items-center text-slate-400 text-sm">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {course.duration}
                    </div>
                    <div className="flex items-center text-slate-400 text-sm">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                      </svg>
                      {course.modules} modules
                    </div>
                    <div className="flex items-center text-slate-400 text-sm">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                      {course.enrolled.toLocaleString()} enrolled
                    </div>
                  </div>
                  <button className="w-full mt-4 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white font-semibold transition-colors">
                    Enroll Now
                  </button>
                </SimpleCardContent>
              </SimpleCard>
            ))}
          </div>
        )}

        <div className="mt-12 bg-gradient-to-r from-gray-500 to-gray-600 rounded-xl p-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-white mb-4">Ready to Become an Expert?</h2>
            <p className="text-white/90 mb-6 max-w-2xl mx-auto">
              Join thousands of security researchers learning cutting-edge techniques and earning certifications recognized by the industry.
            </p>
            <button className="px-8 py-3 bg-white text-cyan-600 rounded-lg font-semibold hover:bg-slate-100 transition-colors">
              View All Courses
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
