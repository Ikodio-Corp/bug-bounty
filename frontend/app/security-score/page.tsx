"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'

interface ScoreData {
  score: number
  grade: string
  components: {
    technical_security: number
    process_maturity: number
    compliance: number
    historical_track_record: number
  }
  vulnerability_count: number
  critical_vulnerabilities: number
  high_vulnerabilities: number
}

interface HistoryEntry {
  score: number
  change_from_previous: number
  recorded_at: string
}

export default function SecurityScorePage() {
  const [scoreData, setScoreData] = useState<ScoreData | null>(null)
  const [history, setHistory] = useState<HistoryEntry[]>([])
  const [loading, setLoading] = useState(false)

  const calculateScore = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/security-score/calculate', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      const data = await response.json()
      setScoreData(data.data)
    } catch (error) {
      console.error('Error calculating score:', error)
    }
    setLoading(false)
  }

  const saveScore = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/security-score/save', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      const data = await response.json()
      if (data.success) {
        alert('Score saved successfully!')
        loadHistory()
      }
    } catch (error) {
      console.error('Error saving score:', error)
    }
    setLoading(false)
  }

  const loadHistory = async () => {
    try {
      const response = await fetch('/api/security-score/history/me', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      const data = await response.json()
      setHistory(data.data || [])
    } catch (error) {
      console.error('Error loading history:', error)
    }
  }

  useEffect(() => {
    calculateScore()
    loadHistory()
  }, [])

  const getGradeColor = (grade: string) => {
    if (grade.startsWith('A')) return 'text-green-600'
    if (grade.startsWith('B')) return 'text-blue-600'
    if (grade.startsWith('C')) return 'text-yellow-600'
    if (grade.startsWith('D')) return 'text-orange-600'
    return 'text-red-600'
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Security Credit Score</h1>

      {scoreData && (
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow text-center">
            <h2 className="text-lg mb-2">Your Score</h2>
            <div className={`text-6xl font-bold ${getGradeColor(scoreData.grade)}`}>
              {scoreData.score}
            </div>
            <div className={`text-3xl font-semibold mt-2 ${getGradeColor(scoreData.grade)}`}>
              {scoreData.grade}
            </div>
            <p className="text-sm text-gray-600 mt-2">Scale: 300-850 (FICO-style)</p>
            <Button onClick={saveScore} disabled={loading} className="mt-4">
              Save Score
            </Button>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold mb-4">Score Components</h2>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Technical Security (40%)</span>
                  <span className="font-semibold">{scoreData.components.technical_security.toFixed(1)}</span>
                </div>
                <div className="bg-gray-200 h-2 rounded">
                  <div 
                    className="bg-blue-600 h-2 rounded" 
                    style={{ width: `${scoreData.components.technical_security}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Process Maturity (25%)</span>
                  <span className="font-semibold">{scoreData.components.process_maturity.toFixed(1)}</span>
                </div>
                <div className="bg-gray-200 h-2 rounded">
                  <div 
                    className="bg-green-600 h-2 rounded" 
                    style={{ width: `${scoreData.components.process_maturity}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Compliance (20%)</span>
                  <span className="font-semibold">{scoreData.components.compliance.toFixed(1)}</span>
                </div>
                <div className="bg-gray-200 h-2 rounded">
                  <div 
                    className="bg-purple-600 h-2 rounded" 
                    style={{ width: `${scoreData.components.compliance}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Historical Record (15%)</span>
                  <span className="font-semibold">{scoreData.components.historical_track_record.toFixed(1)}</span>
                </div>
                <div className="bg-gray-200 h-2 rounded">
                  <div 
                    className="bg-orange-600 h-2 rounded" 
                    style={{ width: `${scoreData.components.historical_track_record}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold mb-4">Vulnerabilities</h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">Total</span>
                <span className="text-2xl font-bold">{scoreData.vulnerability_count}</span>
              </div>
              <div className="flex justify-between items-center border-t pt-2">
                <span className="text-sm">Critical</span>
                <span className="text-xl font-semibold text-red-600">{scoreData.critical_vulnerabilities}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">High</span>
                <span className="text-xl font-semibold text-orange-600">{scoreData.high_vulnerabilities}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-2xl font-semibold mb-4">Score History</h2>
        {history.length === 0 ? (
          <p className="text-gray-500">No history yet</p>
        ) : (
          <div className="space-y-2">
            {history.map((entry, index) => (
              <div key={index} className="flex justify-between items-center border-b pb-2">
                <span className="text-sm text-gray-600">
                  {new Date(entry.recorded_at).toLocaleDateString()}
                </span>
                <div className="flex items-center gap-4">
                  <span className="font-semibold">{entry.score}</span>
                  {entry.change_from_previous !== null && (
                    <span className={`text-sm ${entry.change_from_previous > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {entry.change_from_previous > 0 ? '+' : ''}{entry.change_from_previous}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="mt-8 bg-blue-50 p-6 rounded-lg">
        <h2 className="text-xl font-semibold mb-4">About Security Credit Score</h2>
        <p className="text-sm mb-4">
          Like FICO for credit, our Security Credit Score provides a standardized measure of your company's security posture.
          Scores range from 300 (worst) to 850 (best).
        </p>
        <ul className="space-y-2 text-sm">
          <li><strong>A+ (800-850):</strong> Excellent security posture</li>
          <li><strong>A (750-799):</strong> Very good security practices</li>
          <li><strong>B (650-749):</strong> Good security with room for improvement</li>
          <li><strong>C (550-649):</strong> Fair security, needs attention</li>
          <li><strong>D-F (300-549):</strong> Poor security, immediate action required</li>
        </ul>
      </div>
    </div>
  )
}
