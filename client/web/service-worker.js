/**
 * HoneyNet Progressive Web App Service Worker
 * שירות עובד מתקדם לאפליקציית רשת מתקדמת
 */

const CACHE_NAME = 'honeynet-v1.2.0';
const STATIC_CACHE = 'honeynet-static-v1.2.0';
const DYNAMIC_CACHE = 'honeynet-dynamic-v1.2.0';
const API_CACHE = 'honeynet-api-v1.2.0';

// Files to cache immediately
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/manifest.json',
    '/css/style.css',
    '/css/dashboard.css',
    '/js/app.js',
    '/js/dashboard.js',
    '/js/threat-monitor.js',
    '/images/logo-192.png',
    '/images/logo-512.png',
    '/images/favicon.ico',
    '/fonts/inter-regular.woff2',
    '/fonts/inter-bold.woff2'
];

// API endpoints to cache
const API_ENDPOINTS = [
    '/api/dashboard/stats',
    '/api/threats/recent',
    '/api/honeypots/status',
    '/api/system/health'
];

// Cache strategies
const CACHE_STRATEGIES = {
    CACHE_FIRST: 'cache-first',
    NETWORK_FIRST: 'network-first',
    STALE_WHILE_REVALIDATE: 'stale-while-revalidate',
    NETWORK_ONLY: 'network-only',
    CACHE_ONLY: 'cache-only'
};

// Install event - cache static assets
self.addEventListener('install', event => {
    console.log('🔧 Service Worker installing...');
    
    event.waitUntil(
        Promise.all([
            // Cache static assets
            caches.open(STATIC_CACHE).then(cache => {
                console.log('📦 Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            }),
            
            // Skip waiting to activate immediately
            self.skipWaiting()
        ])
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('✅ Service Worker activated');
    
    event.waitUntil(
        Promise.all([
            // Clean up old caches
            caches.keys().then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE && 
                            cacheName !== DYNAMIC_CACHE && 
                            cacheName !== API_CACHE) {
                            console.log('🗑️ Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            }),
            
            // Take control of all clients
            self.clients.claim()
        ])
    );
});

// Fetch event - handle network requests
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Handle different types of requests
    if (url.pathname.startsWith('/api/')) {
        // API requests - network first with cache fallback
        event.respondWith(handleApiRequest(request));
    } else if (STATIC_ASSETS.includes(url.pathname)) {
        // Static assets - cache first
        event.respondWith(handleStaticRequest(request));
    } else if (url.pathname.endsWith('.js') || 
               url.pathname.endsWith('.css') || 
               url.pathname.endsWith('.png') || 
               url.pathname.endsWith('.jpg') || 
               url.pathname.endsWith('.svg')) {
        // Other assets - stale while revalidate
        event.respondWith(handleAssetRequest(request));
    } else {
        // HTML pages - network first with cache fallback
        event.respondWith(handlePageRequest(request));
    }
});

// Handle API requests with network-first strategy
async function handleApiRequest(request) {
    const url = new URL(request.url);
    
    try {
        // Try network first
        const networkResponse = await fetch(request.clone());
        
        if (networkResponse.ok) {
            // Cache successful API responses (with TTL)
            const cache = await caches.open(API_CACHE);
            const responseClone = networkResponse.clone();
            
            // Add timestamp for TTL
            const responseWithTimestamp = new Response(responseClone.body, {
                status: responseClone.status,
                statusText: responseClone.statusText,
                headers: {
                    ...Object.fromEntries(responseClone.headers.entries()),
                    'sw-cached-at': Date.now().toString()
                }
            });
            
            await cache.put(request, responseWithTimestamp);
            return networkResponse;
        }
    } catch (error) {
        console.warn('🌐 Network request failed, trying cache:', error);
    }
    
    // Fallback to cache
    const cache = await caches.open(API_CACHE);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
        // Check if cached response is still valid (5 minutes TTL)
        const cachedAt = cachedResponse.headers.get('sw-cached-at');
        const now = Date.now();
        const fiveMinutes = 5 * 60 * 1000;
        
        if (cachedAt && (now - parseInt(cachedAt)) < fiveMinutes) {
            console.log('📋 Serving fresh cached API response');
            return cachedResponse;
        } else {
            console.log('⏰ Cached API response expired, serving stale data');
            // Return stale data but mark it as such
            const staleResponse = new Response(cachedResponse.body, {
                status: cachedResponse.status,
                statusText: cachedResponse.statusText,
                headers: {
                    ...Object.fromEntries(cachedResponse.headers.entries()),
                    'sw-stale': 'true'
                }
            });
            return staleResponse;
        }
    }
    
    // Return offline response for critical endpoints
    if (url.pathname.includes('/dashboard/stats')) {
        return new Response(JSON.stringify({
            status: 'offline',
            message: 'Dashboard data unavailable offline',
            cached_data: null
        }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' }
        });
    }
    
    return new Response('Offline - API unavailable', { status: 503 });
}

// Handle static requests with cache-first strategy
async function handleStaticRequest(request) {
    const cache = await caches.open(STATIC_CACHE);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
        console.log('📦 Serving from static cache:', request.url);
        return cachedResponse;
    }
    
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            await cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.error('❌ Failed to fetch static asset:', error);
        return new Response('Asset unavailable offline', { status: 503 });
    }
}

// Handle asset requests with stale-while-revalidate strategy
async function handleAssetRequest(request) {
    const cache = await caches.open(DYNAMIC_CACHE);
    const cachedResponse = await cache.match(request);
    
    // Return cached version immediately if available
    if (cachedResponse) {
        console.log('🔄 Serving from cache, updating in background:', request.url);
        
        // Update cache in background
        fetch(request).then(networkResponse => {
            if (networkResponse.ok) {
                cache.put(request, networkResponse.clone());
            }
        }).catch(error => {
            console.warn('Background update failed:', error);
        });
        
        return cachedResponse;
    }
    
    // No cached version, fetch from network
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            await cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        return new Response('Asset unavailable', { status: 503 });
    }
}

// Handle page requests with network-first strategy
async function handlePageRequest(request) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            await cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.warn('🌐 Network failed for page, trying cache');
        
        const cache = await caches.open(DYNAMIC_CACHE);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page
        return new Response(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>HoneyNet - Offline</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        text-align: center;
                    }
                    .offline-icon {
                        font-size: 4rem;
                        margin-bottom: 1rem;
                    }
                    .offline-title {
                        font-size: 2rem;
                        margin-bottom: 1rem;
                        font-weight: 600;
                    }
                    .offline-message {
                        font-size: 1.1rem;
                        opacity: 0.9;
                        max-width: 500px;
                        line-height: 1.6;
                    }
                    .retry-button {
                        margin-top: 2rem;
                        padding: 12px 24px;
                        background: rgba(255, 255, 255, 0.2);
                        border: 2px solid rgba(255, 255, 255, 0.3);
                        border-radius: 8px;
                        color: white;
                        font-size: 1rem;
                        cursor: pointer;
                        transition: all 0.3s ease;
                    }
                    .retry-button:hover {
                        background: rgba(255, 255, 255, 0.3);
                        border-color: rgba(255, 255, 255, 0.5);
                    }
                </style>
            </head>
            <body>
                <div class="offline-icon">🛡️</div>
                <h1 class="offline-title">HoneyNet - Offline Mode</h1>
                <p class="offline-message">
                    You're currently offline. Some features may not be available, 
                    but cached data is still accessible. Check your connection and try again.
                </p>
                <button class="retry-button" onclick="window.location.reload()">
                    Try Again
                </button>
            </body>
            </html>
        `, {
            status: 200,
            headers: { 'Content-Type': 'text/html' }
        });
    }
}

// Background sync for offline actions
self.addEventListener('sync', event => {
    console.log('🔄 Background sync triggered:', event.tag);
    
    if (event.tag === 'threat-report') {
        event.waitUntil(syncThreatReports());
    } else if (event.tag === 'analytics-data') {
        event.waitUntil(syncAnalyticsData());
    }
});

// Sync threat reports when back online
async function syncThreatReports() {
    try {
        // Get pending reports from IndexedDB
        const pendingReports = await getPendingThreatReports();
        
        for (const report of pendingReports) {
            try {
                const response = await fetch('/api/threats/report', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(report.data)
                });
                
                if (response.ok) {
                    await removePendingThreatReport(report.id);
                    console.log('✅ Synced threat report:', report.id);
                }
            } catch (error) {
                console.error('❌ Failed to sync threat report:', error);
            }
        }
    } catch (error) {
        console.error('❌ Background sync failed:', error);
    }
}

// Sync analytics data when back online
async function syncAnalyticsData() {
    try {
        const pendingAnalytics = await getPendingAnalyticsData();
        
        for (const analytics of pendingAnalytics) {
            try {
                const response = await fetch('/api/analytics/events', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(analytics.data)
                });
                
                if (response.ok) {
                    await removePendingAnalyticsData(analytics.id);
                    console.log('✅ Synced analytics data:', analytics.id);
                }
            } catch (error) {
                console.error('❌ Failed to sync analytics:', error);
            }
        }
    } catch (error) {
        console.error('❌ Analytics sync failed:', error);
    }
}

// Push notification handling
self.addEventListener('push', event => {
    console.log('📱 Push notification received');
    
    const options = {
        body: 'New security threat detected!',
        icon: '/images/logo-192.png',
        badge: '/images/badge-72.png',
        vibrate: [200, 100, 200],
        data: {
            url: '/dashboard'
        },
        actions: [
            {
                action: 'view',
                title: 'View Details',
                icon: '/images/view-icon.png'
            },
            {
                action: 'dismiss',
                title: 'Dismiss',
                icon: '/images/dismiss-icon.png'
            }
        ]
    };
    
    if (event.data) {
        try {
            const data = event.data.json();
            options.body = data.message || options.body;
            options.data = { ...options.data, ...data };
        } catch (error) {
            console.error('Failed to parse push data:', error);
        }
    }
    
    event.waitUntil(
        self.registration.showNotification('HoneyNet Security Alert', options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
    console.log('🔔 Notification clicked:', event.action);
    
    event.notification.close();
    
    if (event.action === 'view' || !event.action) {
        const url = event.notification.data?.url || '/dashboard';
        
        event.waitUntil(
            clients.matchAll({ type: 'window' }).then(clientList => {
                // Check if app is already open
                for (const client of clientList) {
                    if (client.url.includes(url) && 'focus' in client) {
                        return client.focus();
                    }
                }
                
                // Open new window
                if (clients.openWindow) {
                    return clients.openWindow(url);
                }
            })
        );
    }
});

// Message handling from main thread
self.addEventListener('message', event => {
    console.log('💬 Message received:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    } else if (event.data && event.data.type === 'GET_VERSION') {
        event.ports[0].postMessage({ version: CACHE_NAME });
    } else if (event.data && event.data.type === 'CLEAR_CACHE') {
        clearAllCaches().then(() => {
            event.ports[0].postMessage({ success: true });
        });
    }
});

// Utility functions for IndexedDB operations
async function getPendingThreatReports() {
    // Simplified - in real implementation would use IndexedDB
    return [];
}

async function removePendingThreatReport(id) {
    // Simplified - in real implementation would use IndexedDB
    return true;
}

async function getPendingAnalyticsData() {
    // Simplified - in real implementation would use IndexedDB
    return [];
}

async function removePendingAnalyticsData(id) {
    // Simplified - in real implementation would use IndexedDB
    return true;
}

async function clearAllCaches() {
    const cacheNames = await caches.keys();
    return Promise.all(
        cacheNames.map(cacheName => caches.delete(cacheName))
    );
}

console.log('🚀 HoneyNet Service Worker loaded successfully');
