// Load matieres from API and cache locally with filiere filtering
let _matieresCache = null;

async function loadMatieresFromAPI() {
  if (_matieresCache) return _matieresCache;
  try {
    const data = await API.matieres.getAll();
    const matieres = data.matieres || data;
    if (Array.isArray(matieres)) {
      _matieresCache = matieres;
      localStorage.setItem('matieres_cache', JSON.stringify(matieres));
      return matieres;
    }
  } catch (e) {
    console.warn('Failed to load matieres from API:', e);
  }
  // Fallback to cache
  const cached = localStorage.getItem('matieres_cache');
  return cached ? JSON.parse(cached) : [];
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
  await loadMatieresFromAPI();
}

// Initialize on DOM ready
if (typeof window !== 'undefined') {
  document.addEventListener('DOMContentLoaded', initMatieresLoader);
}

window.loadMatieresFromAPI = loadMatieresFromAPI;
window.getMatiersByFiliere = getMatiersByFiliere;
window.initMatieresLoader = initMatieresLoader;
