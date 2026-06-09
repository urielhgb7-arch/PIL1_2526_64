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
        deactivateCompetence: (matiereId) => fetchAPI(`/profile/competences/${matiereId}/deactivate`, 'PUT')
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
// Check authentication
function checkAuth(redirectTo = 'signin.html') {
  const isAuthenticated = localStorage.getItem('isAuthenticated');
  if (!isAuthenticated && window.location.pathname.includes('dashboard')) {
    window.location.href = redirectTo;
  }
}

// Navigate to page
function navigateTo(page) {
  window.location.href = page;
}

// Logout
function logout() {
  localStorage.removeItem('isAuthenticated');
  localStorage.removeItem('userEmail');
  localStorage.removeItem('userData');
  localStorage.removeItem('onboardingCompleted');
  const redirectPath = window.location.pathname.includes('/pages/') ? '../index.html' : 'index.html';
  window.location.href = redirectPath;
}

// Get user data
function getUserData() {
  const userData = localStorage.getItem('userData');
  return userData ? JSON.parse(userData) : null;
}

// Save user data
function saveUserData(data) {
  localStorage.setItem('userData', JSON.stringify(data));
}

// Toggle password visibility
function togglePassword(inputId) {
  const input = document.getElementById(inputId);
  const iconHide = document.getElementById(`${inputId}-icon-hide`);
  const iconShow = document.getElementById(`${inputId}-icon-show`);
  
  if (input.type === 'password') {
    input.type = 'text';
    iconHide.classList.add('hidden');
    iconShow.classList.remove('hidden');
  } else {
    input.type = 'password';
    iconHide.classList.remove('hidden');
    iconShow.classList.add('hidden');
  }
}

// Format date
function formatDate(date) {
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(date).toLocaleDateString('fr-FR', options);
}

// Format time
function formatTime(date) {
  const options = { hour: '2-digit', minute: '2-digit' };
  return new Date(date).toLocaleTimeString('fr-FR', options);
}
// Load matieres from API and cache locally with filiere + niveau filtering
let _matieresCache = null;

const DEFAULT_MATIERES = [
  { id: 1, nom: 'Algorithmique', filiere: 'GL', annee: 'L1' },
  { id: 2, nom: 'Structures de données', filiere: 'GL', annee: 'L2' },
  { id: 3, nom: 'Base de données SQL', filiere: 'GL', annee: 'L1' },
  { id: 4, nom: 'Programmation Orientée Objet', filiere: 'GL', annee: 'L2' },
  { id: 5, nom: 'Génie logiciel', filiere: 'GL', annee: 'L3' },
  { id: 6, nom: 'Architecture des ordinateurs', filiere: 'GL', annee: 'L1' },
  { id: 7, nom: 'Systèmes d\'exploitation', filiere: 'GL', annee: 'L2' },
  { id: 8, nom: 'Web Development', filiere: 'GL', annee: 'L2' },
  { id: 9, nom: 'Réseaux informatiques', filiere: 'RSI', annee: 'L1' },
  { id: 10, nom: 'Sécurité des réseaux', filiere: 'RSI', annee: 'L2' },
  { id: 11, nom: 'Télécommunications', filiere: 'RSI', annee: 'L2' },
  { id: 12, nom: 'Administration système', filiere: 'RSI', annee: 'L3' },
  { id: 13, nom: 'Cyberdéfense', filiere: 'Sécurité', annee: 'L3' },
  { id: 14, nom: 'Cryptographie', filiere: 'Sécurité', annee: 'L2' },
  { id: 15, nom: 'Sécurité des applications', filiere: 'Sécurité', annee: 'L3' },
  { id: 16, nom: 'Audit de sécurité', filiere: 'Sécurité', annee: 'L3' },
  { id: 17, nom: 'Intelligence artificielle', filiere: 'GL', annee: 'L3' },
  { id: 18, nom: 'Machine Learning', filiere: 'GL', annee: 'M1' },
  { id: 19, nom: 'Big Data', filiere: 'RSI', annee: 'M1' },
  { id: 20, nom: 'Cloud Computing', filiere: 'GL', annee: 'M1' },
  { id: 21, nom: 'Développement mobile', filiere: 'GL', annee: 'L3' },
  { id: 22, nom: 'Gestion de projet informatique', filiere: 'GL', annee: 'M2' },
  { id: 23, nom: 'Langage SQL avancé', filiere: 'RSI', annee: 'L3' },
  { id: 24, nom: 'Administration de bases de données', filiere: 'RSI', annee: 'M1' },
  { id: 25, nom: 'Sécurité web', filiere: 'Sécurité', annee: 'L3' },
  { id: 26, nom: 'Ethical Hacking', filiere: 'Sécurité', annee: 'M1' }
];

async function loadMatieresFromAPI() {
  if (_matieresCache) return _matieresCache;
  try {
    const data = await API.matieres.getAll();
    const matieres = data.matieres || data;
    if (Array.isArray(matieres) && matieres.length > 0) {
      _matieresCache = matieres;
      localStorage.setItem('matieres_cache', JSON.stringify(matieres));
      return matieres;
    }
  } catch (e) {
    console.warn('Failed to load matieres from API:', e);
  }

  const cached = localStorage.getItem('matieres_cache');
  if (cached) {
    try {
      _matieresCache = JSON.parse(cached);
      return _matieresCache;
    } catch (e) {
      console.warn('Invalid matieres cache:', e);
    }
  }

  _matieresCache = DEFAULT_MATIERES;
  return _matieresCache;
}

function getMatiersByFiliere(filiere = null) {
  if (!_matieresCache) return [];
  if (!filiere) return _matieresCache;
  return _matieresCache.filter(m => {
    const mFiliere = m.filiere || m.filiere_nom || m.departement || '';
    return mFiliere.toLowerCase().includes(filiere.toLowerCase()) ||
           filiere.toLowerCase().includes(mFiliere.toLowerCase());
  });
}

function getMatieresByFiliereAndNiveau(filiere = null, niveau = null) {
  if (!_matieresCache) return [];
  return _matieresCache.filter(m => {
    if (filiere) {
      const mFiliere = m.filiere || m.filiere_nom || m.departement || '';
      const matchFiliere = mFiliere.toLowerCase().includes(filiere.toLowerCase()) ||
                           filiere.toLowerCase().includes(mFiliere.toLowerCase());
      if (!matchFiliere) return false;
    }
    if (niveau) {
      const mNiveau = m.annee || m.niveau || m.annee_scolaire || '';
      if (mNiveau.toLowerCase() !== niveau.toLowerCase()) return false;
    }
    return true;
  });
}

async function initMatieresLoader() {
  if (/^\/(pages\/)?($|index\.html|signin\.html|signup\.html|reset-password\.html)/.test(window.location.pathname)) return;
  await loadMatieresFromAPI();
}

// Initialize on DOM ready
if (typeof window !== 'undefined') {
  document.addEventListener('DOMContentLoaded', initMatieresLoader);
}

window.loadMatieresFromAPI = loadMatieresFromAPI;
window.getMatiersByFiliere = getMatiersByFiliere;
window.getMatieresByFiliereAndNiveau = getMatieresByFiliereAndNiveau;
window.initMatieresLoader = initMatieresLoader;
// Centralized notifications badge updater
async function fetchUnreadCount() {
  try {
    const d = await API.notifications.getAll(true);
    const unread = d.unread_count ?? ((d.notifications || []).filter(n => !n.is_read && !n.lu).length);
    return unread;
  } catch (e) {
    console.warn('fetchUnreadCount', e);
    return 0;
  }
}

async function updateNotificationsBadge() {
  const unread = await fetchUnreadCount();
  const has = unread > 0;
  // find all bell elements we added
  const selectors = ['.site-bell', '.notif-bell', '.notification-btn'];
  selectors.forEach(sel => {
    document.querySelectorAll(sel).forEach(el => {
      if (has) el.classList.add('has-unread'); else el.classList.remove('has-unread');
      // update accessible label if present
      const label = el.getAttribute('aria-label') || '';
      el.setAttribute('aria-label', has ? `${label} — ${unread} non lue(s)` : label.replace(/ ?—.*$/, ''));
    });
  });
}

// Polling option to keep badge updated
let _notifInterval = null;
function startNotificationsBadgePoll(intervalMs = 30000) {
  updateNotificationsBadge();
  if (_notifInterval) clearInterval(_notifInterval);
  _notifInterval = setInterval(updateNotificationsBadge, intervalMs);
}

// Init on DOM ready
if (typeof window !== 'undefined') {
  document.addEventListener('DOMContentLoaded', () => {
    const pub = /^\/(pages\/)?($|index\.html|signin\.html|signup\.html|reset-password\.html)/.test(window.location.pathname);
    if (!pub) startNotificationsBadgePoll();
  });
}

// expose for manual control
window.updateNotificationsBadge = updateNotificationsBadge;
window.startNotificationsBadgePoll = startNotificationsBadgePoll;
