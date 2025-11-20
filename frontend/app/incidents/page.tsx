'use client';

import { useState, useEffect } from 'react';
import { SimpleCard } from '@/components/ui/simple-card';
import { SimpleBadge } from '@/components/ui/simple-badge';
import { Button } from '@/components/ui/button';

interface Incident {
  id: number;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'investigating' | 'identified' | 'monitoring' | 'resolved';
  affected_services: string[];
  started_at: string;
  resolved_at: string | null;
  updates: IncidentUpdate[];
}

interface IncidentUpdate {
  id: number;
  message: string;
  created_at: string;
  author: string;
}

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('active');

  useEffect(() => {
    fetchIncidents();
  }, [filter]);

  const fetchIncidents = async () => {
    try {
      const response = await fetch(`/api/incidents?status=${filter}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setIncidents(data);
      }
    } catch (error) {
      console.error('Failed to fetch incidents:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'destructive';
      case 'high': return 'warning';
      case 'medium': return 'default';
      case 'low': return 'outline';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'investigating': return 'warning';
      case 'identified': return 'default';
      case 'monitoring': return 'outline';
      case 'resolved': return 'success';
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
      <h1 className="text-4xl font-bold mb-8">Security Incidents</h1>

      <div className="flex gap-3 mb-6">
        <Button 
          variant={filter === 'active' ? 'default' : 'outline'}
          onClick={() => setFilter('active')}
        >
          Active
        </Button>
        <Button 
          variant={filter === 'resolved' ? 'default' : 'outline'}
          onClick={() => setFilter('resolved')}
        >
          Resolved
        </Button>
        <Button 
          variant={filter === 'all' ? 'default' : 'outline'}
          onClick={() => setFilter('all')}
        >
          All
        </Button>
      </div>

      <div className="space-y-6">
        {incidents.map((incident) => (
          <SimpleCard key={incident.id}>
            <div className="mb-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold mb-2">{incident.title}</h3>
                  <p className="text-gray-700">{incident.description}</p>
                </div>
                <div className="flex flex-col gap-2">
                  <SimpleBadge variant={getSeverityColor(incident.severity)}>
                    {incident.severity}
                  </SimpleBadge>
                  <SimpleBadge variant={getStatusColor(incident.status)}>
                    {incident.status}
                  </SimpleBadge>
                </div>
              </div>

              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">Affected Services:</p>
                <div className="flex flex-wrap gap-2">
                  {incident.affected_services.map((service, idx) => (
                    <SimpleBadge key={idx} variant="outline">
                      {service}
                    </SimpleBadge>
                  ))}
                </div>
              </div>

              <div className="border-t pt-4">
                <h4 className="font-semibold mb-3">Timeline</h4>
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 rounded-full bg-red-500 mt-2"></div>
                    <div>
                      <p className="text-sm text-gray-600">
                        {new Date(incident.started_at).toLocaleString()}
                      </p>
                      <p className="font-medium">Incident started</p>
                    </div>
                  </div>

                  {incident.updates.map((update) => (
                    <div key={update.id} className="flex items-start gap-3">
                      <div className="w-2 h-2 rounded-full bg-blue-500 mt-2"></div>
                      <div>
                        <p className="text-sm text-gray-600">
                          {new Date(update.created_at).toLocaleString()}
                        </p>
                        <p className="font-medium">{update.message}</p>
                        <p className="text-sm text-gray-500">by {update.author}</p>
                      </div>
                    </div>
                  ))}

                  {incident.resolved_at && (
                    <div className="flex items-start gap-3">
                      <div className="w-2 h-2 rounded-full bg-green-500 mt-2"></div>
                      <div>
                        <p className="text-sm text-gray-600">
                          {new Date(incident.resolved_at).toLocaleString()}
                        </p>
                        <p className="font-medium">Incident resolved</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </SimpleCard>
        ))}

        {incidents.length === 0 && (
          <SimpleCard>
            <p className="text-center text-gray-600 py-8">
              No incidents found.
            </p>
          </SimpleCard>
        )}
      </div>
    </div>
  );
}
