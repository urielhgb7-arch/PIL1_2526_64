# IFRI MentorLink

Plateforme de mentorat academique basee sur un matching intelligent.

## Stack

- Flask
- PostgreSQL
- SQLAlchemy
- Socket.IO
- HTML
- CSS
- JavaScript

## Equipe & Roles

| # | Membre | Groupe | Role |
|---|--------|--------|------|
| 1 | GOUTONDE Bidossessi Conceptia Sharone | F2 | Developpeur Frontend |
| 2 | HOUEGBELO Uriel Verghis Olsen | — | Tech Lead / Backend |
| 3 | LOTSU Emmanuel Richard Kwasi | B3 | Developpeur Backend |
| 4 | HOUNNOUKON Agossou Prince | F4 | Rapporteur |
| 5 | YESSOUFOU Scham's-Deen | F3 | Developpeur Frontend |
| 6 | TOCHENALI Paola Eloane | B2 | Developpeur Backend |
| 7 | 

## Structure du projet

```
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
 README.md
```

## Installation locale

1. Cloner le depot
```bash
git clone https://github.com/votre-org/projet-flask.git
cd PIL1_2526_64
```

2. Creer un environnement virtuel
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

3. Installer les dependances backend
```bash
cd backend
pip install -r requirements.txt
```

4. Lancer le backend
```bash
python run.py
```
Le backend ecoute par defaut sur `http://127.0.0.1:5000`.

5. Lancer le frontend de test
```bash
cd ../Frontend
python -m http.server 8000
```
Ouvrir `http://127.0.0.1:8000/` dans un navigateur.

## Tests en local et sur plusieurs navigateurs

### Tests backend automatises
Pour executer les tests backend sur votre machine locale :

1. Activez votre environnement virtuel depuis la racine du projet :
```bash
cd D:\IFRI-MentorLink\backend
..\ .venv\Scripts\activate
```
2. Installez les dependances si ce n'est pas deja fait :
```bash
pip install -r requirements.txt
```
3. Lancez la suite complete de tests :
```bash
python -m pytest -q
```

#### Executer des tests cibles
- Pour tester uniquement les demandes :
```bash
python -m pytest tests/test_backend.py -q
```
- Pour tester les offres et reponses aux offres :
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
  - recuperation du profil
  - liste des matieres
  - suggestions de matching
  - conversations et messages
  - notifications
  - WebSocket
  - polling

### Test WebSocket (3 navigateurs)
1. Ouvre `http://127.0.0.1:8000/pages/debug.html` dans trois navigateurs differents.
2. Connecte-toi avec le meme compte dans chaque navigateur.
3. Dans chaque navigateur, clique sur `Connecter WebSocket`.
4. Clique sur `S'enregistrer (user_id)` pour associer le socket a l'utilisateur.
5. Renseigne la meme `Conversation ID` dans chaque navigateur.
6. Clique sur `Joindre conversation` dans chaque navigateur.
7. Dans un navigateur, clique sur `Envoyer message WebSocket`.
8. Verifie que les autres navigateurs recoivent bien l'evenement `new_message`.

### Test polling
1. Ouvre la page de test dans au moins un navigateur.
2. Clique sur `Demarrer polling`.
3. Dans un autre onglet ou un autre navigateur, envoie un message ou ajoute du contenu qui devrait etre detecte.
4. Verifie dans le premier navigateur que les nouvelles donnees sont recuperees toutes les 5 secondes.
5. Clique sur `Arreter polling` pour mettre fin au test.

### Notes importantes
- Assure-toi que le backend est demarre avant d'ouvrir la page debug.
- Si `127.0.0.1:5000` ne fonctionne pas, verifie le port et l'URL dans `Frontend/pages/debug.html`.
- Le front de test est concu pour etre simple, mais il couvre toutes les fonctionnalites backend actuelles.

## Deploiement (Render)

- URL de production : [https://ifri-mentorlink.onrender.com](https://ifri-mentorlink.onrender.com)
- Build command : pip install -r requirements.txt
- Start command : gunicorn app:app

## Planning

| Jour | Objectif | Date |
|------|----------|------|
| J1 | Structure validee + Flask Hello World + Render configure | 3 juin |
| J2 | Base de donnees + Authentification + Deploiement actif | 4 juin |
| J3 | Backend profils + competences + disponibilites | 5 juin |
| J4 |  |  |
| J5 |  |  |
| J6 |  |  |
| J7 |  |  |



## Rapport d'integration

Le rapport officiel est disponible dans rapport.html.

---
*Projet IFRI — PIL1_2526 — Session encadrement J2 : 13h–18h*
