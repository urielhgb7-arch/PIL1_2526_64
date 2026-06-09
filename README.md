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
- ##  Équipe & Rôles

| # | Membre | Groupe | Rôle |
|---|--------|--------|------|
| 1 | **GOUTONDE Bidossessi Conceptia Sharone** | F2 | Développeur Frontend |
| 2 | **HOUEGBELO Uriel Verghis Olsen** | — |  Tech Lead / Backend |
| 3 | **LOTSU Emmanuel Richard Kwasi** | B3 | Développeur Backend |
| 4 | **HOUNNOUKON Agossou Prince** | F4 | Développeur Backend / Render |
| 5 | **YESSOUFOU Scham's-Deen** | F3 | Développeur Fullstack |
| 6 | **TOCHENALI Paola Eloane** | B2 | Développeur Frontend |
##  Structure du projet

PIL1_2526_64/
 backend/
    app/
       __init__.py
       database/
          __init__.py
       config/
          __init__.py
          logging_config.py
       middleware/
          auth_guard.py
       models/
       routes/
       services/
       sockets/
    run.py
    requirements.txt
 Frontend/
    index.html
    pages/
       login.html
       debug.html
    js/
       api.js
    css/
    assets/
 docs/
 rapport.html
 README.md

##  Installation locale

1. Cloner le dépôt
```bash
git clone https://github.com/votre-org/projet-flask.git
cd PIL1_2526_64
```

2. Créer un environnement virtuel
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

3. Installer les dépendances backend
```bash
cd backend
pip install -r requirements.txt
```

4. Lancer le backend
```bash
python run.py
```
Le backend écoute par défaut sur `http://127.0.0.1:5000`.

5. Lancer le frontend de test
```bash
cd ../Frontend
python -m http.server 8000
```
Ouvrir `http://127.0.0.1:8000/` dans un navigateur.

##  Tests en local et sur plusieurs navigateurs

### Tests backend automatisés
Pour exécuter les tests backend sur votre machine locale :

1. Activez votre environnement virtuel depuis la racine du projet :
```bash
cd D:\IFRI-MentorLink\backend
..\ .venv\Scripts\activate
```
2. Installez les dépendances si ce n'est pas déjà fait :
```bash
pip install -r requirements.txt
```
3. Lancez la suite complète de tests :
```bash
python -m pytest -q
```

#### Exécuter des tests ciblés
- Pour tester uniquement les demandes :
```bash
python -m pytest tests/test_backend.py -q
```
- Pour tester les offres et réponses aux offres :
```bash
python -m pytest tests/test_offers.py -q
```
- Pour tester les sockets :
```bash
python -m pytest tests/test_sockets.py -q
```

> Si les tests utilisent plusieurs profils ou sockets, assurez-vous de lancer `python -m pytest` depuis le dossier `backend`.

### Page de test frontend
- Utilise `Frontend/pages/debug.html`.
- Elle permet de tester :
  - inscription et connexion
  - récupération du profil
  - liste des matières
  - suggestions de matching
  - conversations et messages
  - notifications
  - WebSocket
  - polling

### Test WebSocket (3 navigateurs)
1. Ouvre `http://127.0.0.1:8000/pages/debug.html` dans trois navigateurs différents.
2. Connecte-toi avec le même compte dans chaque navigateur.
3. Dans chaque navigateur, clique sur `Connecter WebSocket`.
4. Clique sur `S'enregistrer (user_id)` pour associer le socket à l'utilisateur.
5. Renseigne la même `Conversation ID` dans chaque navigateur.
6. Clique sur `Joindre conversation` dans chaque navigateur.
7. Dans un navigateur, clique sur `Envoyer message WebSocket`.
8. Vérifie que les autres navigateurs reçoivent bien l'événement `new_message`.

### Test polling
1. Ouvre la page de test dans au moins un navigateur.
2. Clique sur `Démarrer polling`.
3. Dans un autre onglet ou un autre navigateur, envoie un message ou ajoute du contenu qui devrait être détecté.
4. Vérifie dans le premier navigateur que les nouvelles données sont récupérées toutes les 5 secondes.
5. Clique sur `Arrêter polling` pour mettre fin au test.

### Notes importantes
- Assure-toi que le backend est démarré avant d'ouvrir la page debug.
- Si `127.0.0.1:5000` ne fonctionne pas, vérifie le port et l'URL dans `Frontend/pages/debug.html`.
- Le front de test est conçu pour être simple, mais il couvre toutes les fonctionnalités backend actuelles.

##  Déploiement (Render)

- URL de production : https://votre-app.onrender.com
- Build command : pip install -r requirements.txt
- Start command : gunicorn app:app

##  Planning

| Jour | Objectif | Date |
|------|----------|------|
| J1 | Structure validée + Flask Hello World + Render configuré | 3 juin |
| J2 | Base de données + Authentification + Déploiement actif | 4 juin |
| J3 | Backend profils + compétences + disponibilités | 5 juin |

##  Livrables

- [x] Repo cloné par tous les membres
- [x] App Flask qui tourne en local
- [x] Compte Render créé
- [ ] /register et /login fonctionnels en production
- [ ] rapport.html complété
- [ ] Collection Postman commitée dans /docs

##  Rapport d'intégration

Le rapport officiel est disponible dans rapport.html.

---
*Projet IFRI — PIL1_2526 — Session encadrement J2 : 13h–18h*

