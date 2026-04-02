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

    const input = identifier.trim();
    
    // 1. Si c'est déjà un email
    if (input.includes('@')) return input;

    // 2. Si c'est un ID professionnel (format XXXX999999)
    if (/^[A-Z]{4}[0-9]{6}$/.test(input.toUpperCase())) {
        return `${input.toUpperCase()}@nkawari.local`;
    }

    // 3. Si c'est un numéro de téléphone (on cherche dans la table profiles)
    // On nettoie le numéro (suppression espaces pour la recherche si nécessaire, mais on compare tel quel si startsWith +224)
    const phone = input.replace(/\s/g, '');
    if (phone.startsWith('+224') || /^\d{9}$/.test(phone)) {
        const finalPhone = phone.startsWith('+224') ? phone : '+224' + phone;
        const { data, error } = await window.supabaseClient
            .from('profiles')
            .select('email')
            .eq('phone', finalPhone)
            .maybeSingle();

        if (error) throw new Error("Erreur lors de la recherche du téléphone");
        if (!data) throw new Error("Aucun compte associé à ce numéro");
        return data.email;
    }

    throw new Error("Format d'identifiant invalide");
}

// 1️⃣ Connexion
window.signInWithSupabase = async function(identifier, password) {
    console.log("signInWithSupabase appelé");
    try {
        const email = await findEmailFromIdentifier(identifier);
        const { data, error } = await window.supabaseClient.auth.signInWithPassword({
            email: email,
            password: password
        });

        if (error) throw new Error(error.message);

        localStorage.setItem('user', JSON.stringify(data.user));
        window.location.href = "dashboard.html";
        return data;
    } catch (err) {
        console.error("Erreur de connexion:", err.message);
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
        console.error("Erreur d'inscription:", error.message);
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
