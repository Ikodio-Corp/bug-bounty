'use client';

import { useState, useEffect } from 'react';
import { SimpleCard } from '@/components/ui/simple-card';
import { SimpleBadge } from '@/components/ui/simple-badge';
import { Button } from '@/components/ui/button';

interface ESGMetric {
  id: number;
  company_name: string;
  overall_score: number;
  environmental_score: number;
  social_score: number;
  governance_score: number;
  security_posture: number;
  vulnerabilities_found: number;
  compliance_level: number;
  last_assessment: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
}

export default function ESGPage() {
  const [metrics, setMetrics] = useState<ESGMetric[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchESGMetrics();
  }, []);

  const fetchESGMetrics = async () => {
    try {
      const response = await fetch('/api/esg/metrics', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
      }
    } catch (error) {
      console.error('Failed to fetch ESG metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-500';
    if (score >= 60) return 'text-yellow-500';
    if (score >= 40) return 'text-orange-500';
    return 'text-red-500';
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading ESG metrics...</div>
      </div>
    );
  }

  const avgScore = metrics.length > 0 
    ? metrics.reduce((sum, m) => sum + m.overall_score, 0) / metrics.length 
    : 0;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4">ESG Security Assessment</h1>
        <p className="text-gray-400">
          Environmental, Social, and Governance metrics with integrated cybersecurity assessment
        </p>
      </div>

      <div className="grid md:grid-cols-4 gap-6 mb-8">
        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">Average ESG Score</h3>
          <p className={`text-3xl font-bold ${getScoreColor(avgScore)}`}>
            {avgScore.toFixed(1)}
          </p>
        </SimpleCard>

        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">Companies Assessed</h3>
          <p className="text-3xl font-bold text-blue-500">
            {metrics.length}
          </p>
        </SimpleCard>

        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">High Risk</h3>
          <p className="text-3xl font-bold text-red-500">
            {metrics.filter(m => m.risk_level === 'high' || m.risk_level === 'critical').length}
          </p>
        </SimpleCard>

        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">Total Vulnerabilities</h3>
          <p className="text-3xl font-bold text-orange-500">
            {metrics.reduce((sum, m) => sum + m.vulnerabilities_found, 0)}
          </p>
        </SimpleCard>
      </div>

      <h2 className="text-2xl font-bold mb-4">ESG Assessments</h2>
      <div className="space-y-4">
        {metrics.map((metric) => (
          <SimpleCard key={metric.id}>
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-semibold mb-2">{metric.company_name}</h3>
                <div className="flex items-center gap-3">
                  <SimpleBadge variant={getRiskColor(metric.risk_level)}>
                    {metric.risk_level} risk
                  </SimpleBadge>
                  <span className="text-sm text-gray-400">
                    Last assessed: {new Date(metric.last_assessment).toLocaleDateString()}
                  </span>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500 mb-1">Overall Score</p>
                <p className={`text-4xl font-bold ${getScoreColor(metric.overall_score)}`}>
                  {metric.overall_score}
                </p>
              </div>
            </div>

            <div className="grid md:grid-cols-3 gap-6 mb-4">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium">Environmental</span>
                  <span className={`text-sm font-bold ${getScoreColor(metric.environmental_score)}`}>
                    {metric.environmental_score}
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      metric.environmental_score >= 80 ? 'bg-green-500' :
                      metric.environmental_score >= 60 ? 'bg-yellow-500' :
                      metric.environmental_score >= 40 ? 'bg-orange-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${metric.environmental_score}%` }}
                  ></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium">Social</span>
                  <span className={`text-sm font-bold ${getScoreColor(metric.social_score)}`}>
                    {metric.social_score}
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      metric.social_score >= 80 ? 'bg-green-500' :
                      metric.social_score >= 60 ? 'bg-yellow-500' :
                      metric.social_score >= 40 ? 'bg-orange-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${metric.social_score}%` }}
                  ></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium">Governance</span>
                  <span className={`text-sm font-bold ${getScoreColor(metric.governance_score)}`}>
                    {metric.governance_score}
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      metric.governance_score >= 80 ? 'bg-green-500' :
                      metric.governance_score >= 60 ? 'bg-yellow-500' :
                      metric.governance_score >= 40 ? 'bg-orange-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${metric.governance_score}%` }}
                  ></div>
                </div>
              </div>
            </div>

            <div className="grid md:grid-cols-3 gap-6 bg-slate-800 p-4 rounded">
              <div>
                <p className="text-sm text-gray-500 mb-1">Security Posture</p>
                <p className={`text-xl font-bold ${getScoreColor(metric.security_posture)}`}>
                  {metric.security_posture}%
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500 mb-1">Vulnerabilities Found</p>
                <p className="text-xl font-bold text-orange-500">
                  {metric.vulnerabilities_found}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500 mb-1">Compliance Level</p>
                <p className={`text-xl font-bold ${getScoreColor(metric.compliance_level)}`}>
                  {metric.compliance_level}%
                </p>
              </div>
            </div>

            <div className="mt-4 flex gap-3">
              <Button size="sm">View Full Report</Button>
              <Button size="sm" variant="outline">Export Data</Button>
            </div>
          </SimpleCard>
        ))}

        {metrics.length === 0 && (
          <SimpleCard>
            <p className="text-center text-gray-500 py-8">
              No ESG assessments available. Start your first assessment to see results.
            </p>
          </SimpleCard>
        )}
      </div>
    </div>
  );
}
