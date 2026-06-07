/**
 * MentorLink — Grille de disponibilités
 * Gère la sélection des créneaux, les boutons rapides,
 * le compteur et la récupération des données pour l'API.
 */

// =============================================
// CONFIGURATION
// =============================================

const HORAIRES = [
    '8h-9h', '9h-10h', '10h-11h', '11h-12h',
    '12h-13h', '13h-14h', '14h-15h', '15h-16h',
    '16h-17h', '17h-18h', '18h-19h', '19h-20h', '20h-21h'
];

const JOURS = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche'];

// Matinées = 8h à 12h (indices 0 à 3)
const INDICES_MATINEES = [0, 1, 2, 3];
// Après-midis = 13h à 17h (indices 5 à 8)
const INDICES_APRES_MIDIS = [5, 6, 7, 8];

// =============================================
// ÉTAT
// =============================================

// selectedSlots[horaire][jour] = true/false
const selectedSlots = {};

HORAIRES.forEach(h => {
    selectedSlots[h] = {};
    JOURS.forEach(j => {
        selectedSlots[h][j] = false;
    });
});

// =============================================
// GÉNÉRATION DE LA GRILLE
// =============================================

function buildGrid() {
    const tbody = document.getElementById('gridBody');
    tbody.innerHTML = '';

    HORAIRES.forEach((horaire, rowIndex) => {
        const tr = document.createElement('tr');

        // Colonne horaire
        const tdLabel = document.createElement('td');
        tdLabel.className = 'horaire-label';
        tdLabel.textContent = horaire;
        tr.appendChild(tdLabel);

        // Colonnes jours
        JOURS.forEach(jour => {
            const td = document.createElement('td');
            td.className = 'grid-cell';

            const btn = document.createElement('button');
            btn.className = 'slot';
            btn.dataset.horaire = horaire;
            btn.dataset.jour = jour;
            btn.setAttribute('aria-label', `${horaire} - ${jour}`);
            btn.setAttribute('type', 'button');

            btn.addEventListener('click', () => toggleSlot(horaire, jour, btn));

            td.appendChild(btn);
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });
}

// =============================================
// TOGGLE D'UN CRÉNEAU
// =============================================

function toggleSlot(horaire, jour, btn) {
    selectedSlots[horaire][jour] = !selectedSlots[horaire][jour];
    btn.classList.toggle('selected', selectedSlots[horaire][jour]);
    updateCompteur();
}

// =============================================
// SÉLECTION RAPIDE
// =============================================

function setRangeSlots(indices, valeur) {
    const tbody = document.getElementById('gridBody');
    const rows = tbody.querySelectorAll('tr');

    indices.forEach(idx => {
        const horaire = HORAIRES[idx];
        const row = rows[idx];
        if (!row) return;

        JOURS.forEach((jour, colIdx) => {
            selectedSlots[horaire][jour] = valeur;
            // +1 car 1ère colonne = label
            const btn = row.querySelectorAll('.slot')[colIdx];
            if (btn) btn.classList.toggle('selected', valeur);
        });
    });

    updateCompteur();
}

function resetAll() {
    HORAIRES.forEach(h => {
        JOURS.forEach(j => {
            selectedSlots[h][j] = false;
        });
    });
    document.querySelectorAll('.slot').forEach(btn => btn.classList.remove('selected'));
    updateCompteur();
}

// =============================================
// COMPTEUR
// =============================================

function updateCompteur() {
    let count = 0;
    HORAIRES.forEach(h => {
        JOURS.forEach(j => {
            if (selectedSlots[h][j]) count++;
        });
    });
    document.getElementById('compteur').textContent = count;
}

// =============================================
// RÉCUPÉRER LES DONNÉES POUR L'API
// =============================================

/**
 * Retourne un tableau des créneaux sélectionnés,
 * prêt à envoyer à API.profile.addDisponibilite()
 * Format : [{ jour: 'lundi', horaire: '8h-9h' }, ...]
 */
function getSelectedDisponibilites() {
    const result = [];
    HORAIRES.forEach(h => {
        JOURS.forEach(j => {
            if (selectedSlots[h][j]) {
                result.push({ jour: j, horaire: h });
            }
        });
    });
    return result;
}

// =============================================
// ÉVÉNEMENTS
// =============================================

document.getElementById('btnMatinees').addEventListener('click', () => {
    setRangeSlots(INDICES_MATINEES, true);
});

document.getElementById('btnApresMidis').addEventListener('click', () => {
    setRangeSlots(INDICES_APRES_MIDIS, true);
});

document.getElementById('btnReset').addEventListener('click', resetAll);

document.getElementById('btnPrecedent').addEventListener('click', () => {
    window.history.back();
});

document.getElementById('btnTerminer').addEventListener('click', async () => {
    const disponibilites = getSelectedDisponibilites();

    if (disponibilites.length === 0) {
        alert('Veuillez sélectionner au moins un créneau.');
        return;
    }

    const btn = document.getElementById('btnTerminer');
    btn.disabled = true;
    btn.textContent = 'Enregistrement...';

    try {
        // Envoi à l'API (nécessite api.js chargé)
        for (const dispo of disponibilites) {
            await API.profile.addDisponibilite(dispo);
        }
        window.location.href = 'dashboard.html';

    } catch (err) {
        alert('Erreur : ' + err.message);
        btn.disabled = false;
        btn.innerHTML = 'Terminer ›';
    }
});

// =============================================
// INIT
// =============================================

buildGrid();