# IFRI MentorLink

Plateforme de mentorat académique **peer-to-peer** pour l'Institut de Formation et de Recherche en Informatique (IFRI).  
Les étudiants peuvent publier des offres d'aide ou des demandes de mentorat, et un algorithme de **matching intelligent** les met en relation selon les compétences, disponibilités et filières.

## Stack

| Couche | Technologie |
|--------|-------------|
| Backend | Python 3.11+ / Flask / SQLAlchemy |
| Base de données | PostgreSQL (Render) / SQLite (local) |
| Temps réel | Socket.IO (Flask-SocketIO) |
| Frontend | HTML / JavaScript vanilla / Tailwind CSS (CDN) |
| Auth | JWT (PyJWT) |
| Tests | pytest |
| Déploiement | Render (Web Service + PostgreSQL) |

## Architecture

```
Frontend/                          Backend/
├── index.html        ← accueil    ├── run.py
├── pages/            ← app        ├── app/
│   ├── signin.html                │   ├── __init__.py   ← création Flask, CORS, Socket.IO
│   ├── signup.html                │   ├── routes/       ← API REST
│   ├── dashboard.html             │   ├── models/       ← SQLAlchemy models
│   ├── matching.html              │   ├── services/     ← matching, feedback
│   ├── requests.html              │   ├── sockets/      ← Socket.IO events
│   ├── messages.html              │   └── middleware/   ← auth guard JWT
│   ├── settings.html              └── requirements.txt
│   ├── onboarding.html
│   ├── notifications.html
│   └── debug.html
├── js/
│   ├── bundle.js     ← API client + utilitaires + matières + badge notifs
│   └── notifications.js   ← page notifications uniquement
└── css/
    └── styles.css
```

### Fonctionnement

1. L'utilisateur s'inscrit / se connecte → reçoit un **JWT** stocké dans `localStorage`
2. Le dashboard affiche ses stats (offres, demandes, matchings, note moyenne)
3. L'utilisateur peut **publier** une offre (proposer son aide) ou une demande (chercher de l'aide), avec matières, créneaux et niveau d'urgence
4. L'algorithme de **matching** suggère des profils compatibles selon :
   - Compétences / lacunes des matières
   - Disponibilités (créneaux horaires)
   - Filière et niveau
   - Note moyenne (feedback des mentors précédents)
5. Le matching s'affiche dans une interface "swipe" (accepter / refuser)
6. Une fois matchés, les utilisateurs peuvent **discuter en temps réel** via Socket.IO
7. Les notifications sont mises à jour par **polling** toutes les 30s

### Requêtes HTTP par page

Chaque page charge 2-3 ressources externes + 1 bundle :

| Ressource | Type |
|-----------|------|
| `https://cdn.tailwindcss.com` | CSS utility (CDN) |
| `https://cdn.jsdelivr.net/npm/@tabler/icons-*` | Icônes (CDN) |
| `../js/bundle.js` (ou `js/bundle.js` sur l'accueil) | JS applicatif |
| `../css/styles.css` | Styles personnalisés |

## 🚀 Lancer l'UI en local

### 1. Backend

```bash
# Depuis la racine du projet
cd backend
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
python run.py
```

Le backend écoute sur `http://127.0.0.1:5000`.

> 💡 Par défaut le frontend se connecte à `http://127.0.0.1:5000/api`.  
> Pour utiliser une autre URL, définissez `window.API_BASE_URL` dans la console avant de naviguer, ou modifiez `js/bundle.js`.

### 2. Frontend

**Option A — Live Server (recommandé)**

```bash
cd Frontend
npx live-server --port=5500
```

**Option B — Serveur HTTP simple**

```bash
cd Frontend
python -m http.server 5500
```

Ouvrir `http://127.0.0.1:5500/` dans un navigateur.

### 3. Pages principales

| Page | URL | Rôle |
|------|-----|------|
| Accueil | `/index.html` | Landing page |
| Inscription | `/pages/signup.html` | Création de compte |
| Connexion | `/pages/signin.html` | Connexion JWT |
| Dashboard | `/pages/dashboard.html` | Vue d'ensemble |
| Publications | `/pages/requests.html` | CRUD offres/demandes |
| Matching | `/pages/matching.html` | Swipe & matcher |
| Messages | `/pages/messages.html` | Chat temps réel |
| Paramètres | `/pages/settings.html` | Profil, compétences, dispo |
| Notifications | `/pages/notifications.html` | Historique des notifs |
| Onboarding | `/pages/onboarding.html` | Première connexion |
| Debug | `/pages/debug.html` | Tests API/WS |

## ☁️ Déploiement (Render)

### Backend (Web Service)

1. Créer un Web Service sur [Render](https://render.com)
2. Branch : `develop`
3. Root directory : `backend`
4. Build command : `pip install -r requirements.txt`
5. Start command : `gunicorn -k eventlet -w 1 run:app`
6. Ajouter une base PostgreSQL (créer une DB via Render Dashboard)
7. Variables d'environnement :
   - `DATABASE_URL` → URL PostgreSQL interne Render
   - `SECRET_KEY` → clé secrète JWT
   - `FLASK_ENV=production`

### Frontend

Le frontend est **statique** (pas de build step). Vous pouvez :

- Le servir via Render comme **Static Site** pointant vers `Frontend/`
- Ou l'héberger sur **GitHub Pages**, **Netlify** ou **Vercel**

> ⚠️ En production, le frontend se connecte automatiquement à `https://ifri-mentorlink.onrender.com/api`.  
> Pour changer l'URL backend, définissez `window.API_BASE_URL` avant tout appel API.

## 🧪 Tests

```bash
cd backend
pytest -q
```

Tests unitaires et d'intégration pour : auth, profils, offres, demandes, matching, messages, notifications, sockets.

## 👥 Équipe

| Membre | Rôle |
|--------|------|
| **GOUTONDE Bidossessi Conceptia Sharone** | Développeur Frontend |
| **HOUEGBELO Uriel Verghis Olsen** | Tech Lead / Backend |
| **LOTSU Emmanuel Richard Kwasi** | Développeur Backend |
| **HOUNNOUKON Agossou Prince** | Développeur Backend / Déploiement |
| **YESSOUFOU Scham's-Deen** | Développeur Fullstack |
| **TOCHENALI Paola Eloane** | Développeur Frontend |

---

*Projet IFRI — PIL1_2526*
