/**
 * MentorLink — Configuration & Client API Centralisé
 * Rôle : Gérer l'URL du serveur, joindre automatiquement le token JWT,
 * et intercepter les erreurs globales.
 */

const API_BASE_URL = (window.API_BASE_URL || (
    window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost'
        ? 'http://127.0.0.1:5000/api'
        : 'https://ifri-mentorlink.onrender.com/api'
));

console.log('[API] Using base URL:', API_BASE_URL);

async function uploadFileAPI(endpoint, method = 'POST', formData = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = localStorage.getItem('mentorlink_token');

    const headers = { 'Accept': 'application/json' };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = { method, headers, body: formData };

    function getLoginRedirectPath() {
        const path = window.location.pathname;
        if (path.includes('/pages/')) {
            return 'signin.html';
        }
        return 'pages/signin.html';
    }

    try {
        const response = await fetch(url, config);

        if (response.status === 401) {
            const pub = /^\/(pages\/)?($|index\.html|signin\.html|signup\.html|reset-password\.html)/.test(window.location.pathname);
            if (pub) {
                throw new Error('Non authentifié');
            }
            console.warn('Session expirée. Redirection vers login.');
            localStorage.removeItem('mentorlink_token');
            localStorage.removeItem('mentorlink_user');
            window.location.href = getLoginRedirectPath();
            throw new Error('Session expirée. Veuillez vous reconnecter.');
        }

        let data;
        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('application/json')) {
            data = await response.json();
        } else {
            const text = await response.text();
            try { data = JSON.parse(text); } catch (_) { data = { message: text }; }
        }

        if (!response.ok) {
            throw new Error(data.message || `Erreur Serveur (Code ${response.status})`);
        }

        return data;
    } catch (error) {
        console.error(`[API Upload Error] ${endpoint}:`, error);
        throw error;
    }
}

async function fetchAPI(endpoint, method = 'GET', body = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = localStorage.getItem('mentorlink_token');

    const headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = { method, headers };

    if (body && (method === 'POST' || method === 'PUT' || method === 'DELETE')) {
        config.body = JSON.stringify(body);
    }

    function getLoginRedirectPath() {
        const path = window.location.pathname;
        if (path.includes('/pages/')) {
            return 'signin.html';
        }
        return 'pages/signin.html';
    }

    try {
        const response = await fetch(url, config);

        if (response.status === 401) {
            const pub = /^\/(pages\/)?($|index\.html|signin\.html|signup\.html|reset-password\.html)/.test(window.location.pathname);
            if (pub) {
                throw new Error('Non authentifié');
            }
            console.warn('Session expirée. Redirection vers login.');
            localStorage.removeItem('mentorlink_token');
            localStorage.removeItem('mentorlink_user');
            window.location.href = getLoginRedirectPath();
            throw new Error('Session expirée. Veuillez vous reconnecter.');
        }

        // Tente de parser le JSON ; si la réponse n'est pas du JSON, on utilise le texte
        let data;
        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('application/json')) {
            data = await response.json();
        } else {
            const text = await response.text();
            try { data = JSON.parse(text); } catch (_) { data = { message: text }; }
        }

        if (!response.ok) {
            throw new Error(data.message || `Erreur Serveur (Code ${response.status})`);
        }

        return data;
    } catch (error) {
        console.error(`[API Error] ${endpoint}:`, error);
        throw error;
    }
}

const API = {
    auth: {
        register: (userData) => fetchAPI('/auth/register', 'POST', userData),
        login: (credentials) => fetchAPI('/auth/login', 'POST', credentials),
        forgotPassword: (data) => fetchAPI('/auth/forgot-password', 'POST', data),
        resetPassword: (data) => fetchAPI('/auth/reset-password', 'POST', data),
        changePassword: (data) => {
            const payload = {
                old_password: data.old_password || data.ancien_mot_de_passe || data.oldPassword,
                new_password: data.new_password || data.nouveau_mot_de_passe || data.newPassword
            };
            return fetchAPI('/auth/change-password', 'PUT', payload);
        }
    },

    profile: {
        getMe: () => fetchAPI('/profile/me', 'GET'),
        updateMe: (data) => fetchAPI('/profile/me', 'PUT', data),
        addCompetence: (data) => fetchAPI('/profile/competences', 'POST', data),
        removeCompetence: (data) => fetchAPI('/profile/competences', 'DELETE', data),
        addLacune: (data) => fetchAPI('/profile/lacunes', 'POST', data),
        removeLacune: (data) => fetchAPI('/profile/lacunes', 'DELETE', data),
        addDisponibilite: (data) => fetchAPI('/profile/disponibilites', 'POST', data),
        removeDisponibilite: (data) => fetchAPI('/profile/disponibilites', 'DELETE', data),
        activateCompetence: (matiereId) => fetchAPI(`/profile/competences/${matiereId}/activate`, 'PUT'),
        deactivateCompetence: (matiereId) => fetchAPI(`/profile/competences/${matiereId}/deactivate`, 'PUT'),
        updateAvatar: (data) => fetchAPI('/profile/avatar', 'PUT', data),
        uploadAvatar: (formData) => uploadFileAPI('/profile/avatar/upload', 'POST', formData)
    },

    matching: {
        getSuggestions: (filters = {}) => {
            const params = new URLSearchParams(filters).toString();
            return fetchAPI(`/matches/suggestions${params ? '?' + params : ''}`, 'GET');
        },
        requestMatch: (studentId, body) => fetchAPI(`/matches/${studentId}/request`, 'POST', body),
        accept: (matchId) => fetchAPI(`/matches/${matchId}/accept`, 'POST'),
        reject: (matchId) => fetchAPI(`/matches/${matchId}/reject`, 'POST'),
        getReceived: () => fetchAPI('/matches/received', 'GET'),
        getSent: () => fetchAPI('/matches/sent', 'GET')
    },

    messages: {
        getConversations: () => fetchAPI('/conversations', 'GET'),
        create: (userId) => fetchAPI('/conversations', 'POST', { user_id: userId }),
        getHistory: (convId) => fetchAPI(`/conversations/${convId}/messages`, 'GET'),
        send: (convId, text) => fetchAPI(`/conversations/${convId}/messages`, 'POST', { contenu: text })
    },

    notifications: {
        getAll: (unreadOnly = false) => fetchAPI(`/notifications${unreadOnly ? '?unread_only=true' : ''}`, 'GET'),
        markRead: (id) => fetchAPI(`/notifications/${id}/read`, 'PUT'),
        markAllRead: () => fetchAPI('/notifications/read-all', 'PUT'),
        delete: (id) => fetchAPI(`/notifications/${id}`, 'DELETE')
    },

    offers: {
        getAll: () => fetchAPI('/offers', 'GET'),
        getMine: () => fetchAPI('/offers/mine', 'GET'),
        create: (data) => fetchAPI('/offers', 'POST', data),
        delete: (id) => fetchAPI(`/offers/${id}`, 'DELETE'),
        respond: (id) => fetchAPI(`/offers/${id}/respond`, 'POST')
    },

    demands: {
        getAll: () => fetchAPI('/demands', 'GET'),
        getMine: () => fetchAPI('/demands/mine', 'GET'),
        create: (data) => fetchAPI('/demands', 'POST', data),
        delete: (id) => fetchAPI(`/demands/${id}`, 'DELETE'),
        offerHelp: (id) => fetchAPI(`/demands/${id}/offer-help`, 'POST')
    },


    matieres: {
        getAll: () => fetchAPI('/matieres', 'GET')
    }
};

window.API = API;
