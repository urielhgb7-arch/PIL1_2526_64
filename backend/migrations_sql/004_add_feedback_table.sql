-- Migration 004: Add feedbacks table for user ratings
-- Run manually after applying ORM changes: db.create_all()

CREATE TABLE IF NOT EXISTS feedbacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_user_id INTEGER NOT NULL,
    to_user_id INTEGER NOT NULL,
    matching_id INTEGER NOT NULL,
    note INTEGER NOT NULL CHECK(note >= 1 AND note <= 5),
    commentaire TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_user_id) REFERENCES users(id),
    FOREIGN KEY (to_user_id) REFERENCES users(id),
    FOREIGN KEY (matching_id) REFERENCES matching(id),
    UNIQUE(from_user_id, matching_id)
);
