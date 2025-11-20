'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { SimpleCard } from '@/components/ui/simple-card';
import { SimpleBadge } from '@/components/ui/simple-badge';

interface ApiKey {
  id: number;
  name: string;
  key: string;
  last_used: string;
  created_at: string;
  permissions: string[];
  active: boolean;
}

export default function ApiKeysPage() {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([]);

  useEffect(() => {
    fetchApiKeys();
  }, []);

  const fetchApiKeys = async () => {
    try {
      const response = await fetch('/api/api-keys', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setApiKeys(data);
      }
    } catch (error) {
      console.error('Failed to fetch API keys:', error);
    } finally {
      setLoading(false);
    }
  };

  const createApiKey = async () => {
    try {
      const response = await fetch('/api/api-keys', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          name: newKeyName,
          permissions: selectedPermissions
        })
      });

      if (response.ok) {
        const data = await response.json();
        setApiKeys([...apiKeys, data]);
        setShowCreateModal(false);
        setNewKeyName('');
        setSelectedPermissions([]);
      }
    } catch (error) {
      console.error('Failed to create API key:', error);
    }
  };

  const revokeApiKey = async (id: number) => {
    try {
      const response = await fetch(`/api/api-keys/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        setApiKeys(apiKeys.filter(key => key.id !== id));
      }
    } catch (error) {
      console.error('Failed to revoke API key:', error);
    }
  };

  const permissions = [
    'read:bugs', 'write:bugs', 'read:scans', 'write:scans',
    'read:marketplace', 'write:marketplace', 'admin'
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold">API Keys</h1>
        <Button onClick={() => setShowCreateModal(true)}>
          Create New API Key
        </Button>
      </div>

      <div className="grid gap-6">
        {apiKeys.map((apiKey) => (
          <SimpleCard key={apiKey.id}>
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-xl font-semibold">{apiKey.name}</h3>
                  <SimpleBadge variant={apiKey.active ? 'success' : 'default'}>
                    {apiKey.active ? 'Active' : 'Inactive'}
                  </SimpleBadge>
                </div>
                
                <div className="mb-3">
                  <code className="bg-gray-100 px-3 py-1 rounded text-sm">
                    {apiKey.key}
                  </code>
                </div>

                <div className="flex flex-wrap gap-2 mb-3">
                  {apiKey.permissions.map((perm, idx) => (
                    <SimpleBadge key={idx} variant="outline">
                      {perm}
                    </SimpleBadge>
                  ))}
                </div>

                <div className="text-sm text-gray-600">
                  <p>Created: {new Date(apiKey.created_at).toLocaleDateString()}</p>
                  <p>Last used: {apiKey.last_used ? new Date(apiKey.last_used).toLocaleDateString() : 'Never'}</p>
                </div>
              </div>

              <Button 
                variant="destructive"
                onClick={() => revokeApiKey(apiKey.id)}
              >
                Revoke
              </Button>
            </div>
          </SimpleCard>
        ))}

        {apiKeys.length === 0 && (
          <SimpleCard>
            <p className="text-center text-gray-600 py-8">
              No API keys found. Create one to get started.
            </p>
          </SimpleCard>
        )}
      </div>

      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-2xl font-bold mb-4">Create New API Key</h2>
            
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">
                Key Name
              </label>
              <input
                type="text"
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
                className="w-full border rounded px-3 py-2"
                placeholder="My API Key"
              />
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">
                Permissions
              </label>
              <div className="space-y-2">
                {permissions.map((perm) => (
                  <label key={perm} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={selectedPermissions.includes(perm)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedPermissions([...selectedPermissions, perm]);
                        } else {
                          setSelectedPermissions(selectedPermissions.filter(p => p !== perm));
                        }
                      }}
                      className="mr-2"
                    />
                    {perm}
                  </label>
                ))}
              </div>
            </div>

            <div className="flex gap-3">
              <Button onClick={createApiKey} className="flex-1">
                Create
              </Button>
              <Button 
                variant="outline" 
                onClick={() => setShowCreateModal(false)}
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
