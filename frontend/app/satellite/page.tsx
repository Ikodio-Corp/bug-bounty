'use client';

import { useState, useEffect } from 'react';
import { SimpleCard } from '@/components/ui/simple-card';
import { SimpleBadge } from '@/components/ui/simple-badge';
import { Button } from '@/components/ui/button';

interface SatelliteData {
  id: number;
  satellite_name: string;
  target_coordinates: {
    lat: number;
    lng: number;
  };
  image_url: string;
  resolution: number;
  capture_date: string;
  analysis_status: 'pending' | 'processing' | 'completed';
  findings: any[];
}

export default function SatellitePage() {
  const [satelliteData, setSatelliteData] = useState<SatelliteData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCoords, setSelectedCoords] = useState({ lat: 37.7749, lng: -122.4194 });

  useEffect(() => {
    fetchSatelliteData();
  }, []);

  const fetchSatelliteData = async () => {
    try {
      const response = await fetch('/api/satellite/imagery', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setSatelliteData(data);
      }
    } catch (error) {
      console.error('Failed to fetch satellite data:', error);
    } finally {
      setLoading(false);
    }
  };

  const requestSatelliteImagery = async () => {
    try {
      const response = await fetch('/api/satellite/request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          coordinates: selectedCoords,
          resolution: 'high',
          analysis_type: 'infrastructure'
        })
      });

      if (response.ok) {
        fetchSatelliteData();
      }
    } catch (error) {
      console.error('Failed to request satellite imagery:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading satellite intelligence...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4">Satellite Intelligence</h1>
        <p className="text-gray-400">
          Leverage satellite imagery and geospatial analysis for infrastructure security assessment
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">Active Scans</h3>
          <p className="text-3xl font-bold text-white">
            {satelliteData.filter(d => d.analysis_status === 'processing').length}
          </p>
        </SimpleCard>

        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">Completed</h3>
          <p className="text-3xl font-bold text-green-500">
            {satelliteData.filter(d => d.analysis_status === 'completed').length}
          </p>
        </SimpleCard>

        <SimpleCard>
          <h3 className="text-lg font-semibold mb-2">Total Coverage</h3>
          <p className="text-3xl font-bold text-white">
            {satelliteData.length} km²
          </p>
        </SimpleCard>
      </div>

      <SimpleCard className="mb-6">
        <h2 className="text-2xl font-bold mb-4">Request Satellite Imagery</h2>
        <div className="grid md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-2">Latitude</label>
            <input
              type="number"
              step="0.0001"
              value={selectedCoords.lat}
              onChange={(e) => setSelectedCoords({...selectedCoords, lat: parseFloat(e.target.value)})}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Longitude</label>
            <input
              type="number"
              step="0.0001"
              value={selectedCoords.lng}
              onChange={(e) => setSelectedCoords({...selectedCoords, lng: parseFloat(e.target.value)})}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded"
            />
          </div>
        </div>
        <Button onClick={requestSatelliteImagery}>
          Request Imagery Analysis
        </Button>
      </SimpleCard>

      <h2 className="text-2xl font-bold mb-4">Satellite Data</h2>
      <div className="grid md:grid-cols-2 gap-6">
        {satelliteData.map((data) => (
          <SimpleCard key={data.id}>
            <div className="mb-4">
              {data.image_url ? (
                <img 
                  src={data.image_url} 
                  alt="Satellite imagery"
                  className="w-full h-48 object-cover rounded"
                />
              ) : (
                <div className="w-full h-48 bg-slate-800 rounded flex items-center justify-center">
                  <span className="text-gray-500">Processing imagery...</span>
                </div>
              )}
            </div>

            <div className="flex items-center gap-3 mb-3">
              <h3 className="text-lg font-semibold">{data.satellite_name}</h3>
              <SimpleBadge variant={
                data.analysis_status === 'completed' ? 'success' :
                data.analysis_status === 'processing' ? 'info' : 'warning'
              }>
                {data.analysis_status}
              </SimpleBadge>
            </div>

            <div className="grid grid-cols-2 gap-3 mb-3">
              <div>
                <p className="text-sm text-gray-500">Coordinates</p>
                <p className="text-sm font-medium">
                  {data.target_coordinates.lat.toFixed(4)}, {data.target_coordinates.lng.toFixed(4)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Resolution</p>
                <p className="text-sm font-medium">{data.resolution}m</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Capture Date</p>
                <p className="text-sm font-medium">
                  {new Date(data.capture_date).toLocaleDateString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Findings</p>
                <p className="text-sm font-medium">{data.findings.length}</p>
              </div>
            </div>

            <Button size="sm" className="w-full">
              View Analysis
            </Button>
          </SimpleCard>
        ))}

        {satelliteData.length === 0 && (
          <div className="col-span-full">
            <SimpleCard>
              <p className="text-center text-gray-500 py-8">
                No satellite data available. Request imagery analysis above.
              </p>
            </SimpleCard>
          </div>
        )}
      </div>
    </div>
  );
}
