// Supabase Client and Auth functions for N'Ka Wari
console.log("supabase.js initializing...");

const supabaseUrl = 'https://fvrdaulagutwhlrgrcta.supabase.co';
const supabaseKey = 'sb_publishable_CxLEYNMH7gsv-zpcIJQmKg_fFfQ1NNu';

if (typeof window.supabase === 'undefined') {
    console.error("ERREUR : Le SDK Supabase (via CDN) n'est pas chargé !");
} else {
    window.supabaseClient = window.supabase.createClient(supabaseUrl, supabaseKey);
    console.log("Client Supabase initialisé");
}

// Fonction utilitaire pour trouver l'email à partir d'un identifiant quelconque
async function findEmailFromIdentifier(identifier) {
    if (!identifier) throw new Error("Identifiant requis");
    
    // Nettoyage des espaces éventuels autour
    const input = identifier.trim();
    console.log("Recherche pour :", input);

    // 1. Email direct
    if (input.includes('@')) {
        console.log("Email détecté :", input);
        return input;
    }

    // 2. ID professionnel (format XXXX999999)
    if (/^[A-Z]{4}[0-9]{6}$/.test(input.toUpperCase())) {
        const email = `${input.toUpperCase()}@nkawari.local`;
        console.log("ID pro converti en email :", email);
        return email;
    }

    // 3. Numéro de téléphone (format +224...)
    if (input.startsWith('+224')) {
        // Normalisation : suppression espaces et tirets
        const normalized = input.replace(/\s|-/g, '');
        console.log("Téléphone normalisé :", normalized);

        if (!/^\+224[0-9]{9}$/.test(normalized)) {
            throw new Error("Format de numéro +224 invalide");
        }

        const { data, error } = await window.supabaseClient
            .from('profiles')
            .select('email')
            .eq('phone', normalized)
            .maybeSingle();

        console.log("Résultat recherche téléphone :", data, error);

        if (error || !data) {
            throw new Error("Aucun compte associé à ce numéro");
        }
        return data.email;
    }

    throw new Error("Format d'identifiant invalide");
}

// 1️⃣ Connexion
window.signInWithSupabase = async function(identifier, password) {
    console.log("signInWithSupabase appelé");
    try {
        const email = await findEmailFromIdentifier(identifier);
        console.log("Tentative de connexion pour :", email);
        
        const { data, error } = await window.supabaseClient.auth.signInWithPassword({
            email: email,
            password: password
        });

        if (error) throw new Error(error.message);

        console.log("Connexion réussie !");
        localStorage.setItem('user', JSON.stringify(data.user));
        window.location.href = "dashboard.html";
        return data;
    } catch (err) {
        console.error("Erreur de connexion :", err.message);
        if (window.showToast) window.showToast(err.message, "error");
        else alert("Erreur : " + err.message);
        throw err;
    }
};

// 2️⃣ Inscription
window.signUpWithSupabase = async function(userData) {
    console.log("signUpWithSupabase appelé");
    
    // On utilise l'ID généré (ex: RAMO123456) comme base pour l'Email technique
    const idPrefix = userData.display_id || userData.phone.replace(/\s/g, '');
    const emailTech = userData.email.includes('@') ? userData.email : (idPrefix + "@nkawari.local");

    const { data, error } = await window.supabaseClient.auth.signUp({
        email: emailTech,
        password: userData.password,
        options: {
            data: {
                first_name: userData.first_name,
                last_name: userData.last_name,
                phone: userData.phone,
                secret_question: userData.secret_question,
                secret_answer: userData.secret_answer,
                display_id: userData.display_id
            }
        }
    });

    if (error) {
        console.error("Erreur d'inscription :", error.message);
        throw error;
    }
    
    console.log("Inscription réussie ! ID:", userData.display_id);
    return data;
};

// 3️⃣ Déconnexion
window.logoutFromSupabase = async function() {
    await window.supabaseClient.auth.signOut();
    window.location.href = 'index.html';
};

// 4️⃣ Vérification de session
window.checkSession = async function() {
    const { data: { session }, error } = await window.supabaseClient.auth.getSession();
    if (error || !session) {
        const path = window.location.pathname;
        if (!path.includes('login.html') && !path.includes('index.html') && !path.includes('register.html')) {
            window.location.href = 'login.html';
        }
        return null;
    }
    return session.user;
};
