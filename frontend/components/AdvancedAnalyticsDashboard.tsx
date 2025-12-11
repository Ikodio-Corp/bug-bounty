'use client';

import { useEffect, useState } from 'react';
import { useMobile } from '@/hooks/useMobile';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface AnalyticsData {
  bugs: {
    total: number;
    byStatus: { name: string; value: number }[];
    bySeverity: { name: string; value: number }[];
    trend: { date: string; count: number }[];
  };
  scans: {
    total: number;
    active: number;
    completed: number;
    trend: { date: string; count: number }[];
  };
  users: {
    total: number;
    active: number;
    trend: { date: string; count: number }[];
  };
  revenue: {
    total: number;
    bySource: { name: string; value: number }[];
    trend: { date: string; amount: number }[];
  };
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function AdvancedAnalyticsDashboard() {
  const { isMobile, isTablet } = useMobile();
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('7d');

  useEffect(() => {
    fetchAnalyticsData();
  }, [timeRange]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/analytics?range=${timeRange}`);
      const result = await response.json();
      setData(result);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
      </div>
    );
  }

  return (
    <div className={`${isMobile ? 'p-4' : 'p-6'} space-y-6`}>
      <div className={`flex ${isMobile ? 'flex-col gap-4' : 'justify-between items-center'}`}>
        <h1 className={`${isMobile ? 'text-2xl' : 'text-3xl'} font-bold text-white`}>Advanced Analytics</h1>
        
        <div className={`flex gap-2 ${isMobile ? 'w-full overflow-x-auto' : ''}`}>
          {['24h', '7d', '30d', '90d'].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`${isMobile ? 'flex-shrink-0 px-3 py-2 text-sm' : 'px-4 py-2'} rounded ${
                timeRange === range
                  ? 'bg-white text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      <div className={`grid ${isMobile ? 'grid-cols-2' : isTablet ? 'md:grid-cols-2' : 'lg:grid-cols-4'} gap-${isMobile ? '4' : '6'}`}>
        <MetricCard
          title="Total Bugs"
          value={data.bugs.total}
          change="+12%"
          positive={true}
        />
        <MetricCard
          title="Active Scans"
          value={data.scans.active}
          change="+5%"
          positive={true}
        />
        <MetricCard
          title="Active Users"
          value={data.users.active}
          change="+8%"
          positive={true}
        />
        <MetricCard
          title="Total Revenue"
          value={`$${data.revenue.total.toLocaleString()}`}
          change="+15%"
          positive={true}
        />
      </div>

      {/* Bug Analytics */}
      <div className={`grid ${isMobile ? 'grid-cols-1' : 'lg:grid-cols-2'} gap-${isMobile ? '4' : '6'}`}>
        <div className={`bg-gray-800 rounded-lg ${isMobile ? 'p-4' : 'p-6'}`}>
          <h2 className={`${isMobile ? 'text-lg' : 'text-xl'} font-semibold text-white mb-4`}>Bugs by Status</h2>
          <ResponsiveContainer width="100%" height={isMobile ? 250 : 300}>
            <PieChart>
              <Pie
                data={data.bugs.byStatus}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={isMobile ? 60 : 100}
                fill="#8884d8"
                dataKey="value"
              >
                {data.bugs.byStatus.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className={`bg-gray-800 rounded-lg ${isMobile ? 'p-4' : 'p-6'}`}>
          <h2 className={`${isMobile ? 'text-lg' : 'text-xl'} font-semibold text-white mb-4`}>Bugs by Severity</h2>
          <ResponsiveContainer width="100%" height={isMobile ? 250 : 300}>
            <BarChart data={data.bugs.bySeverity}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none' }} />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Trend Charts */}
      <div className={`grid ${isMobile ? 'grid-cols-1' : 'lg:grid-cols-2'} gap-${isMobile ? '4' : '6'}`}>
        <div className={`bg-gray-800 rounded-lg ${isMobile ? 'p-4' : 'p-6'}`}>
          <h2 className={`${isMobile ? 'text-lg' : 'text-xl'} font-semibold text-white mb-4`}>Bug Discovery Trend</h2>
          <ResponsiveContainer width="100%" height={isMobile ? 250 : 300}>
            <LineChart data={data.bugs.trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none' }} />
              <Legend />
              <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Scan Activity Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.scans.trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none' }} />
              <Legend />
              <Line type="monotone" dataKey="count" stroke="#10b981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Revenue Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Revenue by Source</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data.revenue.bySource}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: $${value.toLocaleString()}`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {data.revenue.bySource.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Revenue Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.revenue.trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none' }} />
              <Legend />
              <Line type="monotone" dataKey="amount" stroke="#f59e0b" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* User Activity */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">User Activity Trend</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data.users.trend}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="date" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none' }} />
            <Legend />
            <Line type="monotone" dataKey="count" stroke="#8b5cf6" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function MetricCard({ title, value, change, positive }: { 
  title: string; 
  value: number | string; 
  change: string; 
  positive: boolean;
}) {
  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h3 className="text-gray-400 text-sm font-medium mb-2">{title}</h3>
      <div className="flex items-end justify-between">
        <p className="text-3xl font-bold text-white">{value}</p>
        <span className={`text-sm font-medium ${positive ? 'text-green-500' : 'text-red-500'}`}>
          {change}
        </span>
      </div>
    </div>
  );
}
