/**
 * Gestion dynamique du profil et du changement de mot de passe
 */

// Gestion de l'affichage du formulaire de mot de passe
window.togglePasswordForm = function() {
    console.log("Tentative d'affichage du formulaire Password");
    
    // Cacher le formulaire PIN s'il est ouvert
    const pinSection = document.getElementById('pin-form-section');
    const btnPinLink = document.getElementById('btn-toggle-pin-link');
    if (pinSection) pinSection.style.display = 'none';
    if (btnPinLink) btnPinLink.style.opacity = '1';

    const section = document.getElementById('password-form-section');
    const toggleBtn = document.getElementById('btn-toggle-pwd');
    if (!section) {
        console.error("ERREUR : Section password-form-section introuvable !");
        return;
    }
    
    // Vérification flexible de l'état d'affichage
    const isHidden = window.getComputedStyle(section).display === 'none';
    
    if (isHidden) {
        section.style.display = 'block';
        section.classList.add('animate-fade-in');
        section.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        if (toggleBtn) toggleBtn.style.opacity = '0.5';
    } else {
        section.style.display = 'none';
        if (toggleBtn) toggleBtn.style.opacity = '1';
    }
}

// Les fonctions showPinForm et cacherPinForm sont désormais gérées directement dans le template profil.html pour plus de robustesse.

/**
 * Bascule entre le mode vue et le mode édition du profil
 */
function switchToEdit() {
    document.getElementById('view-mode').style.display = 'none';
    document.getElementById('edit-mode').style.display = 'block';
    
    const editCard = document.querySelector('#edit-mode .profil-card');
    if (editCard) {
        editCard.style.animation = 'fadeInUp 0.4s ease-out';
    }
    
    document.getElementById('edit-prenom').focus();
}

function switchToView() {
    document.getElementById('edit-mode').style.display = 'none';
    document.getElementById('view-mode').style.display = 'block';
    
    const section = document.getElementById('password-form-section');
    if (section) section.style.display = 'none';
}

function updateAvatar() {
    const prenom = document.getElementById('edit-prenom').value;
    const nom = document.getElementById('edit-nom').value;
    const initiales = (prenom[0] || '').toUpperCase() + (nom[0] || '').toUpperCase();
    const avatar = document.getElementById('edit-avatar');
    if (avatar) avatar.textContent = initiales || '?';
}

/**
 * Alterne la visibilité du mot de passe pour un champ donné
 */
window.togglePasswordVisibility = function(inputId, btn) {
    const input = document.getElementById(inputId);
    if (!input) return;

    if (input.type === 'password') {
        input.type = 'text';
        btn.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>`;
    } else {
        input.type = 'password';
        btn.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`;
    }
}

// Gestion AJAX du changement de mot de passe
document.addEventListener("DOMContentLoaded", () => {
    console.log("JS profil chargé.");
    
    const formPwd = document.getElementById('form-pwd-ajax');
    if (formPwd) {
        formPwd.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log("AJAX: Tentative de changement de mot de passe...");
            
            const submitBtn = document.getElementById('submit-pwd');
            const globalError = document.getElementById('global-error');
            const fieldErrors = document.querySelectorAll('.field-error');
            
            // Reset UI
            fieldErrors.forEach(err => { err.style.display = 'none'; err.textContent = ''; });
            if (globalError) {
                globalError.style.display = 'none';
                globalError.textContent = '';
            }
            
            submitBtn.disabled = true;
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Traitement...';

            const formData = new FormData(this);
            console.log("AJAX: Envoi vers", this.action);
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => {
                console.log("AJAX: Réponse HTTP", response.status);
                return response.json();
            })
            .then(data => {
                console.log("AJAX: Données JSON", data);
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
                
                if (data.success) {
                    // Affichage premium du succès
                    const formSection = document.getElementById('password-form-section');
                    if (formSection) {
                        formSection.innerHTML = `
                            <div style="text-align: center; padding: 20px; animation: scaleIn 0.3s ease-out;">
                                <div style="margin-bottom: 15px; color: #22c55e;">
                                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                                    </svg>
                                </div>
                                <h4 style="color: #166534; margin: 0 0 8px 0;">C'est fait !</h4>
                                <p style="color: #15803d; font-size: 13px; margin: 0;">${data.message}</p>
                            </div>
                        `;
                    }
                    
                    // Rechargement après un court instant pour laisser l'utilisateur apprécier le succès
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                } else {
                    if (data.redirect_url) {
                        // Alerte de sécurité premium
                        const formSection = document.getElementById('password-form-section');
                        if (formSection) {
                            formSection.innerHTML = `
                                <div style="text-align: center; padding: 25px; background: #fee2e2; border-radius: 12px; animation: scaleIn 0.3s ease-out; border: 2px solid #ef4444;">
                                    <div style="margin-bottom: 15px; color: #dc2626;">
                                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                                            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                                            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                                            <line x1="12" y1="15" x2="12" y2="17"></line>
                                        </svg>
                                    </div>
                                    <h4 style="color: #991b1b; margin: 0 0 8px 0; font-weight: 700;">Alerte de Sécurité</h4>
                                    <p style="color: #b91c1c; font-size: 13px; margin: 0; line-height: 1.5;">${data.error}</p>
                                    <div style="margin-top: 15px; font-size: 11px; color: #991b1b; font-weight: 600;">Redirection sécurisée en cours...</div>
                                </div>
                            `;
                        }
                        
                        setTimeout(() => {
                            window.location.href = data.redirect_url;
                        }, 2500);
                        return;
                    }
                    
                    if (data.field) {
                        const errorSpan = document.getElementById(`error-${data.field}`);
                        if (errorSpan) {
                            errorSpan.textContent = data.error;
                            errorSpan.style.display = 'block';
                        }
                    } else if (data.error && globalError) {
                        globalError.textContent = data.error;
                        globalError.style.display = 'block';
                    }
                }
            })
            .catch(err => {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
                console.error('AJAX Error:', err);
                if (globalError) {
                    globalError.textContent = "Erreur de connexion au serveur.";
                    globalError.style.display = 'block';
                }
            });
        });
    }

});
