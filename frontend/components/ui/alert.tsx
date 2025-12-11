import * as React from 'react'

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'success' | 'warning' | 'error'
  children: React.ReactNode
}

export function Alert({ variant = 'default', children, className = '', ...props }: AlertProps) {
  const variants = {
    default: 'bg-slate-800 border-slate-700 text-slate-300',
    success: 'bg-gray-700 border-gray-600 text-white',
    warning: 'bg-gray-600 border-gray-500 text-white',
    error: 'bg-gray-800 border-gray-700 text-white'
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
