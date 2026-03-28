// Main App Logic for N'Ka Wari
console.log("app.js loaded");

// Expose functions to window for global access
window.createKarfa = async function() {
    console.log("createKarfa called");
    
    const session = await checkSession();
    if (!session) return;

    const nom = prompt("Nom du Karfa (ex: Karfa de Mamadou) :");
    if (!nom) return;

    const montant = prompt("Montant (GNF) :");
    if (!montant) return;

    try {
        const { data, error } = await supabase
            .from('karfa')
            .insert([{ 
                user_id: session.id, 
                name: nom, 
                amount: parseFloat(montant),
                created_at: new Date()
            }]);

        if (error) throw error;
        
        alert("Karfa créé avec succès !");
        window.location.reload();
    } catch (err) {
        console.error("Erreur creation Karfa:", err.message);
        alert("Erreur: " + err.message);
    }
};

window.createDette = async function() {
    console.log("createDette called");
    
    const session = await checkSession();
    if (!session) return;

    const destinataire = prompt("Nom du créancier/débiteur :");
    if (!destinataire) return;

    const montant = prompt("Montant (GNF) :");
    if (!montant) return;

    try {
        const { data, error } = await supabase
            .from('dettes')
            .insert([{ 
                user_id: session.id, 
                person: destinataire, 
                amount: parseFloat(montant),
                status: 'active',
                created_at: new Date()
            }]);

        if (error) throw error;
        
        alert("Dette enregistrée !");
        window.location.reload();
    } catch (err) {
        console.error("Erreur creation Dette:", err.message);
        alert("Erreur: " + err.message);
    }
};

window.toggleMenu = function() {
    console.log("toggleMenu called");
    // Animation ou classe pour le menu (à implémenter si besoin)
    alert("Menu latéral (en cours d'intégration)");
};

window.toggleNotifications = function() {
    console.log("toggleNotifications called");
    alert("Notifications (Aucune pour le moment)");
};
