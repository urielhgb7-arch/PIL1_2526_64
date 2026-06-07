const API_BASE_URL = "http://localhost:5000/api";
const token = localStorage.getItem('token');

let localUserData = null;
let currentProfiles = [];
let currentIndex = 0;
let isEditMode = false;
let startX = 0;

let activeChatId = null; // ID de l'étudiant avec qui on discute actuellement

if (!token) { window.location.href = "login.html"; }

document.addEventListener('DOMContentLoaded', () => {
    loadUserProfile();
    loadSwipeRecommendations();
    loadReceivedRequests(); // Chargement de l'onglet demandes
    loadChatDiscussions();  // Chargement des conversations
});

// ==========================================
// A. NAVIGATION ENTRE LES ENGINS (TABS)
// ==========================================
function switchTab(tabName) {
    ['dashboardSection', 'swipeSection', 'demandesSection', 'messagesSection'].forEach(s => document.getElementById(s).classList.add('hidden'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('text-blue-400', 'bg-slate-900/50').classList.add('text-slate-400'));
    
    document.getElementById(`${tabName}Section`).classList.remove('hidden');
    document.getElementById(`nav-${tabName}`).classList.add('text-blue-400', 'bg-slate-900/50');
    
    if (tabName === 'demandes') loadReceivedRequests();
    if (tabName === 'messages') loadChatDiscussions();
}

// ==========================================
// B. GESTION DES DEMANDES (INTERESSÉS)
// ==========================================
async function loadReceivedRequests() {
    const container = document.getElementById('demandesContainer');
    try {
        const response = await fetch(`${API_BASE_URL}/match/requests`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const requests = await response.json();

        if (!response.ok || requests.length === 0) {
            container.innerHTML = `<p class="text-sm text-slate-500 italic col-span-2">Aucune demande en attente pour le moment.</p>`;
            return;
        }

        container.innerHTML = requests.map(req => {
            const sender = req.senderId; 
            const photo = sender.photoUrl || `https://ui-avatars.com/api/?name=${sender.firstname}+${sender.lastname}`;
            return `
                <div id="req-${req._id}" class="bg-slate-800 border border-slate-700/60 rounded-2xl p-4 flex items-center justify-between gap-4">
                    <div class="flex items-center gap-3">
                        <img src="${photo}" class="w-12 h-12 rounded-full object-cover border border-slate-700">
                        <div>
                            <h4 class="text-sm font-bold text-white">${sender.firstname} ${sender.lastname.toUpperCase()}</h4>
                            <p class="text-xs text-blue-400 font-medium">${sender.filiere} — ${sender.niveau}</p>
                        </div>
                    </div>
                    <div class="flex gap-2">
                        <button onclick="respondRequest('${req._id}', 'decline')" class="bg-red-500/20 border border-red-500/40 text-red-400 text-xs px-3 py-2 rounded-xl hover:bg-red-600 hover:text-white transition">✖</button>
                        <button onclick="respondRequest('${req._id}', 'accept')" class="bg-blue-500/20 border border-blue-500/40 text-blue-400 text-xs px-3 py-2 rounded-xl hover:bg-blue-600 hover:text-white transition">✔ Accepter</button>
                    </div>
                </div>
            `;
        }).join('');
    } catch (err) {
        console.error(err);
    }
}

async function respondRequest(requestId, action) {
    try {
        const response = await fetch(`${API_BASE_URL}/match/respond`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ requestId, action })
        });

        if (response.ok) {
            document.getElementById(`req-${requestId}`).remove();
            
            if (action === 'accept') {
                triggerNotification("Demande acceptée ! Conversation ouverte dans l'onglet Messages.", "success");
                // Recharge des listes
                loadChatDiscussions();
            } else {
                triggerNotification("Demande déclinée.", "success");
            }
        }
    } catch (err) {
        console.error(err);
    }
}

// ==========================================
// C. MESSAGERIE TYPE TELEGRAM
// ==========================================
async function loadChatDiscussions() {
    const listWrapper = document.getElementById('chatListContainer');
    try {
        const response = await fetch(`${API_BASE_URL}/chats`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const discussions = await response.json();

        if (!response.ok || discussions.length === 0) {
            listWrapper.innerHTML = `<p class="text-xs text-slate-500 text-center pt-8">Aucun échange actif.</p>`;
            document.getElementById('noChatSelected').classList.remove('hidden');
            document.getElementById('chatWindow').classList.add('hidden');
            return;
        }

        if(!activeChatId) {
            document.getElementById('noChatSelected').classList.remove('hidden');
        }

        listWrapper.innerHTML = discussions.map(chat => {
            const target = chat.participant; 
            const img = target.photoUrl || `https://ui-avatars.com/api/?name=${target.firstname}+${target.lastname}`;
            const activeClass = activeChatId === target._id ? 'bg-slate-800/80 border-l-4 border-blue-500' : 'hover:bg-slate-800/30';
            
            return `
                <div onclick="openDiscussion('${target._id}', '${target.firstname} ${target.lastname}', '${img}')" class="p-4 flex items-center gap-3 cursor-pointer transition ${activeClass}">
                    <img src="${img}" class="w-11 h-11 rounded-full object-cover">
                    <div class="flex-1 min-w-0">
                        <div class="flex justify-between items-baseline">
                            <h4 class="text-sm font-bold text-slate-200 truncate">${target.firstname} ${target.lastname}</h4>
                            <span class="text-[10px] text-slate-500">12:45</span>
                        </div>
                        <p class="text-xs text-slate-400 truncate mt-0.5">${chat.lastMessage || 'Aucun message'}</p>
                    </div>
                </div>
            `;
        }).join('');
    } catch (err) {
        console.error(err);
    }
}

async function openDiscussion(targetUserId, fullname, photoUrl) {
    activeChatId = targetUserId;
    document.getElementById('noChatSelected').classList.add('hidden');
    const win = document.getElementById('chatWindow');
    win.classList.remove('hidden');

    document.getElementById('chatWinPhoto').src = photoUrl;
    document.getElementById('chatWinName').textContent = fullname;

    loadMessages(targetUserId);
}

async function loadMessages(targetUserId) {
    const msgBox = document.getElementById('chatMessagesBox');
    try {
        const response = await fetch(`${API_BASE_URL}/chats/${targetUserId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const messages = await response.json();

        msgBox.innerHTML = messages.map(msg => {
            const isMe = msg.senderId === localUserData._id;
            
            // Si c'est un message système automatisé lors du match
            if (msg.isSystem) {
                return `
                    <div class="self-center bg-blue-950/40 border border-blue-900/40 text-blue-300 text-[11px] px-4 py-1.5 rounded-full my-2 font-medium max-w-xs text-center">
                        🤝 ${msg.text}
                    </div>
                `;
            }

            // Structure des bulles de message à la Telegram
            const bubbleStyle = isMe 
                ? 'bg-blue-600 text-white self-end rounded-2xl rounded-tr-none' 
                : 'bg-slate-800 text-slate-200 self-start rounded-2xl rounded-tl-none';

            return `
                <div class="max-w-[75%] px-4 py-2.5 shadow-md text-sm ${bubbleStyle}">
                    <p class="leading-relaxed select-text">${msg.text}</p>
                    <span class="block text-[9px] text-right mt-1 opacity-60">12:46</span>
                </div>
            `;
        }).join('');
        
        msgBox.scrollTop = msgBox.scrollHeight; // Défilement vers le bas automatique
    } catch (err) {
        console.error(err);
    }
}

// Envoi d'un message depuis le formulaire Telegram
document.getElementById('chatInputForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('chatMessageInput');
    const text = input.value.trim();
    if (!text || !activeChatId) return;

    try {
        const response = await fetch(`${API_BASE_URL}/chats/send`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ receiverId: activeChatId, text })
        });

        if (response.ok) {
            input.value = "";
            loadMessages(activeChatId); // Rafraîchir l'historique
        }
    } catch (err) {
        console.error(err);
    }
});

// ==========================================
// D. CODE INVARIANT DE PROFIL & SWIPE
// ==========================================
async function loadUserProfile() {
    try {
        const response = await fetch(`${API_BASE_URL}/users/profile`, { headers: { 'Authorization': `Bearer ${token}` } });
        const data = await response.json();
        if (response.ok) {
            localUserData = data;
            const fallback = `https://ui-avatars.com/api/?name=${data.firstname}+${data.lastname}`;
            document.getElementById('viewPhoto').src = data.photoUrl || fallback;
            document.getElementById('viewFullName').textContent = `${data.firstname} ${data.lastname.toUpperCase()}`;
            document.getElementById('viewRole').textContent = data.role === 'mentor' ? '🎙️ Mentor' : '🎓 Mentoré';
            document.getElementById('viewContact').textContent = `✉️ ${data.email} | 📞 ${data.phone}`;
            document.getElementById('viewFiliere').textContent = data.filiere || 'Non renseignée';
            document.getElementById('viewNiveau').textContent = data.niveau || 'Non renseigné';
            const wrapper = document.getElementById('viewSkillsContainer');
            wrapper.innerHTML = "";
            populateBadges(data.role === 'mentor' ? data.competences : data.lacunes, wrapper);
        }
    } catch(e){}
}

async function loadSwipeRecommendations() {
    try {
        const response = await fetch(`${API_BASE_URL}/match/recommendations`, { headers: { 'Authorization': `Bearer ${token}` } });
        const dataset = await response.json();
        if (response.ok && dataset.length > 0) { currentProfiles = dataset; currentIndex = 0; renderCard(); }
    } catch(e){}
}

function renderCard() {
    const box = document.getElementById('cardContainer');
    if (currentIndex >= currentProfiles.length) {
        box.innerHTML = `<div class="text-center pt-20 text-slate-500"><p>🎉 Plus aucun profil disponible.</p></div>`;
        return;
    }
    const currentProfile = currentProfiles[currentIndex];
    const imageSource = currentProfile.photoUrl || `https://ui-avatars.com/api/?name=${currentProfile.firstname}+${currentProfile.lastname}`;

    box.innerHTML = `
        <div id="activeCard" class="swipe-card absolute inset-0 bg-slate-800 border border-slate-700 rounded-2xl p-5 flex flex-col justify-between shadow-2xl overflow-hidden">
            <div class="flex justify-between items-center border-b border-slate-700/50 pb-3">
                <span class="text-xs font-bold bg-blue-500/10 border border-blue-500/30 text-blue-400 px-2.5 py-1 rounded-lg uppercase">🎓 ${currentProfile.niveau}</span>
                <div class="flex items-center gap-1.5 bg-emerald-500/10 border border-emerald-500/30 px-3 py-1 rounded-full"><span class="text-sm font-black text-emerald-400">${currentProfile.matchPercentage}% Match</span></div>
            </div>
            <div class="flex flex-col items-center my-auto space-y-4">
                <div class="w-32 h-32 rounded-full overflow-hidden border-4 border-slate-900 shadow-xl bg-slate-900"><img src="${imageSource}" class="w-full h-full object-cover pointer-events-none"></div>
                <div class="text-center">
                    <h3 class="text-2xl font-extrabold text-white">${currentProfile.firstname} <span class="uppercase text-slate-300">${currentProfile.lastname}</span></h3>
                    <p class="text-sm text-slate-400 mt-1">Filière : <span class="text-slate-200 font-semibold">${currentProfile.filiere}</span></p>
                </div>
            </div>
            <div class="md:hidden flex flex-col items-center pt-2">
                <button onclick="toggleMobileActions(event)" class="text-slate-400 text-lg p-1 outline-none">•••</button>
                <div id="mobileMenu" class="hidden gap-5 mt-2">
                    <button onclick="handleAction('decline')" class="bg-red-500/20 border border-red-500 text-red-400 p-3 rounded-full">✕</button>
                    <button onclick="handleAction('accept')" class="bg-blue-500/20 border border-blue-500 text-blue-400 p-3 rounded-full">✓</button>
                </div>
            </div>
        </div>
    `;
    bindDragGestures();
}

function toggleMobileActions(e) { e.stopPropagation(); document.getElementById('mobileMenu').classList.toggle('hidden'); }

async function handleAction(actionType) {
    const targetCard = document.getElementById('activeCard');
    if (!targetCard) return;
    const targetedUser = currentProfiles[currentIndex];
    targetCard.classList.add(actionType === 'accept' ? 'swiped-right' : 'swiped-left');

    try {
        await fetch(`${API_BASE_URL}/match/action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ targetUserId: targetedUser._id, action: actionType })
        });
    } catch (err) {}

    setTimeout(() => { currentIndex++; renderCard(); }, 300);
}

function bindDragGestures() {
    const target = document.getElementById('activeCard');
    if (!target) return;
    target.addEventListener('mousedown', initiateDrag);
    target.addEventListener('touchstart', initiateDrag);
    function initiateDrag(e) {
        startX = e.type === 'touchstart' ? e.touches[0].clientX : e.clientX;
        document.addEventListener('mousemove', processingDrag);
        document.addEventListener('touchmove', processingDrag);
        document.addEventListener('mouseup', terminateDrag);
        document.addEventListener('touchend', terminateDrag);
    }
    function processingDrag(e) {
        const clientX = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX;
        target.style.transform = `translateX(${clientX - startX}px) rotate(${(clientX - startX) / 15}deg)`;
    }
    function terminateDrag(e) {
        const endX = e.type === 'touchend' ? e.changedTouches[0].clientX : e.clientX;
        if (endX - startX > 120) handleAction('accept');
        else if (endX - startX < -120) handleAction('decline');
        else target.style.transform = 'none';
        document.removeEventListener('mousemove', processingDrag);
        document.removeEventListener('touchmove', processingDrag);
        document.removeEventListener('mouseup', terminateDrag);
        document.removeEventListener('touchend', terminateDrag);
    }
}

function toggleEditMode() {
    isEditMode = !isEditMode;
    const view = document.getElementById('profileViewMode');
    const form = document.getElementById('profileEditForm');
    const btn = document.getElementById('editToggleBtn');
    if (isEditMode) { view.classList.add('hidden'); form.classList.remove('hidden'); btn.textContent = "👁️ Profil"; }
    else { view.classList.remove('hidden'); form.classList.add('hidden'); btn.textContent = "✏️ Modifier"; loadUserProfile(); }
}

async function previewAndUploadPhoto() {
    const file = document.getElementById('photoInput').files[0];
    if (!file) return;
    const payload = new FormData(); payload.append('photo', file);
    try {
        const res = await fetch(`${API_BASE_URL}/users/upload-photo`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` }, body: payload });
        if (res.ok) { const d = await res.json(); if(localUserData) localUserData.photoUrl = d.photoUrl; triggerNotification("Photo mise à jour !", "success"); }
    } catch(e){}
}

function triggerNotification(msg, status) {
    const alertBox = document.getElementById('dbAlertBanner');
    alertBox.textContent = msg; alertBox.classList.remove('hidden', 'bg-red-950/50', 'text-red-400', 'bg-emerald-950/50', 'text-emerald-400');
    alertBox.classList.add(status === 'error' ? 'bg-red-950/50' : 'bg-emerald-950/50');
    setTimeout(() => alertBox.classList.add('hidden'), 4000);
}