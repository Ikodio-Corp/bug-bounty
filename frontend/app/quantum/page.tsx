'use client';

import { useState, useEffect } from 'react';
import { SimpleCard } from '@/components/ui/simple-card';
import { SimpleBadge } from '@/components/ui/simple-badge';
import { Button } from '@/components/ui/button';

interface QuantumJob {
  id: number;
  name: string;
  algorithm: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  qubits: number;
  circuit_depth: number;
  execution_time: number | null;
  result: any;
  created_at: string;
}

export default function QuantumPage() {
  const [jobs, setJobs] = useState<QuantumJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('shor');

  useEffect(() => {
    fetchQuantumJobs();
  }, []);

  const fetchQuantumJobs = async () => {
    try {
      const response = await fetch('/api/quantum/jobs', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setJobs(data);
      }
    } catch (error) {
      console.error('Failed to fetch quantum jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const createQuantumJob = async () => {
    try {
      const response = await fetch('/api/quantum/jobs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          algorithm: selectedAlgorithm,
          qubits: 8,
          parameters: {}
        })
      });

      if (response.ok) {
        fetchQuantumJobs();
      }
    } catch (error) {
      console.error('Failed to create quantum job:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'running': return 'info';
      case 'queued': return 'warning';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading quantum computing interface...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4">Quantum Computing Security</h1>
        <p className="text-gray-400">
          Leverage quantum algorithms for cryptographic analysis and vulnerability detection
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">Active Jobs</h3>
          <p className="text-3xl font-bold text-blue-500">
            {jobs.filter(j => j.status === 'running').length}
          </p>
        </SimpleCard>

        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">Completed</h3>
          <p className="text-3xl font-bold text-green-500">
            {jobs.filter(j => j.status === 'completed').length}
          </p>
        </SimpleCard>

        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">Total Qubits Used</h3>
          <p className="text-3xl font-bold text-purple-500">
            {jobs.reduce((sum, j) => sum + j.qubits, 0)}
          </p>
        </SimpleCard>
      </div>

      <SimpleCard className="mb-6">
        <h2 className="text-2xl font-bold mb-4">Create Quantum Job</h2>
        <div className="grid md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-2">Algorithm</label>
            <select
              value={selectedAlgorithm}
              onChange={(e) => setSelectedAlgorithm(e.target.value)}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded"
            >
              <option value="shor">Shor's Algorithm - Factorization</option>
              <option value="grover">Grover's Algorithm - Search</option>
              <option value="vqe">VQE - Quantum Chemistry</option>
              <option value="qaoa">QAOA - Optimization</option>
            </select>
          </div>
        </div>
        <Button onClick={createQuantumJob}>
          Execute Quantum Job
        </Button>
      </SimpleCard>

      <h2 className="text-2xl font-bold mb-4">Job History</h2>
      <div className="space-y-4">
        {jobs.map((job) => (
          <SimpleCard key={job.id}>
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-xl font-semibold">{job.name}</h3>
                  <SimpleBadge variant={getStatusColor(job.status)}>
                    {job.status}
                  </SimpleBadge>
                </div>

                <div className="grid md:grid-cols-4 gap-4 mb-3">
                  <div>
                    <p className="text-sm text-gray-500">Algorithm</p>
                    <p className="font-medium">{job.algorithm}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Qubits</p>
                    <p className="font-medium">{job.qubits}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Circuit Depth</p>
                    <p className="font-medium">{job.circuit_depth}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Execution Time</p>
                    <p className="font-medium">
                      {job.execution_time ? `${job.execution_time}ms` : '-'}
                    </p>
                  </div>
                </div>

                {job.result && (
                  <div className="bg-slate-800 p-3 rounded text-sm">
                    <p className="text-gray-400 mb-1">Result:</p>
                    <pre className="text-green-400">
                      {JSON.stringify(job.result, null, 2)}
                    </pre>
                  </div>
                )}
              </div>

              <Button size="sm" variant="outline">
                View Details
              </Button>
            </div>
          </SimpleCard>
        ))}

        {jobs.length === 0 && (
          <SimpleCard>
            <p className="text-center text-gray-500 py-8">
              No quantum jobs found. Create your first quantum computing job above.
            </p>
          </SimpleCard>
        )}
      </div>
    </div>
  );
}
