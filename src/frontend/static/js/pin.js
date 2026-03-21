/**
 * Gestion dynamique de la réinitialisation du PIN (N'ka Wari)
 */
document.addEventListener('DOMContentLoaded', () => {
    // Éléments Étape 1: Identification
    const formIdentify = document.getElementById('form-identify');
    const stepIdentify = document.getElementById('step-identify');
    const btnVerify = document.getElementById('btn-verify');

    // Éléments Étape 2: Réinitialisation
    const formReset = document.getElementById('form-reset');
    const stepReset = document.getElementById('step-reset');
    const btnReset = document.getElementById('btn-reset-final');
    
    // Éléments UI Communs
    const stepDesc = document.getElementById('step-description');
    const headerIcon = document.getElementById('header-icon');
    const pageTitle = document.getElementById('page-title');
    const alertBox = document.getElementById('alert-container');
    const alertMsg = document.getElementById('alert-message');

    /**
     * Affiche une alerte stylisée
     */
    function showAlert(msg, type = 'error') {
        alertMsg.textContent = msg;
        alertBox.style.display = 'block';
        if (type === 'success') {
            alertMsg.style.background = '#dcfce7';
            alertMsg.style.color = '#166534';
            alertMsg.style.borderColor = '#22c55e';
            alertMsg.style.borderLeftWidth = '4px';
        } else {
            alertMsg.style.background = '#fee2e2';
            alertMsg.style.color = '#991b1b';
            alertMsg.style.borderColor = '#fecaca';
            alertMsg.style.borderLeftWidth = '4px';
        }
        // Animation de secousse pour les erreurs
        if (type === 'error') {
            alertMsg.classList.remove('animate-shake');
            void alertMsg.offsetWidth; // Trigger reflow
            alertMsg.classList.add('animate-shake');
        }
    }

    // GESTION ÉTAPE 1: VÉRIFICATION ID + PASSWORD
    if (formIdentify) {
        formIdentify.addEventListener('submit', function(e) {
            e.preventDefault();
            btnVerify.disabled = true;
            btnVerify.innerHTML = '<span class="spinner"></span> Vérification...';
            alertBox.style.display = 'none';

            const formData = new FormData(this);
            formData.append('action', 'verifier_identite');

            fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Succès identification -> Passage étape 2
                    stepIdentify.style.display = 'none';
                    stepReset.style.display = 'block';
                    stepReset.classList.add('animate-fade-in');
                    
                    // Update UI
                    stepDesc.textContent = 'Configurez votre nouveau code PIN de sécurité';
                    pageTitle.textContent = 'Nouveau PIN';
                    if (headerIcon) {
                        headerIcon.innerHTML = `
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3m-3-3l2.5-2.5"></path>
                            </svg>
                        `;
                        headerIcon.style.background = 'linear-gradient(135deg, #dcfce7 0%, #f0fdf4 100%)';
                        headerIcon.style.color = '#22c55e';
                    }
                    
                    showAlert(data.message, 'success');
                } else {
                    showAlert(data.message);
                    btnVerify.disabled = false;
                    btnVerify.textContent = "Vérifier et réinitialiser";
                }
            })
            .catch(err => {
                console.error('Erreur AJAX Identification:', err);
                showAlert("Erreur de communication avec le serveur.");
                btnVerify.disabled = false;
                btnVerify.textContent = "Vérifier et réinitialiser";
            });
        });
    }

    // GESTION ÉTAPE 2: RÉINITIALISATION DU PIN
    if (formReset) {
        formReset.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const newPin = document.getElementById('new_pin').value;
            const confirmPin = document.getElementById('confirm_pin').value;

            // Validation Côté Client
            if (newPin !== confirmPin) {
                showAlert("Les codes PIN ne correspondent pas.");
                return;
            }

            if (![4, 6].includes(newPin.length) || !/^\d+$/.test(newPin)) {
                showAlert("Le code PIN doit comporter 4 ou 6 chiffres.");
                return;
            }

            btnReset.disabled = true;
            btnReset.innerHTML = '<span class="spinner"></span> Enregistrement...';
            alertBox.style.display = 'none';

            const formData = new FormData(this);
            formData.append('action', 'reinitialiser');

            fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = data.redirect_url;
                } else {
                    showAlert(data.message);
                    btnReset.disabled = false;
                    btnReset.textContent = 'Enregistrer le nouveau PIN';
                }
            })
            .catch(err => {
                console.error('Erreur AJAX Réinitialisation:', err);
                showAlert("Erreur lors de la sauvegarde du nouveau PIN.");
                btnReset.disabled = false;
                btnReset.textContent = 'Enregistrer le nouveau PIN';
            });
        });
    }
});

/**
 * Fonction globale pour basculer la visibilité d'un champ mot de passe
 * @param {string} inputId L'ID du champ input
 * @param {HTMLElement} iconElement L'élément span contenant l'icône
 */
window.togglePasswordVisibility = function(inputId, iconElement) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    // Toggle type
    if (input.type === 'password') {
        input.type = 'text';
        // Icône oeil barré (eye-off)
        iconElement.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="eye-off-icon">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                <line x1="1" y1="1" x2="23" y2="23"></line>
            </svg>
        `;
        iconElement.style.color = '#f59e0b'; // Couleur d'interaction
    } else {
        input.type = 'password';
        // Icône oeil normal (eye)
        iconElement.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="eye-icon">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                <circle cx="12" cy="12" r="3"></circle>
            </svg>
        `;
        iconElement.style.color = '#94a3b8'; // Couleur par défaut
    }
};
