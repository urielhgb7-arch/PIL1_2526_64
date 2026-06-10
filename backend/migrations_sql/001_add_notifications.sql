-- Migration: Add notifications table
-- Review and run manually or convert to Alembic migration.

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    titre TEXT NOT NULL,
    contenu TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'system',
    read INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- OPTIONAL: archive and drop offers (UNCOMMENT after backup)
-- -- Archive offers
-- CREATE TABLE IF NOT EXISTS offers_archive AS SELECT * FROM offers;
-- -- Drop original offers table
-- DROP TABLE IF EXISTS offers;
