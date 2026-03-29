// Bypass Cache - SW Update
const CACHE_NAME = 'nkawari-cache-v-kill';

self.addEventListener('install', event => {
    // Force le nouveau Service Worker à s'installer immédiatement
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    // Nettoie TOUS les anciens caches au moment de l'activation
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.map(key => caches.delete(key))
            );
        }).then(() => {
            // Prend le contrôle immédiat des pages ouvertes
            return self.clients.claim();
        })
    );
});

self.addEventListener('fetch', event => {
    // Ne rien mettre en cache ! On force la requête réseau.
    // Si la requête échoue (hors ligne), on laisse l'erreur se propager.
    event.respondWith(fetch(event.request));
});
