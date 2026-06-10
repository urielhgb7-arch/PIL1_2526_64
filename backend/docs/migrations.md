# Guide de migrations (Alembic / SQL)

But
---
Fournir une procédure sûre pour ajouter la table `notifications` et, si souhaité, supprimer la table `offers` après archivage.

Prérequis
---------
- Installer `alembic` dans l'environnement : `pip install alembic`
- Initialiser Alembic dans `backend/` si ce n'est pas fait :

```bash
cd backend
alembic init migrations
```

Procédure recommandée
---------------------
1. S'assurer d'avoir une sauvegarde de la base de données (dump) avant toute migration destructive.
2. Créer une migration Alembic pour ajouter `notifications` :

```bash
alembic revision -m "add notifications table" --autogenerate
alembic upgrade head
```

3. Pour supprimer `offers` :
   - Créer une migration séparée qui **archive** les données (INSERT INTO archive_offers SELECT * FROM offers) puis supprime la table.
   - Ne pas appliquer la migration de suppression sans validation en staging.

SQL de migration exemple
------------------------
Voir `backend/migrations/001_add_notifications.sql` pour un script prêt à exécuter si vous n'utilisez pas Alembic.

Bonnes pratiques
----------------
- Faire une migration par changement logique (ajout table, modification index, etc.).
- Ajouter des tests d'intégration qui exécutent les migrations sur une base de test.
- Documenter chaque migration dans le changelog de release.
