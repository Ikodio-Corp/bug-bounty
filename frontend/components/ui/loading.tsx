import * as React from 'react'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function LoadingSpinner({ size = 'md', className = '' }: LoadingSpinnerProps) {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  }

  return (
    <div className={`${sizes[size]} ${className}`}>
      <div className="animate-spin rounded-full border-4 border-slate-700 border-t-cyan-500 h-full w-full" />
    </div>
  )
}

interface LoadingProps {
  text?: string
}

export function Loading({ text = 'Loading...' }: LoadingProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <LoadingSpinner size="lg" />
      <p className="mt-4 text-slate-400">{text}</p>
    </div>
  )
}

export function LoadingOverlay() {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-xl p-8 flex flex-col items-center">
        <LoadingSpinner size="lg" />
        <p className="mt-4 text-white">Processing...</p>
      </div>
    </div>
  )
}
