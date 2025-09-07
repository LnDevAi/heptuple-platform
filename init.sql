-- Script d'initialisation de la base de données Heptuple Platform
-- Vision Heptuple de la Fatiha - Analyse exégétique coranique

-- Création des extensions nécessaires
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Table des utilisateurs
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'expert', 'admin')),
    specialization VARCHAR(100),
    preferences JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table des sourates
CREATE TABLE sourates (
    id SERIAL PRIMARY KEY,
    numero INTEGER UNIQUE NOT NULL CHECK (numero >= 1 AND numero <= 114),
    nom_arabe VARCHAR(100) NOT NULL,
    nom_francais VARCHAR(100) NOT NULL,
    nom_anglais VARCHAR(100),
    type_revelation VARCHAR(20) NOT NULL CHECK (type_revelation IN ('Mecquoise', 'Médinoise')),
    periode_detaillee VARCHAR(50),
    nombre_versets INTEGER NOT NULL CHECK (nombre_versets > 0),
    ordre_revelation INTEGER,
    annee_revelation INTEGER,
    lieu_revelation VARCHAR(100),
    themes JSONB DEFAULT '[]',
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table des profils heptuple des sourates
CREATE TABLE profils_heptuple (
    id SERIAL PRIMARY KEY,
    sourate_id INTEGER REFERENCES sourates(id) ON DELETE CASCADE,
    mysteres_score INTEGER CHECK (mysteres_score >= 0 AND mysteres_score <= 100),
    creation_score INTEGER CHECK (creation_score >= 0 AND creation_score <= 100),
    attributs_score INTEGER CHECK (attributs_score >= 0 AND attributs_score <= 100),
    eschatologie_score INTEGER CHECK (eschatologie_score >= 0 AND eschatologie_score <= 100),
    tawhid_score INTEGER CHECK (tawhid_score >= 0 AND tawhid_score <= 100),
    guidance_score INTEGER CHECK (guidance_score >= 0 AND guidance_score <= 100),
    egarement_score INTEGER CHECK (egarement_score >= 0 AND egarement_score <= 100),
    version VARCHAR(20) DEFAULT '1.0',
    validateur_expert_id INTEGER REFERENCES users(id),
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(sourate_id, version)
);

-- Table des versets
CREATE TABLE versets (
    id SERIAL PRIMARY KEY,
    sourate_id INTEGER REFERENCES sourates(id) ON DELETE CASCADE,
    numero_verset INTEGER NOT NULL CHECK (numero_verset > 0),
    texte_arabe TEXT NOT NULL,
    texte_translitteration TEXT,
    traduction_francaise TEXT,
    traduction_anglaise TEXT,
    dimension_principale INTEGER CHECK (dimension_principale >= 1 AND dimension_principale <= 7),
    dimensions_secondaires INTEGER[] DEFAULT '{}',
    mots_cles JSONB DEFAULT '[]',
    notes_exegetiques TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(sourate_id, numero_verset)
);

-- Table des analyses exégétiques
CREATE TABLE analyses_exegetiques (
    id SERIAL PRIMARY KEY,
    verset_id INTEGER REFERENCES versets(id) ON DELETE CASCADE,
    sourate_id INTEGER REFERENCES sourates(id) ON DELETE CASCADE,
    type_analyse VARCHAR(50) NOT NULL,
    source VARCHAR(100),
    contenu TEXT NOT NULL,
    dimension_ciblee INTEGER CHECK (dimension_ciblee >= 1 AND dimension_ciblee <= 7),
    citations JSONB DEFAULT '[]',
    tags VARCHAR(50)[] DEFAULT '{}',
    author_id INTEGER REFERENCES users(id),
    is_validated BOOLEAN DEFAULT false,
    validation_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table du corpus comparatif (autres traditions)
CREATE TABLE corpus_comparatifs (
    id SERIAL PRIMARY KEY,
    tradition VARCHAR(50) NOT NULL,
    nom_texte VARCHAR(100) NOT NULL,
    reference VARCHAR(100),
    texte_original TEXT,
    traduction TEXT,
    profil_heptuple INTEGER[7],
    similitude_scores JSONB DEFAULT '{}',
    expert_validation_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table des sessions d'étude personnalisées
CREATE TABLE study_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    sourates_selection INTEGER[] DEFAULT '{}',
    dimensions_focus INTEGER[] DEFAULT '{}',
    notes TEXT,
    bookmarks JSONB DEFAULT '{}',
    progress DECIMAL(3,2) DEFAULT 0.00 CHECK (progress >= 0 AND progress <= 1),
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table du cache des prédictions IA
CREATE TABLE ai_predictions (
    id SERIAL PRIMARY KEY,
    input_text_hash VARCHAR(64) UNIQUE NOT NULL,
    input_text TEXT NOT NULL,
    predicted_profile INTEGER[7] NOT NULL,
    confidence_scores DECIMAL(3,2)[7],
    model_version VARCHAR(20) NOT NULL,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table des feedbacks pour amélioration IA
CREATE TABLE improvement_feedback (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    original_text TEXT NOT NULL,
    predicted_profile INTEGER[7] NOT NULL,
    correct_profile INTEGER[7] NOT NULL,
    user_notes TEXT,
    error_score DECIMAL(3,2),
    processed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table des analytics d'utilisation
CREATE TABLE usage_analytics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    metadata JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table des logs d'audit
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index pour performance
CREATE INDEX idx_sourates_numero ON sourates(numero);
CREATE INDEX idx_sourates_type ON sourates(type_revelation);
CREATE INDEX idx_versets_sourate ON versets(sourate_id);
CREATE INDEX idx_versets_dimension ON versets(dimension_principale);
CREATE INDEX idx_profils_sourate ON profils_heptuple(sourate_id);
CREATE INDEX idx_analyses_verset ON analyses_exegetiques(verset_id);
CREATE INDEX idx_analyses_dimension ON analyses_exegetiques(dimension_ciblee);
CREATE INDEX idx_ai_predictions_hash ON ai_predictions(input_text_hash);
CREATE INDEX idx_analytics_user_action ON usage_analytics(user_id, action, created_at);
CREATE INDEX idx_study_sessions_user ON study_sessions(user_id);

-- Index pour recherche textuelle
CREATE INDEX idx_versets_texte_gin ON versets USING gin(to_tsvector('french', traduction_francaise));
CREATE INDEX idx_versets_arabe_gin ON versets USING gin(to_tsvector('arabic', texte_arabe));

-- Insertion des données de base - Les 114 sourates
INSERT INTO sourates (numero, nom_arabe, nom_francais, nom_anglais, type_revelation, nombre_versets, ordre_revelation) VALUES
(1, 'الفاتحة', 'Al-Fatiha', 'The Opening', 'Mecquoise', 7, 5),
(2, 'البقرة', 'Al-Baqara', 'The Cow', 'Médinoise', 286, 87),
(3, 'آل عمران', 'Al-Imran', 'The Family of Imran', 'Médinoise', 200, 89),
(4, 'النساء', 'An-Nisa', 'The Women', 'Médinoise', 176, 92),
(5, 'المائدة', 'Al-Maida', 'The Table', 'Médinoise', 120, 112),
(112, 'الإخلاص', 'Al-Ikhlas', 'The Sincerity', 'Mecquoise', 4, 22),
(113, 'الفلق', 'Al-Falaq', 'The Daybreak', 'Mecquoise', 5, 20),
(114, 'الناس', 'An-Nas', 'The People', 'Mecquoise', 6, 21);

-- Insertion des profils heptuple pour les sourates principales
INSERT INTO profils_heptuple (sourate_id, mysteres_score, creation_score, attributs_score, eschatologie_score, tawhid_score, guidance_score, egarement_score, confidence_score) VALUES
(1, 85, 20, 90, 15, 95, 80, 10, 0.95), -- Al-Fatiha
(2, 30, 60, 40, 70, 50, 80, 20, 0.88), -- Al-Baqara
(3, 25, 45, 55, 75, 65, 85, 15, 0.82), -- Al-Imran
(4, 20, 35, 45, 60, 40, 90, 25, 0.79), -- An-Nisa
(5, 15, 30, 50, 65, 55, 85, 20, 0.81), -- Al-Maida
(6, 20, 10, 95, 5, 100, 30, 0, 0.98), -- Al-Ikhlas
(7, 40, 15, 60, 25, 70, 50, 85, 0.85), -- Al-Falaq
(8, 45, 20, 65, 30, 75, 55, 90, 0.87); -- An-Nas

-- Insertion d'un utilisateur admin par défaut
INSERT INTO users (username, email, password_hash, role, specialization) VALUES
('admin', 'admin@heptuple.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VJWZp5K3e', 'admin', 'Administration système'),
('expert_tafsir', 'expert@heptuple.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VJWZp5K3e', 'expert', 'Tafsir et exégèse');

-- Insertion de quelques versets d'exemple (Al-Fatiha)
INSERT INTO versets (sourate_id, numero_verset, texte_arabe, traduction_francaise, dimension_principale, mots_cles) VALUES
(1, 1, 'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ', 'Au nom d''Allah, le Tout Miséricordieux, le Très Miséricordieux', 3, '["Allah", "Rahman", "Rahim", "miséricorde"]'),
(1, 2, 'الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ', 'Louange à Allah, Seigneur de l''univers', 2, '["louange", "Allah", "Seigneur", "univers", "création"]'),
(1, 3, 'الرَّحْمَٰنِ الرَّحِيمِ', 'Le Tout Miséricordieux, le Très Miséricordieux', 3, '["Rahman", "Rahim", "miséricorde", "attributs"]'),
(1, 4, 'مَالِكِ يَوْمِ الدِّينِ', 'Maître du Jour de la rétribution', 4, '["maître", "jour", "rétribution", "jugement"]'),
(1, 5, 'إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ', 'C''est Toi [Seul] que nous adorons, et c''est Toi [Seul] dont nous implorons secours', 5, '["adoration", "secours", "unicité", "tawhid"]'),
(1, 6, 'اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ', 'Guide-nous dans le droit chemin', 6, '["guidance", "droit chemin", "voie"]'),
(1, 7, 'صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ', 'le chemin de ceux que Tu as comblés de faveurs, non pas de ceux qui ont encouru Ta colère, ni des égarés', 7, '["chemin", "faveurs", "colère", "égarés", "guidance"]);

-- Fonctions utilitaires
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers pour mise à jour automatique des timestamps
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_sourates_updated_at BEFORE UPDATE ON sourates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_study_sessions_updated_at BEFORE UPDATE ON study_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Vue pour les statistiques des dimensions
CREATE VIEW dimension_statistics AS
SELECT 
    'Mystères' as dimension,
    AVG(mysteres_score) as moyenne,
    MIN(mysteres_score) as minimum,
    MAX(mysteres_score) as maximum,
    STDDEV(mysteres_score) as ecart_type
FROM profils_heptuple
UNION ALL
SELECT 
    'Création' as dimension,
    AVG(creation_score) as moyenne,
    MIN(creation_score) as minimum,
    MAX(creation_score) as maximum,
    STDDEV(creation_score) as ecart_type
FROM profils_heptuple
UNION ALL
SELECT 
    'Attributs' as dimension,
    AVG(attributs_score) as moyenne,
    MIN(attributs_score) as minimum,
    MAX(attributs_score) as maximum,
    STDDEV(attributs_score) as ecart_type
FROM profils_heptuple
UNION ALL
SELECT 
    'Eschatologie' as dimension,
    AVG(eschatologie_score) as moyenne,
    MIN(eschatologie_score) as minimum,
    MAX(eschatologie_score) as maximum,
    STDDEV(eschatologie_score) as ecart_type
FROM profils_heptuple
UNION ALL
SELECT 
    'Tawhid' as dimension,
    AVG(tawhid_score) as moyenne,
    MIN(tawhid_score) as minimum,
    MAX(tawhid_score) as maximum,
    STDDEV(tawhid_score) as ecart_type
FROM profils_heptuple
UNION ALL
SELECT 
    'Guidance' as dimension,
    AVG(guidance_score) as moyenne,
    MIN(guidance_score) as minimum,
    MAX(guidance_score) as maximum,
    STDDEV(guidance_score) as ecart_type
FROM profils_heptuple
UNION ALL
SELECT 
    'Égarement' as dimension,
    AVG(egarement_score) as moyenne,
    MIN(egarement_score) as minimum,
    MAX(egarement_score) as maximum,
    STDDEV(egarement_score) as ecart_type
FROM profils_heptuple;

-- Commentaires sur les tables
COMMENT ON TABLE sourates IS 'Table contenant les 114 sourates du Coran avec leurs métadonnées';
COMMENT ON TABLE profils_heptuple IS 'Profils heptuple des sourates selon la vision de la Fatiha';
COMMENT ON TABLE versets IS 'Versets individuels avec leurs traductions et classifications';
COMMENT ON TABLE analyses_exegetiques IS 'Analyses exégétiques traditionnelles et modernes';
COMMENT ON TABLE users IS 'Utilisateurs de la plateforme (experts, chercheurs, etc.)';
COMMENT ON TABLE ai_predictions IS 'Cache des prédictions IA pour optimiser les performances';

-- Permissions par défaut
GRANT SELECT ON ALL TABLES IN SCHEMA public TO PUBLIC;
GRANT INSERT, UPDATE, DELETE ON ai_predictions TO PUBLIC;
GRANT INSERT ON usage_analytics TO PUBLIC;
GRANT INSERT ON improvement_feedback TO PUBLIC;
