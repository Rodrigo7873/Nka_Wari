// Supabase Client and Auth functions for N'Ka Wari
console.log("supabase.js initializing...");

const supabaseUrl = 'https://fvrdaulagutwhlrgrcta.supabase.co';
const supabaseKey = 'sb_publishable_CxLEYNMH7gsv-zpcIJQmKg_fFfQ1NNu';

if (typeof window.supabase === 'undefined') {
    console.error("ERREUR : Le SDK Supabase (via CDN) n'est pas chargé !");
} else {
    // Si window.supabase est déjà un client (possède auth), on ne le réinitialise pas inutilement
    if (typeof window.supabase.auth === 'undefined') {
        const supabaseClient = window.supabase.createClient(supabaseUrl, supabaseKey);
        window.supabase = supabaseClient;
        console.log("Supabase client initialisé.");
    }
}

// Fonction utilitaire pour trouver l'email à partir d'un identifiant quelconque
async function findEmailFromIdentifier(identifier) {
    if (!identifier) throw new Error("Identifiant requis");
    
    const input = identifier.trim();
    console.log("🔍 Recherche pour identifiant :", input);

    // 1. ID professionnel (format XXXX999999)
    if (/^[A-Z]{4}[0-9]{6}$/.test(input.toUpperCase())) {
        const email = `${input.toUpperCase()}@nkawari.local`;
        console.log("ID pro détecté :", email);
        return email;
    }

    // 2. Numéro de téléphone (format local 620 ou international +224)
    if (input.startsWith('+224') || /^620[\s\-]*[0-9]{2}[\s\-]*[0-9]{2}[\s\-]*[0-9]{2}$/.test(input)) {
        let normalized = input.replace(/\s|-/g, '');
        if (!normalized.startsWith('+224')) {
            normalized = '+224' + normalized;
        }
        console.log("📞 Téléphone normalisé :", normalized);

        // Validation du format final
        if (!/^\+224[0-9]{9}$/.test(normalized)) {
            throw new Error("Numéro invalide (doit être +224 suivi de 9 chiffres)");
        }

        // Recherche dans profiles en utilisant window.supabase
        const { data, error } = await window.supabase
            .from('profiles')
            .select('email')
            .eq('phone', normalized)
            .maybeSingle();

        console.log("📧 Résultat recherche :", data, error);

        if (error || !data) {
            throw new Error("Aucun compte associé à ce numéro");
        }
        return data.email;
    }

    throw new Error("Format d'identifiant invalide (ID ou téléphone requis)");
}

// 1️⃣ Connexion
window.signInWithSupabase = async function(identifier, password) {
    console.log("signInWithSupabase appelé");
    try {
        const email = await findEmailFromIdentifier(identifier);
        
        const { data, error } = await window.supabase.auth.signInWithPassword({
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
        throw err;
    }
};

// 2️⃣ Inscription
window.signUpWithSupabase = async function(userData) {
    console.log("signUpWithSupabase appelé");
    
    const idPrefix = userData.display_id || userData.phone.replace(/\s/g, '');
    const emailTech = userData.email.includes('@') ? userData.email : (idPrefix + "@nkawari.local");

    const { data, error } = await window.supabase.auth.signUp({
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
    await window.supabase.auth.signOut();
    window.location.href = 'index.html';
};

// 4️⃣ Vérification de session
window.checkSession = async function() {
    const { data: { session }, error } = await window.supabase.auth.getSession();
    if (error || !session) {
        const path = window.location.pathname;
        if (!path.includes('login.html') && !path.includes('index.html') && !path.includes('register.html')) {
            window.location.href = 'login.html';
        }
        return null;
    }
    return session.user;
};
