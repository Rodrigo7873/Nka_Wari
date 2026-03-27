// Initialize Supabase Client
const supabaseUrl = 'https://VOTRE_PROJET_SUPABASE.supabase.co';
const supabaseKey = 'VOTRE_CLE_ANONYME_SUPABASE';

const supabase = window.supabase.createClient(supabaseUrl, supabaseKey);

// Déconnexion
async function logoutFromSupabase() {
    await supabase.auth.signOut();
    window.location.href = 'index.html';
}

// Connexion (Améliorée pour gérer Tel ou Email)
async function signInWithSupabase(identifier, password, mode = 'email') {
    let loginParams = { password: password };

    if (mode === 'tel') {
        // Nettoyage et formatage pour Supabase (ex: +224...)
        let phone = identifier.replace(/\s/g, '');
        if (!phone.startsWith('+')) phone = '+224' + phone;
        loginParams.phone = phone;
    } else {
        loginParams.email = identifier;
    }

    const { data, error } = await supabase.auth.signInWithPassword(loginParams);

    if (error) throw error;
    
    window.location.href = 'dashboard.html';
    return data;
}

// Inscription
async function signUpWithSupabase(email, password) {
    const { data, error } = await supabase.auth.signUp({
        email: email,
        password: password,
    });

    if (error) throw error;
    window.location.href = 'login.html';
    return data;
}

// Vérification de session
async function checkSession() {
    const { data: { session }, error } = await supabase.auth.getSession();
    if (error || !session) {
        if (!window.location.href.includes('login.html') && !window.location.href.includes('index.html') && !window.location.href.includes('register.html')) {
            window.location.href = 'login.html';
        }
        return null;
    }
    return session.user;
}
