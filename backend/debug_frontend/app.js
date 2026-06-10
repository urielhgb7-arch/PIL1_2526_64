const DEFAULT_BACKEND_URL = 'http://127.0.0.1:5000/api';
let BACKEND_API_BASE = DEFAULT_BACKEND_URL;
let authToken = null;
let latestRequest = null;
let latestResponse = null;

const severityMap = {
    'Basse': 'Basse',
    'Moyenne': 'Moyenne',
    'Haute': 'Haute',
    'Urgente': 'Urgente'
};

function init() {
    document.getElementById('backendUrl').value = BACKEND_API_BASE;
    document.getElementById('saveBackendUrl').addEventListener('click', saveBackendUrl);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('logoutButton').addEventListener('click', handleLogout);
    document.getElementById('loadProfile').addEventListener('click', loadProfile);
    document.getElementById('updateProfileForm').addEventListener('submit', handleUpdateProfile);
    document.getElementById('loadMatieres').addEventListener('click', loadMatieres);
    document.getElementById('addCompetenceForm').addEventListener('submit', handleAddCompetence);
    document.getElementById('addWeaknessForm').addEventListener('submit', handleAddWeakness);
    document.getElementById('addAvailabilityForm').addEventListener('submit', handleAddAvailability);
    document.getElementById('runMatching').addEventListener('click', runMatching);
    document.getElementById('createRequest').addEventListener('click', handleCreateRequest);
    document.getElementById('viewSentRequests').addEventListener('click', () => loadRequests('sent'));
    document.getElementById('viewReceivedRequests').addEventListener('click', () => loadRequests('received'));
    document.getElementById('loadNotifications').addEventListener('click', loadNotifications);
    document.getElementById('markAllRead').addEventListener('click', markAllNotificationsRead);
    document.getElementById('loadConversations').addEventListener('click', loadConversations);
    document.getElementById('openConversation').addEventListener('click', openConversation);
    document.getElementById('sendMessageForm').addEventListener('submit', handleSendMessage);
    document.getElementById('viewProfileJson').addEventListener('click', loadProfile);
    updateStatus();
}

function saveBackendUrl() {
    BACKEND_API_BASE = document.getElementById('backendUrl').value.trim() || DEFAULT_BACKEND_URL;
    displayInfo(`Backend URL défini sur ${BACKEND_API_BASE}`);
}

function updateStatus() {
    const statusText = document.getElementById('statusText');
    const userEmail = document.getElementById('userEmail');
    if (authToken) {
        statusText.innerText = 'Connecté';
        userEmail.innerText = localStorage.getItem('debug_user_email') || '-';
    } else {
        statusText.innerText = 'Déconnecté';
        userEmail.innerText = '-';
    }
}

function saveToken(token, email) {
    authToken = token;
    localStorage.setItem('debug_api_token', token);
    localStorage.setItem('debug_user_email', email || '');
    updateStatus();
}

function loadSavedToken() {
    const token = localStorage.getItem('debug_api_token');
    if (token) {
        authToken = token;
    }
    updateStatus();
}

function clearSession() {
    authToken = null;
    localStorage.removeItem('debug_api_token');
    localStorage.removeItem('debug_user_email');
    updateStatus();
    displayInfo('Session déconnectée.');
}

function buildHeaders() {
    const headers = { 'Accept': 'application/json', 'Content-Type': 'application/json' };
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }
    return headers;
}

async function apiFetch(path, options = {}) {
    const url = `${BACKEND_API_BASE}${path}`;
    const config = { headers: buildHeaders(), ...options };
    if (config.body && typeof config.body !== 'string') {
        config.body = JSON.stringify(config.body);
    }

    latestRequest = { method: config.method || 'GET', url, body: config.body ? JSON.parse(config.body) : null };
    renderRequestInspector();

    try {
        const response = await fetch(url, config);
        const contentType = response.headers.get('content-type') || '';
        let body = null;
        if (contentType.includes('application/json')) {
            body = await response.json();
        } else {
            body = await response.text();
        }

        latestResponse = { status: response.status, body };
        renderResponse();

        if (!response.ok) {
            throw new Error(`HTTP ${response.status} - ${JSON.stringify(body)}`);
        }
        return body;
    } catch (error) {
        latestResponse = { status: 'ERROR', body: error.message };
        renderResponse();
        throw error;
    }
}

function renderRequestInspector() {
    const inspector = document.getElementById('requestInspector');
    inspector.textContent = JSON.stringify(latestRequest, null, 2);
}

function renderResponse() {
    const output = document.getElementById('apiResponse');
    output.textContent = JSON.stringify(latestResponse, null, 2);
}

function displayInfo(message) {
    const output = document.getElementById('apiResponse');
    latestResponse = { status: 'INFO', body: message };
    renderResponse();
}

async function handleRegister(event) {
    event.preventDefault();
    const form = event.target;
    const data = Object.fromEntries(new FormData(form).entries());
    try {
        const body = {
            email: data.email,
            password: data.password,
            nom: data.nom,
            prenom: data.prenom,
            filiere: data.filiere,
            niveau: data.niveau,
            format_preference: data.format_preference
        };
        const response = await apiFetch('/auth/register', { method: 'POST', body });
        displayInfo(`Inscription réussie : ${response.message}`);
        form.reset();
    } catch (err) {
        displayError(err);
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const form = event.target;
    const data = Object.fromEntries(new FormData(form).entries());
    try {
        const response = await apiFetch('/auth/login', { method: 'POST', body: { email: data.email, password: data.password } });
        saveToken(response.token, response.user.email);
        displayInfo('Connexion réussie.');
    } catch (err) {
        displayError(err);
    }
}

function handleLogout() {
    clearSession();
}

async function loadProfile() {
    try {
        const profile = await apiFetch('/profile/me');
        document.getElementById('profileData').textContent = JSON.stringify(profile, null, 2);
    } catch (err) {
        displayError(err);
    }
}

async function handleUpdateProfile(event) {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.target).entries());
    const payload = {
        nom: data.nom || undefined,
        prenom: data.prenom || undefined,
        filiere: data.filiere || undefined,
        niveau: data.niveau || undefined,
        format_preference: data.format_preference || undefined,
        bio: data.bio || undefined,
        telephone: data.telephone || undefined,
        disponible: event.target.elements.disponible.checked
    };
    try {
        await apiFetch('/profile/me', { method: 'PUT', body: payload });
        displayInfo('Profil mis à jour. Rechargez le profil pour voir les changements.');
    } catch (err) {
        displayError(err);
    }
}

async function loadMatieres() {
    try {
        const matieres = await apiFetch('/matieres');
        const options = matieres.map(m => `<option value="${m.id}">${m.nom} (${m.filiere || 'N/A'} - ${m.annee || 'N/A'})</option>`).join('');
        
        // Remplit tous les selects de matières
        document.getElementById('competenceMatiere').innerHTML = options;
        document.getElementById('weaknessMatiere').innerHTML = options;
        document.getElementById('requestMatiere').innerHTML = options;
        
        displayInfo(`✅ ${matieres.length} matières chargées et remplies dans les listes déroulantes.`);
    } catch (err) {
        displayError(err);
    }
}

async function handleAddCompetence(event) {
    event.preventDefault();
    const form = event.target;
    const data = Object.fromEntries(new FormData(form).entries());
    const payload = {
        matiere_id: Number(data.matiere_id),
        niveau: data.niveau,
        is_available_to_help: form.elements.is_available_to_help.checked
    };
    try {
        const result = await apiFetch('/profile/competences', { method: 'POST', body: payload });
        document.getElementById('competenceResult').textContent = JSON.stringify(result, null, 2);
        form.reset();
    } catch (err) {
        displayError(err);
    }
}

async function handleAddWeakness(event) {
    event.preventDefault();
    const form = event.target;
    const data = Object.fromEntries(new FormData(form).entries());
    const payload = { matiere_id: Number(data.matiere_id), priorite: data.priorite };
    try {
        const result = await apiFetch('/profile/lacunes', { method: 'POST', body: payload });
        document.getElementById('weaknessResult').textContent = JSON.stringify(result, null, 2);
        form.reset();
    } catch (err) {
        displayError(err);
    }
}

async function handleAddAvailability(event) {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.target).entries());
    const payload = { jour: data.jour, creneau: data.creneau };
    try {
        const result = await apiFetch('/profile/disponibilites', { method: 'POST', body: payload });
        document.getElementById('availabilityResult').textContent = JSON.stringify(result, null, 2);
        event.target.reset();
    } catch (err) {
        displayError(err);
    }
}

async function runMatching() {
    try {
        const matches = await apiFetch('/matches/suggestions');
        renderMatching(matches.matches || []);
    } catch (err) {
        displayError(err);
    }
}

function renderMatching(matches) {
    const container = document.getElementById('matchingResults');
    if (!matches.length) {
        container.innerHTML = '<div class="response-box">Aucun matching trouvé.</div>';
        return;
    }
    container.innerHTML = matches.map(match => {
        const reasons = match.explication?.raisons?.join(' • ') || '';
        const detail = match.score_detail || {};
        return `
            <div class="match-card">
                <h3>${match.prenom} ${match.nom} (${match.filiere} - ${match.niveau})</h3>
                <strong>Score : ${match.score}%</strong>
                <p>${reasons}</p>
                <div class="match-details">
                    <div>Compétence : ${detail.matiere || 0}/35</div>
                    <div>Niveau : ${detail.niveau_vs_gravite || 0}/20</div>
                    <div>Disponibilités : ${detail.disponibilites || 0}/25</div>
                    <div>Année : ${detail.meme_niveau || 0}/10</div>
                    <div>Filière : ${detail.meme_filiere || 0}/10</div>
                    <div>Format : ${detail.format_preference || 0}/10</div>
                </div>
                <div class="field-row"><label>ID étudiant</label><span>${match.student_id}</span></div>
                <button onclick="acceptMatch(${match.student_id}, ${match.profile_id}, ${match.matched_subjects?.[0]?.matiere_id || 0})">Accept</button>
                <button onclick="rejectMatch(${match.student_id}, ${match.profile_id}, ${match.matched_subjects?.[0]?.matiere_id || 0})">Reject</button>
            </div>
        `;
    }).join('');
}

async function acceptMatch(studentId, profileId, matiereId) {
    try {
        const payload = { matiere_id: matiereId, score: 0 };
        const result = await apiFetch(`/matches/${studentId}/request`, { method: 'POST', body: payload });
        let msg = 'Requête envoyée: ' + result.message;
        if (result.conversation_id) {
            msg += ` (conversation_id: ${result.conversation_id})`;
            // Affiche la conversation id dans l'UI
            document.getElementById('requestsResult').textContent = JSON.stringify(result, null, 2);
        }
        alert(msg);
    } catch (err) {
        displayError(err);
    }
}

async function rejectMatch(studentId, profileId, matiereId) {
    alert('Pour tester le rejet, utilisez la route /api/matches/{id}/reject depuis les requêtes reçues.');
}

async function handleCreateRequest() {
    const candidateId = Number(document.getElementById('requestCandidateId').value);
    const matiereId = Number(document.getElementById('requestMatiere').value);
    if (!candidateId || !matiereId) {
        displayInfo('Veuillez saisir un candidate ID et un matiere ID.');
        return;
    }
    try {
        const result = await apiFetch(`/matches/${candidateId}/request`, { method: 'POST', body: { matiere_id: matiereId, score: 0 } });
        document.getElementById('requestsResult').textContent = JSON.stringify(result, null, 2);
        if (result.conversation_id) {
            displayInfo(`Conversation créée: ${result.conversation_id}`);
        }
    } catch (err) {
        displayError(err);
    }
}

async function loadRequests(type) {
    try {
        const endpoint = type === 'sent' ? '/matches/sent' : '/matches/received';
        const result = await apiFetch(endpoint);
        document.getElementById('requestsResult').textContent = JSON.stringify(result, null, 2);
    } catch (err) {
        displayError(err);
    }
}

async function loadNotifications() {
    try {
        const result = await apiFetch('/notifications');
        
        if (!result.notifications || result.notifications.length === 0) {
            document.getElementById('notificationsList').innerHTML = '<p style="color: #888;">Aucune notification</p>';
            document.getElementById('notificationCount').innerText = '0 notifications';
            document.getElementById('unreadCount').innerText = '0 non lues';
            return;
        }

        document.getElementById('notificationCount').innerText = `${result.total} notification${result.total > 1 ? 's' : ''}`;
        document.getElementById('unreadCount').innerText = `${result.unread_count} non lue${result.unread_count > 1 ? 's' : ''}`;

        const notificationsList = document.getElementById('notificationsList');
        notificationsList.innerHTML = result.notifications.map(n => `
            <div class="notification-item ${n.is_read ? '' : 'unread'}">
                <div class="notification-content">
                    <h4>${escapeHtml(n.titre)}</h4>
                    <p>${escapeHtml(n.contenu)}</p>
                    <div class="notification-meta">
                        <span class="notification-type">${escapeHtml(n.type)}</span>
                        <span>${new Date(n.created_at).toLocaleString('fr-FR')}</span>
                    </div>
                </div>
                <div class="notification-actions">
                    ${n.is_read ? '<span style="color: #888; font-size: 12px;">✓ Lue</span>' : 
                      `<button class="mark-read" onclick="markNotificationRead(${n.id})">Marquer lue</button>`}
                    <button class="delete" onclick="deleteNotification(${n.id})">Supprimer</button>
                </div>
            </div>
        `).join('');

        displayInfo(`✅ ${result.total} notification(s) chargée(s)`);
    } catch (err) {
        displayError(err);
    }
}

async function markNotificationRead(notifId) {
    try {
        const result = await apiFetch(`/notifications/${notifId}/read`, { method: 'PUT' });
        displayInfo('✓ Notification marquée comme lue');
        loadNotifications(); // Reload
    } catch (err) {
        displayError(err);
    }
}

async function markAllNotificationsRead() {
    try {
        const result = await apiFetch(`/notifications/read-all`, { method: 'PUT' });
        displayInfo(`✅ ${result.count} notification(s) marquée(s) comme lue(s)`);
        loadNotifications(); // Reload
    } catch (err) {
        displayError(err);
    }
}

async function deleteNotification(notifId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette notification ?')) {
        return;
    }
    try {
        const result = await apiFetch(`/notifications/${notifId}`, { method: 'DELETE' });
        displayInfo('✓ Notification supprimée');
        loadNotifications(); // Reload
    } catch (err) {
        displayError(err);
    }
}

async function loadConversations() {
    try {
        const result = await apiFetch('/conversations');
        document.getElementById('conversationsResult').textContent = JSON.stringify(result, null, 2);
    } catch (err) {
        displayError(err);
    }
}

async function openConversation() {
    const conversationId = Number(document.getElementById('conversationId').value);
    if (!conversationId) {
        displayInfo('Veuillez saisir un conversation ID.');
        return;
    }
    try {
        const messages = await apiFetch(`/conversations/${conversationId}/messages`);
        document.getElementById('conversationMessages').textContent = JSON.stringify(messages, null, 2);
    } catch (err) {
        displayError(err);
    }
}

async function handleSendMessage(event) {
    event.preventDefault();
    const conversationId = Number(document.getElementById('conversationId').value);
    const data = Object.fromEntries(new FormData(event.target).entries());
    if (!conversationId || !data.contenu) {
        displayInfo('Conversation ID et message requis.');
        return;
    }
    try {
        const result = await apiFetch(`/conversations/${conversationId}/messages`, { method: 'POST', body: { contenu: data.contenu } });
        document.getElementById('conversationMessages').textContent = JSON.stringify(result, null, 2);
        event.target.reset();
    } catch (err) {
        displayError(err);
    }
}

function displayError(error) {
    latestResponse = { status: 'ERROR', body: error.message || error };
    renderResponse();
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

loadSavedToken();
window.acceptMatch = acceptMatch;
window.rejectMatch = rejectMatch;
window.markNotificationRead = markNotificationRead;
window.deleteNotification = deleteNotification;
window.onload = init;
