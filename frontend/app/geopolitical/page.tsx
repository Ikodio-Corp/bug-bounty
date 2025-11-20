'use client';

import { useState, useEffect } from 'react';
import { SimpleCard } from '@/components/ui/simple-card';
import { SimpleBadge } from '@/components/ui/simple-badge';

interface GeopoliticalEvent {
  id: number;
  event_type: string;
  region: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  threat_level: number;
  affected_sectors: string[];
  recommendations: string[];
  timestamp: string;
}

export default function GeopoliticalPage() {
  const [events, setEvents] = useState<GeopoliticalEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRegion, setSelectedRegion] = useState('all');

  useEffect(() => {
    fetchGeopoliticalEvents();
  }, [selectedRegion]);

  const fetchGeopoliticalEvents = async () => {
    try {
      const url = selectedRegion === 'all' 
        ? '/api/geopolitical/events'
        : `/api/geopolitical/events?region=${selectedRegion}`;
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setEvents(data);
      }
    } catch (error) {
      console.error('Failed to fetch geopolitical events:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading geopolitical intelligence...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4">Geopolitical Intelligence</h1>
        <p className="text-gray-400">
          Real-time monitoring of geopolitical events and their impact on cybersecurity landscape
        </p>
      </div>

      <div className="grid md:grid-cols-4 gap-6 mb-8">
        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">Critical Events</h3>
          <p className="text-3xl font-bold text-red-500">
            {events.filter(e => e.severity === 'critical').length}
          </p>
        </SimpleCard>

        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">High Priority</h3>
          <p className="text-3xl font-bold text-orange-500">
            {events.filter(e => e.severity === 'high').length}
          </p>
        </SimpleCard>

        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">Medium</h3>
          <p className="text-3xl font-bold text-yellow-500">
            {events.filter(e => e.severity === 'medium').length}
          </p>
        </SimpleCard>

        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">Low</h3>
          <p className="text-3xl font-bold text-green-500">
            {events.filter(e => e.severity === 'low').length}
          </p>
        </SimpleCard>
      </div>

      <SimpleCard className="mb-6">
        <div className="flex items-center gap-4">
          <label className="font-medium">Filter by Region:</label>
          <select
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
            className="px-3 py-2 bg-slate-800 border border-slate-700 rounded"
          >
            <option value="all">All Regions</option>
            <option value="north_america">North America</option>
            <option value="europe">Europe</option>
            <option value="asia">Asia</option>
            <option value="middle_east">Middle East</option>
            <option value="africa">Africa</option>
            <option value="south_america">South America</option>
            <option value="oceania">Oceania</option>
          </select>
        </div>
      </SimpleCard>

      <h2 className="text-2xl font-bold mb-4">Recent Events</h2>
      <div className="space-y-4">
        {events.map((event) => (
          <SimpleCard key={event.id}>
            <div className="flex justify-between items-start mb-3">
              <div className="flex items-center gap-3">
                <SimpleBadge variant={getSeverityColor(event.severity)}>
                  {event.severity}
                </SimpleBadge>
                <span className="text-sm text-gray-400">{event.event_type}</span>
                <span className="text-sm text-gray-400">•</span>
                <span className="text-sm text-gray-400">{event.region}</span>
              </div>
              <span className="text-sm text-gray-500">
                {new Date(event.timestamp).toLocaleString()}
              </span>
            </div>

            <h3 className="text-xl font-semibold mb-2">{event.title}</h3>
            <p className="text-gray-300 mb-4">{event.description}</p>

            <div className="grid md:grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-sm text-gray-500 mb-2">Threat Level</p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-700 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        event.threat_level > 75 ? 'bg-red-500' :
                        event.threat_level > 50 ? 'bg-orange-500' :
                        event.threat_level > 25 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${event.threat_level}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium">{event.threat_level}%</span>
                </div>
              </div>

              <div>
                <p className="text-sm text-gray-500 mb-2">Affected Sectors</p>
                <div className="flex flex-wrap gap-2">
                  {event.affected_sectors.map((sector, idx) => (
                    <SimpleBadge key={idx} variant="default">
                      {sector}
                    </SimpleBadge>
                  ))}
                </div>
              </div>
            </div>

            {event.recommendations.length > 0 && (
              <div className="bg-slate-800 p-4 rounded">
                <p className="text-sm font-semibold mb-2">Security Recommendations:</p>
                <ul className="space-y-1">
                  {event.recommendations.map((rec, idx) => (
                    <li key={idx} className="text-sm text-gray-300">
                      • {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </SimpleCard>
        ))}

        {events.length === 0 && (
          <SimpleCard>
            <p className="text-center text-gray-500 py-8">
              No geopolitical events found for the selected region.
            </p>
          </SimpleCard>
        )}
      </div>
    </div>
  );
}
