/* src/frontend/static/js/parametres.js */

/**
 * Envoie les mises à jour en base de données via AJAX sans recharger la page.
 * @param {Object} data - Les données à mettre à jour (ex: {theme: 'sombre'})
 */
function updateParametres(data) {
    const formData = new FormData();
    for (const key in data) {
        formData.append(key, data[key]);
    }

    fetch('/parametres/update-parametres/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: formData
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            console.log('Paramètres mis à jour avec succès');
            // Feedback visuel optionnel (ex: Toast)
        }
    })
    .catch(error => {
        console.error('Erreur lors de la mise à jour des paramètres:', error);
    });
}



/**
 * Active ou désactive les notifications en base.
 * @param {Event} event - L'événement de clic (change)
 * @param {HTMLElement} checkbox - L'élément input checkbox
 */
function updateNotificationPref(event, checkbox) {
    if (event) {
        event.stopPropagation(); // Empêche le clic de remonter (ex: vers un a href parent suspect)
        // event.preventDefault() n'est pas utilisé directement sur le checkbox change car cela l'empêcherait de changer d'état,
        // mais on gère ici la requête AJAX sans rechargement.
    }
    updateParametres({ 'notifications': checkbox.checked });
}

/**
 * Récupère la valeur d'un cookie par son nom.
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

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    console.log("Paramètres JS chargé avec succès.");
});
