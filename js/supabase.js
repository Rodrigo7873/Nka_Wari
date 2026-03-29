// Supabase Client and Auth functions for N'Ka Wari
console.log("supabase.js initializing...");

// Remplacez avec vos clés réelles
const supabaseUrl = 'https://VOTRE_PROJET.supabase.co';
const supabaseKey = 'VOTRE_ANON_KEY';

if (typeof window.supabase === 'undefined') {
    console.error("ERREUR : Le SDK Supabase (via CDN) n'est pas chargé !");
} else {
    window.supabaseClient = window.supabase.createClient(supabaseUrl, supabaseKey);
    console.log("Client Supabase initialisé dans window.supabaseClient");
}

// 1️⃣ Connexion
window.signInWithSupabase = async function(identifier, password, mode = 'email') {
    console.log("signInWithSupabase appelé (mode: " + mode + ")");
    let loginParams = { password: password };
    
    if (mode === 'tel') {
        let phone = identifier.replace(/\s/g, '');
        if (!phone.startsWith('+')) phone = '+224' + phone;
        loginParams.phone = phone;
    } else {
        loginParams.email = identifier;
    }

    const { data, error } = await window.supabaseClient.auth.signInWithPassword(loginParams);
    if (error) {
        console.error("Erreur de connexion:", error.message);
        throw error;
    }
    
    console.log("Connexion réussie ! Redirection...");
    window.location.href = 'dashboard.html';
    return data;
};

// 2️⃣ Inscription
window.signUpWithSupabase = async function(userData) {
    console.log("signUpWithSupabase appelé");
    const { data, error } = await window.supabaseClient.auth.signUp({
        email: userData.email,
        password: userData.password,
        options: {
            data: {
                first_name: userData.first_name,
                last_name: userData.last_name,
                phone: userData.phone,
                secret_question: userData.secret_question,
                secret_answer: userData.secret_answer
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
    console.log("logoutFromSupabase appelé");
    await window.supabaseClient.auth.signOut();
    window.location.href = 'index.html';
};

// 4️⃣ Vérification de session
window.checkSession = async function() {
    console.log("checkSession appelé");
    const { data: { session }, error } = await window.supabaseClient.auth.getSession();
    
    if (error || !session) {
        console.warn("Pas de session active");
        const isPublicPage = window.location.pathname.includes('login.html') || 
                             window.location.pathname.includes('index.html') || 
                             window.location.pathname.includes('register.html');
        
        if (!isPublicPage) {
            console.log("Redirection vers login.html car page protégée.");
            window.location.href = 'login.html';
        }
        return null;
    }
    
    console.log("Session active pour:", session.user.email);
    return session.user;
};

console.log("supabase.js prêt.");
