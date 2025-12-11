'use client';

import { useEffect, useState } from 'react';
import { useWebSocket } from '@/lib/hooks/useWebSocket';
import { SimpleCard } from '@/components/ui/simple-card';
import { SimpleBadge } from '@/components/ui/simple-badge';

interface RealtimeNotification {
  id: string;
  type: 'scan_complete' | 'bug_found' | 'system' | 'payment' | 'guild';
  title: string;
  message: string;
  timestamp: string;
  severity: 'info' | 'warning' | 'success' | 'error';
  data?: any;
}

export function RealtimeNotifications() {
  const [notifications, setNotifications] = useState<RealtimeNotification[]>([]);
  const [showPanel, setShowPanel] = useState(false);

  const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';
  
  const { isConnected, lastMessage } = useWebSocket(wsUrl, {
    onMessage: (data) => {
      if (data.type === 'notification') {
        const notification: RealtimeNotification = {
          id: data.id || Date.now().toString(),
          type: data.notification_type,
          title: data.title,
          message: data.message,
          timestamp: data.timestamp || new Date().toISOString(),
          severity: data.severity || 'info',
          data: data.data,
        };
        
        setNotifications((prev) => [notification, ...prev.slice(0, 49)]);
        
        // Show browser notification if permitted
        if (Notification.permission === 'granted') {
          new Notification(notification.title, {
            body: notification.message,
            icon: '/icon.png',
          });
        }
      }
    },
    reconnect: true,
    reconnectAttempts: 10,
  });

  useEffect(() => {
    // Request notification permission
    if (Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'success': return 'success';
      case 'error': return 'error';
      case 'warning': return 'warning';
      case 'info': return 'info';
      default: return 'default';
    }
  };

  const unreadCount = notifications.length;

  return (
    <>
      {/* Notification Bell */}
      <div className="relative">
        <button
          onClick={() => setShowPanel(!showPanel)}
          className="relative p-2 text-gray-400 hover:text-white transition-colors"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
            />
          </svg>
          {unreadCount > 0 && (
            <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
              {unreadCount > 99 ? '99+' : unreadCount}
            </span>
          )}
        </button>

        {/* WebSocket Status Indicator */}
        <div className={`absolute bottom-0 right-0 w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
      </div>

      {/* Notification Panel */}
      {showPanel && (
        <div className="absolute right-0 mt-2 w-96 max-h-96 overflow-y-auto bg-slate-900 border border-slate-700 rounded-lg shadow-xl z-50">
          <div className="p-4 border-b border-slate-700 flex justify-between items-center">
            <h3 className="font-semibold">Notifications</h3>
            <SimpleBadge variant={isConnected ? 'success' : 'error'}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </SimpleBadge>
          </div>

          <div className="max-h-80 overflow-y-auto">
            {notifications.length > 0 ? (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  className="p-4 border-b border-slate-800 hover:bg-slate-800 transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <SimpleBadge variant={getSeverityColor(notification.severity)}>
                      {notification.type}
                    </SimpleBadge>
                    <span className="text-xs text-gray-500">
                      {new Date(notification.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <h4 className="font-medium mb-1">{notification.title}</h4>
                  <p className="text-sm text-gray-400">{notification.message}</p>
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-gray-500">
                No notifications yet
              </div>
            )}
          </div>

          {notifications.length > 0 && (
            <div className="p-3 border-t border-slate-700">
              <button
                onClick={() => setNotifications([])}
                className="w-full text-sm text-gray-400 hover:text-gray-300 transition-colors"
              >
                Clear all
              </button>
            </div>
          )}
        </div>
      )}
    </>
  );
}
