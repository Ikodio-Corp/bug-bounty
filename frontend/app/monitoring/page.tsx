'use client';

import { useState, useEffect } from 'react';
import { SimpleCard } from '@/components/ui/simple-card';
import { SimpleBadge } from '@/components/ui/simple-badge';

interface MetricData {
  timestamp: string;
  value: number;
}

interface ServiceStatus {
  name: string;
  status: 'operational' | 'degraded' | 'down';
  uptime: number;
  response_time: number;
}

interface MonitoringData {
  services: ServiceStatus[];
  cpu_usage: MetricData[];
  memory_usage: MetricData[];
  disk_usage: number;
  network_in: MetricData[];
  network_out: MetricData[];
  active_scans: number;
  queued_jobs: number;
}

export default function MonitoringPage() {
  const [data, setData] = useState<MonitoringData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMonitoringData();
    const interval = setInterval(fetchMonitoringData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchMonitoringData = async () => {
    try {
      const response = await fetch('/api/monitoring', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const result = await response.json();
        setData(result);
      }
    } catch (error) {
      console.error('Failed to fetch monitoring data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational': return 'success';
      case 'degraded': return 'warning';
      case 'down': return 'destructive';
      default: return 'default';
    }
  };

  const getLatestValue = (metrics: MetricData[]) => {
    return metrics.length > 0 ? metrics[metrics.length - 1].value : 0;
  };

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading monitoring data...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">System Monitoring</h1>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">CPU Usage</h3>
          <p className="text-3xl font-bold text-blue-600">
            {getLatestValue(data.cpu_usage).toFixed(1)}%
          </p>
        </SimpleCard>

        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">Memory Usage</h3>
          <p className="text-3xl font-bold text-green-600">
            {getLatestValue(data.memory_usage).toFixed(1)}%
          </p>
        </SimpleCard>

        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">Disk Usage</h3>
          <p className="text-3xl font-bold text-yellow-600">
            {data.disk_usage.toFixed(1)}%
          </p>
        </SimpleCard>

        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">Active Scans</h3>
          <p className="text-3xl font-bold text-purple-600">
            {data.active_scans}
          </p>
        </SimpleCard>
      </div>

      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-4">Service Status</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.services.map((service, idx) => (
            <SimpleCard key={idx}>
              <div className="flex justify-between items-start mb-3">
                <h3 className="font-semibold">{service.name}</h3>
                <SimpleBadge variant={getStatusColor(service.status)}>
                  {service.status}
                </SimpleBadge>
              </div>
              <div className="space-y-1 text-sm">
                <p>Uptime: {service.uptime.toFixed(2)}%</p>
                <p>Response: {service.response_time}ms</p>
              </div>
            </SimpleCard>
          ))}
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <SimpleCard>
          <h3 className="text-xl font-semibold mb-4">Network Traffic</h3>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-600 mb-1">Incoming</p>
              <p className="text-2xl font-bold text-blue-600">
                {getLatestValue(data.network_in).toFixed(2)} MB/s
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Outgoing</p>
              <p className="text-2xl font-bold text-green-600">
                {getLatestValue(data.network_out).toFixed(2)} MB/s
              </p>
            </div>
          </div>
        </SimpleCard>

        <SimpleCard>
          <h3 className="text-xl font-semibold mb-4">Job Queue</h3>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-600 mb-1">Queued Jobs</p>
              <p className="text-2xl font-bold text-yellow-600">
                {data.queued_jobs}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Processing</p>
              <p className="text-2xl font-bold text-purple-600">
                {data.active_scans}
              </p>
            </div>
          </div>
        </SimpleCard>
      </div>
    </div>
  );
}
