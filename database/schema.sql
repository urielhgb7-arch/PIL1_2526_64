-- ============================================================================
-- ROADMAP : CONTEXTE BASE DE DONNÉES - PROJET IFRI MENTORLINK
-- ============================================================================

-- Suppression ordonnée des tables si elles existent (pour les réinitialisations de test)
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS matching CASCADE;
DROP TABLE IF EXISTS profil_lacunes CASCADE;
DROP TABLE IF EXISTS profil_competences CASCADE;
DROP TABLE IF EXISTS disponibilites CASCADE;
DROP TABLE IF EXISTS offers CASCADE;
DROP TABLE IF EXISTS demands CASCADE;
DROP TABLE IF EXISTS matieres CASCADE;
DROP TABLE IF EXISTS profiles CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ----------------------------------------------------------------------------
-- 1. AUTHENTIFICATION & SÉCURITÉ
-- ----------------------------------------------------------------------------
-- Rôle 'student' par défaut pour permettre la double casquette Mentor/Mentoré
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 2. PROFILS UTILISATEURS (IFRI)
-- ----------------------------------------------------------------------------
CREATE TABLE profiles (
    id SERIAL PRIMARY KEY,
    user_id INT UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    filiere VARCHAR(50) NOT NULL, -- ex: GL (Génie Logiciel), RSI, etc.
    niveau VARCHAR(10) NOT NULL,  -- ex: L1, L2, L3, M1, M2
    bio TEXT,
    telephone VARCHAR(20),
    avatar_url TEXT DEFAULT 'https://via.placeholder.com/150',
    disponible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 3. DISPONIBILITÉS (Agenda d'étude indexé par bloc d'une heure)
-- ----------------------------------------------------------------------------
CREATE TABLE disponibilites (
    id SERIAL PRIMARY KEY,
    profile_id INT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    jour VARCHAR(15) NOT NULL CHECK (
        jour IN ('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche')
    ), 
    creneau VARCHAR(10) NOT NULL CHECK (
        creneau IN (
            '08-09', '09-10', '10-11', '11-12', -- Matinée
            '12-13', '13-14',                   -- Pause déjeuner
            '14-15', '15-16', '16-17', '17-18', -- Après-midi
            '18-19', '19-20', '20-21'           -- Soirée
        )
    )
);

-- ----------------------------------------------------------------------------
-- 4. RÉFÉRENTIEL DES MATIÈRES (IFRI)
-- ----------------------------------------------------------------------------
CREATE TABLE matieres (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL
);

-- ----------------------------------------------------------------------------
-- 5. PROFILING & CRITÈRES DE MATCHING (Compétences vs Lacunes)
-- ----------------------------------------------------------------------------
-- Table de jointure Many-to-Many pour les points forts (Mentorat potentiel)
CREATE TABLE profil_competences (
    profile_id INT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    matiere_id INT NOT NULL REFERENCES matieres(id) ON DELETE CASCADE,
    niveau VARCHAR(20) DEFAULT 'Intermédiaire' CHECK (niveau IN ('Débutant', 'Intermédiaire', 'Avancé', 'Expert')),
    PRIMARY KEY (profile_id, matiere_id)
);

-- Table de jointure Many-to-Many pour les points faibles (Besoins d'aide)
CREATE TABLE profil_lacunes (
    profile_id INT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    matiere_id INT NOT NULL REFERENCES matieres(id) ON DELETE CASCADE,
    priorite VARCHAR(20) DEFAULT 'Moyenne' CHECK (priorite IN ('Basse', 'Moyenne', 'Haute', 'Urgente')),
    PRIMARY KEY (profile_id, matiere_id)
);

-- ----------------------------------------------------------------------------
-- 6. PUBLICATIONS & SYSTÈME D'ANNONCES PONCTUELLES
-- ----------------------------------------------------------------------------
-- Offres explicites formulées par les Mentors
CREATE TABLE offers (
    id SERIAL PRIMARY KEY,
    profile_id INT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    matiere_id INT NOT NULL REFERENCES matieres(id) ON DELETE CASCADE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Demandes explicites formulées par les Mentorés
CREATE TABLE demands (
    id SERIAL PRIMARY KEY,
    profile_id INT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    matiere_id INT NOT NULL REFERENCES matieres(id) ON DELETE CASCADE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 7. MATCHING (F2 & B2)
-- ----------------------------------------------------------------------------
CREATE TABLE matching (
    id SERIAL PRIMARY KEY,
    user_one_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_two_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    initiator_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE, -- Qui a initié le match
    matiere_id INT NOT NULL REFERENCES matieres(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected')),
    score FLOAT NOT NULL, -- Score de compatibilité calculé par l'algorithme de matching
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_one_id, user_two_id, matiere_id)
);

-- ----------------------------------------------------------------------------
-- 8. MESSAGERIE (F2 & B2)
-- ----------------------------------------------------------------------------
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_one_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_two_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_pair UNIQUE (user_one_id, user_two_id)
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    contenu TEXT NOT NULL,
    date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 9. EXPÉRIENCE TEMPS RÉEL (Notifications historiques)
-- ----------------------------------------------------------------------------
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    titre VARCHAR(100) NOT NULL, 
    contenu TEXT NOT NULL,
    type VARCHAR(30) NOT NULL, -- 'message', 'match_system', 'alert'
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================================
-- INITIALISATION DES DONNÉES (Pour les tests de l'équipe Backend & Frontend)
-- ============================================================================

-- Injection des matières officielles de l'IFRI
INSERT INTO matieres (nom) VALUES 
('Algorithmique'), 
('Architecture des ordinateurs'), 
('Base de données (SQL)'), 
('Programmation Web (HTML/CSS/JS)'), 
('Réseaux et Télécoms'), 
('Système d''exploitation Linux'), 
('Génie Logiciel'),
('Anglais Technique');