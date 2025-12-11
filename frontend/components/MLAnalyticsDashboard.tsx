"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Activity,
  TrendingUp,
  TrendingDown,
  Brain,
  Target,
  AlertCircle,
  CheckCircle2,
  XCircle,
  BarChart3,
  LineChart,
  PieChart,
  RefreshCw
} from 'lucide-react'

interface MLStatistics {
  total_scans: number
  total_predictions: number
  high_confidence_predictions: number
  average_confidence: number
  average_processing_time_ms: number
  period_days: number
}

interface ModelPerformance {
  model_type: string
  period_days: number
  total_feedback: number
  accuracy: number
  precision: number
  recall: number
  f1_score: number
  average_confidence: number
  confusion_matrix: {
    true_positive: number
    false_positive: number
    true_negative: number
    false_negative: number
  }
}

interface FeedbackStats {
  total_feedback: number
  correct_predictions: number
  incorrect_predictions: number
  accuracy_rate: number
  average_response_time_hours: number
  feedback_by_type: Record<string, number>
  period_days: number
}

export default function MLAnalyticsDashboard() {
  const [mlStats, setMLStats] = useState<MLStatistics | null>(null)
  const [modelPerformance, setModelPerformance] = useState<ModelPerformance | null>(null)
  const [feedbackStats, setFeedbackStats] = useState<FeedbackStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedPeriod, setSelectedPeriod] = useState(30)

  useEffect(() => {
    fetchMLAnalytics()
  }, [selectedPeriod])

  const fetchMLAnalytics = async () => {
    setLoading(true)
    try {
      const [statsRes, perfRes, feedbackRes] = await Promise.all([
        fetch(`/api/ml/statistics/predictions?days=${selectedPeriod}`),
        fetch(`/api/ml/performance/rule_based?days=${selectedPeriod}`),
        fetch(`/api/ml/statistics/feedback?days=${selectedPeriod}`)
      ])

      if (statsRes.ok) setMLStats(await statsRes.json())
      if (perfRes.ok) setModelPerformance(await perfRes.json())
      if (feedbackRes.ok) setFeedbackStats(await feedbackRes.json())
    } catch (error) {
      console.error('Failed to fetch ML analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'text-green-600 dark:text-green-400'
    if (confidence >= 0.7) return 'text-white dark:text-gray-400'
    if (confidence >= 0.5) return 'text-yellow-600 dark:text-yellow-400'
    return 'text-red-600 dark:text-red-400'
  }

  const getPerformanceColor = (value: number, metric: string) => {
    const thresholds = {
      accuracy: { good: 0.85, medium: 0.7 },
      precision: { good: 0.8, medium: 0.6 },
      recall: { good: 0.8, medium: 0.6 },
      f1_score: { good: 0.8, medium: 0.6 }
    }

    const threshold = thresholds[metric as keyof typeof thresholds]
    if (!threshold) return 'text-gray-600'

    if (value >= threshold.good) return 'text-green-600 dark:text-green-400'
    if (value >= threshold.medium) return 'text-yellow-600 dark:text-yellow-400'
    return 'text-red-600 dark:text-red-400'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white/20"></div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-600 to-gray-700 bg-clip-text text-transparent">
            ML Analytics Dashboard
          </h1>
          <p className="text-muted-foreground mt-2">
            Monitor ML model performance and prediction accuracy
          </p>
        </div>
        <div className="flex gap-3">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(Number(e.target.value))}
            className="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
          <Button onClick={fetchMLAnalytics} variant="outline">
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-2 border-white/20 bg-gradient-to-br from-gray-800 to-transparent dark:from-gray-900/20">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Predictions</CardTitle>
            <Brain className="h-4 w-4 text-white" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mlStats?.total_predictions || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              From {mlStats?.total_scans || 0} scans
            </p>
          </CardContent>
        </Card>

        <Card className="border-2 border-green-500/20 bg-gradient-to-br from-green-50 to-transparent dark:from-green-950/20">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">High Confidence</CardTitle>
            <Target className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mlStats?.high_confidence_predictions || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {mlStats?.total_predictions ? 
                Math.round((mlStats.high_confidence_predictions / mlStats.total_predictions) * 100) : 0}% of total
            </p>
          </CardContent>
        </Card>

        <Card className="border-2 border-white/20 bg-gradient-to-br from-gray-800 to-transparent dark:from-gray-900/20">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Avg Confidence</CardTitle>
            <TrendingUp className="h-4 w-4 text-white" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${getConfidenceColor(mlStats?.average_confidence || 0)}`}>
              {((mlStats?.average_confidence || 0) * 100).toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {mlStats?.average_processing_time_ms?.toFixed(0)}ms avg processing
            </p>
          </CardContent>
        </Card>

        <Card className="border-2 border-orange-500/20 bg-gradient-to-br from-orange-50 to-transparent dark:from-orange-950/20">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Model Accuracy</CardTitle>
            <Activity className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${getPerformanceColor(modelPerformance?.accuracy || 0, 'accuracy')}`}>
              {((modelPerformance?.accuracy || 0) * 100).toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              From {modelPerformance?.total_feedback || 0} feedback
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analytics */}
      <Tabs defaultValue="performance" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="performance">Model Performance</TabsTrigger>
          <TabsTrigger value="feedback">Feedback Analysis</TabsTrigger>
          <TabsTrigger value="confidence">Confidence Scores</TabsTrigger>
        </TabsList>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Model Performance Metrics</CardTitle>
              <CardDescription>
                Evaluation metrics from user feedback over the last {selectedPeriod} days
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Metrics Grid */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 rounded-lg bg-gray-50 dark:bg-gray-900">
                    <span className="font-medium">Accuracy</span>
                    <span className={`text-2xl font-bold ${getPerformanceColor(modelPerformance?.accuracy || 0, 'accuracy')}`}>
                      {((modelPerformance?.accuracy || 0) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-4 rounded-lg bg-gray-50 dark:bg-gray-900">
                    <span className="font-medium">Precision</span>
                    <span className={`text-2xl font-bold ${getPerformanceColor(modelPerformance?.precision || 0, 'precision')}`}>
                      {((modelPerformance?.precision || 0) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-4 rounded-lg bg-gray-50 dark:bg-gray-900">
                    <span className="font-medium">Recall</span>
                    <span className={`text-2xl font-bold ${getPerformanceColor(modelPerformance?.recall || 0, 'recall')}`}>
                      {((modelPerformance?.recall || 0) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-4 rounded-lg bg-gray-50 dark:bg-gray-900">
                    <span className="font-medium">F1 Score</span>
                    <span className={`text-2xl font-bold ${getPerformanceColor(modelPerformance?.f1_score || 0, 'f1_score')}`}>
                      {((modelPerformance?.f1_score || 0) * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>

                {/* Confusion Matrix */}
                <div className="space-y-4">
                  <h3 className="font-semibold text-lg">Confusion Matrix</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <Card className="border-2 border-green-500/20">
                      <CardHeader className="pb-3">
                        <div className="flex items-center gap-2">
                          <CheckCircle2 className="h-5 w-5 text-green-600" />
                          <CardTitle className="text-sm">True Positive</CardTitle>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="text-3xl font-bold text-green-600">
                          {modelPerformance?.confusion_matrix?.true_positive || 0}
                        </div>
                      </CardContent>
                    </Card>

                    <Card className="border-2 border-red-500/20">
                      <CardHeader className="pb-3">
                        <div className="flex items-center gap-2">
                          <XCircle className="h-5 w-5 text-red-600" />
                          <CardTitle className="text-sm">False Positive</CardTitle>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="text-3xl font-bold text-red-600">
                          {modelPerformance?.confusion_matrix?.false_positive || 0}
                        </div>
                      </CardContent>
                    </Card>

                    <Card className="border-2 border-orange-500/20">
                      <CardHeader className="pb-3">
                        <div className="flex items-center gap-2">
                          <AlertCircle className="h-5 w-5 text-orange-600" />
                          <CardTitle className="text-sm">False Negative</CardTitle>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="text-3xl font-bold text-orange-600">
                          {modelPerformance?.confusion_matrix?.false_negative || 0}
                        </div>
                      </CardContent>
                    </Card>

                    <Card className="border-2 border-white/20">
                      <CardHeader className="pb-3">
                        <div className="flex items-center gap-2">
                          <CheckCircle2 className="h-5 w-5 text-white" />
                          <CardTitle className="text-sm">True Negative</CardTitle>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="text-3xl font-bold text-white">
                          {modelPerformance?.confusion_matrix?.true_negative || 0}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Feedback Tab */}
        <TabsContent value="feedback" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>User Feedback Statistics</CardTitle>
              <CardDescription>
                Feedback received from users validating ML predictions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-2">
                  <div className="text-sm font-medium text-muted-foreground">Total Feedback</div>
                  <div className="text-3xl font-bold">{feedbackStats?.total_feedback || 0}</div>
                </div>
                <div className="space-y-2">
                  <div className="text-sm font-medium text-muted-foreground">Correct Predictions</div>
                  <div className="text-3xl font-bold text-green-600">
                    {feedbackStats?.correct_predictions || 0}
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-sm font-medium text-muted-foreground">Incorrect Predictions</div>
                  <div className="text-3xl font-bold text-red-600">
                    {feedbackStats?.incorrect_predictions || 0}
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t">
                <div className="flex items-center justify-between">
                  <span className="font-medium">Accuracy Rate</span>
                  <span className="text-2xl font-bold text-green-600">
                    {((feedbackStats?.accuracy_rate || 0) * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="mt-4 flex items-center justify-between">
                  <span className="font-medium">Avg Response Time</span>
                  <span className="text-lg font-semibold">
                    {feedbackStats?.average_response_time_hours?.toFixed(1)}h
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Confidence Tab */}
        <TabsContent value="confidence" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Confidence Score Distribution</CardTitle>
              <CardDescription>
                Distribution of prediction confidence scores
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-lg bg-gradient-to-r from-green-50 to-transparent dark:from-green-950/20">
                  <div>
                    <div className="font-semibold">Very High (≥90%)</div>
                    <div className="text-sm text-muted-foreground">Highly reliable predictions</div>
                  </div>
                  <Badge variant="default" className="bg-green-600">
                    {mlStats?.total_predictions ? 
                      Math.round((mlStats.high_confidence_predictions / mlStats.total_predictions) * 100) : 0}%
                  </Badge>
                </div>

                <div className="flex items-center justify-between p-4 rounded-lg bg-gradient-to-r from-gray-800 to-transparent dark:from-gray-900/20">
                  <div>
                    <div className="font-semibold">High (70-89%)</div>
                    <div className="text-sm text-muted-foreground">Good confidence level</div>
                  </div>
                  <Badge variant="default" className="bg-white">
                    25%
                  </Badge>
                </div>

                <div className="flex items-center justify-between p-4 rounded-lg bg-gradient-to-r from-yellow-50 to-transparent dark:from-yellow-950/20">
                  <div>
                    <div className="font-semibold">Medium (50-69%)</div>
                    <div className="text-sm text-muted-foreground">Moderate confidence</div>
                  </div>
                  <Badge variant="default" className="bg-yellow-600">
                    10%
                  </Badge>
                </div>

                <div className="flex items-center justify-between p-4 rounded-lg bg-gradient-to-r from-red-50 to-transparent dark:from-red-950/20">
                  <div>
                    <div className="font-semibold">Low (&lt;50%)</div>
                    <div className="text-sm text-muted-foreground">Requires verification</div>
                  </div>
                  <Badge variant="default" className="bg-red-600">
                    5%
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
