// Supabase Configuration
// Remplacez par vos clés réelles
const supabaseUrl = 'https://VOTRE_PROJET.supabase.co';
const supabaseKey = 'VOTRE_ANON_KEY';

const supabase = window.supabase.createClient(supabaseUrl, supabaseKey);

/**
 * AUTHENTICATION
 */

async function signInWithSupabase(identifier, password, mode = 'email') {
    let loginParams = { password: password };
    if (mode === 'tel') {
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

async function signUpWithSupabase(userData) {
    const { data, error } = await supabase.auth.signUp({
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
    if (error) throw error;
    return data;
}

async function logoutFromSupabase() {
    await supabase.auth.signOut();
    window.location.href = 'index.html';
}

async function checkSession() {
    const { data: { session }, error } = await supabase.auth.getSession();
    if (error || !session) {
        const path = window.location.pathname;
        if (!path.includes('login.html') && !path.includes('index.html') && !path.includes('register.html')) {
            window.location.href = 'login.html';
        }
        return null;
    }
    return session;
}

/**
 * PIN MANAGEMENT
 */

async function verifyPIN(pin) {
    const { data: { user } } = await supabase.auth.getUser();
    const { data, error } = await supabase
        .from('user_profiles')
        .select('pin_code')
        .eq('user_id', user.id)
        .single();
    
    if (error || data.pin_code !== pin) return false;
    return true;
}

async function setupPIN(pin) {
    const { data: { user } } = await supabase.auth.getUser();
    const { error } = await supabase
        .from('user_profiles')
        .upsert({ user_id: user.id, pin_code: pin });
    if (error) throw error;
}

/**
 * DATA CRUD (STUBS)
 */

async function fetchDashboardStats() {
    // Exemple de fetch Supabase
    // const { data, error } = await supabase.from('operations').select('*');
    return {
        patrimoine_net: 0,
        total_cash: 0,
        prix_or: 0
    };
}
