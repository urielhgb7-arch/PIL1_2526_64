# Guide des Tests UI - MentorLink Backend

**Date**: 2026-06-07  
**URL de Test**: http://127.0.0.1:5000/debug  
**Backend**: http://127.0.0.1:5000/api

---

## 🚀 Démarrage

### 1. Lancer le serveur backend
```bash
cd backend
python -m flask run --debug
# Serveur accessible à http://localhost:5000
```

### 2. Accéder à l'interface de test
Ouvrir dans le navigateur: **http://127.0.0.1:5000/debug**

---

## 📖 Guide Complet du Workflow

Ce guide vous montre comment tester le **workflow complet de matching avec créneaux obligatoires**.

### Scénario de Test: 2 Utilisateurs

**Alice** (Demandeur):
- Email: alice@test.com
- Matière: Mathématiques
- Demande pour: **Lundi 14-15** (créneau obligatoire)

**Bob** (Aidant):
- Email: bob@test.com
- Compétence: Mathématiques (Avancé)
- Disponibilité: **Lundi 14-15** ✅

---

## Step 1️⃣: Créer deux utilisateurs

### Alice (Demandeur)

1. **Aller à "Authentification" → "Inscription"**
   - Email: `alice@test.com`
   - Mot de passe: `password123`
   - Nom: `Alice`
   - Prénom: `Dupont`
   - Filière: `Informatique`
   - Année: `L2`
   - Format: `hybride`
   - ➡️ Cliquer **"Inscrire"**

2. **Vérifier la réponse** dans "Dernière réponse API"
   ```json
   {
     "message": "Compte créé avec succès"
   }
   ```

3. **Se connecter**
   - Email: `alice@test.com`
   - Mot de passe: `password123`
   - ➡️ Cliquer **"Se connecter"**

4. **Vérifier la connexion**
   - Le champ "Statut" doit afficher: "Connecté ✅"
   - Le champ "Utilisateur" doit afficher: `alice@test.com`

---

### Bob (Aidant)

1. **Se déconnecter** (Alice)
   - ➡️ Cliquer **"Se déconnecter"** en bas à gauche
   - Vérifier "Statut" = "Déconnecté"

2. **Inscrire Bob**
   - Email: `bob@test.com`
   - Mot de passe: `password456`
   - Nom: `Bob`
   - Prénom: `Martin`
   - Filière: `Informatique`
   - Année: `L3`
   - Format: `hybride`
   - ➡️ Cliquer **"Inscrire"**

3. **Se connecter comme Bob**
   - Email: `bob@test.com`
   - Mot de passe: `password456`
   - ➡️ Cliquer **"Se connecter"**

---

## Step 2️⃣: Configurer les compétences et lacunes

### Alice - Ajouter sa Lacune

1. **Alice doit être connectée**
   
2. **Aller à "Faiblesses"**
   - Matière: **Mathématiques**
   - Gravité: **Haute**
   - ➡️ Cliquer **"Ajouter faiblesse"**

3. **Vérifier dans "Résultat faiblesse"**
   ```json
   {
     "message": "Lacune créée avec succès"
   }
   ```

### Bob - Ajouter sa Compétence

1. **Se déconnecter Alice → Se connecter Bob**
   
2. **Aller à "Compétences"**
   - Matière: **Mathématiques**
   - Niveau: **Avancé**
   - ✅ Cocher "Disponible pour aider"
   - ➡️ Cliquer **"Ajouter compétence"**

3. **Vérifier** dans "Résultat compétence"
   ```json
   {
     "message": "Compétence créée avec succès"
   }
   ```

---

## Step 3️⃣: Ajouter les Disponibilités

### Alice - Ajouter Disponibilité

1. **Alice connectée**

2. **Aller à "Disponibilités"**
   - Jour: **Lundi**
   - Créneau: **14:00-15:00**
   - ➡️ Cliquer **"Ajouter créneau"**

3. **Vérifier** dans "Résultat disponibilité"

### Bob - Ajouter Disponibilité

1. **Se déconnecter Alice → Se connecter Bob**

2. **Ajouter disponibilité Bob**
   - Jour: **Lundi**
   - Créneau: **14:00-15:00**
   - ➡️ Cliquer **"Ajouter créneau"**

---

## Step 4️⃣: Alice Crée une Demande

### ⭐ Créer la Demande avec Créneau Obligatoire

1. **Alice doit être connectée**

2. **Aller à "Créer une Demande" (section nouvelle)**
   - Matière: **Mathématiques**
   - Jour: **Lundi** ⭐ (OBLIGATOIRE)
   - Créneau: **14-15** ⭐ (OBLIGATOIRE)
   - Description: "Besoin d'aide en calcul différentiel"
   - ➡️ Cliquer **"Créer demande"**

3. **Vérifier la création**
   ```json
   {
     "message": "Demande créée avec succès",
     "id": 1
   }
   ```
   
   📌 **Noter l'ID de la demande (ex: 1)**

---

## Step 5️⃣: Alice Cherche des Candidats

### 🔍 Matching Filtre par Créneau

1. **Alice reste connectée**

2. **Aller à "Chercher des Candidats"**
   - ID Demande: **1** (l'ID de la demande créée)
   - ➡️ Cliquer **"Chercher candidats"**

3. **Vérifier les résultats**
   
   ✅ **Bob doit apparaître** (car il a Lundi 14-15 disponible ET compétent)
   
   ```json
   {
     "total": 1,
     "matches": [
       {
         "student_id": 2,
         "nom": "Bob",
         "prenom": "Martin",
         "score": 100,
         "matched_subjects": [
           {
             "nom": "Mathématiques",
             "niveau_competence": "Avancé",
             "priorite_lacune": "Haute"
           }
         ],
         "explication": {
           "score_pct": "100%",
           "raisons": [
             "Compétent en Mathématiques (niveau Avancé)",
             "1 créneau(x) disponible(s) en commun",
             "Même filière",
             "Même année académique",
             "Même format d'apprentissage"
           ]
         }
       }
     ]
   }
   ```

---

## Step 6️⃣: Alice Envoie une Demande à Bob

### 💬 Créer le Match

1. **Alice reste connectée**

2. **Aller à "Envoyer une Demande"**
   - Candidat ID: **2** (Bob)
   - Demande ID: **1** (la demande créée)
   - Score de compatibilité: **100**
   - ➡️ Cliquer **"Envoyer demande de match"**

3. **Vérifier le résultat**
   ```json
   {
     "message": "Demande envoyée avec succès",
     "matching_id": 1,
     "status": "pending"
   }
   ```

   📌 **Noter l'ID du matching (ex: 1)**

---

## Step 7️⃣: Bob Voit la Demande Reçue

### 📥 Voir les Demandes Reçues

1. **Se déconnecter Alice → Se connecter Bob**

2. **Aller à "Gérer les Demandes" → "Mes demandes reçues"**
   - ➡️ Cliquer le bouton

3. **Vérifier le tableau**

   | ID | Personne | Jour | Créneau | Score | Statut | Action |
   |----|----------|------|---------|-------|--------|--------|
   | 1 | Alice Dupont | Lundi | 14-15 | 100 | pending | ✅ Accepter / ❌ Refuser |

   ✅ **Le créneau "Lundi 14-15" doit s'afficher**

---

## Step 8️⃣: Bob Accepte le Match

### ✅ Acceptation = Réservation du Créneau

1. **Bob voit la demande reçue**

2. **Dans le tableau, cliquer "✅ Accepter"** (ou manuellement)
   
   **Si action manuelle:**
   - Matching ID: **1**
   - ➡️ Cliquer **"Accepter"**

3. **Vérifier l'acceptation**
   ```json
   {
     "message": "Match accepté ! Vous pouvez maintenant discuter.",
     "status": "accepted",
     "conversation_id": 1
   }
   ```

   ✅ **Une conversation a été créée automatiquement**

---

## Step 9️⃣: Vérifier la Réservation du Créneau

### 🔒 Slot Réservé = Indisponible pour Autres

1. **Alice se reconnecte**

2. **Alice crée une 2e demande** (test)
   - Matière: **Mathématiques**
   - Jour: **Lundi**
   - Créneau: **14-15** (même que la première)
   - Description: "Deuxième demande test"
   - ➡️ **Créer demande**

3. **Alice cherche les candidats pour cette 2e demande**
   - ➡️ Cliquer **"Chercher candidats"** avec le nouvel ID

4. **Vérifier le résultat**
   
   ❌ **Bob ne doit PAS apparaître** (son créneau est réservé)
   
   ```json
   {
     "total": 0,
     "matches": [],
     "message": "Aucun candidat trouvé. Complétez vos lacunes et disponibilités."
   }
   ```

   ✅ **Test de réservation réussi!**

---

## 🔟: Converser via WebSocket (Optional)

### 💬 Échanger des Messages

1. **Bob connecté**

2. **Aller à "Conversations"**
   - Conversation ID: **1** (créée automatiquement)
   - ➡️ Cliquer **"Ouvrir conversation"**

3. **Vérifier le message**
   
4. **Envoyer un message**
   - Message: "Bonjour Alice, je peux t'aider !"
   - ➡️ Cliquer **"Envoyer message"**

5. **Se reconnecter comme Alice**
   - Ouvrir la même conversation
   - ➡️ Vérifier que le message de Bob s'affiche

---

## 📊 Résumé des Tests

| # | Test | Statut |
|---|------|--------|
| 1 | 👤 Créer 2 utilisateurs | ✅ |
| 2 | 📚 Ajouter compétence/lacune | ✅ |
| 3 | 📅 Ajouter disponibilités (Lundi 14-15) | ✅ |
| 4 | 📋 Créer demande avec créneau | ✅ |
| 5 | 🔍 Matching filtre par créneau | ✅ |
| 6 | 💬 Envoyer demande de match | ✅ |
| 7 | 📥 Voir demandes reçues | ✅ |
| 8 | ✅ Accepter match = réserver slot | ✅ |
| 9 | 🔒 Slot réservé exclu des futurs matchs | ✅ |
| 10 | 💬 Converser via WebSocket | ✅ |

---

## 🔧 Cas de Test Supplémentaires

### Test: Refuser un Match

1. **Créer un autre utilisateur Charlie**
2. **Charlie envoie une demande à Alice**
3. **Alice reçoit la demande**
4. **Cliquer "❌ Refuser"** dans le tableau
5. **Vérifier** que le statut passe à "rejected"

### Test: Matching sans demand_id

1. **Alice cherche des candidats SANS demand_id**
   - Ne pas spécifier d'ID
   - Utiliser "Matching" (legacy)
2. **Vérifier** que les suggestions incluent ses disponibilités générales

### Test: Créneau Invalide

1. **Créer une demande avec créneau invalide**
   - Créneau: "99-100"
2. **Vérifier le message d'erreur**
   ```json
   {
     "message": "creneau invalide"
   }
   ```

---

## 🐛 Dépannage

### "La demande n'existe pas"
- Vérifier l'ID de la demande
- Vérifier qu'elle a été créée avec succès

### "Le candidat n'a pas le créneau"
- Le candidat doit avoir ajouté la disponibilité pour le même jour/créneau
- Les créneaux sont sensibles à la casse (ex: "Lundi" ≠ "lundi")

### "Match non autorisé"
- Vérifier que vous êtes connecté avec le bon compte
- L'initiateur du match doit être le demandeur

### Token JWT expiré
- Se déconnecter et reconnecter
- Le token est sauvegardé dans localStorage

---

## 🔐 Points de Sécurité Testés

- ✅ Vérification JWT sur toutes les routes protégées
- ✅ Validation des données (jour/creneau valides)
- ✅ Vérification d'autorisation (ne peut matcher que sa propre demande)
- ✅ Isolation des données (voir uniquement ses propres données)

---

## 📸 Dépannage UI

### Les boutons n'apparaissent pas
- Vérifier que localStorage n'est pas plein
- Ouvrir la console (F12) pour voir les erreurs

### "Erreur CORS"
- Vérifier que le backend tourne sur http://127.0.0.1:5000
- Vérifier que l'API URL est correcte dans la configuration

### Les réponses ne s'affichent pas
- Ouvrir la console (F12)
- Vérifier les requêtes réseau (onglet Network)

---

## 📚 Documentation Complète

Voir aussi:
- [BACKEND_STATUS.md](../BACKEND_STATUS.md) - État complet du backend
- [backend/README.md](../backend/README.md) - Documentation backend
- [API Endpoints](../docs/openapi.yaml) - Spécification OpenAPI (si disponible)

---

**✅ Test terminé avec succès!**

Vous avez testé le workflow complet:
1. Création de demande avec créneaux obligatoires
2. Matching filtré strictement par créneau
3. Réservation automatique à l'acceptation
4. Exclusion des slots réservés des futurs matchs
