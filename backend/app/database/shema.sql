-- Suppression des tables si elles existent (pour les réinitialisations de test)
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS profile_competences CASCADE;
DROP TABLE IF EXISTS disponibilites CASCADE;
DROP TABLE IF EXISTS offers CASCADE;
DROP TABLE IF EXISTS demands CASCADE;
DROP TABLE IF EXISTS profiles CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 1. Table des Utilisateurs (Authentification)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('mentor', 'mentore', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Table des Profils détaillés
CREATE TABLE profiles (
    id SERIAL PRIMARY KEY,
    user_id INT UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    filiere VARCHAR(50) NOT NULL, -- GL, RSI, etc.
    niveau VARCHAR(10) NOT NULL,  -- L1, L2, L3
    bio TEXT,
    telephone VARCHAR(20),
    avatar_url TEXT DEFAULT 'https://via.placeholder.com/150',
    disponible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Table des Disponibilités (Agenda d'étude)
-- 3. Table des Disponibilités (Approche B : Créneaux de 1h indexés)
CREATE TABLE disponibilites (
    id SERIAL PRIMARY KEY,
    profile_id INT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    
    -- Contrainte pour bloquer uniquement les vrais jours de la semaine
    jour VARCHAR(15) NOT NULL CHECK (
        jour IN ('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche')
    ), 
    
    -- Contrainte CHECK pour valider UNIQUEMENT les blocs stricts de 1h à l'IFRI
    creneau VARCHAR(10) NOT NULL CHECK (
        creneau IN (
            '08-09', '09-10', '10-11', '11-12', -- Créneaux de la matinée
            '12-13', '13-14',                   -- Pause déjeuner / milieu de journée
            '14-15', '15-16', '16-17', '17-18', -- Créneaux de l'après-midi
            '18-19', '19-20' ,'20-21'                    -- Créneaux du soir
        )
    )
);

-- 4. Table des Offres de Mentorat (Ce que les Mentors maîtrisent)
CREATE TABLE offers (
    id SERIAL PRIMARY KEY,
    profile_id INT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    matiere VARCHAR(100) NOT NULL, -- ex: Algorithmique, Base de données
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Table des Demandes d'aide (Ce que les Mentorés recherchent)
CREATE TABLE demands (
    id SERIAL PRIMARY KEY,
    profile_id INT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    matiere VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Table des Conversations
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_one_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_two_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_pair UNIQUE (user_one_id, user_two_id)
);

-- 7. Table des Messages
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    contenu TEXT NOT NULL,
    date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);