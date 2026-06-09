# IFRI_MentorLink — PIL1_2526_64

> Application web de mise en relation mentor–mentoré au sein de l'IFRI  
> Projet Intégrateur L1 — Année universitaire 2025–2026  
> Université d'Abomey-Calavi — IFRI

---

## 👥 Membres du groupe

| Nom | Filière | Rôle |
|-----|---------|------|
| HOUEGBELO Uriel Verghis Olsen | GL | Tech Lead / Backend |
| GOUTONDE Bidossessi Conceptia Sharone | SI | Développeur Frontend |
| LOTSU Emmanuel Richard Kwasi | SI | Développeur Backend / Render |
| HOUNNOUKON Agossou Prince | SI | Développeur Frontend & Messagerie |
| YESSOUFOU Scham's-Deen | GL | Développeur Fullstack & Matching |
| TOCHENALI Paola Eloane | GL | Développeur Backend |
| MOUTOUAMA Liwêto Eben-Ezer | IM | Développeur Frontend UI/UX |

---

## 📁 Structure du projet

```
PIL1_2526_64/
├── index.html              # Rapport de projet
├── README.md               # Ce fichier
├── database.sql            # Structure de la base de données
├── frontend/
│   ├── index.html          # Page d'accueil
│   ├── login.html          # Connexion
│   ├── register.html       # Inscription
│   ├── dashboard.html      # Tableau de bord
│   ├── profile.html        # Profil utilisateur
│   ├── matching.html       # Résultats de matching
│   ├── messages.html       # Messagerie
│   └── assets/
│       ├── css/style.css
│       ├── js/main.js
│       └── img/
└── backend/
    ├── app.py
    ├── models.py
    ├── config.py
    ├── requirements.txt
    └── routes/
        ├── auth.py
        ├── profile.py
        ├── matching.py
        └── messages.py
```

---

## ⚙️ Installation & lancement

### Prérequis
- Python 3.10+
- PostgreSQL 14+
- pgAdmin 4
- Git

### 1. Cloner le dépôt
```bash
git clone https://github.com/[votre-org]/PIL1_2526_64.git
cd PIL1_2526_64
```

### 2. Créer l'environnement virtuel
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
pip install -r backend/requirements.txt
```

### 3. Créer la base de données dans pgAdmin
- Ouvrir pgAdmin
- Clic droit sur **Databases** → **Create** → **Database**
- Nommer la base : `mentorlink`
- Ouvrir **Query Tool** → charger `database.sql` → **F5**

### 4. Configurer le backend
```python
# backend/config.py
DB_HOST     = "localhost"
DB_NAME     = "mentorlink"
DB_USER     = "postgres"
DB_PASSWORD = "votre_mot_de_passe"
SECRET_KEY  = "une_cle_secrete_longue_et_unique"
```

### 5. Lancer le serveur
```bash
cd backend
python app.py
```
Accéder à l'application : **http://localhost:5000**

---

## 🔗 Collaborateurs GitHub

Les encadrants suivants ont accès au dépôt :
- [@ratheilesse](https://github.com/ratheilesse)
- [@primearwyn](https://github.com/primearwyn)
- [@MaryseGAHOU](https://github.com/MaryseGAHOU)

---

## 📅 Calendrier du projet

| Date | Étape |
|------|-------|
| 1 juin 2026 | Lancement du projet |
| 3–4 juin 2026 | Échanges encadrement & bonnes pratiques |
| 8–9 juin 2026 | Suivi par groupe |
| **10 juin 2026** | **Dépôt final (23h59)** |
| 12–13 juin 2026 | Présentations & évaluation finale |

---

## 🛠️ Technologies utilisées

| Couche | Technologie |
|--------|-------------|
| Frontend | HTML5, CSS3, JavaScript, Tailwind CSS |
| Backend | Python, Flask |
| Base de données | PostgreSQL |
| Versioning | Git & GitHub |
| Gestion de projet | Trello |
| Déploiement | Render |

---

*IFRI — Université d'Abomey-Calavi — Groupe PIL1_2526_64*
