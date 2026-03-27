import nkaDB from './db.js';

/**
 * Gestion de la synchronisation bidirectionnelle N'Ka Wari (PWA <-> Supabase via Django)
 */

window.addEventListener('online', () => {
    console.log('🌐 Connexion rétablie : Phase de synchronisation (IndexedDB -> Supabase)...');
    updateOnlineStatus(true);
    processQueue();
});

window.addEventListener('offline', () => {
    console.warn('⚡ Mode hors ligne activé.');
    updateOnlineStatus(false);
});

function updateOnlineStatus(isOnline) {
    const statusEl = document.getElementById('offline-indicator');
    if (statusEl) {
        statusEl.style.display = isOnline ? 'none' : 'flex';
    }
}

/**
 * Récupère le CSRF token natif de Django pour l'API
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Traite la file d'attente (Queue) et contacte l'Endpoint Supabase dédié
 * Implémente la gestion des conflits (Dernière écriture gagnante gérée par le Backend)
 */
async function processQueue() {
    if (!navigator.onLine) return;

    try {
        // Via Dexie.js (toArray)
        const queue = await nkaDB.queue.toArray();
        if (queue.length === 0) return;

        console.log(`🚀 Reprise de la synchronisation : ${queue.length} opérations en attente...`);

        // Important: l'URL ci-dessous doit être mappée par le développeur vers `sync_pwa_to_supabase`
        // Ex: path('api/sync-supabase/', sync_pwa_to_supabase) dans urls.py.
        const SYNC_EXPOSED_API = '/api/sync-supabase/'; 

        for (const op of queue) {
            try {
                // Construction du payload pour l'API intermédiaire Django -> Supabase
                const payload = {
                    type: op.type || 'CREATE',
                    table: op.table,
                    data: op.data
                };

                const response = await fetch(SYNC_EXPOSED_API, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    // Supprime avec succès de Dexie.js
                    await nkaDB.queue.delete(op.id);
                    console.log(`✅ Opération ${op.type} [${op.table}] synchronisée sur Supabase !`);
                } else {
                    console.warn(`✖️ Échec d'envoi pour l'opération ${op.id}, réponse serveur non KO. Reprise ultérieure.`);
                }
            } catch (err) {
                console.error("🛑 Perturbation réseau ou API inaccessible durant l'envoi. Pause de la Sync.", err);
                break; // Stop la boucle sur une erreur grave, on réessaie plus tard (Event 'online' ou refresh)
            }
        }
    } catch (err) {
        console.error("Erreur critique IndexedDB (Dexie) lors de l'accès à la Queue de sync", err);
    }
}

// Lancement au démarrage PWA
document.addEventListener('DOMContentLoaded', () => {
    updateOnlineStatus(navigator.onLine);
    if (navigator.onLine) {
        processQueue();
    }
});
