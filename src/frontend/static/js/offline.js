import nkaDB from './db.js';

/**
 * Interception des requêtes réseau
 * Capture automatiquement les appels fetch() en cas de déconnexion.
 */
const originalFetch = window.fetch;

window.fetch = async function(...args) {
    const [resource, config] = args;
    const urlStr = typeof resource === 'string' ? resource : (resource ? resource.url : '');
    const method = (config && config.method) ? config.method.toUpperCase() : 'GET';
    
    // Si en ligne, on laisse passer la requête normalement
    if (navigator.onLine) {
        return originalFetch.apply(this, args);
    }
    
    // Si la méthode n'est pas modifiante (GET), on laisse le Service Worker gérer le cache offline
    if (method === 'GET' || method === 'HEAD') {
        return originalFetch.apply(this, args);
    }

    console.warn("⚠️ Mode Hors-ligne : interception de la requête.");

    // Analyser le payload
    let data = {};
    if (config && config.body && typeof config.body === 'string') {
        try {
            data = JSON.parse(config.body);
        } catch(e) {
            console.error("Impossible de parser le body de la requête originelle.");
        }
    }

    // Déterminer l'action (Typing CRUD)
    let type = 'CREATE';
    if (method === 'PUT' || method === 'PATCH') type = 'UPDATE';
    if (method === 'DELETE') type = 'DELETE';
    
    // Le développeur (ou nous) peut injecter un type explicite dans data
    if (data.action_type) type = data.action_type;

    // Déduire la table (très utile pour la sync Django-Supabase)
    let table = data.table_name || 'unknown';
    if (urlStr.includes('karfa')) table = 'karfa';
    else if (urlStr.includes('dettes')) table = 'dettes';
    else if (urlStr.includes('comptes')) table = 'comptes';

    // Injection dans Dexie.js (file d'attente IndexedDB)
    await nkaDB.queue.add({
        type: type,
        table: table,
        data: data,
        url: urlStr,
        timestamp: Date.now(),
        status: 'pending'
    });
    
    console.log(`💾 Action ${type} sur la table [${table}] mise en file d'attente (IndexedDB).`);

    // Force une réponse 200 factice pour l'interface frontend (PWA) afin que l'UI réagisse comme si l'action avait réussi.
    return new Response(JSON.stringify({ 
        offline: true, 
        message: 'Action sauvegardée localement (prête à être synchronisée).',
        status: 'queued' 
    }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
    });
};

/**
 * Fonction helper explicite, pour les devs souhaitant bypasser le Wrapper fetch
 */
export async function addActionToSyncQueue(type, table, data) {
    if (!navigator.onLine) {
        await nkaDB.queue.add({
            type: type,
            table: table,
            data: data,
            timestamp: Date.now(),
            status: 'pending'
        });
        return true;
    }
    return false;
}
