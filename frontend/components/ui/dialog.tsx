import * as React from 'react'

interface DialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  children: React.ReactNode
}

export function Dialog({ open, onOpenChange, children }: DialogProps) {
  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="fixed inset-0 bg-black/50"
        onClick={() => onOpenChange(false)}
      />
      <div className="relative z-50">{children}</div>
    </div>
  )
}

interface DialogContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export function DialogContent({ children, className = '', ...props }: DialogContentProps) {
  return (
    <div
      className={`bg-slate-800 rounded-xl p-8 max-w-md w-full mx-4 shadow-xl border border-slate-700 ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

interface DialogHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export function DialogHeader({ children, className = '', ...props }: DialogHeaderProps) {
  return (
    <div className={`flex flex-col space-y-1.5 mb-4 ${className}`} {...props}>
      {children}
    </div>
  )
}

interface DialogTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode
}

export function DialogTitle({ children, className = '', ...props }: DialogTitleProps) {
  return (
    <h2 className={`text-2xl font-bold text-white ${className}`} {...props}>
      {children}
    </h2>
  )
}

interface DialogDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children: React.ReactNode
}

export function DialogDescription({ children, className = '', ...props }: DialogDescriptionProps) {
  return (
    <p className={`text-slate-400 ${className}`} {...props}>
      {children}
    </p>
  )
}

interface DialogFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export function DialogFooter({ children, className = '', ...props }: DialogFooterProps) {
  return (
    <div className={`flex gap-4 mt-6 ${className}`} {...props}>
      {children}
    </div>
  )
}
