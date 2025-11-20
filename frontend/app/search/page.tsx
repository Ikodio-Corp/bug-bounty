'use client';

import { useState } from 'react';
import { SimpleCard } from '@/components/ui/simple-card';
import { Button } from '@/components/ui/button';

interface SearchFilters {
  query: string;
  severity: string[];
  status: string[];
  dateRange: string;
  category: string;
}

export default function SearchPage() {
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    severity: [],
    status: [],
    dateRange: 'all',
    category: 'all'
  });
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchType, setSearchType] = useState<'bugs' | 'scans' | 'users' | 'guilds'>('bugs');

  const handleSearch = async () => {
    setLoading(true);
    try {
      const queryParams = new URLSearchParams({
        q: filters.query,
        type: searchType,
        severity: filters.severity.join(','),
        status: filters.status.join(','),
        dateRange: filters.dateRange,
        category: filters.category
      });

      const response = await fetch(`/api/search?${queryParams}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data.results);
      }
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Advanced Search</h1>

      <SimpleCard className="mb-6">
        <div className="space-y-4">
          <div>
            <input
              type="text"
              value={filters.query}
              onChange={(e) => setFilters({ ...filters, query: e.target.value })}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search for bugs, scans, users..."
              className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-gray-400"
            />
          </div>

          <div className="flex gap-3">
            {(['bugs', 'scans', 'users', 'guilds'] as const).map((type) => (
              <Button
                key={type}
                variant={searchType === type ? 'default' : 'outline'}
                onClick={() => setSearchType(type)}
              >
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </Button>
            ))}
          </div>

          {searchType === 'bugs' && (
            <div className="grid md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Severity</label>
                <select
                  multiple
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded"
                  onChange={(e) => {
                    const selected = Array.from(e.target.selectedOptions, option => option.value);
                    setFilters({ ...filters, severity: selected });
                  }}
                >
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Status</label>
                <select
                  multiple
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded"
                  onChange={(e) => {
                    const selected = Array.from(e.target.selectedOptions, option => option.value);
                    setFilters({ ...filters, status: selected });
                  }}
                >
                  <option value="open">Open</option>
                  <option value="verified">Verified</option>
                  <option value="fixed">Fixed</option>
                  <option value="closed">Closed</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Date Range</label>
                <select
                  value={filters.dateRange}
                  onChange={(e) => setFilters({ ...filters, dateRange: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded"
                >
                  <option value="all">All Time</option>
                  <option value="today">Today</option>
                  <option value="week">This Week</option>
                  <option value="month">This Month</option>
                  <option value="year">This Year</option>
                </select>
              </div>
            </div>
          )}

          <Button onClick={handleSearch} className="w-full">
            {loading ? 'Searching...' : 'Search'}
          </Button>
        </div>
      </SimpleCard>

      <div className="space-y-4">
        {results.length > 0 ? (
          results.map((result, idx) => (
            <SimpleCard key={idx}>
              <div>
                <h3 className="text-xl font-semibold mb-2">{result.title || result.name}</h3>
                <p className="text-gray-400 mb-3">{result.description}</p>
                <div className="flex gap-3">
                  <Button size="sm">View Details</Button>
                </div>
              </div>
            </SimpleCard>
          ))
        ) : (
          <SimpleCard>
            <p className="text-center text-gray-500 py-8">
              {filters.query ? 'No results found. Try adjusting your search criteria.' : 'Start searching to see results.'}
            </p>
          </SimpleCard>
        )}
      </div>
    </div>
  );
}
