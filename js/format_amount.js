/**
 * Formate un montant en ajoutant des espaces tous les 3 chiffres.
 */
function formatMontant(input) {
    // Supprimer tout ce qui n'est pas un chiffre
    let valeur = input.value.replace(/\D/g, '');
    
    // Limiter à 12 chiffres maximum
    if (valeur.length > 12) {
        valeur = valeur.slice(0, 12);
    }
    
    // Formater avec des espaces
    if (valeur.length > 0) {
        valeur = valeur.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    }
    
    input.value = valeur;
}

/**
 * Nettoie les champs de montant avant la soumission du formulaire.
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser le formatage pour les champs pré-remplis
    document.querySelectorAll('input[oninput*="formatMontant"]').forEach(input => {
        formatMontant(input);
    });

    // Nettoyer avant envoi
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            this.querySelectorAll('input[oninput*="formatMontant"]').forEach(input => {
                input.value = input.value.replace(/\s/g, '');
            });
        });
    });
});
