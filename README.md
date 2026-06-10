# IFRI MentorLink

Plateforme de mentorat académique basée sur un matching intelligent.

## Stack

- **Backend** : Flask, PostgreSQL, SQLAlchemy, Socket.IO, JWT
- **Frontend** : HTML/CSS/JS, Tailwind CSS (CDN), Tabler Icons
- **Déploiement** : Render (backend), Vercel (frontend)

## Équipe & Rôles

| # | Membre | Groupe | Rôle |
|---|--------|--------|------|
| 1 | GOUTONDE Bidossessi Conceptia Sharone | F2 | Développeur Frontend |
| 2 | HOUEGBELO Uriel Verghis Olsen | — | Tech Lead / Fullstack |
| 3 | LOTSU Emmanuel Richard Kwasi | B3 | Développeur Backend |
| 4 | HOUNNOUKON Agossou Prince | F4 | Rapporteur |
| 5 | YESSOUFOU Scham's-Deen | F3 | Développeur Frontend |
| 6 | TOCHENALI Paola Eloane | B2 | Développeur Backend |
| 7 | MOUTOUAMA Liwêto Eben-Ezer | F1 | Développeur Frontend |

## Structure du projet

```
PIL1_2526_64/
  backend/
    app/
      __init__.py              # Factory create_app(), blueprints, CORS
      config/                  # DevelopmentConfig / ProductionConfig
      database/                # SQLAlchemy init + connexion PostgreSQL
      middleware/               # auth_guard.py (décorateur @token_required)
      models/                  # User, Profile, Offer, Demand, Matching…
      routes/                  # auth, profile, matching, messages, notifications, offers
      services/                # email_service, matching algorithm
      sockets/                 # Socket.IO events (chat)
      validators.py            # Regex, enum validators
    run.py
    requirements.txt
  Frontend/
    index.html                 # Landing page
    pages/
      signin.html              # Connexion
      signup.html              # Inscription
      dashboard.html           # Tableau de bord
      requests.html            # Offres & demandes
      matching.html            # Matching (swipe)
      messages.html            # Chat temps réel
      settings.html            # Paramètres profil
      notifications.html       # Centre notifications
      onboarding.html          # Questionnaire post-inscription
      reset-password.html      # Réinitialisation mot de passe
      debug.html               # Tests API/WebSocket
    js/
      bundle.js                # API client + utils globaux (concatené)
      api.js                   # Source : fetchAPI + namespace API.*
      script.js                # Source : auth, logout, helpers
      matieres-loader.js       # Source : chargement matières
      notifications-badge.js   # Source : badge notifications
    css/
      styles.css               # Design sombre personnalisé
    assets/                    # Images, icônes
  database/
    schema.sql                 # DDL complet (PostgreSQL)
  docs/
    UML/                       # Diagrammes de classes
  scripts/                     # Utilitaires
```

---

## API REST — Documentation

Base URL : `/api` (dev : `http://127.0.0.1:5000/api` — prod : `https://ifri-mentorlink.onrender.com/api`)

Authentification : header `Authorization: Bearer <JWT>` — Token obtenu via `POST /api/auth/login`.

### Authentification (`auth_bp`)

| Méthode | Route | Description | Body |
|---------|-------|-------------|------|
| POST | `/auth/register` | Création de compte | `email`, `password`, `nom`, `prenom`, `telephone` (01[4569]XXXXXXX), `accepte_aide` |
| POST | `/auth/login` | Connexion JWT | `email`, `password` |
| POST | `/auth/forgot-password` | Demande de réinit | `email` |
| POST | `/auth/reset-password` | Réinit mot de passe | `token`, `new_password` |
| PUT | `/auth/change-password` | Changement mot de passe | `old_password`, `new_password` |
| DELETE | `/auth/delete-account` | Suppression compte | — |

### Profil (`profile_bp`)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/profile/me` | Récupérer mon profil (compétences, lacunes, dispo, avatar) |
| PUT | `/profile/me` | Mettre à jour mon profil (nom, prénom, téléphone, avatar_url…) |
| POST | `/profile/competences` | Ajouter une compétence (`matiere_id`, `niveau`, `is_available_to_help`) |
| DELETE | `/profile/competences` | Supprimer une compétence (`matiere_id`) |
| POST | `/profile/lacunes` | Ajouter une lacune (`matiere_id`, `priorite`) |
| DELETE | `/profile/lacunes` | Supprimer une lacune (`matiere_id`) |
| PUT | `/profile/competences/{id}/activate` | Réactiver une compétence |
| PUT | `/profile/competences/{id}/deactivate` | Désactiver une compétence |
| POST | `/profile/disponibilites` | Ajouter une disponibilité (`jour`, `creneau`) |
| DELETE | `/profile/disponibilites` | Supprimer une disponibilité (`jour`, `creneau`) |
| GET | `/matieres` | Liste des matières (filière + niveau) |

### Offres & Demandes (`offers_bp`)

| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/offers` | Créer une offre |
| GET | `/offers` | Liste toutes les offres (avec publicateur + avatar) |
| GET | `/offers/mine` | Mes offres |
| DELETE | `/offers/{id}` | Supprimer une offre |
| POST | `/offers/{id}/respond` | Postuler à une offre |
| POST | `/demands` | Créer une demande |
| GET | `/demands` | Liste toutes les demandes |
| GET | `/demands/mine` | Mes demandes |
| DELETE | `/demands/{id}` | Supprimer une demande |
| POST | `/demands/{id}/offer-help` | Proposer son aide |

### Matching (`matching_bp`)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/matches/suggestions` | Suggestions de matching (filtres : `matiere_id`, `filiere`, `niveau`) |
| POST | `/matches/{student_id}/request` | Envoyer une demande de match |
| POST | `/matches/{matching_id}/accept` | Accepter un match |
| POST | `/matches/{matching_id}/reject` | Refuser un match |
| GET | `/matches/received` | Demandes reçues |
| GET | `/matches/sent` | Demandes envoyées |

### Messagerie (`messages_bp`)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/conversations` | Liste des conversations |
| POST | `/conversations` | Créer une conversation (`user_id`) |
| GET | `/conversations/{id}/messages` | Historique des messages |
| POST | `/conversations/{id}/messages` | Envoyer un message (`contenu`) |

### Notifications (`notifications_bp`)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/notifications` | Liste des notifications |
| PUT | `/notifications/{id}/read` | Marquer comme lue |
| PUT | `/notifications/read-all` | Tout marquer comme lu |
| DELETE | `/notifications/{id}` | Supprimer une notification |

### Santé

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/health` | Health-check du serveur |

---

## Client API Frontend (`Frontend/js/api.js`)

Toutes les routes ci-dessus sont exposées via l'objet global `window.API` :

```js
// Auth
API.auth.register({ email, password, nom, prenom, telephone })
API.auth.login({ email, password })

// Profil
API.profile.getMe()
API.profile.updateMe({ nom, prenom, telephone, avatar_url, filiere, niveau })
API.profile.addCompetence({ matiere_id, niveau, is_available_to_help })
API.profile.removeCompetence({ matiere_id })
API.profile.addLacune({ matiere_id, priorite })
API.profile.removeLacune({ matiere_id })
API.profile.addDisponibilite({ jour, creneau })
API.profile.removeDisponibilite({ jour, creneau })

// Offres & Demandes
API.offers.getAll()
API.offers.getMine()
API.offers.create({ matiere_id, description, format_preference, disponibilites })
API.offers.delete(id)
API.offers.respond(id)
API.demands.getAll()
API.demands.getMine()
API.demands.create({ matiere_id, description, format, jours, creneau, urgence })
API.demands.delete(id)
API.demands.offerHelp(id)

// Matching
API.matching.getSuggestions({ matiere_id, filiere, niveau })
API.matching.requestMatch(studentId, { matiere_id, score })
API.matching.accept(matchId)
API.matching.reject(matchId)
API.matching.getReceived()
API.matching.getSent()

// Messages
API.messages.getConversations()
API.messages.create(userId)
API.messages.getHistory(convId)
API.messages.send(convId, text)

// Notifications
API.notifications.getAll(unreadOnly)
API.notifications.markRead(id)
API.notifications.markAllRead()
API.notifications.delete(id)

// Matières
API.matieres.getAll()
```

Le token JWT est automatiquement attaché à chaque requête via `localStorage.getItem('mentorlink_token')`.  
Les erreurs 401 redirigent vers la page de connexion (sauf sur les pages publiques).

---

## Algorithme de Matching

Fichier : `backend/app/services/matching.py`

Score sur **100 points**, calculé pour chaque candidat :

| Critère | Max | Règle |
|---------|-----|-------|
| **Matière** | 35 | Candidat compétent dans la matière de la demande → 35 pts. Autres matières seulement → 10 pts |
| **Niveau vs urgence** | 20 | Rapport entre le niveau de compétence (1–4) et la priorité de la lacune (1–4) |
| **Disponibilités** | 25 | Fraction des créneaux de la demande couverts par le candidat. 0 si aucun |
| **Même année** | 10 | Si `niveau` identique |
| **Même filière** | 10 | Si `filiere` identique |
| **Même format** | 10 | Si `format_preference` identique |
| **Pénalité rejet** | -5 | Si l'utilisateur a déjà rejeté ce candidat |

```
score = min(100, matiere + niveau + dispos + meme_niveau + meme_filiere + format + penalite)
```

### Variantes

- **Général** — `calculate_matches_general()` : parcourt toutes les lacunes de l'utilisateur et trouve les candidats compétents sur au moins une matière recherchée. Score matière = 35 × (matières matchées / total lacunes).
- **Par demande** — `calculate_matches_demand()` : trouve des candidats pour une demande spécifique (jour + créneau). Vérifie la matière (35 pts si correspond, 10 si autres compétences uniquement). Exclut les candidats sans créneau disponible correspondant à celui de la demande.

### Réservations de créneaux

Quand un matching est **accepté**, le créneau de l'aidant est marqué `is_reserved = True`. Il n'apparaît plus dans les futures suggestions (les disponibilités réservées sont exclues de la requête SQL via le filtre `is_reserved = False`).

### Seuil et limite

- **Score minimum** : 55 / 100 — les candidats en dessous sont exclus des résultats.
- **Nombre maximum** : 50 résultats — au-delà, seuls les 50 meilleurs sont renvoyés.

### Optimisation N+1

Pour éviter une explosion de requêtes SQL, toutes les données liées (utilisateurs, compétences, disponibilités) sont pré-chargées en **3 requêtes massives** avant la boucle de scoring (via `filter(…id.in_(…))` et stockées dans des dictionnaires indexés par `profile_id`). La boucle principale n'effectue **aucune requête DB** par candidat.

---

## Installation locale

```bash
git clone https://github.com/urielhgb7-arch/PIL1_2526_64.git
cd PIL1_2526_64
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate      # macOS/Linux
cd backend
pip install -r requirements.txt
```

Créer `backend/.env.local` :
```
DATABASE_URL=postgresql://postgres:mdp@localhost:5432/mentorlink
```

```bash
python run.py                  # Backend → http://127.0.0.1:5000
```

Dans un second terminal :
```bash
cd Frontend
npx live-server --port=5500    # Frontend → http://127.0.0.1:5500
```

---

## Tests

```bash
cd backend
python -m pytest -q
```

Couvre : auth, profils, offres, demandes, matching, messages.

---

## Déploiement

**Backend (Render)** — `https://ifri-mentorlink.onrender.com`
- Start : `gunicorn -k eventlet -w 1 run:app`
- Variables : `DATABASE_URL`, `SECRET_KEY`, `FLASK_ENV=production`

**Frontend (Vercel)** — `https://ifrimentorlink.vercel.app`
- Branch : `develop`
- Fichier statique (HTML/CSS/JS), pas de build.

---

*Projet IFRI — PIL1_2526*
