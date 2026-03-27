import Dexie from 'https://unpkg.com/dexie@3.2.4/dist/dexie.mjs';

/**
 * Base de données locale offline-first N'Ka Wari via Dexie.js
 */
const nkaDB = new Dexie('nka-wari-db');

// Stores : table : id primaire
nkaDB.version(2).stores({
    karfa: 'id, date, status',
    dettes: 'id, date, status',
    comptes: 'id, date, status',
    queue: '++id, type, table, url, timestamp, status' // File d'attente
});

window.nkaDB = nkaDB;
export default nkaDB;
