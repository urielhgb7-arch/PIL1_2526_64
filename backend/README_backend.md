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

### 4. Installer PostgreSQL

**Windows** — Télécharger et installer depuis [postgresql.org/download](https://www.postgresql.org/download/windows/).
Pendant l'installation, notez le mot de passe défini pour l'utilisateur `postgres`.

**macOS :**
```bash
brew install postgresql@16
brew services start postgresql@16
```

**Linux (Debian/Ubuntu) :**
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 5. Créer la base de données

```bash
# Se connecter à PostgreSQL (Windows : chercher "pgAdmin" ou utiliser psql)
psql -U postgres

# Dans psql, exécuter :
CREATE DATABASE mentorlink;
\q
```

> Si `psql` n'est pas reconnu, ajoutez `C:\Program Files\PostgreSQL\16\bin` à votre `PATH`.

### 6. Configurer la connexion

Créer un fichier `backend/.env.local` :

```env
DATABASE_URL=postgresql://postgres:votre_mot_de_passe@localhost:5432/mentorlink
```

**Variables optionnelles** (si vous utilisez d'autres identifiants) :

| Variable | Défaut | Description |
|----------|--------|-------------|
| `DB_USER` | `postgres` | Utilisateur PostgreSQL |
| `DB_PASSWORD` | `postgres` | Mot de passe |
| `DB_HOST` | `localhost` | Hôte |
| `DB_PORT` | `5432` | Port |
| `DB_NAME` | `mentorlink` | Nom de la base |

### 7. Lancer les migrations

```bash
flask db upgrade
```

### 8. Démarrer le serveur backend

```bash
python run.py
```

Le serveur écoute sur `http://127.0.0.1:5000`.

### 9. Lancer le frontend

Ouvrir un **second terminal** :

```bash
# Depuis la racine du projet
cd Frontend

# Option A — Live Server (recommandé)
npx live-server --port=5500

# Option B — Serveur HTTP Python
python -m http.server 5500
```

### 10. Ouvrir le site

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

## Sécurité — Hachage des mots de passe

Le hachage est centralisé dans `app/models/user.py` via **Werkzeug** (`werkzeug.security`).

```python
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    password_hash = db.Column(db.String(255), nullable=False)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

**Algorithme** : `pbkdf2:sha256` (défaut Werkzeug), 260 000 itérations, sel aléatoire intégré au hash.  
Stocké en colonne `password_hash` sous forme `pbkdf2:sha256:<iterations>$<salt>$<hash>`.

**Points d'appel** — `app/routes/auth.py` : inscription (L127), connexion (L191), réinitialisation (L301), changement (L320–327), suppression compte (L347).

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
