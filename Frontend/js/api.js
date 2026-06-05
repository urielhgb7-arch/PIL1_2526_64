/**
 * MentorLink — Configuration & Client API Centralisé
 * Rôle : Gérer l'URL du serveur, joindre automatiquement le token JWT,
 * et intercepter les erreurs globales.
 */

const API_BASE_URL = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost'
    ? 'http://127.0.0.1:5000/api'
    : 'https://ton-app-backend.onrender.com/api'; // ← Remplace par ta vraie URL Render

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

    if (body && (method === 'POST' || method === 'PUT')) {
        config.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(url, config);

        if (response.status === 401) {
            console.warn('Session expirée. Redirection vers login.');
            localStorage.removeItem('mentorlink_token');
            localStorage.removeItem('mentorlink_user');
            if (!window.location.pathname.includes('login.html')) {
                window.location.href = '/Frontend/pages/login.html';
            }
            throw new Error('Session expirée. Veuillez vous reconnecter.');
        }

        const data = await response.json();

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
        login: (credentials) => fetchAPI('/auth/login', 'POST', credentials)
    },

    profile: {
        getMe: () => fetchAPI('/profile/me', 'GET'),
        updateMe: (data) => fetchAPI('/profile/me', 'PUT', data),
        addCompetence: (data) => fetchAPI('/profile/competences', 'POST', data),
        removeCompetence: (data) => fetchAPI('/profile/competences', 'DELETE', data),
        addDisponibilite: (data) => fetchAPI('/profile/disponibilites', 'POST', data),
        removeDisponibilite: (data) => fetchAPI('/profile/disponibilites', 'DELETE', data)
    },

    matching: {
        getSuggestions: (filters = {}) => {
            const params = new URLSearchParams(filters).toString();
            return fetchAPI(`/matches/suggestions${params ? '?' + params : ''}`, 'GET');
        },
        accept: (matchId) => fetchAPI(`/matches/${matchId}/accept`, 'POST'),
        reject: (matchId) => fetchAPI(`/matches/${matchId}/reject`, 'POST')
    },

    messages: {
        getConversations: () => fetchAPI('/conversations', 'GET'),
        create: (userId) => fetchAPI('/conversations', 'POST', { user_id: userId }),
        getHistory: (convId) => fetchAPI(`/conversations/${convId}/messages`, 'GET'),
        send: (convId, text) => fetchAPI(`/conversations/${convId}/messages`, 'POST', { contenu: text })
    },

    notifications: {
        getAll: () => fetchAPI('/notifications', 'GET'),
        markRead: (id) => fetchAPI(`/notifications/${id}/read`, 'PUT')
    },

    matieres: {
        getAll: () => fetchAPI('/matieres', 'GET')
    }
};

window.API = API;
