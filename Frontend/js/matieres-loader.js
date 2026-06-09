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
  const authPages = /signin\.html|signup\.html|reset-password\.html/.test(window.location.pathname);
  if (authPages) return;
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
