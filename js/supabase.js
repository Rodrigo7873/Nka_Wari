// Initialize Supabase Client
// Remplacez avec vos clés Supabase réelles pour le déploiement
const supabaseUrl = 'https://VOTRE_PROJET_SUPABASE.supabase.co';
const supabaseKey = 'VOTRE_CLE_ANONYME_SUPABASE';

const supabase = window.supabase.createClient(supabaseUrl, supabaseKey);

// Déconnexion
async function logoutFromSupabase() {
    const { error } = await supabase.auth.signOut();
    if (error) {
        console.error("Erreur de déconnexion:", error.message);
    }
    window.location.href = 'index.html';
}

// Connexion
async function signInWithSupabase(email, password) {
    const { data, error } = await supabase.auth.signInWithPassword({
        email: email,
        password: password,
    });

    if (error) {
        throw error;
    }
    
    // Si succès, redirection
    window.location.href = 'dashboard.html';
    return data;
}

// Inscription
async function signUpWithSupabase(email, password) {
    const { data, error } = await supabase.auth.signUp({
        email: email,
        password: password,
    });

    if (error) {
        throw error;
    }
    
    // Si succès, redirection vers login avec message
    window.location.href = 'login.html';
    return data;
}

// Vérification de session
async function checkSession() {
    const { data: { session }, error } = await supabase.auth.getSession();
    
    if (error || !session) {
        window.location.href = 'login.html';
        return null;
    }
    
    return session.user;
}
