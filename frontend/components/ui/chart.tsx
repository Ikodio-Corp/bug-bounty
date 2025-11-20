'use client';

import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

interface LineChartProps {
  data: {
    labels: string[];
    datasets: {
      label: string;
      data: number[];
      borderColor?: string;
      backgroundColor?: string;
      tension?: number;
    }[];
  };
  title?: string;
  height?: number;
}

export function LineChart({ data, title, height = 300 }: LineChartProps) {
  const options: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: '#e5e7eb',
        },
      },
      title: {
        display: !!title,
        text: title,
        color: '#e5e7eb',
        font: {
          size: 16,
        },
      },
    },
    scales: {
      x: {
        ticks: { color: '#9ca3af' },
        grid: { color: '#374151' },
      },
      y: {
        ticks: { color: '#9ca3af' },
        grid: { color: '#374151' },
      },
    },
  };

  return (
    <div style={{ height }}>
      <Line data={data} options={options} />
    </div>
  );
}

interface BarChartProps {
  data: {
    labels: string[];
    datasets: {
      label: string;
      data: number[];
      backgroundColor?: string | string[];
      borderColor?: string | string[];
      borderWidth?: number;
    }[];
  };
  title?: string;
  height?: number;
  horizontal?: boolean;
}

export function BarChart({ data, title, height = 300, horizontal = false }: BarChartProps) {
  const options: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: horizontal ? 'y' : 'x',
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: '#e5e7eb',
        },
      },
      title: {
        display: !!title,
        text: title,
        color: '#e5e7eb',
        font: {
          size: 16,
        },
      },
    },
    scales: {
      x: {
        ticks: { color: '#9ca3af' },
        grid: { color: '#374151' },
      },
      y: {
        ticks: { color: '#9ca3af' },
        grid: { color: '#374151' },
      },
    },
  };

  return (
    <div style={{ height }}>
      <Bar data={data} options={options} />
    </div>
  );
}

interface PieChartProps {
  data: {
    labels: string[];
    datasets: {
      data: number[];
      backgroundColor?: string[];
      borderColor?: string[];
      borderWidth?: number;
    }[];
  };
  title?: string;
  height?: number;
}

export function PieChart({ data, title, height = 300 }: PieChartProps) {
  const options: ChartOptions<'pie'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
        labels: {
          color: '#e5e7eb',
        },
      },
      title: {
        display: !!title,
        text: title,
        color: '#e5e7eb',
        font: {
          size: 16,
        },
      },
    },
  };

  return (
    <div style={{ height }}>
      <Pie data={data} options={options} />
    </div>
  );
}

interface DoughnutChartProps {
  data: {
    labels: string[];
    datasets: {
      data: number[];
      backgroundColor?: string[];
      borderColor?: string[];
      borderWidth?: number;
    }[];
  };
  title?: string;
  height?: number;
  centerText?: string;
}

export function DoughnutChart({ data, title, height = 300, centerText }: DoughnutChartProps) {
  const options: ChartOptions<'doughnut'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
        labels: {
          color: '#e5e7eb',
        },
      },
      title: {
        display: !!title,
        text: title,
        color: '#e5e7eb',
        font: {
          size: 16,
        },
      },
    },
  };

  return (
    <div style={{ height }} className="relative">
      <Doughnut data={data} options={options} />
      {centerText && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center">
            <div className="text-2xl font-bold text-white">{centerText}</div>
          </div>
        </div>
      )}
    </div>
  );
}

// Utility function to generate color palettes
export const chartColors = {
  primary: ['#3b82f6', '#60a5fa', '#93c5fd', '#dbeafe'],
  success: ['#10b981', '#34d399', '#6ee7b7', '#d1fae5'],
  warning: ['#f59e0b', '#fbbf24', '#fcd34d', '#fef3c7'],
  danger: ['#ef4444', '#f87171', '#fca5a5', '#fee2e2'],
  purple: ['#8b5cf6', '#a78bfa', '#c4b5fd', '#ede9fe'],
  mixed: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'],
};
