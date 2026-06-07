# Backend IFRI MentorLink - État du Système

**Date**: 2026-06-07  
**Version**: 1.0 (Matching avec slots obligatoires)  
**Tests**: ✅ 35/35 passing

---

## 📋 Vue d'ensemble

Le backend implémente un **système de matching intelligent** basé sur :
- Création de **demandes avec créneaux obligatoires** (jour + heure)
- **Filtrage strict** des candidats par créneau
- **Réservation de créneaux** lors de l'acceptation d'un match
- **Gestion des conversations** et messages WebSocket
- **Authentification JWT** et gestion des utilisateurs

---

## 🔧 Architecture

### Stack Technique
- **Framework**: Flask + Flask-JWT-Extended
- **ORM**: SQLAlchemy
- **Base de données**: SQLite (dev) / PostgreSQL (prod)
- **Temps réel**: Socket.IO (WebSocket)
- **Tests**: pytest + Flask Test Client

### Structure des dossiers
```
backend/
├── app/
│   ├── routes/
│   │   ├── auth.py              # Authentification, inscription, réinitialisation mot de passe
│   │   ├── offers.py            # Offers (non utilisé actuellement) + Demands
│   │   ├── matching.py          # Moteur de matching et matchs
│   │   ├── profile.py           # Profils utilisateurs, compétences, lacunes, disponibilités
│   │   ├── messages.py          # Conversations et messages HTTP
│   │   └── notifications.py     # Notifications
│   ├── models/
│   │   ├── user.py              # User, PasswordResetToken
│   │   ├── profile.py           # Profile, ProfilCompetence, ProfilLacune, Disponible
│   │   ├── services.py          # Matiere, Offer, Demand, Matching, ProfilCompetence, ProfilLacune
│   │   └── messages.py          # Conversation, Message, Notification
│   ├── services/
│   │   └── matching.py          # Moteur de calcul des scores de matching
│   ├── sockets/
│   │   └── chat.py              # WebSocket pour messages en temps réel
│   ├── middleware/
│   │   └── auth_guard.py        # Protection des routes
│   ├── validators.py            # Validations réutilisables
│   ├── config/
│   │   └── __init__.py          # Configuration (remplace config.py supprimé)
│   ├── database.py              # Initialisation SQLAlchemy
│   └── __init__.py              # Initialisation Flask
├── tests/
│   ├── test_backend.py          # Tests principaux (35 tests)
│   ├── test_profile.py          # Tests profil
│   ├── test_messages.py         # Tests messages
│   └── conftest.py              # Fixtures pytest
├── run.py                       # Point d'entrée
├── requirements.txt             # Dépendances
├── init_db.py                   # Initialisation base de données
└── check_db.py                  # Diagnostic base de données
```

---

## 🌐 Endpoints Implémentés

### **Authentification** (`/api/auth`)

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/api/auth/register` | POST | Inscription utilisateur | ❌ |
| `/api/auth/login` | POST | Connexion | ❌ |
| `/api/auth/forgot-password` | POST | Demande réinitialisation mot de passe | ❌ |
| `/api/auth/reset-password` | POST | Réinitialisation mot de passe | ❌ |

### **Profils** (`/api/profile`)

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/api/profile/me` | GET | Récupérer mon profil | ✅ |
| `/api/profile/me` | PUT | Mettre à jour mon profil | ✅ |
| `/api/profile/<user_id>` | GET | Récupérer le profil d'un utilisateur | ✅ |
| `/api/profile/me/disponibilites` | GET | Mes créneaux de disponibilité | ✅ |
| `/api/profile/disponibilites` | POST | Ajouter un créneau | ✅ |
| `/api/profile/disponibilites/<jour>/<creneau>` | DELETE | Supprimer un créneau | ✅ |
| `/api/profile/competences` | POST | Ajouter une compétence | ✅ |
| `/api/profile/competences/<matiere_id>/activate` | PUT | Activer/désactiver une compétence | ✅ |
| `/api/profile/competences` | GET | Mes compétences | ✅ |
| `/api/profile/lacunes` | POST | Ajouter une lacune | ✅ |
| `/api/profile/lacunes` | GET | Mes lacunes | ✅ |
| `/api/profile/lacunes/<matiere_id>` | DELETE | Supprimer une lacune | ✅ |

### **Demandes** (`/api/demands`)

| Endpoint | Méthode | Description | Paramètres | Auth |
|----------|---------|-------------|-----------|------|
| `/api/demands` | POST | **Créer une demande** | `matiere_id`, `jour` ⭐, `creneau` ⭐, `description` | ✅ |
| `/api/demands` | GET | Lister toutes les demandes | Aucun | ❌ |
| `/api/demands/<demand_id>` | DELETE | Supprimer une demande | ID de demande | ✅ |

⭐ = **Obligatoire et nouve feature**

### **Matching** (`/api/matches`)

| Endpoint | Méthode | Description | Paramètres | Auth |
|----------|---------|-------------|-----------|------|
| `/api/matches/suggestions` | GET | **Lister les candidats** | `demand_id` ⭐ ou `matiere_id` | ✅ |
| `/api/matches/<student_id>/request` | POST | **Envoyer une demande** | Body: `demand_id` ⭐, `score` | ✅ |
| `/api/matches/<matching_id>/accept` | POST | **Accepter un match** | - | ✅ |
| `/api/matches/<matching_id>/reject` | POST | **Refuser un match** | - | ✅ |
| `/api/matches/received` | GET | **Mes demandes reçues** (candidat) | - | ✅ |
| `/api/matches/sent` | GET | **Mes demandes envoyées** (demandeur) | - | ✅ |

⭐ = **Feature avec slots obligatoires**

### **Conversations & Messages** (`/api/conversations`, `/api/messages`)

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/api/conversations` | POST | Créer/récupérer une conversation | ✅ |
| `/api/conversations/<conv_id>/messages` | GET | Lister les messages d'une conversation | ✅ |
| `/api/conversations/<conv_id>/messages` | POST | Envoyer un message | ✅ |
| `/api/polling/messages` | GET | Polling pour nouveaux messages | ✅ |

### **Notifications** (`/api/notifications`)

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/api/notifications` | GET | Lister mes notifications | ✅ |
| `/api/notifications/<notif_id>/read` | PUT | Marquer une notification comme lue | ✅ |

### **Matières** (`/api/matieres`)

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/api/matieres` | GET | Lister toutes les matières | ❌ |

### **Health Check**

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/api/health` | GET | Vérifier le statut du serveur | ❌ |

---

## ⭐ Nouvelle Feature: Matching avec Créneaux Obligatoires

### **Workflow Complet**

```
┌─────────────────────────────────────────────────────────┐
│ 1. DEMANDEUR crée une DEMANDE                          │
│    POST /api/demands                                    │
│    Body: {matiere_id, jour, creneau, description}      │
│    → Demande créée avec slot (ex: Lundi 10-11)         │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 2. DEMANDEUR consulte les SUGGESTIONS                   │
│    GET /api/matches/suggestions?demand_id=X            │
│    → Filtre STRICT: candidats avec créneau Lundi 10-11 │
│                     ET slot pas réservé (is_reserved=0)│
│    → Score sur 100 (matière, niveau, dispos, filière)   │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 3. DEMANDEUR ENVOIE UNE DEMANDE                         │
│    POST /api/matches/<candidate_id>/request            │
│    Body: {demand_id, score}                             │
│    → Vérifie que candidat a Lundi 10-11 disponible     │
│    → Crée Matching(status='pending')                   │
│    → Notifie le candidat                               │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 4. CANDIDAT VOIR LES DEMANDES REÇUES                    │
│    GET /api/matches/received                            │
│    → Affiche jour + creneau pour chaque match           │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 5. CANDIDAT ACCEPTE LE MATCH                            │
│    POST /api/matches/<matching_id>/accept              │
│    → Change status → 'accepted'                         │
│    → RÉSERVE le créneau Lundi 10-11 (is_reserved=1)    │
│    → Crée Conversation automatiquement                 │
│    → Notifie le demandeur                              │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 6. OUVERTURE DE LA DISCUSSION                           │
│    WebSocket: join conversation_id                      │
│    → Échange de messages en temps réel                 │
│    → Messages persistés en base                        │
└─────────────────────────────────────────────────────────┘
```

### **Points Clés**

1. **Demande = Créneau Obligatoire**
   - `jour` et `creneau` sont obligatoires dans `POST /api/demands`
   - Validés par `is_valid_day()` et `is_valid_creneau()`

2. **Matching Strict par Créneau**
   - `GET /api/matches/suggestions?demand_id=X` filtre les candidats
   - Condition : candidat doit avoir `(jour, creneau)` ET `is_reserved=False`
   - Sans `demand_id`, utilise disponibilités du profil

3. **Réservation au Moment de l'Acceptation**
   - `POST /api/matches/<matching_id>/accept`
   - Marque le `Disponible` du candidat comme `is_reserved=True`
   - Empêche d'autres demandeurs d'accéder au même créneau

4. **Visibilité des Slots dans les Réponses**
   - `/api/matches/received` et `/api/matches/sent` incluent `jour` et `creneau`
   - Le demandeur peut voir quel créneau il a demandé

---

## 📊 Modèles de Données

### **User** (`users` table)
```sql
id: INTEGER PRIMARY KEY
email: VARCHAR(120) UNIQUE NOT NULL
password_hash: VARCHAR(255)
role: VARCHAR(20) DEFAULT 'student'
created_at: DATETIME
```

### **Profile** (`profiles` table)
```sql
id: INTEGER PRIMARY KEY
user_id: INTEGER FOREIGN KEY (users.id)
nom: VARCHAR(100)
prenom: VARCHAR(100)
filiere: VARCHAR(50)
niveau: VARCHAR(20)      -- L1, L2, L3
format_preference: VARCHAR(20)  -- présentiel, en_ligne, hybride
bio: TEXT
avatar_url: VARCHAR(255)
telephone: VARCHAR(20)
```

### **Demand** (`demands` table) ⭐ **NEW**
```sql
id: INTEGER PRIMARY KEY
profile_id: INTEGER FOREIGN KEY (profiles.id)
matiere_id: INTEGER FOREIGN KEY (matieres.id)
jour: VARCHAR(15) NOT NULL      -- Lundi, Mardi, etc.
creneau: VARCHAR(10) NOT NULL   -- 10-11, 14-15, etc.
description: TEXT
created_at: DATETIME
```

### **Disponible** (`disponibles` table) ⭐ **UPDATED**
```sql
id: INTEGER PRIMARY KEY
profile_id: INTEGER FOREIGN KEY (profiles.id)
jour: VARCHAR(15) NOT NULL
creneau: VARCHAR(50) NOT NULL
is_reserved: BOOLEAN DEFAULT False  ⭐ NEW FIELD
created_at: DATETIME
```

### **Matching** (`matching` table) ⭐ **UPDATED**
```sql
id: INTEGER PRIMARY KEY
user_one_id: INTEGER FOREIGN KEY (users.id)  -- demandeur
user_two_id: INTEGER FOREIGN KEY (users.id)  -- candidat
initiator_id: INTEGER FOREIGN KEY (users.id)  -- qui a swipé
demand_id: INTEGER FOREIGN KEY (demands.id)  ⭐ NEW FIELD
matiere_id: INTEGER FOREIGN KEY (matieres.id)
status: VARCHAR(20) DEFAULT 'pending'  -- pending/accepted/rejected
score: FLOAT
created_at: DATETIME
UNIQUE(user_one_id, user_two_id, demand_id)
```

### **Conversation** (`conversations` table)
```sql
id: INTEGER PRIMARY KEY
user_one_id: INTEGER FOREIGN KEY (users.id)
user_two_id: INTEGER FOREIGN KEY (users.id)
created_at: DATETIME
```

### **Message** (`messages` table)
```sql
id: INTEGER PRIMARY KEY
conversation_id: INTEGER FOREIGN KEY (conversations.id)
sender_id: INTEGER FOREIGN KEY (users.id)
contenu: TEXT NOT NULL
created_at: DATETIME
```

---

## 🧪 Couverture de Tests

### Nouveaux Tests (6 tests)
- ✅ `test_create_demand_requires_slot` - Valide que jour/creneau sont obligatoires
- ✅ `test_create_demand_with_valid_slot` - Création demande réussie
- ✅ `test_matching_with_demand_id_filters_by_slot` - Filtre strict par créneau
- ✅ `test_request_match_with_demand_checks_candidate_slot_availability` - Vérification disponibilité
- ✅ `test_accept_match_reserves_helper_slot` - Réservation du créneau
- ✅ `test_reserved_slots_excluded_from_future_matching` - Slots réservés exclus

### Tests Existants (29 tests)
- ✅ Auth (inscription, login, réinitialisation)
- ✅ Matching (compatibilité, formats)
- ✅ Profils (compétences, lacunes, disponibilités)
- ✅ Messages et conversations
- ✅ Notifications
- ✅ WebSocket/Socket.IO

**Total**: 35/35 tests passing ✅

---

## 🚀 Démarrage du Serveur

### Développement
```bash
cd backend
python -m flask run --debug
# Le serveur tourne sur http://localhost:5000
```

### Tests
```bash
cd backend
python -m pytest tests/test_backend.py -v
```

### Initialisation de la BD
```bash
cd backend
python init_db.py  # Crée les tables
python check_db.py # Diagnostic
```

---

## 📝 Variables d'Environnement

```bash
FLASK_ENV=development          # ou production
FLASK_APP=app
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-key
DATABASE_URL=sqlite:///ifri.db  # ou postgresql://...
DEBUG=True                       # False en production
```

---

## ⚠️ Limitations Actuelles

1. **Pas de migration DB automatique** - Utiliser `init_db.py` ou Alembic
2. **WebSocket** - Socket.IO en dev mode, adapter pour production
3. **Authentification SMS/Email** - À implémenter
4. **Paiements** - À implémenter
5. **Système de notes** - À implémenter

---

## 🔜 Prochaines Étapes

- [ ] Interface frontend pour visualiser le workflow complet
- [ ] Tests UI intégrés (Playwright/Cypress)
- [ ] Migrations de BD avec Alembic
- [ ] Déploiement production (Gunicorn + Nginx)
- [ ] Ajout du système de notes/avis
- [ ] Fonction de search/filtres avancés

---

## 📞 Contact & Support

Pour des questions sur l'architecture ou le backend :
- Architecture: Conforme au PDF "IFRI_Mentorlink_Vision_du_Système_de_Matching.pdf"
- Schéma: Voir [database/schema.sql](database/schema.sql)
