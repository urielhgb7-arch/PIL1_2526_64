# Notifications — modèle et usage

Objectif
-------
Documenter le modèle `Notification` attendu, ses champs, son rôle et les usages côté backend et frontend.

Contexte
-------
Le système de matching crée des notifications pour informer les utilisateurs lors de:
- réception d'une demande d'accompagnement
- acceptation d'une demande
- refus d'une demande

La codebase actuelle émet des instances `Notification(...)` depuis `matching.py`. Pour éviter des erreurs d'importation et clarifier le comportement, voici la spécification recommandée.

Modèle SQL attendu
-----------------
Table: `notifications`

- `id` INT PRIMARY KEY AUTOINCREMENT
- `user_id` INT NOT NULL  -- destinataire (FK -> users.id)
- `titre` TEXT NOT NULL
- `contenu` TEXT NOT NULL
- `type` TEXT NOT NULL DEFAULT 'system'  -- ex: 'match_system', 'message', 'info'
- `read` BOOLEAN NOT NULL DEFAULT 0
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

Comportement attendu
---------------------
- Lorsqu'un événement pertinent (ex: nouvelle demande) est créé, le backend ajoute une `Notification` pointant sur le `user_id` destinataire.
- Les notifications sont immuables sauf pour la colonne `read` qui peut être mise à `true` lorsque l'utilisateur les consulte.
- Endpoint REST minimal:
  - `GET /api/notifications` → liste des notifications pour l'utilisateur courant (paged)
  - `PUT /api/notifications/{id}/read` → marquer comme lue

Exemple d'utilisation (backend)
-------------------------------
```py
notif = Notification(
    user_id=recipient_id,
    titre="Nouvelle demande d'accompagnement",
    contenu=f"{prenom} {nom} souhaite votre aide.",
    type='match_system'
)
db.session.add(notif)
db.session.commit()
```

Exemple d'utilisation (frontend)
--------------------------------
- Appeler `GET /api/notifications` pour afficher la cloche et le listing.
- Appeler `PUT /api/notifications/{id}/read` lors de l'ouverture.

Notes opérationnelles
---------------------
- Si la table `notifications` n'existe pas dans la base, provisionner la migration (voir `backend/migrations/001_add_notifications.sql`).
- Si vous préférez une solution push (WebSocket), conservez quand même la table pour persistance historique.

Décision recommandée
---------------------
- Implémenter le modèle `Notification` tel que décrit. Ne pas supprimer `Offer` automatiquement : vérifier les données historiques avant toute suppression.
