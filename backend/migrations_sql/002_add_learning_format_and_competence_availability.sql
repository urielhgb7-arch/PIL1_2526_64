-- Migration 002: add learning format preference and implicit competence offer availability

ALTER TABLE profiles
ADD COLUMN format_preference VARCHAR(20) NOT NULL DEFAULT 'hybride';

ALTER TABLE profil_competences
ADD COLUMN is_available_to_help BOOLEAN NOT NULL DEFAULT TRUE;
