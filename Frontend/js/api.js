/**
 * MentorLink — Configuration & Client API Centralisé
 * Rôle : Gérer l'URL du serveur, joindre automatiquement le token JWT, 
 * et intercepter les erreurs globales.
 */

// 1. DÉTECTION AUTOMATIQUE DE L'ENVIRONNEMENT (Local vs Render)
// Remplace 'ton-app-backend.onrender.com' par la vraie URL générée par Render pour ton Web Service Flask
const API_BASE_URL = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost'
    ? 'http://127.0.0.1:5000/api'
    : 'https://pil1-2526-64.onrender.com';

/**
 * Fonction maîtresse pour exécuter toutes les requêtes fetch du projet.
 * Ajoute automatiquement le Header 'Authorization: Bearer <token>' si l'utilisateur est connecté.
 * * @param {string} endpoint - Le chemin de la route (ex: '/login' ou '/profile/me')
 * @param {string} method - 'GET', 'POST', 'PUT', 'DELETE'
 * @param {Object|null} body - Les données à envoyer au format JSON (optionnel)
 */
async function fetchAPI(endpoint, method = 'GET', body = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    // Récupération automatique du token JWT stocké lors du login
    const token = localStorage.getItem('mentorlink_token');

    // Configuration par défaut des headers
    const headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    };

    // Si un token existe, on l'injecte sous le standard Bearer
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        method: method,
        headers: headers
    };

    // Si la méthode a besoin d'un corps, on convertit l'objet JS en chaîne JSON
    if (body && (method === 'POST' || method === 'PUT')) {
        config.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(url, config);
        
        // Gestion automatique de l'expiration du Token (Erreur 401 Unauthorized)
        if (response.status === 401) {
            console.warn("Session expirée ou non autorisée. Redirection vers la page de connexion.");
            localStorage.removeItem('mentorlink_token');
            // Optionnel : rediriger automatiquement l'utilisateur s'il n'est pas sur login.html
            if (!window.location.pathname.includes('login.html')) {
                window.location.href = '/Frontend/pages/login.html';
            }
            throw new Error("Session expirée. Veuillez vous reconnecter.");
        }

        const data = await response.json();

        // Si le serveur backend renvoie une erreur (ex: 400 Bad Request, 404 Not Found)
        if (!response.ok) {
            throw new Error(data.message || `Erreur Serveur (Code ${response.status})`);
        }

        return data;

    } catch (error) {
        console.error(`[API Error] Erreur lors de la requête sur ${endpoint}:`, error);
        throw error; // On propage l'erreur pour que l'interface UI puisse l'afficher à l'écran
    }
}

// 2. EXPORTATION DES FONCTIONS CLÉS POUR TES COLLABORATEURS FRONTEND
// Tes équipiers n'auront qu'à appeler ces méthodes prêtes à l'emploi.

const API = {
    // Authentification (Tâche de J2)
    auth: {
        register: (userData) => fetchAPI('/register', 'POST', userData),
        login: (credentials) => fetchAPI('/login', 'POST', credentials)
    },

    // Gestion de profil (Tâche de J3)
    profile: {
        getMe: () => fetchAPI('/profile/me', 'GET'),
        updateMe: (profileData) => fetchAPI('/profile/me', 'PUT'),
        updateSkills: (skills) => fetchAPI('/profile/skills', 'POST'),
        updateAvailabilities: (dispos) => fetchAPI('/profile/availabilities', 'POST')
    },

    // Matching (Tâche de J4)
    matching: {
        getSuggestions: () => fetchAPI('/matches/suggestions', 'GET'),
        accept: (matchId) => fetchAPI(`/matches/${matchId}/accept`, 'POST'),
        reject: (matchId) => fetchAPI(`/matches/${matchId}/reject`, 'POST')
    },

    // Messagerie (Tâche de J4)
    messages: {
        getConversations: () => fetchAPI('/conversations', 'GET'),
        getHistory: (convId) => fetchAPI(`/conversations/${convId}/messages`, 'GET'),
        sendMessage: (convId, text) => fetchAPI(`/conversations/${convId}/messages`, 'POST', { text })
    }
};

// Rendre l'objet API accessible de n'importe où dans les scripts HTML du Frontend
window.MentorLinkAPI = API;