'use client';

import { useMobile } from '@/hooks/useMobile';

interface Column {
  key: string;
  label: string;
  render?: (value: any, row: any) => React.ReactNode;
  mobileHide?: boolean;
}

interface ResponsiveTableProps {
  columns: Column[];
  data: any[];
  keyField?: string;
  onRowClick?: (row: any) => void;
}

export default function ResponsiveTable({
  columns,
  data,
  keyField = 'id',
  onRowClick,
}: ResponsiveTableProps) {
  const { isMobile } = useMobile();

  if (isMobile) {
    // Card layout for mobile
    return (
      <div className="space-y-4">
        {data.map((row, index) => (
          <div
            key={row[keyField] || index}
            onClick={() => onRowClick?.(row)}
            className={`
              bg-gray-800 rounded-lg p-4 space-y-2
              ${onRowClick ? 'cursor-pointer hover:bg-gray-700' : ''}
            `}
          >
            {columns
              .filter(col => !col.mobileHide)
              .map((col) => (
                <div key={col.key} className="flex justify-between items-start">
                  <span className="text-gray-400 text-sm font-medium">
                    {col.label}:
                  </span>
                  <span className="text-white text-sm text-right ml-2">
                    {col.render ? col.render(row[col.key], row) : row[col.key]}
                  </span>
                </div>
              ))}
          </div>
        ))}
      </div>
    );
  }

  // Traditional table for desktop
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-800 border-b border-gray-700">
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                className="px-4 py-3 text-left text-sm font-medium text-gray-300"
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-800">
          {data.map((row, index) => (
            <tr
              key={row[keyField] || index}
              onClick={() => onRowClick?.(row)}
              className={`
                hover:bg-gray-800
                ${onRowClick ? 'cursor-pointer' : ''}
              `}
            >
              {columns.map((col) => (
                <td key={col.key} className="px-4 py-3 text-sm text-gray-300">
                  {col.render ? col.render(row[col.key], row) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
