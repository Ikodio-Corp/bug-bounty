'use client';

import { useState, useEffect } from 'react';
import { SimpleCard } from '@/components/ui/simple-card';
import { SimpleBadge } from '@/components/ui/simple-badge';
import { Button } from '@/components/ui/button';

interface AGIResearch {
  id: number;
  title: string;
  category: string;
  status: 'researching' | 'training' | 'validating' | 'completed';
  accuracy: number;
  training_samples: number;
  model_type: string;
  created_at: string;
  results: any;
}

export default function AGIPage() {
  const [research, setResearch] = useState<AGIResearch[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('vulnerability_prediction');

  useEffect(() => {
    fetchAGIResearch();
  }, []);

  const fetchAGIResearch = async () => {
    try {
      const response = await fetch('/api/agi/research', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setResearch(data);
      }
    } catch (error) {
      console.error('Failed to fetch AGI research:', error);
    } finally {
      setLoading(false);
    }
  };

  const startAGIResearch = async () => {
    try {
      const response = await fetch('/api/agi/research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          category: selectedCategory,
          model_type: 'transformer',
          training_samples: 10000
        })
      });

      if (response.ok) {
        fetchAGIResearch();
      }
    } catch (error) {
      console.error('Failed to start AGI research:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'training': return 'info';
      case 'validating': return 'warning';
      case 'researching': return 'default';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading AGI research platform...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4">AGI Research Platform</h1>
        <p className="text-gray-400">
          Advanced artificial general intelligence for autonomous security research and vulnerability discovery
        </p>
      </div>

      <div className="grid md:grid-cols-4 gap-6 mb-8">
        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">Active Research</h3>
          <p className="text-3xl font-bold text-white">
            {research.filter(r => r.status === 'training' || r.status === 'researching').length}
          </p>
        </SimpleCard>

        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">Completed</h3>
          <p className="text-3xl font-bold text-green-500">
            {research.filter(r => r.status === 'completed').length}
          </p>
        </SimpleCard>

        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">Avg Accuracy</h3>
          <p className="text-3xl font-bold text-white">
            {research.length > 0 
              ? (research.reduce((sum, r) => sum + r.accuracy, 0) / research.length).toFixed(1)
              : 0}%
          </p>
        </SimpleCard>

        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">Total Samples</h3>
          <p className="text-3xl font-bold text-yellow-500">
            {research.reduce((sum, r) => sum + r.training_samples, 0).toLocaleString()}
          </p>
        </SimpleCard>
      </div>

      <SimpleCard className="mb-6">
        <h2 className="text-2xl font-bold mb-4">Start New Research</h2>
        <div className="grid md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-2">Research Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded"
            >
              <option value="vulnerability_prediction">Vulnerability Prediction</option>
              <option value="exploit_generation">Exploit Generation</option>
              <option value="code_analysis">Code Analysis</option>
              <option value="pattern_recognition">Pattern Recognition</option>
              <option value="threat_intelligence">Threat Intelligence</option>
              <option value="autonomous_testing">Autonomous Testing</option>
            </select>
          </div>
        </div>
        <Button onClick={startAGIResearch}>
          Start AGI Research
        </Button>
      </SimpleCard>

      <h2 className="text-2xl font-bold mb-4">Research Projects</h2>
      <div className="space-y-4">
        {research.map((project) => (
          <SimpleCard key={project.id}>
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-3">
                  <h3 className="text-xl font-semibold">{project.title}</h3>
                  <SimpleBadge variant={getStatusColor(project.status)}>
                    {project.status}
                  </SimpleBadge>
                </div>

                <div className="grid md:grid-cols-5 gap-4 mb-4">
                  <div>
                    <p className="text-sm text-gray-500">Category</p>
                    <p className="font-medium">{project.category}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Model Type</p>
                    <p className="font-medium">{project.model_type}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Accuracy</p>
                    <p className="font-medium text-green-400">{project.accuracy}%</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Training Samples</p>
                    <p className="font-medium">{project.training_samples.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Created</p>
                    <p className="font-medium">
                      {new Date(project.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                {project.status === 'training' && (
                  <div className="mb-3">
                    <div className="flex justify-between text-sm mb-1">
                      <span>Training Progress</span>
                      <span>{project.accuracy}%</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-white h-2 rounded-full transition-all"
                        style={{ width: `${project.accuracy}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                {project.results && (
                  <div className="bg-slate-800 p-3 rounded text-sm">
                    <p className="text-gray-400 mb-1">Results Summary:</p>
                    <pre className="text-green-400">
                      {JSON.stringify(project.results, null, 2)}
                    </pre>
                  </div>
                )}
              </div>

              <div className="flex flex-col gap-2">
                <Button size="sm" variant="outline">
                  View Details
                </Button>
                {project.status === 'completed' && (
                  <Button size="sm">
                    Deploy Model
                  </Button>
                )}
              </div>
            </div>
          </SimpleCard>
        ))}

        {research.length === 0 && (
          <SimpleCard>
            <p className="text-center text-gray-500 py-8">
              No research projects found. Start your first AGI research above.
            </p>
          </SimpleCard>
        )}
      </div>
    </div>
  );
}
