# MentorLink — Parcours Utilisateur

## 1. Landing Page (`index.html`)

Présentation de la plateforme. Boutons **Connexion** → `signin.html` et **Inscription** → `signup.html`.

## 2. Inscription (`signup.html`)

- Email, mot de passe (min 8 car., 1 chiffre, 1 lettre), nom, prénom, téléphone béninois (`01[4569]XXXXXXX`, 10 chiffres).
- Le profil est créé avec des valeurs par défaut (`filière=GL`, `niveau=L1`).
- Redirige vers **`onboarding.html`** après succès.

## 3. Onboarding (`onboarding.html`)

Questionnaire pour compléter le profil :
1. **Filière** (GL, SIRI, IM) et **niveau** (L1–L3)
2. **Compétences** (matières où l'utilisateur est à l'aise)
3. **Lacunes** (matières où il a besoin d'aide)
4. **Disponibilités** (créneaux horaires)
5. **Avatar** (photo de profil)

Une fois terminé → redirection vers **`dashboard.html`**.

## 4. Dashboard (`dashboard.html`)

Vue d'ensemble :
- **Carte profil** en haut : nom, email, filière, niveau, avatar, compétences et lacunes (4 max).
- **Métriques** : matchs acceptés, heures de mentorat.
- **Publications récentes** : onglets Offres / Demandes avec filtres par matière.
  - Chaque carte montre le nom et l'avatar du publicateur.
  - Cliquer sur **Voir** → modale détaillée (matière, description, téléphone, dispo).
- **Navigation** : sidebar/MobileNav pour accéder aux autres pages.

## 5. Offres & Demandes (`requests.html`)

Trois sections via onglets :
- **Mes offres** / **Mes demandes** : publications créées par l'utilisateur (suppression possible).
- **Offres disponibles** / **Demandes disponibles** : publications des autres étudiants.
  - Chaque carte affiche l'avatar et le nom du publicateur.
  - Cliquer sur une carte → modale détaillée (téléphone visible si publié).
  - **Postuler** (offre) / **Proposer mon aide** (demande) → crée un match.

### Créer une publication
- Bouton **+ Nouvelle publication** → modale
- Type : Offre / Demande
- Matière, description, format (présentiel/en ligne/hybride), disponibilités, urgence (si demande)
- **Publier** → création via API → retour au dashboard.

## 6. Matching (`matching.html`)

Interface de swipe :
- Cartes d'étudiants suggérées par l'algorithme (basé sur compétences ↔ lacunes, filière, niveau).
- **Swipe droit (Accepter)** → envoie une demande de match.
- **Swipe gauche (Refuser)** → passe à la suggestion suivante.
- Les matchs acceptés créent automatiquement une conversation.

## 7. Messages (`messages.html`)

Chat temps réel via Socket.IO :
- Liste des conversations (avatar + nom du correspondant).
- Cliquer → historique des messages + champ de saisie.
- Les nouveaux messages arrivent en temps réel (événement `new_message`).
- Badge de notifications non lues mis à jour toutes les 30 secondes.

## 8. Paramètres (`settings.html`)

Gestion complète du profil :
- **Avatar** : upload → recadrage (Cropper.js, carré 1:1) → bouton Enregistrer/Annuler. Sauvegardé via API, persistant jusqu'à modification manuelle. Le cache dashboard (`mentorlink_profile_cache`) est mis à jour après validation.
- **Informations** : nom, prénom, email, téléphone, filière, niveau, bio.
- **Compétences** : ajout/suppression avec toggle activation.
- **Lacunes** : ajout/suppression.
- **Disponibilités** : grille de créneaux (cliquer pour ajouter/enlever).
- **Mot de passe** : changement avec ancien + nouveau.

## 9. Notifications (`notifications.html`)

Centre de notifications :
- Non lues en surbrillance.
- Marquer comme lue / tout lire / supprimer.
- Types : `match_system` (demande, acceptation, refus), `message` (nouveau message reçu dans une conversation), `alert`.
- Les notifications de message sont créées côté backend à chaque envoi (socket REST).

## 10. Connexion (`signin.html`)

Authentification JWT. Token stocké dans `localStorage`.  
Lien **Mot de passe oublié ?** → `reset-password.html`.

## 11. Réinitialisation mot de passe (`reset-password.html`)

Deux étapes :
1. Saisie email → envoi token.
2. Saisie token + nouveau mot de passe.

---

## Gestion des tokens & redirections

- `localStorage` stocke : `mentorlink_token`, `mentorlink_user`, `isAuthenticated`, `userData`, `mentorlink_profile_cache`.
- Le cache profil (`mentorlink_profile_cache`) permet un affichage instantané du dashboard sans attendre l'API.
- En cas de 401, l'utilisateur est redirigé vers `signin.html` (sauf pages publiques : index, signin, signup, reset-password).
- Au logout : tous les items localStorage sont effacés.

---

## Architecture fichiers JS

```
js/
  bundle.js        ← Fichier unique chargé par toutes les pages
    ├── api.js     ── Client API (fetchAPI + namespace API.*)
    ├── script.js  ── Helpers (getUserData, logout, formatDate)
    ├── matieres-loader.js ── Chargement matières avec cache
    └── notifications-badge.js ── Badge notifications non lues
  matching.js      ← Chargé uniquement par matching.html
  messaging.js     ← Chargé uniquement par messages.html
  notifications.js ← Chargé uniquement par notifications.html
```

## Palette de couleurs

```css
--background: #08090C    /* Fond principal */
--card:        #0F111A    /* Cartes */
--popover:     #1F2433    /* Surfaces surélevées */
--primary:     #7C6FF7    /* Actions principales */
--success:     #2DD4A0    /* Validations */
--warning:     #F5A623    /* Alertes */
--destructive: #F97066    /* Erreurs */
```

---

## Dépendances externes

- **Tailwind CSS** (CDN) — styling utilitaire
- **Tabler Icons** (CDN) — icônes SVG
- **Socket.IO** (CDN `socket.io.min.js`) — chat temps réel
- **Cropper.js** (CDN) — recadrage photo de profil
