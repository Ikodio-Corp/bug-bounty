'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { SimpleCard, SimpleCardHeader, SimpleCardTitle, SimpleCardContent } from '@/components/ui/simple-card'
import { SimpleBadge } from '@/components/ui/simple-badge'

interface Tutorial {
  id: number
  title: string
  category: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  duration: string
  description: string
  videoUrl?: string
  steps: number
}

export default function TutorialsPage() {
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedDifficulty, setSelectedDifficulty] = useState('all')

  const tutorials: Tutorial[] = [
    {
      id: 1,
      title: 'Getting Started with Bug Bounty Hunting',
      category: 'Basics',
      difficulty: 'beginner',
      duration: '15 min',
      description: 'Learn the fundamentals of bug bounty hunting and how to get started on the IKODIO platform.',
      steps: 5
    },
    {
      id: 2,
      title: 'Setting Up Your First Scan',
      category: 'Scanning',
      difficulty: 'beginner',
      duration: '10 min',
      description: 'Step-by-step guide to configure and run your first automated security scan.',
      steps: 4
    },
    {
      id: 3,
      title: 'Advanced SQL Injection Techniques',
      category: 'Exploitation',
      difficulty: 'advanced',
      duration: '45 min',
      description: 'Deep dive into advanced SQL injection methods including blind SQLi and second-order attacks.',
      videoUrl: 'https://example.com/video3',
      steps: 8
    },
    {
      id: 4,
      title: 'Writing Effective Bug Reports',
      category: 'Reporting',
      difficulty: 'intermediate',
      duration: '20 min',
      description: 'Learn how to write clear, detailed bug reports that get validated faster.',
      steps: 6
    },
    {
      id: 5,
      title: 'XSS Discovery and Exploitation',
      category: 'Exploitation',
      difficulty: 'intermediate',
      duration: '35 min',
      description: 'Master Cross-Site Scripting vulnerabilities from discovery to exploitation.',
      videoUrl: 'https://example.com/video5',
      steps: 7
    },
    {
      id: 6,
      title: 'API Security Testing',
      category: 'Testing',
      difficulty: 'advanced',
      duration: '50 min',
      description: 'Comprehensive guide to testing REST and GraphQL APIs for security vulnerabilities.',
      videoUrl: 'https://example.com/video6',
      steps: 10
    },
    {
      id: 7,
      title: 'Understanding OWASP Top 10',
      category: 'Basics',
      difficulty: 'beginner',
      duration: '30 min',
      description: 'Overview of the OWASP Top 10 web application security risks.',
      steps: 10
    },
    {
      id: 8,
      title: 'Building a Bug Hunting Methodology',
      category: 'Strategy',
      difficulty: 'intermediate',
      duration: '40 min',
      description: 'Develop a systematic approach to finding vulnerabilities efficiently.',
      steps: 8
    }
  ]

  const categories = ['all', ...Array.from(new Set(tutorials.map(t => t.category)))]
  
  const filteredTutorials = tutorials.filter(tutorial => {
    const categoryMatch = selectedCategory === 'all' || tutorial.category === selectedCategory
    const difficultyMatch = selectedDifficulty === 'all' || tutorial.difficulty === selectedDifficulty
    return categoryMatch && difficultyMatch
  })

  const getDifficultyColor = (difficulty: string) => {
    const colors: { [key: string]: any } = {
      beginner: 'success',
      intermediate: 'warning',
      advanced: 'error'
    }
    return colors[difficulty]
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
          <h1 className="text-4xl font-bold text-white mb-2">Tutorials</h1>
          <p className="text-slate-400">Step-by-step guides to master security testing</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <SimpleCard>
            <SimpleCardHeader>
              <SimpleCardTitle className="text-lg">Total Tutorials</SimpleCardTitle>
            </SimpleCardHeader>
            <SimpleCardContent>
              <div className="text-4xl font-bold text-cyan-400">{tutorials.length}</div>
            </SimpleCardContent>
          </SimpleCard>

          <SimpleCard>
            <SimpleCardHeader>
              <SimpleCardTitle className="text-lg">Categories</SimpleCardTitle>
            </SimpleCardHeader>
            <SimpleCardContent>
              <div className="text-4xl font-bold text-gray-400">{categories.length - 1}</div>
            </SimpleCardContent>
          </SimpleCard>

          <SimpleCard>
            <SimpleCardHeader>
              <SimpleCardTitle className="text-lg">With Videos</SimpleCardTitle>
            </SimpleCardHeader>
            <SimpleCardContent>
              <div className="text-4xl font-bold text-green-400">
                {tutorials.filter(t => t.videoUrl).length}
              </div>
            </SimpleCardContent>
          </SimpleCard>
        </div>

        <div className="bg-slate-800 rounded-xl p-6 mb-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <label className="block text-white font-semibold mb-3">Category</label>
              <div className="flex flex-wrap gap-2">
                {categories.map(category => (
                  <button
                    key={category}
                    onClick={() => setSelectedCategory(category)}
                    className={`px-4 py-2 rounded-lg font-semibold transition-colors capitalize ${
                      selectedCategory === category
                        ? 'bg-cyan-600 text-white'
                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    {category}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-white font-semibold mb-3">Difficulty</label>
              <div className="flex flex-wrap gap-2">
                {['all', 'beginner', 'intermediate', 'advanced'].map(difficulty => (
                  <button
                    key={difficulty}
                    onClick={() => setSelectedDifficulty(difficulty)}
                    className={`px-4 py-2 rounded-lg font-semibold transition-colors capitalize ${
                      selectedDifficulty === difficulty
                        ? 'bg-cyan-600 text-white'
                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    {difficulty}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredTutorials.map(tutorial => (
            <SimpleCard key={tutorial.id} className="hover:border-cyan-500 transition-colors">
              <SimpleCardHeader>
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-white mb-2">{tutorial.title}</h3>
                    <p className="text-slate-400 text-sm mb-3">{tutorial.description}</p>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2">
                  <SimpleBadge variant="info">{tutorial.category}</SimpleBadge>
                  <SimpleBadge variant={getDifficultyColor(tutorial.difficulty)}>
                    {tutorial.difficulty}
                  </SimpleBadge>
                  {tutorial.videoUrl && (
                    <SimpleBadge variant="success">
                       Video
                    </SimpleBadge>
                  )}
                </div>
              </SimpleCardHeader>
              <SimpleCardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-slate-400">Duration</div>
                      <div className="text-white font-semibold">{tutorial.duration}</div>
                    </div>
                    <div>
                      <div className="text-slate-400">Steps</div>
                      <div className="text-white font-semibold">{tutorial.steps} steps</div>
                    </div>
                  </div>

                  <div className="pt-4 border-t border-slate-700">
                    <Link href={`/tutorials/${tutorial.id}`}>
                      <button className="w-full px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white font-semibold transition-colors">
                        Start Tutorial
                      </button>
                    </Link>
                  </div>
                </div>
              </SimpleCardContent>
            </SimpleCard>
          ))}
        </div>

        {filteredTutorials.length === 0 && (
          <SimpleCard>
            <SimpleCardContent className="py-12 text-center">
              <div className="text-6xl mb-4"></div>
              <h3 className="text-xl font-semibold text-white mb-2">No Tutorials Found</h3>
              <p className="text-slate-400">Try adjusting your filters</p>
            </SimpleCardContent>
          </SimpleCard>
        )}

        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <SimpleCard>
            <SimpleCardHeader>
              <SimpleCardTitle>Learning Path</SimpleCardTitle>
            </SimpleCardHeader>
            <SimpleCardContent>
              <p className="text-slate-300 mb-4">
                Follow our structured learning path from beginner to advanced
              </p>
              <button className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-700 rounded-lg text-white font-semibold transition-colors">
                View Learning Path
              </button>
            </SimpleCardContent>
          </SimpleCard>

          <SimpleCard>
            <SimpleCardHeader>
              <SimpleCardTitle>Interactive Labs</SimpleCardTitle>
            </SimpleCardHeader>
            <SimpleCardContent>
              <p className="text-slate-300 mb-4">
                Practice in safe, controlled environments with real vulnerabilities
              </p>
              <button className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-white font-semibold transition-colors">
                Browse Labs
              </button>
            </SimpleCardContent>
          </SimpleCard>

          <SimpleCard>
            <SimpleCardHeader>
              <SimpleCardTitle>Community Support</SimpleCardTitle>
            </SimpleCardHeader>
            <SimpleCardContent>
              <p className="text-slate-300 mb-4">
                Get help from experienced hunters in our community forum
              </p>
              <button className="w-full px-4 py-2 bg-white hover:bg-gray-200 rounded-lg text-white font-semibold transition-colors">
                Join Forum
              </button>
            </SimpleCardContent>
          </SimpleCard>
        </div>
      </div>
    </div>
  )
}
