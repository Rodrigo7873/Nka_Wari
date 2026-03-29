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

// 1️⃣ Connexion
window.signInWithSupabase = async function(identifier, password, mode = 'email') {
    console.log("signInWithSupabase appelé (mode: " + mode + ")");
    let loginParams = { password: password };
    let input = identifier.trim();
    
    // Détection intelligente du type d'identifiant
    if (mode === 'tel' || /^\d{9}$/.test(input.replace(/\s/g, ''))) {
        // C'est un numéro de téléphone
        let phone = input.replace(/\s/g, '');
        loginParams.email = phone + "@nkawari.local";
    } else if (!input.includes('@') && /^\d+$/.test(input)) {
        // C'est probablement un ID numérique
        loginParams.email = input + "@nkawari.local";
    } else {
        // C'est un email classique ou un identifiant avec @
        loginParams.email = input;
    }

    console.log("Tentative de connexion avec:", loginParams.email);

    const { data, error } = await window.supabaseClient.auth.signInWithPassword(loginParams);
    if (error) {
        console.error("Erreur de connexion:", error.message);
        throw error;
    }
    
    window.location.href = 'dashboard.html';
    return data;
};

// 2️⃣ Inscription
window.signUpWithSupabase = async function(userData) {
    console.log("signUpWithSupabase appelé");
    
    // On utilise le téléphone comme base pour l'Email technique si aucun email n'est fourni
    const emailTech = userData.email.includes('@') ? userData.email : (userData.phone.replace(/\s/g, '') + "@nkawari.local");

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
                // On peut simuler un ID court basé sur le timestamp ou une partie de l'UUID
                display_id: userData.phone.replace(/\s/g, '')
            }
        }
    });

    if (error) {
        console.error("Erreur d'inscription:", error.message);
        throw error;
    }
    
    console.log("Inscription réussie !");
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
