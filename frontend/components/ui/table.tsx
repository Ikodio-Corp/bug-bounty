import * as React from 'react'

interface TableProps extends React.HTMLAttributes<HTMLTableElement> {
  children: React.ReactNode
}

export function Table({ children, className = '', ...props }: TableProps) {
  return (
    <div className="relative w-full overflow-auto">
      <table className={`w-full caption-bottom text-sm ${className}`} {...props}>
        {children}
      </table>
    </div>
  )
}

interface TableHeaderProps extends React.HTMLAttributes<HTMLTableSectionElement> {
  children: React.ReactNode
}

export function TableHeader({ children, className = '', ...props }: TableHeaderProps) {
  return (
    <thead className={`bg-slate-700 ${className}`} {...props}>
      {children}
    </thead>
  )
}

interface TableBodyProps extends React.HTMLAttributes<HTMLTableSectionElement> {
  children: React.ReactNode
}

export function TableBody({ children, className = '', ...props }: TableBodyProps) {
  return (
    <tbody className={`divide-y divide-slate-700 ${className}`} {...props}>
      {children}
    </tbody>
  )
}

interface TableRowProps extends React.HTMLAttributes<HTMLTableRowElement> {
  children: React.ReactNode
}

export function TableRow({ children, className = '', ...props }: TableRowProps) {
  return (
    <tr className={`hover:bg-slate-700/50 transition-colors ${className}`} {...props}>
      {children}
    </tr>
  )
}

interface TableHeadProps extends React.ThHTMLAttributes<HTMLTableCellElement> {
  children: React.ReactNode
}

export function TableHead({ children, className = '', ...props }: TableHeadProps) {
  return (
    <th
      className={`px-6 py-4 text-left text-sm font-semibold text-slate-300 ${className}`}
      {...props}
    >
      {children}
    </th>
  )
}

interface TableCellProps extends React.TdHTMLAttributes<HTMLTableCellElement> {
  children: React.ReactNode
}

export function TableCell({ children, className = '', ...props }: TableCellProps) {
  return (
    <td className={`px-6 py-4 ${className}`} {...props}>
      {children}
    </td>
  )
}
