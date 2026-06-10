/**
 * MentorLink — Bundle JS unique
 * Regroupe : api.js / script.js / matieres-loader.js / notifications-badge.js / logger.js
 */
// ============================================================
// LOGGER
// ============================================================
const Logger = {
    _injectToastStyles() {
        if (document.getElementById("mentorlink-toast-styles")) return;
        const s = document.createElement("style");
        s.id = "mentorlink-toast-styles";
        s.textContent = `.mentorlink-toast{position:fixed;bottom:1.5rem;right:1.5rem;z-index:99999;padding:.75rem 1.25rem;border-radius:.5rem;color:#fff;font-size:.875rem;font-weight:500;max-width:24rem;box-shadow:0 10px 25px rgba(0,0,0,.3);transform:translateY(1rem);opacity:0;transition:transform .25s ease,opacity .25s ease;pointer-events:none}.mentorlink-toast.show{transform:translateY(0);opacity:1}.mentorlink-toast.success{background:#10b981}.mentorlink-toast.error{background:#ef4444}.mentorlink-toast.info{background:#6366f1}.mentorlink-toast.warning{background:#f59e0b}`;
        document.head.appendChild(s);
    },
    _toast(m, t) {
        this._injectToastStyles();
        const old = document.querySelector(".mentorlink-toast");
        if (old) old.remove();
        const d = document.createElement("div");
        d.className = "mentorlink-toast " + t;
        d.textContent = m;
        document.body.appendChild(d);
        requestAnimationFrame(() => d.classList.add("show"));
        setTimeout(() => { d.classList.remove("show"); setTimeout(() => d.remove(), 300); }, 4000);
    },
    info(m) { this._toast(m, "info"); },
    warn(m) { this._toast(m, "warning"); console.warn(m); },
    error(m) { this._toast(m, "error"); console.error(m); },
    success(m) { this._toast(m, "success"); }
};

// ============================================================
// API
// ============================================================
const API_BASE_URL = (window.API_BASE_URL || (
    window.location.protocol === 'file:' ||
    window.location.hostname === '127.0.0.1' ||
    window.location.hostname === 'localhost'
        ? 'http://127.0.0.1:5000/api'
        : 'https://ifri-mentorlink.onrender.com/api'
));

async function uploadFileAPI(endpoint, method, formData) {
    const url = API_BASE_URL + endpoint;
    const token = localStorage.getItem('mentorlink_token');
    const headers = { 'Accept': 'application/json' };
    if (token) headers['Authorization'] = 'Bearer ' + token;
    const loginPath = () => window.location.pathname.includes('/pages/') ? 'signin.html' : 'pages/signin.html';
    try {
        const res = await fetch(url, { method, headers, body: formData });
        if (res.status === 401) {
            if (/^\/(pages\/)?($|index\.html|signin\.html|signup\.html|reset-password\.html)/.test(window.location.pathname))
                throw new Error('Non authentifi\u00e9');
            localStorage.removeItem('mentorlink_token');
            localStorage.removeItem('mentorlink_user');
            window.location.href = loginPath();
            throw new Error('Session expir\u00e9e');
        }
        const isJson = (res.headers.get('content-type') || '').includes('application/json');
        let data;
        if (isJson) data = await res.json();
        else {
            const text = await res.text();
            try { data = JSON.parse(text); } catch (_) { data = { message: text }; }
        }
        if (!res.ok) throw new Error((data.message || ('Erreur (' + res.status + ')')) + (data.error ? ': ' + data.error : ''));
        return data;
    } catch (e) {
        console.error('[API Upload] ' + endpoint + ':', e);
        throw e;
    }
}

async function fetchAPI(endpoint, method, body) {
    const url = API_BASE_URL + endpoint;
    const token = localStorage.getItem('mentorlink_token');
    const headers = { 'Content-Type': 'application/json', 'Accept': 'application/json' };
    if (token) headers['Authorization'] = 'Bearer ' + token;
    const config = { method, headers };
    if (body && (method === 'POST' || method === 'PUT' || method === 'DELETE'))
        config.body = JSON.stringify(body);
    const loginPath = () => window.location.pathname.includes('/pages/') ? 'signin.html' : 'pages/signin.html';
    try {
        const res = await fetch(url, config);
        if (res.status === 401) {
            if (/^\/(pages\/)?($|index\.html|signin\.html|signup\.html|reset-password\.html)/.test(window.location.pathname))
                throw new Error('Non authentifi\u00e9');
            localStorage.removeItem('mentorlink_token');
            localStorage.removeItem('mentorlink_user');
            window.location.href = loginPath();
            throw new Error('Session expir\u00e9e');
        }
        const isJson = (res.headers.get('content-type') || '').includes('application/json');
        let data;
        if (isJson) data = await res.json();
        else {
            const text = await res.text();
            try { data = JSON.parse(text); } catch (_) { data = { message: text }; }
        }
        if (!res.ok) throw new Error((data.message || ('Erreur (' + res.status + ')')) + (data.error ? ': ' + data.error : ''));
        return data;
    } catch (e) {
        console.error('[API Error] ' + endpoint + ':', e);
        throw e;
    }
}

const API = {
    auth: {
        register: (d) => fetchAPI('/auth/register', 'POST', d),
        login: (d) => fetchAPI('/auth/login', 'POST', d),
        forgotPassword: (d) => fetchAPI('/auth/forgot-password', 'POST', d),
        resetPassword: (d) => fetchAPI('/auth/reset-password', 'POST', d),
        changePassword: (d) => {
            const p = {
                old_password: d.old_password || d.ancien_mot_de_passe || d.oldPassword,
                new_password: d.new_password || d.nouveau_mot_de_passe || d.newPassword
            };
            return fetchAPI('/auth/change-password', 'PUT', p);
        },
        deleteAccount: (d) => {
            const password = typeof d === 'string' ? d : d.password;
            return fetchAPI('/auth/delete-account', 'DELETE', { password });
        }
    },
    profile: {
        getMe: () => fetchAPI('/profile/me', 'GET'),
        updateMe: (d) => fetchAPI('/profile/me', 'PUT', d),
        addCompetence: (d) => fetchAPI('/profile/competences', 'POST', d),
        removeCompetence: (d) => fetchAPI('/profile/competences', 'DELETE', d),
        addLacune: (d) => fetchAPI('/profile/lacunes', 'POST', d),
        removeLacune: (d) => fetchAPI('/profile/lacunes', 'DELETE', d),
        addDisponibilite: (d) => fetchAPI('/profile/disponibilites', 'POST', d),
        removeDisponibilite: (d) => fetchAPI('/profile/disponibilites', 'DELETE', d),
        activateCompetence: (id) => fetchAPI('/profile/competences/' + id + '/activate', 'PUT'),
        deactivateCompetence: (id) => fetchAPI('/profile/competences/' + id + '/deactivate', 'PUT'),
        updateAvatar: (d) => fetchAPI('/profile/avatar', 'PUT', d),
        uploadAvatar: (fd) => uploadFileAPI('/profile/avatar/upload', 'POST', fd)
    },
    matching: {
        getSuggestions: (filters) => {
            filters = filters || {};
            const params = new URLSearchParams(filters).toString();
            return fetchAPI('/matches/suggestions' + (params ? '?' + params : ''), 'GET');
        },
        requestMatch: (id, body) => fetchAPI('/matches/' + id + '/request', 'POST', body),
        accept: (id) => fetchAPI('/matches/' + id + '/accept', 'POST'),
        reject: (id) => fetchAPI('/matches/' + id + '/reject', 'POST'),
        skipMatch: (id, body) => fetchAPI('/matches/' + id + '/skip', 'POST', body),
        getReceived: () => fetchAPI('/matches/received', 'GET'),
        getSent: () => fetchAPI('/matches/sent', 'GET')
    },
    messages: {
        getConversations: () => fetchAPI('/conversations', 'GET'),
        create: (id) => fetchAPI('/conversations', 'POST', { user_id: id }),
        getHistory: (id) => fetchAPI('/conversations/' + id + '/messages', 'GET'),
        send: (id, text) => fetchAPI('/conversations/' + id + '/messages', 'POST', { contenu: text })
    },
    notifications: {
        getAll: (unreadOnly) => fetchAPI('/notifications' + (unreadOnly ? '?unread_only=true' : ''), 'GET'),
        markRead: (id) => fetchAPI('/notifications/' + id + '/read', 'PUT'),
        markAllRead: () => fetchAPI('/notifications/read-all', 'PUT'),
        delete: (id) => fetchAPI('/notifications/' + id, 'DELETE')
    },
    offers: {
        getAll: () => fetchAPI('/offers', 'GET'),
        getMine: () => fetchAPI('/offers/mine', 'GET'),
        create: (d) => fetchAPI('/offers', 'POST', d),
        delete: (id) => fetchAPI('/offers/' + id, 'DELETE'),
        respond: (id) => fetchAPI('/offers/' + id + '/respond', 'POST')
    },
    demands: {
        getAll: () => fetchAPI('/demands', 'GET'),
        getMine: () => fetchAPI('/demands/mine', 'GET'),
        create: (d) => fetchAPI('/demands', 'POST', d),
        delete: (id) => fetchAPI('/demands/' + id, 'DELETE'),
        offerHelp: (id) => fetchAPI('/demands/' + id + '/offer-help', 'POST')
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
    if (!redirectTo)
        redirectTo = window.location.pathname.includes('/pages/') ? 'signin.html' : 'pages/signin.html';
    const pub = /^\/(pages\/)?($|index\.html|signin\.html|signup\.html|reset-password\.html)/;
    if (!pub.test(window.location.pathname) && !localStorage.getItem('mentorlink_token'))
        window.location.replace(redirectTo);
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

function saveUserData(d) { localStorage.setItem('userData', JSON.stringify(d)); }

function togglePassword(id) {
    const input = document.getElementById(id);
    const hide = document.getElementById(id + '-icon-hide');
    const show = document.getElementById(id + '-icon-show');
    if (input.type === 'password') {
        input.type = 'text';
        hide.classList.add('hidden');
        show.classList.remove('hidden');
    } else {
        input.type = 'password';
        hide.classList.remove('hidden');
        show.classList.add('hidden');
    }
}

function formatDate(date) { return new Date(date).toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric' }); }
function formatTime(date) { return new Date(date).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }); }

(function guardRoute() {
    const pub = /^\/(pages\/)?($|index\.html|signin\.html|signup\.html|reset-password\.html)/;
    if (!pub.test(window.location.pathname) && !localStorage.getItem('mentorlink_token')) {
        const p = window.location.pathname.includes('/pages/') ? 'signin.html' : 'pages/signin.html';
        window.location.replace(p);
    }
})();

function showToast(message, type) { Logger._toast(message, type); }

// ============================================================
// MATIERES-LOADER
// ============================================================
var _matieresCache = null;

var DEFAULT_MATIERES = [
  { id: 1, nom: 'Algorithmique', filiere: 'GL', annee: 'L1' },
  { id: 2, nom: 'Structures de donn\u00e9es', filiere: 'GL', annee: 'L2' },
  { id: 3, nom: 'Base de donn\u00e9es SQL', filiere: 'GL', annee: 'L1' },
  { id: 4, nom: 'Programmation Orient\u00e9e Objet', filiere: 'GL', annee: 'L2' },
  { id: 5, nom: 'G\u00e9nie logiciel', filiere: 'GL', annee: 'L3' },
  { id: 6, nom: 'Architecture des ordinateurs', filiere: 'GL', annee: 'L1' },
  { id: 7, nom: "Syst\u00e8mes d'exploitation", filiere: 'GL', annee: 'L2' },
  { id: 8, nom: 'Web Development', filiere: 'GL', annee: 'L2' },
  { id: 9, nom: 'R\u00e9seaux informatiques', filiere: 'RSI', annee: 'L1' },
  { id: 10, nom: 'S\u00e9curit\u00e9 des r\u00e9seaux', filiere: 'RSI', annee: 'L2' },
  { id: 11, nom: 'T\u00e9l\u00e9communications', filiere: 'RSI', annee: 'L2' },
  { id: 12, nom: 'Administration syst\u00e8me', filiere: 'RSI', annee: 'L3' },
  { id: 13, nom: 'Cyberd\u00e9fense', filiere: 'S\u00e9curit\u00e9', annee: 'L3' },
  { id: 14, nom: 'Cryptographie', filiere: 'S\u00e9curit\u00e9', annee: 'L2' },
  { id: 15, nom: 'S\u00e9curit\u00e9 des applications', filiere: 'S\u00e9curit\u00e9', annee: 'L3' },
  { id: 16, nom: 'Audit de s\u00e9curit\u00e9', filiere: 'S\u00e9curit\u00e9', annee: 'L3' },
  { id: 17, nom: 'Intelligence artificielle', filiere: 'GL', annee: 'L3' },
  { id: 18, nom: 'Machine Learning', filiere: 'GL', annee: 'M1' },
  { id: 19, nom: 'Big Data', filiere: 'RSI', annee: 'M1' },
  { id: 20, nom: 'Cloud Computing', filiere: 'GL', annee: 'M1' },
  { id: 21, nom: 'D\u00e9veloppement mobile', filiere: 'GL', annee: 'L3' },
  { id: 22, nom: 'Gestion de projet informatique', filiere: 'GL', annee: 'M2' },
  { id: 23, nom: 'Langage SQL avanc\u00e9', filiere: 'RSI', annee: 'L3' },
  { id: 24, nom: 'Administration de bases de donn\u00e9es', filiere: 'RSI', annee: 'M1' },
  { id: 25, nom: 'S\u00e9curit\u00e9 web', filiere: 'S\u00e9curit\u00e9', annee: 'L3' },
  { id: 26, nom: 'Ethical Hacking', filiere: 'S\u00e9curit\u00e9', annee: 'M1' }
];

async function loadMatieresFromAPI() {
  if (_matieresCache) return _matieresCache;
  try {
    var data = await API.matieres.getAll();
    var matieres = data.matieres || data;
    if (Array.isArray(matieres) && matieres.length > 0) {
      _matieresCache = matieres;
      window._matieresList = matieres;
      localStorage.setItem('matieres_cache', JSON.stringify(matieres));
      return matieres;
    }
  } catch (e) {
    console.warn('Failed to load matieres from API:', e);
  }
  var cached = localStorage.getItem('matieres_cache');
  if (cached) {
    try {
      _matieresCache = JSON.parse(cached);
      window._matieresList = _matieresCache;
      return _matieresCache;
    } catch (e) {
      console.warn('Invalid matieres cache:', e);
    }
  }
  _matieresCache = DEFAULT_MATIERES;
  window._matieresList = DEFAULT_MATIERES;
  return _matieresCache;
}

function getMatiersByFiliere(filiere) {
  if (!_matieresCache) return [];
  if (!filiere) return _matieresCache;
  return _matieresCache.filter(function(m) {
    var mFiliere = m.filiere || m.filiere_nom || m.departement || '';
    return mFiliere.toLowerCase().includes(filiere.toLowerCase()) ||
           filiere.toLowerCase().includes(mFiliere.toLowerCase());
  });
}

function getMatieresByFiliereAndNiveau(filiere, niveau) {
  if (!_matieresCache) return [];
  return _matieresCache.filter(function(m) {
    if (filiere) {
      var mFiliere = m.filiere || m.filiere_nom || m.departement || '';
      var matchFiliere = mFiliere.toLowerCase().includes(filiere.toLowerCase()) ||
                         filiere.toLowerCase().includes(mFiliere.toLowerCase());
      if (!matchFiliere) return false;
    }
    if (niveau) {
      var mNiveau = m.annee || m.niveau || m.annee_scolaire || '';
      if (mNiveau.toLowerCase() !== niveau.toLowerCase()) return false;
    }
    return true;
  });
}

// Keep existing helpers for backward compat
function getMatieresList() { return window._matieresList || []; }
function getMatiereLabel(id) {
    if (!window._matieresList) return id;
    var found = window._matieresList.find(function(m) { return String(m.id) === String(id); });
    return found ? found.nom : id;
}
function renderMatiereOptions(sel, selectedId) {
    if (!window._matieresList) return;
    sel.innerHTML = '<option value="">S\u00e9lectionnez une mati\u00e8re</option>';
    window._matieresList.forEach(function(m) {
        var opt = document.createElement('option');
        opt.value = m.id;
        opt.textContent = m.nom;
        if (String(m.id) === String(selectedId)) opt.selected = true;
        sel.appendChild(opt);
    });
}

// Auto-load matieres on page load if authenticated
(async function initMatieres() {
    if (!localStorage.getItem('mentorlink_token')) return;
    try { await loadMatieresFromAPI(); } catch (_) {}
})();

// ============================================================
// NIVEAU / FILIERE LABELS
// ============================================================
var _NIVEAU_LABELS = {
    L1: "Licence 1",
    L2: "Licence 2",
    L3: "Licence 3",
    M1: "Master 1",
    M2: "Master 2",
};
var _FILIERE_LABELS = {
    GL: "G\u00e9nie Logiciel",
    RSI: "R\u00e9seaux et Syst\u00e8mes d'Information",
    SI: "Syst\u00e8mes d'Information",
    IA: "Intelligence Artificielle",
    IM: "Ing\u00e9nierie Math\u00e9matique",
    SIRI: "S\u00e9curit\u00e9 Informatique",
    SEoIT: "Software Engineering",
};
function niveauLabel(val) {
    return _NIVEAU_LABELS[val] || val || "\u2014";
}
function filiereLabel(val, short) {
    if (!val) return "\u2014";
    if (short) return val;
    return _FILIERE_LABELS[val] ? _FILIERE_LABELS[val] + " (" + val + ")" : val;
}

// ============================================================
// NOTIFICATIONS-BADGE — petit point jaune sur la cloche
// ============================================================
function toggleBellDot(show) {
    document.querySelectorAll('.site-bell').forEach(el => {
        el.classList.toggle('has-unread', show);
    });
}

async function updateNotificationsBadge() {
    if (!localStorage.getItem('mentorlink_token')) return;
    try {
        const data = await API.notifications.getAll(true);
        const count = (data && data.notifications) ? data.notifications.length : 0;
        toggleBellDot(count > 0);
    } catch (_) {}
}

(async function initNotificationsBadge() {
    await updateNotificationsBadge();
    if (localStorage.getItem('mentorlink_token')) {
        setInterval(updateNotificationsBadge, 30000);
    }
})();
