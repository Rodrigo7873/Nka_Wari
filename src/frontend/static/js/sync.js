/**
 * Gestion de la synchronisation N'Ka Wari
 */
window.addEventListener('online', () => {
    console.log('Connexion rétablie : Synchronisation en cours...');
    processQueue();
    updateOnlineStatus(true);
});

window.addEventListener('offline', () => {
    console.log('Mode hors ligne activé.');
    updateOnlineStatus(false);
});

function updateOnlineStatus(isOnline) {
    const statusEl = document.getElementById('offline-indicator');
    if (statusEl) {
        statusEl.style.display = isOnline ? 'none' : 'flex';
    }
}

/**
 * Traite la file d'attente des opérations effectuées hors ligne
 */
async function processQueue() {
    if (!navigator.onLine) return;

    try {
        const queue = await window.nkaDB.getAll('queue');
        if (queue.length === 0) return;

        console.log(`Début de la synchronisation de ${queue.length} opérations...`);

        for (const op of queue) {
            try {
                const response = await fetch(op.url, {
                    method: op.method || 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(op.data)
                });

                if (response.ok) {
                    await window.nkaDB.delete('queue', op.id);
                    console.log(`Opération synchronisée : ${op.url}`);
                }
            } catch (err) {
                console.error('Erreur lors de la synchronisation d\'une opération', err);
                break; // Arrête si erreur réseau
            }
        }
    } catch (err) {
        console.error('Erreur de lecture de la file d\'attente', err);
    }
}

/**
 * Ajoute une opération à la file d'attente si hors ligne
 */
async function queueOfflineAction(url, data, method = 'POST') {
    if (window.nkaDB) {
        await window.nkaDB.add('queue', {
            url,
            data,
            method,
            timestamp: Date.now()
        });
        console.log('Action ajoutée à la file d\'attente hors ligne.');
    }
}

// Initialisation au chargement
document.addEventListener('DOMContentLoaded', () => {
    updateOnlineStatus(navigator.onLine);
    if (navigator.onLine) processQueue();
});
