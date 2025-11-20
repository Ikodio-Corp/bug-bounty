import * as React from 'react'

interface SimpleCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export function SimpleCard({ children, className = '', ...props }: SimpleCardProps) {
  return (
    <div
      className={`rounded-lg border border-slate-700 bg-slate-800 text-slate-50 shadow-sm ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

interface SimpleCardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export function SimpleCardHeader({ children, className = '', ...props }: SimpleCardHeaderProps) {
  return (
    <div className={`flex flex-col space-y-1.5 p-6 ${className}`} {...props}>
      {children}
    </div>
  )
}

interface SimpleCardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode
}

export function SimpleCardTitle({ children, className = '', ...props }: SimpleCardTitleProps) {
  return (
    <h3
      className={`text-2xl font-semibold leading-none tracking-tight ${className}`}
      {...props}
    >
      {children}
    </h3>
  )
}

interface SimpleCardDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children: React.ReactNode
}

export function SimpleCardDescription({ children, className = '', ...props }: SimpleCardDescriptionProps) {
  return (
    <p className={`text-sm text-slate-400 ${className}`} {...props}>
      {children}
    </p>
  )
}

interface SimpleCardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export function SimpleCardContent({ children, className = '', ...props }: SimpleCardContentProps) {
  return (
    <div className={`p-6 pt-0 ${className}`} {...props}>
      {children}
    </div>
  )
}
