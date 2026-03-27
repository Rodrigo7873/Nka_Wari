const CACHE_NAME = 'nkawari-cache-v2';

const STATIC_ASSETS = [
    '/',
    '/offline/',
    '/static/manifest.json',
    '/static/css/base.css',
    '/static/css/core.css',
    '/static/js/db.js',
    '/static/js/sync.js',
    '/static/icons/icon-72x72.png',
    '/static/icons/icon-96x96.png',
    '/static/icons/icon-128x128.png',
    '/static/icons/icon-144x144.png',
    '/static/icons/icon-152x152.png',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-256x256.png',
    '/static/icons/icon-512x512.png',
    '/static/images/logo.jpg'
];

// Installation du Service Worker
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('SW: Pre-caching assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => self.skipWaiting())
    );
});

// Activation et nettoyage des anciens caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.filter(key => key !== CACHE_NAME)
                    .map(key => caches.delete(key))
            );
        }).then(() => self.clients.claim())
    );
});

// Stratégie Stale-While-Revalidate
self.addEventListener('fetch', event => {
    if (event.request.method !== 'GET') return;

    event.respondWith(
        caches.open(CACHE_NAME).then(cache => {
            return cache.match(event.request).then(cachedResponse => {
                const fetchedResponse = fetch(event.request).then(networkResponse => {
                    if (networkResponse.ok) {
                        cache.put(event.request, networkResponse.clone());
                    }
                    return networkResponse;
                }).catch(() => {
                    // Hors ligne
                    return cachedResponse || caches.match('/offline/');
                });

                return cachedResponse || fetchedResponse;
            });
        })
    );
});
