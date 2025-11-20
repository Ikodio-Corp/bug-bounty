import * as React from 'react'

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'success' | 'warning' | 'error'
  children: React.ReactNode
}

export function Alert({ variant = 'default', children, className = '', ...props }: AlertProps) {
  const variants = {
    default: 'bg-slate-800 border-slate-700 text-slate-300',
    success: 'bg-green-900/20 border-green-500/50 text-green-400',
    warning: 'bg-yellow-900/20 border-yellow-500/50 text-yellow-400',
    error: 'bg-red-900/20 border-red-500/50 text-red-400'
  }

  return (
    <div
      className={`relative w-full rounded-lg border p-4 ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

interface AlertTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode
}

export function AlertTitle({ children, className = '', ...props }: AlertTitleProps) {
  return (
    <h5 className={`mb-1 font-medium leading-none tracking-tight ${className}`} {...props}>
      {children}
    </h5>
  )
}

interface AlertDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children: React.ReactNode
}

export function AlertDescription({ children, className = '', ...props }: AlertDescriptionProps) {
  return (
    <div className={`text-sm opacity-90 ${className}`} {...props}>
      {children}
    </div>
  )
}
