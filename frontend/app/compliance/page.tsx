'use client';

import { useState, useEffect } from 'react';
import { SimpleCard } from '@/components/ui/simple-card';
import { SimpleBadge } from '@/components/ui/simple-badge';

interface ComplianceStandard {
  id: number;
  name: string;
  description: string;
  compliance_percentage: number;
  status: 'compliant' | 'partial' | 'non-compliant';
  last_audit: string;
  next_audit: string;
  requirements: ComplianceRequirement[];
}

interface ComplianceRequirement {
  id: number;
  title: string;
  description: string;
  status: 'met' | 'partial' | 'not-met';
  evidence: string[];
}

export default function CompliancePage() {
  const [standards, setStandards] = useState<ComplianceStandard[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStandard, setSelectedStandard] = useState<ComplianceStandard | null>(null);

  useEffect(() => {
    fetchCompliance();
  }, []);

  const fetchCompliance = async () => {
    try {
      const response = await fetch('/api/compliance', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setStandards(data);
      }
    } catch (error) {
      console.error('Failed to fetch compliance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'compliant':
      case 'met':
        return 'success';
      case 'partial':
        return 'warning';
      case 'non-compliant':
      case 'not-met':
        return 'destructive';
      default:
        return 'default';
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
      <h1 className="text-4xl font-bold mb-8">Compliance Dashboard</h1>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {standards.map((standard) => (
          <SimpleCard 
            key={standard.id}
            onClick={() => setSelectedStandard(standard)}
          >
            <div className="cursor-pointer">
              <div className="flex justify-between items-start mb-3">
                <h3 className="text-xl font-semibold">{standard.name}</h3>
                <SimpleBadge variant={getStatusColor(standard.status)}>
                  {standard.status}
                </SimpleBadge>
              </div>

              <p className="text-gray-600 mb-4">{standard.description}</p>

              <div className="mb-4">
                <div className="flex justify-between text-sm mb-1">
                  <span>Compliance</span>
                  <span className="font-semibold">{standard.compliance_percentage}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full"
                    style={{ width: `${standard.compliance_percentage}%` }}
                  ></div>
                </div>
              </div>

              <div className="text-sm text-gray-600 space-y-1">
                <p>Last Audit: {new Date(standard.last_audit).toLocaleDateString()}</p>
                <p>Next Audit: {new Date(standard.next_audit).toLocaleDateString()}</p>
                <p>Requirements: {standard.requirements.length}</p>
              </div>
            </div>
          </SimpleCard>
        ))}
      </div>

      {selectedStandard && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-2xl font-bold mb-2">{selectedStandard.name}</h2>
                <p className="text-gray-600">{selectedStandard.description}</p>
              </div>
              <button 
                onClick={() => setSelectedStandard(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                Close
              </button>
            </div>

            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-3">Overall Status</h3>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Compliance</p>
                  <p className="text-2xl font-bold text-green-600">
                    {selectedStandard.compliance_percentage}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Status</p>
                  <SimpleBadge variant={getStatusColor(selectedStandard.status)}>
                    {selectedStandard.status}
                  </SimpleBadge>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Requirements</p>
                  <p className="text-2xl font-bold">
                    {selectedStandard.requirements.length}
                  </p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-3">Requirements</h3>
              <div className="space-y-4">
                {selectedStandard.requirements.map((req) => (
                  <div key={req.id} className="border rounded p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-semibold">{req.title}</h4>
                      <SimpleBadge variant={getStatusColor(req.status)}>
                        {req.status}
                      </SimpleBadge>
                    </div>
                    <p className="text-gray-600 mb-3">{req.description}</p>
                    
                    {req.evidence.length > 0 && (
                      <div>
                        <p className="text-sm font-medium mb-1">Evidence:</p>
                        <ul className="text-sm text-gray-600 list-disc list-inside">
                          {req.evidence.map((item, idx) => (
                            <li key={idx}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
