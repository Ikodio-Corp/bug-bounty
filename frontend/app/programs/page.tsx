'use client';

import { useState, useEffect } from 'react';
import { SimpleCard } from '@/components/ui/simple-card';
import { SimpleBadge } from '@/components/ui/simple-badge';
import { Button } from '@/components/ui/button';

interface Program {
  id: number;
  name: string;
  company: string;
  description: string;
  bounty_range: string;
  scopes: string[];
  status: string;
  submissions: number;
  rating: number;
  response_time: string;
  created_at: string;
}

export default function ProgramsPage() {
  const [programs, setPrograms] = useState<Program[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchPrograms();
  }, [filter]);

  const fetchPrograms = async () => {
    try {
      const response = await fetch(`/api/programs?status=${filter}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setPrograms(data);
      }
    } catch (error) {
      console.error('Failed to fetch programs:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'paused': return 'warning';
      case 'closed': return 'default';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4">Bug Bounty Programs</h1>
        <p className="text-gray-600">
          Browse and participate in bug bounty programs from top companies
        </p>
      </div>

      <div className="flex gap-3 mb-6">
        <Button 
          variant={filter === 'all' ? 'default' : 'outline'}
          onClick={() => setFilter('all')}
        >
          All Programs
        </Button>
        <Button 
          variant={filter === 'active' ? 'default' : 'outline'}
          onClick={() => setFilter('active')}
        >
          Active
        </Button>
        <Button 
          variant={filter === 'paused' ? 'default' : 'outline'}
          onClick={() => setFilter('paused')}
        >
          Paused
        </Button>
        <Button 
          variant={filter === 'closed' ? 'default' : 'outline'}
          onClick={() => setFilter('closed')}
        >
          Closed
        </Button>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {programs.map((program) => (
          <SimpleCard key={program.id}>
            <div className="mb-4">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h3 className="text-xl font-semibold">{program.name}</h3>
                  <p className="text-gray-600">{program.company}</p>
                </div>
                <SimpleBadge variant={getStatusColor(program.status)}>
                  {program.status}
                </SimpleBadge>
              </div>
              
              <p className="text-gray-700 mb-3">{program.description}</p>

              <div className="grid grid-cols-2 gap-4 mb-3">
                <div>
                  <p className="text-sm text-gray-500">Bounty Range</p>
                  <p className="font-semibold text-green-600">{program.bounty_range}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Response Time</p>
                  <p className="font-semibold">{program.response_time}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Submissions</p>
                  <p className="font-semibold">{program.submissions}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Rating</p>
                  <p className="font-semibold">{program.rating}/5.0</p>
                </div>
              </div>

              <div className="mb-4">
                <p className="text-sm text-gray-500 mb-2">Scopes</p>
                <div className="flex flex-wrap gap-2">
                  {program.scopes.map((scope, idx) => (
                    <SimpleBadge key={idx} variant="outline">
                      {scope}
                    </SimpleBadge>
                  ))}
                </div>
              </div>

              <div className="flex gap-3">
                <Button className="flex-1">View Details</Button>
                <Button variant="outline" className="flex-1">Submit Bug</Button>
              </div>
            </div>
          </SimpleCard>
        ))}

        {programs.length === 0 && (
          <div className="col-span-full">
            <SimpleCard>
              <p className="text-center text-gray-600 py-8">
                No programs found matching your filters.
              </p>
            </SimpleCard>
          </div>
        )}
      </div>
    </div>
  );
}
