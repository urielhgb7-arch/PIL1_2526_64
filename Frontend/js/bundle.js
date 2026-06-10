/**
 * MentorLink — Bundle JS unique
 * Regroupe : api.js / script.js / matieres-loader.js / notifications-badge.js / logger.js
 * Généré le 10/06/2026
 */
// ============================================================
// LOGGER
// ============================================================
const Logger = {
    _injectToastStyles() {
        if (document.getElementById("mentorlink-toast-styles")) return;
        const style = document.createElement("style");
        style.id = "mentorlink-toast-styles";
        style.textContent = `
.mentorlink-toast {
  position: fixed; bottom: 1.5rem; right: 1.5rem; z-index: 99999;
  padding: 0.75rem 1.25rem; border-radius: 0.5rem; color: #fff;
  font-size: 0.875rem; font-weight: 500; max-width: 24rem;
  box-shadow: 0 10px 25px rgba(0,0,0,0.3);
  transform: translateY(1rem); opacity: 0;
  transition: transform 0.25s ease, opacity 0.25s ease;
  pointer-events: none;
}
.mentorlink-toast.show { transform: translateY(0); opacity: 1; }
.mentorlink-toast.success { background: #10b981; }
.mentorlink-toast.error { background: #ef4444; }
.mentorlink-toast.info { background: #6366f1; }
.mentorlink-toast.warning { background: #f59e0b; }
`;
        document.head.appendChild(style);
    },

    _toast(message, type = "info") {
        this._injectToastStyles();
        const existing = document.querySelector(".mentorlink-toast");
        if (existing) existing.remove();
        const div = document.createElement("div");
        div.className = `mentorlink-toast ${type}`;
        div.textContent = message;
        document.body.appendChild(div);
        requestAnimationFrame(() => div.classList.add("show"));
        setTimeout(() => {
            div.classList.remove("show");
            setTimeout(() => div.remove(), 300);
        }, 4000);
    },

    info(msg) { this._toast(msg, "info"); },
    warn(msg) { this._toast(msg, "warning"); console.warn(msg); },
    error(msg) { this._toast(msg, "error"); console.error(msg); },
    success(msg) { this._toast(msg, "success"); }
};

// ============================================================
// API
// ============================================================
const API_BASE_URL = (window.API_BASE_URL || (
    window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost'
        ? 'http://127.0.0.1:5000/api'
        : 'https://ifri-mentorlink.onrender.com/api'
));

async function uploadFileAPI(endpoint, method = 'POST', formData = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = localStorage.getItem('mentorlink_token');
    const headers = { 'Accept': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    function getLoginRedirectPath() {
        return window.location.pathname.includes('/pages/') ? 'signin.html' : 'pages/signin.html';
    }

    try {
        const response = await fetch(url, { method, headers, body: formData });
        if (response.status === 401) {
            const pub = /^\/(pages\/)?($|index\.html|signin\.html|signup\.html|reset-password\.html)/.test(window.location.pathname);
            if (pub) throw new Error('Non authentifié');
            localStorage.removeItem('mentorlink_token');
            localStorage.removeItem('mentorlink_user');
            window.location.href = getLoginRedirectPath();
            throw new Error('Session expirée. Veuillez vous reconnecter.');
        }
        let data;
        const ct = response.headers.get('content-type') || '';
        if (ct.includes('application/json')) {
            data = await response.json();
        } else {
            const text = await response.text();
            try { data = JSON.parse(text); } catch (_) { data = { message: text }; }
        }
        if (!response.ok) throw new Error(data.message || `Erreur Serveur (Code ${response.status})`);
        return data;
    } catch (error) {
        console.error(`[API Upload Error] ${endpoint}:`, error);
        throw error;
    }
}

async function fetchAPI(endpoint, method = 'GET', body = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = localStorage.getItem('mentorlink_token');
    const headers = { 'Content-Type': 'application/json', 'Accept': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const config = { method, headers };
    if (body && (method === 'POST' || method === 'PUT' || method === 'DELETE')) {
        config.body = JSON.stringify(body);
    }

    function getLoginRedirectPath() {
        return window.location.pathname.includes('/pages/') ? 'signin.html' : 'pages/signin.html';
    }

    try {
        const response = await fetch(url, config);
        if (response.status === 401) {
            const pub = /^\/(pages\/)?($|index\.html|signin\.html|signup\.html|reset-password\.html)/.test(window.location.pathname);
            if (pub) throw new Error('Non authentifié');
            localStorage.removeItem('mentorlink_token');
            localStorage.removeItem('mentorlink_user');
            window.location.href = getLoginRedirectPath();
            throw new Error('Session expirée. Veuillez vous reconnecter.');
        }
        let data;
        const ct = response.headers.get('content-type') || '';
        if (ct.includes('application/json')) {
            data = await response.json();
        } else {
            const text = await response.text();
            try { data = JSON.parse(text); } catch (_) { data = { message: text }; }
        }
        if (!response.ok) throw new Error(data.message || `Erreur Serveur (Code ${response.status})`);
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

// ============================================================
// SCRIPT.JS — Utilitaires partagés
// ============================================================
const API_BASE = API_BASE_URL;

function checkAuth(redirectTo) {
  if (!redirectTo) {
    redirectTo = window.location.pathname.includes('/pages/') ? 'signin.html' : 'pages/signin.html';
  }
  const pub = /^\/(pages\/)?($|index\.html|signin\.html|signup\.html|reset-password\.html)/;
  if (!pub.test(window.location.pathname) && !localStorage.getItem('mentorlink_token')) {
    window.location.replace(redirectTo);
  }
}
function navigateTo(page) { window.location.href = page; }
function logout() {
  localStorage.removeItem('isAuthenticated');
  localStorage.removeItem('userEmail');
  localStorage.removeItem('userData');
  localStorage.removeItem('onboardingCompleted');
  localStorage.removeItem('mentorlink_token');
  localStorage.removeItem('mentorlink_user');
  localStorage.removeItem('mentorlink_profile_cache');
  const p = window.location.pathname.includes('/pages/') ? '../index.html' : 'index.html';
  window.location.href = p;
}
function getUserData() {
  const d = localStorage.getItem('userData');
  return d ? JSON.parse(d) : null;
}
function saveUserData(data) { localStorage.setItem('userData', JSON.stringify(data)); }
function togglePassword(inputId) {
  const input = document.getElementById(inputId);
  const hide = document.getElementById(inputId+'-icon-hide');
  const show = document.getElementById(inputId+'-icon-show');
  if (input.type === 'password') { input.type = 'text'; hide.classList.add('hidden'); show.classList.remove('hidden'); }
  else { input.type = 'password'; hide.classList.remove('hidden'); show.classList.add('hidden'); }
}
// Legacy formatDate/formatTime (override originaux du bundle)
function formatDate(date) { return new Date(date).toLocaleDateString('fr-FR',{year:'numeric',month:'long',day:'numeric'}); }
function formatTime(date) { return new Date(date).toLocaleTimeString('fr-FR',{hour:'2-digit',minute:'2-digit'}); }

// Redirection si non connecté
(function guardRoute() {
    const pub = /^\/(pages\/)?($|index\.html|signin\.html|signup\.html|reset-password\.html)/;
    if (!pub.test(window.location.pathname) && !localStorage.getItem('mentorlink_token')) {
        const loginPage = window.location.pathname.includes('/pages/') ? 'signin.html' : 'pages/signin.html';
        window.location.replace(loginPage);
    }
})();

function showToast(message, type) {
    Logger._toast(message, type);
}

function formatDate(isoString) {
    if (!isoString) return '';
    const d = new Date(isoString);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    return `${day}/${month}/${year} ${hours}:${minutes}`;
}

// ============================================================
// MATIERES-LOADER
// ============================================================
(async function loadMatieres() {
    try {
        const data = await API.matieres.getAll();
        if (data && data.matieres) {
            window._matieresList = data.matieres;
        }
    } catch (_) {}
})();

function getMatieresList() {
    return window._matieresList || [];
}

function getMatiereLabel(matiereId) {
    if (!window._matieresList) return matiereId;
    const found = window._matieresList.find(m => String(m.id) === String(matiereId));
    return found ? found.nom : matiereId;
}

function renderMatiereOptions(selectEl, selectedId) {
    if (!window._matieresList) return;
    selectEl.innerHTML = '<option value="">Sélectionnez une matière</option>';
    window._matieresList.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m.id;
        opt.textContent = m.nom;
        if (String(m.id) === String(selectedId)) opt.selected = true;
        selectEl.appendChild(opt);
    });
}

// ============================================================
// NOTIFICATIONS-BADGE
// ============================================================
(async function initNotificationsBadge() {
    if (!localStorage.getItem('mentorlink_token')) return;
    try {
        const data = await API.notifications.getAll(true);
        const unreadCount = (data && data.notifications) ? data.notifications.length : 0;
        const badge = document.getElementById('notifications-badge');
        const link = document.querySelector('a[href*="notifications"]');
        if (badge) {
            badge.textContent = unreadCount;
            badge.classList.toggle('hidden', unreadCount === 0);
        }
        if (link && unreadCount > 0) {
            link.innerHTML += ` <span id="notifications-badge-alt" class="bg-red-500 text-white text-xs rounded-full px-1.5">${unreadCount}</span>`;
        }
    } catch (_) {}
})();
