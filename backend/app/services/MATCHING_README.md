# Algorithme de Matching - MentorLink

## Vue d'ensemble

L'algorithme de matching met en relation des etudiants ayant des **lacunes** (besoins d'aide) avec des etudiants **competents** (pouvant aider) sur les memes matieres. Le score est calcule sur **100 points** en combinant 7 criteres.

Fichier principal : `backend/app/services/matching.py`

---

## Score total (sur 100)

```
score = min(100, matiere + niveau_vs_gravite + disponibilites + meme_niveau + meme_filiere + format_preference + penalite_rejet)
```

| Critere               | Max | Description |
|------------------------|-----|-------------|
| Matiere               | 35  | Correspondance sur la matiere demandee |
| Niveau vs Gravite     | 20  | Rapport competence / urgence de la lacune |
| Disponibilites        | 25  | Creneaux horaires en commun |
| Meme niveau academique| 10  | Meme annee d'etude (L1-L3, M1-M2) |
| Meme filiere          | 10  | Meme filiere (GL, RSI, MIAGE, etc.) |
| Format preference     | 10  | Meme format d'apprentissage |
| Penalite rejet        | -5  | Si l'aidant a deja ete rejete par le demandeur |
| **Total**             | **100** | |

### Seuil et limite

- **Score minimum** : 55/100 - les candidats en dessous sont exclus
- **Nombre maximum** : 50 resultats - seuls les 50 meilleurs sont renvoyes

---

## Details des criteres

### 1. Matiere (35 pts)

- **Mode general** (`calculate_matches_general`) : 35 pts multiplie par le ratio (matieres matchées / total lacunes). Exemple : 2 lacunes sur 3 matchées → 35 x 2/3 = 23.33 pts
- **Mode demande** (`calculate_matches_demand`) : 35 pts si le candidat est competent sur la matiere exacte de la demande, 10 pts s'il a d'autres competences mais pas celle-ci

### 2. Niveau vs Gravite (20 pts)

Rapport entre le niveau de competence et la priorite de la lacune :

```
niveaux = { 'Debutant': 1, 'Intermediaire': 2, 'Avance': 3, 'Expert': 4 }
lacunes = { 'Basse': 1, 'Moyenne': 2, 'Haute': 3, 'Urgente': 4 }

ratio = min(niveau / priorite, 1.0)
score = ratio * 20
```

Un expert (4) sur une lacune urgente (4) → 20 pts. Un debutant (1) sur une lacune haute (3) → 6.67 pts.

### 3. Disponibilites (25 pts)

Fraction des creneaux de la demande couverts par le candidat :

```
score = min(creneaux_communs / total_creneaux_demande, 1.0) * 25
```

Si aucun creneau en commun → le candidat est exclu du resultat (pour le mode demande).

### 4. Meme niveau academique (10 pts)

10 pts si le candidat est dans la meme annee d'etude (L1, L2, L3, M1, M2).

### 5. Meme filiere (10 pts)

10 pts si le candidat est dans la meme filiere (GL, RSI, MIAGE, etc.).

### 6. Format preference (10 pts)

10 pts si les deux etudiants preferent le meme format d'apprentissage (presentiel, distanciel, hybride).

### 7. Penalite rejet (-5 pts)

-5 pts si l'aidant a deja ete rejete par le demandeur dans un matching precedent.

---

## Deux modes de matching

### Mode general (`calculate_matches_general`)

Appele lorsque l'utilisateur demande des suggestions sans cibler une demande specifique.

1. Recupere toutes les lacunes de l'utilisateur
2. Trouve les etudiants competents sur au moins une de ces matieres
3. Calcule le score pour chaque candidat
4. Retourne les 50 meilleurs candidats scores >= 55

### Mode demande (`calculate_matches_demand`)

Appele lorsqu'un utilisateur cible une demande specifique (offre d'aide).

1. Verifie que la demande appartient bien a l'utilisateur
2. Filtre sur la matiere exacte de la demande (35 pts si matiere correspond, 10 pts sinon)
3. Exclut les candidats sans creneau disponible correspondant au creneau de la demande
4. Calcule le score pour chaque candidat restant
5. Retourne les 50 meilleurs

---

## Optimisation N+1

Pour eviter une explosion de requetes SQL (une requete par candidat), l'algorithme pre-charge toutes les donnees en **3 requetes massives** avant la boucle de scoring :

1. **Utilisateurs** : `User.query.filter(User.id.in_(candidate_user_ids)).all()` → stockes dans `users_map`
2. **Competences** : `ProfilCompetence.query.filter(ProfilCompetence.profile_id.in_(candidate_ids), ...).all()` → stockes dans `competences_map`
3. **Disponibilites** : `Disponible.query.filter(Disponible.profile_id.in_(candidate_ids), ...).all()` → stockes dans `dispos_map`

La boucle principale n'effectue **aucune requete DB** par candidat - elle consulte uniquement les dictionnaires pre-charges.

---

## Exclusions et blocages

L'algorithme exclut automatiquement les utilisateurs suivants :

- L'utilisateur lui-meme
- Les utilisateurs deja en relation de matching (status `pending` ou `accepted`)
- Les utilisateurs que le demandeur a deja rejetes (status `rejected` avec `initiator_id = current_user_id`)
- Les utilisateurs sans competence active (`is_available_to_help = False`)
- Les utilisateurs sans creneau disponible correspondant (mode demande)

Les utilisateurs qui ont rejete le demandeur ne sont pas bloques mais recoivent une penalite de -5 pts.

---

## Reservations de creneaux

Quand un matching est accepte, le creneau de l'aidant est marque `is_reserved = True`. Il n'apparait plus dans les futures suggestions (filtre `is_reserved = False` dans les requetes de disponibilites).

---

## Structure des donnees retournees

Chaque candidat est retourne avec la structure suivante :

```json
{
  "student_id": 1,
  "profile_id": 1,
  "nom": "Dupont",
  "prenom": "Jean",
  "filiere": "GL",
  "niveau": "L3",
  "avatar_url": "...",
  "bio": "...",
  "format_preference": "hybride",
  "score": 85.5,
  "matched_subjects": [
    {
      "matiere_id": 1,
      "nom": "Algorithmique",
      "niveau_competence": "Avance",
      "priorite_lacune": "Haute"
    }
  ],
  "competences": [
    {
      "matiere_id": 1,
      "nom": "Algorithmique",
      "niveau": "Avance"
    }
  ],
  "shared_slots": [
    { "jour": "Lundi", "creneau": "08h-10h" }
  ],
  "explication": {
    "score_pct": "85.5%",
    "raisons": [
      "Competent en Algorithmique (niveau Avance)",
      "2 creneau(x) disponible(s) en commun",
      "Meme filiere",
      "Meme annee academique",
      "Meme format d'apprentissage"
    ]
  },
  "score_detail": {
    "matiere": 35,
    "niveau_vs_gravite": 15.5,
    "disponibilites": 25,
    "meme_niveau": 10,
    "meme_filiere": 10,
    "format_preference": 10,
    "penalite_rejet": 0
  },
  "rejected_before": false
}
```

---

## Fonctions de reference

| Fonction | Role |
|----------|------|
| `_score_niveau_vs_gravite(niveau, priorite)` | Calcule le score de competence vs urgence (0-20) |
| `_score_disponibilites(demand_slots, candidate_slots)` | Calcule le score de disponibilites (0-25) |
| `_score_format_bonus(format1, format2)` | Calcule le bonus de format (0 ou 10) |
| `_build_explanation(...)` | Construit le message d'explication du score |
| `_get_excluded_user_ids(user_id)` | Recupere les IDs bloques et rejetes |
| `_make_candidate_result(...)` | Cree l'objet JSON de resultat pour un candidat |
| `_limit_results(results)` | Filtre (score >= 55) et limite (50 max) les resultats |
| `calculate_matches_general(user_id, matiere_id)` | Mode general - suggestions basees sur les lacunes |
| `calculate_matches_demand(user_id, demand_id)` | Mode demande - suggestions pour une demande specifique |
| `calculate_matches(user_id, matiere_id, demand_id)` | Point d'entree unique, dispatche vers le bon mode |

---

## Tests

Les tests de l'algorithme se trouvent dans :

- `backend/tests/test_backend.py` : tests de matching (suggestions, compatibilite, format, disponibilites)
- `backend/tests/test_matching.py` : tests de creation de conversation suite a un matching
- `backend/tests/test_offers.py` : tests de matching via offres/demandes

Lancer les tests :

```bash
cd backend
python -m pytest tests/ -v
```
