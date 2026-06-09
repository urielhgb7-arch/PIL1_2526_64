# IFRI MentorLink — Backend

## Déploiement local (du clonage à la vue du site)

### 1. Cloner le dépôt

```bash
git clone https://github.com/urielhgb7-arch/PIL1_2526_64.git
cd PIL1_2526_64
```

### 2. Créer l'environnement virtuel

```bash
# Depuis la racine du projet
python -m venv .venv

# Activer (Windows)
.venv\Scripts\activate

# Activer (macOS / Linux)
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
cd backend
pip install -r requirements.txt
```

### 4. Configurer la base de données

**Option A — SQLite (par défaut, aucun setup requis)**

Le projet utilise SQLite automatiquement si `DATABASE_URL` n'est pas défini :
```python
# backend/app/config/__init__.py — ligne 44
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/app.db'
```

**Option B — PostgreSQL (production)**

Créer un fichier `backend/.env.local` :
```
DATABASE_URL=postgresql://utilisateur:motdepasse@localhost:5432/mentorlink
```

### 5. Lancer les migrations

```bash
flask db upgrade
```

Si c'est la première fois, les tables sont aussi créées automatiquement via `db.create_all()` dans `app/__init__.py`.

### 6. Démarrer le serveur backend

```bash
python run.py
```

Le serveur écoute sur `http://127.0.0.1:5000`.

### 7. Lancer le frontend

Ouvrir un **second terminal** :

```bash
# Depuis la racine du projet
cd Frontend

# Option A — Live Server (recommandé)
npx live-server --port=5500

# Option B — Serveur HTTP Python
python -m http.server 5500
```

### 8. Ouvrir le site

Naviguer vers `http://127.0.0.1:5500/` dans un navigateur.

---

## Pages principales

| Page | URL | Description |
|------|-----|-------------|
| Accueil | `/index.html` | Landing page |
| Inscription | `/pages/signup.html` | Création de compte |
| Connexion | `/pages/signin.html` | Connexion JWT |
| Dashboard | `/pages/dashboard.html` | Vue d'ensemble |
| Publications | `/pages/requests.html` | Offres / demandes |
| Matching | `/pages/matching.html` | Swipe & matcher |
| Messages | `/pages/messages.html` | Chat temps réel |
| Paramètres | `/pages/settings.html` | Profil, compétences |
| Notifications | `/pages/notifications.html` | Notifications |
| Debug | `/pages/debug.html` | Tests API/WebSocket |

---

## Tests

```bash
cd backend
pytest -q
```

---

## Déploiement (Render)

1. Créer un **Web Service** sur [Render](https://render.com)
2. **Branch** : `develop`
3. **Root directory** : `backend`
4. **Build command** : `pip install -r requirements.txt`
5. **Start command** : `gunicorn -k eventlet -w 1 run:app`
6. **Variables d'environnement** :
   - `DATABASE_URL` → URL PostgreSQL fournie par Render
   - `SECRET_KEY` → clé secrète JWT
   - `FLASK_ENV=production`
