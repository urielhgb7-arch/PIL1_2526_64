# MentorLink Backend Debug Frontend

Interface temporaire isolée pour tester les APIs du backend MentorLink sans toucher au frontend de production.

## Emplacement
- `backend/debug_frontend/index.html`
- `backend/debug_frontend/styles.css`
- `backend/debug_frontend/app.js`

## Objectif
Cette UI permet de tester :
- authentification `/api/auth`
- profil `/api/profile/me`
- compétences `/api/profile/competences`
- matching `/api/matches/suggestions`
- demandes `/api/matches/sent`, `/api/matches/received`, `/api/matches/{id}/request`
- notifications `/api/notifications`
- conversations `/api/conversations`
- messages `/api/conversations/{id}/messages`

## Lancer
1. Démarrer le backend Flask comme d'habitude depuis `d:\IFRI-MentorLink\backend`.
2. Ouvrir un terminal dans `d:\IFRI-MentorLink\backend\debug_frontend`.
3. Lancer un serveur local :
   - `python -m http.server 8000`
4. Ouvrir dans le navigateur :
   - `http://127.0.0.1:8000`

> Le fichier `index.html` charge `app.js` et effectue des requêtes vers le backend. Lancer depuis HTTP évite les problèmes CORS/`file://`.

## Utilisation
- Configurez l’URL du backend si besoin (par défaut `http://127.0.0.1:5000/api`).
- Inscrivez un nouvel utilisateur ou connectez-vous.
- Chargez le profil, mettez-le à jour et testez les routes de profil.
- Chargez les matières pour remplir les sélecteurs de compétences et de faiblesses.
- Testez le matching, les demandes, les notifications et les conversations.

## Remarque
Cette interface est conçue uniquement pour tester le backend. Ne modifiez pas le dossier `Frontend/` de production.

## Suppression après tests
Pour supprimer l’UI de test :
- supprimez le dossier `backend/debug_frontend`.
