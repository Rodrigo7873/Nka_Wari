// UI and Dashboard functions for N'Ka Wari
console.log("app.js initializing...");

// 1️⃣ Système de Notification (Toasts) Moderne
window.showToast = function(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    // Anti-Spam: Ne pas ajouter si le même message est déjà affiché
    const existingToasts = container.querySelectorAll('.toast');
    for (let t of existingToasts) {
        if (t.innerText.includes(message)) return;
    }

    // Gestion du nombre maximum (ex: 3)
    if (existingToasts.length >= 3) {
        existingToasts[0].classList.add('hide');
        setTimeout(() => existingToasts[0].remove(), 300);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = '🔔';
    if(type === 'success') icon = '✅';
    if(type === 'error') icon = '❌';
    if(type === 'warning') icon = '⚠️';

    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    
    toast.onclick = () => {
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 400);
    };

    container.appendChild(toast);

    setTimeout(() => {
        if(toast.parentElement) {
            toast.classList.add('hide');
            setTimeout(() => toast.remove(), 400);
        }
    }, 3500);
};

// Override standard alert for a better feel (Optional but recommended)
// window.alert = (msg) => window.showToast(msg, 'info');

// 2️⃣ Actions du Dashboard
window.createKarfa = function() {
    window.showToast("Ouverture de l'interface Karfa...", "success");
    // Logique à implémenter pour Supabase
};

window.createDette = function() {
    window.showToast("Ouverture de l'interface Dette...", "success");
};

window.addCollecte = function() {
    window.showToast("Nouvelle collecte orpaillage...", "success");
};

window.addVente = function() {
    window.showToast("Enregistrement vente d'or...", "success");
};

// 3️⃣ Initialisation au chargement
document.addEventListener('DOMContentLoaded', async () => {
    console.log("DOM chargé, vérification session...");
    if (window.checkSession) {
        const user = await window.checkSession();
        if (user && document.getElementById('userNameGreeting')) {
            const firstName = user.user_metadata?.first_name || 'Utilisateur';
            document.getElementById('userNameGreeting').textContent = `Bonjour, ${firstName}`;
        }
    }
});
