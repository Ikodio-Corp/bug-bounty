// Service Worker for IKODIO BugBounty Platform PWA

const CACHE_NAME = 'ikodio-bugbounty-v1';
const RUNTIME_CACHE = 'ikodio-runtime-v1';

// Assets to cache on install
const PRECACHE_ASSETS = [
  '/',
  '/dashboard',
  '/bugs',
  '/scans',
  '/marketplace',
  '/offline',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png'
];

// API routes that should be network-first
const API_ROUTES = [
  '/api/auth',
  '/api/bugs',
  '/api/scans',
  '/api/users'
];

// Install event - cache critical assets
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Precaching assets');
        return cache.addAll(PRECACHE_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((cacheName) => {
            return cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE;
          })
          .map((cacheName) => {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip cross-origin requests
  if (url.origin !== location.origin) {
    return;
  }
  
  // API requests - Network first, fallback to cache
  if (API_ROUTES.some(route => url.pathname.startsWith(route))) {
    event.respondWith(networkFirst(request));
    return;
  }
  
  // HTML pages - Network first, fallback to cache
  if (request.mode === 'navigate') {
    event.respondWith(networkFirst(request));
    return;
  }
  
  // Static assets - Cache first, fallback to network
  event.respondWith(cacheFirst(request));
});

// Cache-first strategy
async function cacheFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);
  
  if (cached) {
    console.log('[Service Worker] Cache hit:', request.url);
    return cached;
  }
  
  try {
    const response = await fetch(request);
    
    // Cache successful responses
    if (response.ok) {
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.error('[Service Worker] Fetch failed:', error);
    
    // Return offline page for navigation requests
    if (request.mode === 'navigate') {
      return cache.match('/offline');
    }
    
    throw error;
  }
}

// Network-first strategy
async function networkFirst(request) {
  const cache = await caches.open(RUNTIME_CACHE);
  
  try {
    const response = await fetch(request);
    
    // Cache successful responses
    if (response.ok) {
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.error('[Service Worker] Network failed, trying cache:', error);
    
    const cached = await cache.match(request);
    
    if (cached) {
      console.log('[Service Worker] Serving from cache:', request.url);
      return cached;
    }
    
    // Return offline page for navigation requests
    if (request.mode === 'navigate') {
      return cache.match('/offline');
    }
    
    throw error;
  }
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('[Service Worker] Background sync:', event.tag);
  
  if (event.tag === 'sync-bugs') {
    event.waitUntil(syncBugs());
  } else if (event.tag === 'sync-scans') {
    event.waitUntil(syncScans());
  }
});

async function syncBugs() {
  try {
    const cache = await caches.open('offline-bugs');
    const requests = await cache.keys();
    
    for (const request of requests) {
      try {
        const response = await fetch(request);
        if (response.ok) {
          await cache.delete(request);
        }
      } catch (error) {
        console.error('[Service Worker] Sync failed for:', request.url);
      }
    }
  } catch (error) {
    console.error('[Service Worker] Bug sync failed:', error);
  }
}

async function syncScans() {
  try {
    const cache = await caches.open('offline-scans');
    const requests = await cache.keys();
    
    for (const request of requests) {
      try {
        const response = await fetch(request);
        if (response.ok) {
          await cache.delete(request);
        }
      } catch (error) {
        console.error('[Service Worker] Sync failed for:', request.url);
      }
    }
  } catch (error) {
    console.error('[Service Worker] Scan sync failed:', error);
  }
}

// Push notifications
self.addEventListener('push', (event) => {
  console.log('[Service Worker] Push received:', event);
  
  let data = {
    title: 'IKODIO Notification',
    body: 'You have a new notification',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png'
  };
  
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data.body = event.data.text();
    }
  }
  
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: data.icon,
      badge: data.badge,
      data: data.url,
      actions: data.actions || []
    })
  );
});

// Notification click
self.addEventListener('notificationclick', (event) => {
  console.log('[Service Worker] Notification clicked:', event);
  
  event.notification.close();
  
  const urlToOpen = event.notification.data || '/';
  
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        // Focus existing window if available
        for (const client of clientList) {
          if (client.url === urlToOpen && 'focus' in client) {
            return client.focus();
          }
        }
        
        // Open new window
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen);
        }
      })
  );
});

// Message handler
self.addEventListener('message', (event) => {
  console.log('[Service Worker] Message received:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CACHE_URLS') {
    event.waitUntil(
      caches.open(CACHE_NAME).then((cache) => {
        return cache.addAll(event.data.urls);
      })
    );
  }
  
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => caches.delete(cacheName))
        );
      })
    );
  }
});

// Periodic background sync
self.addEventListener('periodicsync', (event) => {
  console.log('[Service Worker] Periodic sync:', event.tag);
  
  if (event.tag === 'update-bugs') {
    event.waitUntil(updateBugsCache());
  } else if (event.tag === 'update-scans') {
    event.waitUntil(updateScansCache());
  }
});

async function updateBugsCache() {
  try {
    const response = await fetch('/api/bugs?limit=20');
    if (response.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      await cache.put('/api/bugs?limit=20', response);
    }
  } catch (error) {
    console.error('[Service Worker] Update bugs cache failed:', error);
  }
}

async function updateScansCache() {
  try {
    const response = await fetch('/api/scans?limit=20');
    if (response.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      await cache.put('/api/scans?limit=20', response);
    }
  } catch (error) {
    console.error('[Service Worker] Update scans cache failed:', error);
  }
}
