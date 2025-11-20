'use client';

import { useMobile } from '@/hooks/useMobile';
import {
  ResponsiveContainer,
  LineChart,
  BarChart,
  PieChart,
  Line,
  Bar,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

interface ResponsiveChartProps {
  type: 'line' | 'bar' | 'pie';
  data: any[];
  dataKey?: string;
  xAxisKey?: string;
  colors?: string[];
  height?: number;
}

export default function ResponsiveChart({
  type,
  data,
  dataKey = 'value',
  xAxisKey = 'name',
  colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'],
  height,
}: ResponsiveChartProps) {
  const { isMobile, screenWidth } = useMobile();

  // Adjust chart height based on device
  const chartHeight = height || (isMobile ? 250 : 350);

  // Mobile-optimized chart settings
  const fontSize = isMobile ? 10 : 12;
  const tickMargin = isMobile ? 5 : 10;

  if (type === 'pie') {
    return (
      <ResponsiveContainer width="100%" height={chartHeight}>
        <PieChart>
          <Pie
            data={data}
            dataKey={dataKey}
            nameKey={xAxisKey}
            cx="50%"
            cy="50%"
            outerRadius={isMobile ? 60 : 80}
            label={!isMobile}
            labelLine={!isMobile}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend
            wrapperStyle={{ fontSize }}
            iconSize={isMobile ? 8 : 12}
          />
        </PieChart>
      </ResponsiveContainer>
    );
  }

  if (type === 'bar') {
    return (
      <ResponsiveContainer width="100%" height={chartHeight}>
        <BarChart data={data} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            dataKey={xAxisKey}
            stroke="#9ca3af"
            fontSize={fontSize}
            tickMargin={tickMargin}
            angle={isMobile ? -45 : 0}
            textAnchor={isMobile ? 'end' : 'middle'}
            height={isMobile ? 60 : 30}
          />
          <YAxis
            stroke="#9ca3af"
            fontSize={fontSize}
            width={isMobile ? 30 : 60}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1f2937',
              border: '1px solid #374151',
              fontSize,
            }}
          />
          <Legend
            wrapperStyle={{ fontSize }}
            iconSize={isMobile ? 8 : 12}
          />
          <Bar dataKey={dataKey} fill={colors[0]} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    );
  }

  // Line chart
  return (
    <ResponsiveContainer width="100%" height={chartHeight}>
      <LineChart data={data} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis
          dataKey={xAxisKey}
          stroke="#9ca3af"
          fontSize={fontSize}
          tickMargin={tickMargin}
          angle={isMobile ? -45 : 0}
          textAnchor={isMobile ? 'end' : 'middle'}
          height={isMobile ? 60 : 30}
        />
        <YAxis
          stroke="#9ca3af"
          fontSize={fontSize}
          width={isMobile ? 30 : 60}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1f2937',
            border: '1px solid #374151',
            fontSize,
          }}
        />
        <Legend
          wrapperStyle={{ fontSize }}
          iconSize={isMobile ? 8 : 12}
        />
        <Line
          type="monotone"
          dataKey={dataKey}
          stroke={colors[0]}
          strokeWidth={2}
          dot={{ r: isMobile ? 3 : 4 }}
          activeDot={{ r: isMobile ? 5 : 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
