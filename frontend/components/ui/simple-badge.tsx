import * as React from 'react'

interface SimpleBadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info' | 'destructive' | 'outline'
  children: React.ReactNode
}

export function SimpleBadge({ variant = 'default', children, className = '', ...props }: SimpleBadgeProps) {
  const variants = {
    default: 'bg-slate-700 text-slate-300',
    success: 'bg-green-500/20 text-green-400',
    warning: 'bg-yellow-500/20 text-yellow-400',
    error: 'bg-red-500/20 text-red-400',
    info: 'bg-blue-500/20 text-blue-400',
    destructive: 'bg-red-600/20 text-red-500',
    outline: 'border border-slate-600 text-slate-400'
  }

  return (
    <div
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

