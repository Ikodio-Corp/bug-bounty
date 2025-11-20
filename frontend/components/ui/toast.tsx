import * as React from 'react';

interface ToastProps {
  title: string;
  description?: string;
  variant?: 'default' | 'success' | 'error' | 'warning';
  duration?: number;
  onClose?: () => void;
}

export function Toast({ title, description, variant = 'default', duration = 5000, onClose }: ToastProps) {
  const [isVisible, setIsVisible] = React.useState(true);

  React.useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      onClose?.();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  if (!isVisible) return null;

  const variants = {
    default: 'bg-slate-800 border-slate-700',
    success: 'bg-green-800 border-green-700',
    error: 'bg-red-800 border-red-700',
    warning: 'bg-yellow-800 border-yellow-700',
  };

  return (
    <div className={`fixed bottom-4 right-4 p-4 rounded-lg border shadow-lg z-50 min-w-[300px] ${variants[variant]}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h4 className="font-semibold text-white mb-1">{title}</h4>
          {description && <p className="text-sm text-gray-300">{description}</p>}
        </div>
        <button
          onClick={() => {
            setIsVisible(false);
            onClose?.();
          }}
          className="text-gray-400 hover:text-white ml-4"
        >
          ✕
        </button>
      </div>
    </div>
  );
}

interface ToastContainerProps {
  children: React.ReactNode;
}

export function ToastContainer({ children }: ToastContainerProps) {
  return (
    <div className="fixed bottom-0 right-0 p-4 space-y-4 z-50">
      {children}
    </div>
  );
}
