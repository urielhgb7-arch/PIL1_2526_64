API client centralisé — Frontend/js/api.js

But: Ce document décrit les routes utilisées par `Frontend/js/api.js` et les contrats JSON attendus.

Base URL
- `API_BASE_URL` : configuré automatiquement pour `http://127.0.0.1:5000/api` en dev local.
- Toutes les routes appelées sont relatives à `/api` côté backend.

Authentification
- Le token JWT est lu/storé dans `localStorage` sous la clé `mentorlink_token`.
- Le header `Authorization: Bearer <token>` est ajouté automatiquement par `fetchAPI`.

Principaux namespaces exposés (résumé)
- `API.auth`
  - `register(userData)` → POST `/auth/register` (body: email,password,nom,prenom,filiere,niveau,format_preference)
  - `login(credentials)` → POST `/auth/login` (body: email,password)

- `API.profile`
  - `getMe()` → GET `/profile/me`
  - `updateMe(data)` → PUT `/profile/me`
  - `addCompetence(data)` → POST `/profile/competences` (matiere_id,niveau,is_available_to_help)
  - `removeCompetence(data)` → DELETE `/profile/competences` (matiere_id)
  - `addDisponibilite(data)` → POST `/profile/disponibilites` (jour,creneau)
  - `removeDisponibilite(data)` → DELETE `/profile/disponibilites` (jour,creneau)
  - `addLacune(data)` → POST `/profile/lacunes` (matiere_id,priorite)
  - `removeLacune(data)` → DELETE `/profile/lacunes` (matiere_id)

- `API.matching`
  - `getSuggestions(filters)` → GET `/matches/suggestions` (?matiere_id=...)
  - `requestMatch(studentId, body)` → POST `/matches/<studentId>/request` (matiere_id,score)
  - `accept(matchId)` → POST `/matches/<matchId>/accept`
  - `reject(matchId)` → POST `/matches/<matchId>/reject`

- `API.messages`
  - `getConversations()` → GET `/conversations`
  - `create(userId)` → POST `/conversations` (user_id)
  - `getHistory(convId)` → GET `/conversations/<convId>/messages`
  - `send(convId, text)` → POST `/conversations/<convId>/messages` (contenu)

- `API.notifications`
  - `getAll()` → GET `/notifications`
  - `markRead(id)` → PUT `/notifications/<id>/read`

- `API.matieres`
  - `getAll()` → GET `/matieres`

Comportement important côté backend (notes pour l'équipe frontend)
- Quand une demande de matching est créée (`POST /matches/<studentId>/request`),
  le backend crée désormais une `Conversation` immédiatement et renvoie `conversation_id`
  (si la conversation n'existait pas déjà). Cela permet au mentor et au demandeur
  d'échanger dès la création de la demande.

- Quand un matching est accepté (`POST /matches/<matchId>/accept`),
  la conversation est créée (ou récupérée) si nécessaire et l'API renvoie `conversation_id`.
  De plus, la disponibilité de l'aidant est gelée pour la matière correspondante
  (`ProfilCompetence.is_available_to_help = false`) et le profil global peut être
  marqué comme non-disponible (`profile.disponible = false`).

Conseils d'intégration
- Toujours vérifier la présence d'un `token` et gérer les 401 en redirigeant
  vers la page de login.
- Les endpoints acceptent/renvoient JSON; le client doit afficher les messages d'erreur
  contenus dans `message` quand `response.ok` est false.

Contact
- Pour toute modification d'API, parlez d'abord avec l'équipe backend et mettez à jour ce fichier.
