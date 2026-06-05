# IFRI MentorLink

Plateforme de mentorat académique basée sur un matching intelligent.

## Stack

- Flask
- PostgreSQL
- SQLAlchemy
- Socket.IO
- HTML
- CSS
- JavaScript
- ## 👥 Équipe & Rôles

| # | Membre | Groupe | Rôle |
|---|--------|--------|------|
| 1 | **GOUTONDE Bidossessi Conceptia Sharone** | F2 | Développeur Frontend |
| 2 | **HOUEGBELO Uriel Verghis Olsen** | — | 🔧 Tech Lead / Backend |
| 3 | **LOTSU Emmanuel Richard Kwasi** | B3 | Développeur Backend |
| 4 | **HOUNNOUKON Agossou Prince** | F4 | Développeur Backend / Render |
| 5 | **YESSOUFOU Scham's-Deen** | F3 | Développeur Fullstack |
| 6 | **TOCHENALI Paola Eloane** | B2 | Développeur Frontend |
## 🗂️ Structure du projet

projet-flask/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── auth.py
│   │   └── profils.py
│   └── templates/
│       ├── base.html
│       ├── login.html
│       └── register.html
├── docs/
│   └── postman_collection.json
├── rapport.html
├── requirements.txt
├── render.yaml
└── README.md

## ⚙️ Installation locale

# 1. Cloner le dépôt
git clone https://github.com/votre-org/projet-flask.git
cd projet-flask

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate

# 3. Installer les dépendances
<<<<<<< HEAD
pip install -r requirements.txt.
=======
pip install -r requirements.txt
>>>>>>> 031f9fe4370b1d031dac17a56665eacfc3efb57a

# 4. Lancer l'application
flask run

L'application sera disponible sur http://localhost:5000

## 🌐 Déploiement (Render)

- URL de production : https://votre-app.onrender.com
- Build command : pip install -r requirements.txt
- Start command : gunicorn app:app

## 📅 Planning

| Jour | Objectif | Date |
|------|----------|------|
| J1 | Structure validée + Flask Hello World + Render configuré | 3 juin |
| J2 | Base de données + Authentification + Déploiement actif | 4 juin |
| J3 | Backend profils + compétences + disponibilités | 5 juin |

## 📄 Livrables

- [x] Repo cloné par tous les membres
- [x] App Flask qui tourne en local
- [x] Compte Render créé
- [ ] /register et /login fonctionnels en production
- [ ] rapport.html complété
- [ ] Collection Postman commitée dans /docs

## 📝 Rapport d'intégration

Le rapport officiel est disponible dans rapport.html.

---
*Projet IFRI — PIL1_2526 — Session encadrement J2 : 13h–18h*

