'use client';

import { useState } from 'react';
import { Button } from './button';

interface Column<T> {
  key: keyof T | string;
  header: string;
  sortable?: boolean;
  filterable?: boolean;
  render?: (value: any, row: T) => React.ReactNode;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  itemsPerPage?: number;
  searchable?: boolean;
  exportable?: boolean;
  onRowClick?: (row: T) => void;
}

export function DataTable<T extends Record<string, any>>({
  data,
  columns,
  itemsPerPage = 10,
  searchable = true,
  exportable = false,
  onRowClick,
}: DataTableProps<T>) {
  const [currentPage, setCurrentPage] = useState(1);
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<Record<string, string>>({});

  // Filter data
  let filteredData = [...data];

  // Apply search
  if (searchTerm) {
    filteredData = filteredData.filter((row) =>
      Object.values(row).some((value) =>
        String(value).toLowerCase().includes(searchTerm.toLowerCase())
      )
    );
  }

  // Apply column filters
  Object.entries(filters).forEach(([key, value]) => {
    if (value) {
      filteredData = filteredData.filter((row) =>
        String(row[key]).toLowerCase().includes(value.toLowerCase())
      );
    }
  });

  // Apply sorting
  if (sortColumn) {
    filteredData.sort((a, b) => {
      const aVal = a[sortColumn];
      const bVal = b[sortColumn];
      const direction = sortDirection === 'asc' ? 1 : -1;

      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return (aVal - bVal) * direction;
      }
      return String(aVal).localeCompare(String(bVal)) * direction;
    });
  }

  // Pagination
  const totalPages = Math.ceil(filteredData.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedData = filteredData.slice(startIndex, endIndex);

  const handleSort = (columnKey: string) => {
    if (sortColumn === columnKey) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(columnKey);
      setSortDirection('asc');
    }
  };

  const handleExport = () => {
    const csv = [
      columns.map((col) => col.header).join(','),
      ...filteredData.map((row) =>
        columns.map((col) => {
          const value = row[col.key as keyof T];
          return typeof value === 'string' && value.includes(',')
            ? `"${value}"`
            : value;
        }).join(',')
      ),
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'export.csv';
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex justify-between items-center gap-4">
        {searchable && (
          <div className="flex-1 max-w-md">
            <input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        )}

        <div className="flex gap-2">
          {exportable && (
            <Button onClick={handleExport} variant="outline" size="sm">
              Export CSV
            </Button>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto border border-slate-700 rounded-lg">
        <table className="w-full">
          <thead className="bg-slate-800">
            <tr>
              {columns.map((column) => (
                <th
                  key={String(column.key)}
                  className="px-4 py-3 text-left text-sm font-semibold text-gray-300"
                >
                  <div className="flex items-center gap-2">
                    <span>{column.header}</span>
                    {column.sortable && (
                      <button
                        onClick={() => handleSort(String(column.key))}
                        className="hover:text-blue-400 transition-colors"
                      >
                        {sortColumn === column.key ? (
                          sortDirection === 'asc' ? '↑' : '↓'
                        ) : (
                          '↕'
                        )}
                      </button>
                    )}
                  </div>
                  {column.filterable && (
                    <input
                      type="text"
                      placeholder="Filter..."
                      value={filters[String(column.key)] || ''}
                      onChange={(e) => {
                        setFilters({
                          ...filters,
                          [String(column.key)]: e.target.value,
                        });
                        setCurrentPage(1);
                      }}
                      className="mt-2 w-full px-2 py-1 text-xs bg-slate-900 border border-slate-600 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                      onClick={(e) => e.stopPropagation()}
                    />
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-slate-900 divide-y divide-slate-800">
            {paginatedData.length > 0 ? (
              paginatedData.map((row, rowIndex) => (
                <tr
                  key={rowIndex}
                  onClick={() => onRowClick?.(row)}
                  className={`hover:bg-slate-800 transition-colors ${
                    onRowClick ? 'cursor-pointer' : ''
                  }`}
                >
                  {columns.map((column) => (
                    <td
                      key={String(column.key)}
                      className="px-4 py-3 text-sm text-gray-300"
                    >
                      {column.render
                        ? column.render(row[column.key as keyof T], row)
                        : String(row[column.key as keyof T])}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan={columns.length}
                  className="px-4 py-8 text-center text-gray-500"
                >
                  No data found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-400">
            Showing {startIndex + 1} to {Math.min(endIndex, filteredData.length)} of{' '}
            {filteredData.length} entries
          </div>
          <div className="flex gap-2">
            <Button
              onClick={() => setCurrentPage(currentPage - 1)}
              disabled={currentPage === 1}
              variant="outline"
              size="sm"
            >
              Previous
            </Button>
            <div className="flex gap-1">
              {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                let pageNum;
                if (totalPages <= 5) {
                  pageNum = i + 1;
                } else if (currentPage <= 3) {
                  pageNum = i + 1;
                } else if (currentPage >= totalPages - 2) {
                  pageNum = totalPages - 4 + i;
                } else {
                  pageNum = currentPage - 2 + i;
                }

                return (
                  <Button
                    key={i}
                    onClick={() => setCurrentPage(pageNum)}
                    variant={currentPage === pageNum ? 'default' : 'outline'}
                    size="sm"
                  >
                    {pageNum}
                  </Button>
                );
              })}
            </div>
            <Button
              onClick={() => setCurrentPage(currentPage + 1)}
              disabled={currentPage === totalPages}
              variant="outline"
              size="sm"
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
