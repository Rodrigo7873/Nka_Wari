/**
 * Gestion de la base de données locale IndexedDB pour N'Ka Wari
 */
const DB_NAME = 'nka-wari-db';
const DB_VERSION = 1;

class NKaWariDB {
    constructor() {
        this.db = null;
    }

    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(DB_NAME, DB_VERSION);

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                // Stores pour la lecture hors ligne
                if (!db.objectStoreNames.contains('karfa')) db.createObjectStore('karfa', { keyPath: 'id' });
                if (!db.objectStoreNames.contains('dettes')) db.createObjectStore('dettes', { keyPath: 'id' });
                if (!db.objectStoreNames.contains('comptes')) db.createObjectStore('comptes', { keyPath: 'id' });
                
                // File d'attente pour la synchronisation (écriture hors ligne)
                if (!db.objectStoreNames.contains('queue')) {
                    db.createObjectStore('queue', { keyPath: 'id', autoIncrement: true });
                }
            };

            request.onsuccess = (event) => {
                this.db = event.target.result;
                resolve(this.db);
            };

            request.onerror = (event) => reject(event.target.error);
        });
    }

    async add(storeName, data) {
        if (!this.db) await this.init();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.put(data);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async getAll(storeName) {
        if (!this.db) await this.init();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.getAll();
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async delete(storeName, id) {
        if (!this.db) await this.init();
        const transaction = this.db.transaction([storeName], 'readwrite');
        transaction.objectStore(storeName).delete(id);
    }
}

const nkaDB = new NKaWariDB();
window.nkaDB = nkaDB; // Rendre accessible globalement
