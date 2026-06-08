// Load matieres from API and cache locally with filiere filtering
let _matieresCache = null;

const DEFAULT_MATIERES = [
  { id: 1, nom: 'Algorithmique', filiere: 'GL' },
  { id: 2, nom: 'Structures de données', filiere: 'GL' },
  { id: 3, nom: 'Base de données SQL', filiere: 'GL' },
  { id: 4, nom: 'Programmation Orientée Objet', filiere: 'GL' },
  { id: 5, nom: 'Génie logiciel', filiere: 'GL' },
  { id: 6, nom: 'Architecture des ordinateurs', filiere: 'GL' },
  { id: 7, nom: 'Systèmes d’exploitation', filiere: 'GL' },
  { id: 8, nom: 'Web Development', filiere: 'GL' },
  { id: 9, nom: 'Réseaux informatiques', filiere: 'RSI' },
  { id: 10, nom: 'Sécurité des réseaux', filiere: 'RSI' },
  { id: 11, nom: 'Télécommunications', filiere: 'RSI' },
  { id: 12, nom: 'Administration système', filiere: 'RSI' },
  { id: 13, nom: 'Cyberdéfense', filiere: 'Sécurité' },
  { id: 14, nom: 'Cryptographie', filiere: 'Sécurité' },
  { id: 15, nom: 'Sécurité des applications', filiere: 'Sécurité' },
  { id: 16, nom: 'Audit de sécurité', filiere: 'Sécurité' },
  { id: 17, nom: 'Intelligence artificielle', filiere: 'GL' },
  { id: 18, nom: 'Machine Learning', filiere: 'GL' },
  { id: 19, nom: 'Big Data', filiere: 'RSI' },
  { id: 20, nom: 'Cloud Computing', filiere: 'GL' },
  { id: 21, nom: 'Développement mobile', filiere: 'GL' },
  { id: 22, nom: 'Gestion de projet informatique', filiere: 'GL' },
  { id: 23, nom: 'Langage SQL avancé', filiere: 'RSI' },
  { id: 24, nom: 'Administration de bases de données', filiere: 'RSI' },
  { id: 25, nom: 'Sécurité web', filiere: 'Sécurité' },
  { id: 26, nom: 'Ethical Hacking', filiere: 'Sécurité' }
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
window.initMatieresLoader = initMatieresLoader;
