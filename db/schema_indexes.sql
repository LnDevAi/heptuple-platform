-- Indexes and constraints for performance and integrity

-- HADITHS
CREATE INDEX IF NOT EXISTS idx_hadiths_recueil ON hadiths (recueil);
CREATE INDEX IF NOT EXISTS idx_hadiths_authenticite ON hadiths (degre_authenticite);
CREATE INDEX IF NOT EXISTS idx_hadiths_dim ON hadiths (dimension_heptuple);
CREATE INDEX IF NOT EXISTS idx_hadiths_mots_cles ON hadiths USING GIN (mots_cles);
CREATE INDEX IF NOT EXISTS idx_hadiths_themes ON hadiths USING GIN (themes);
CREATE INDEX IF NOT EXISTS idx_hadiths_fr_trgm ON hadiths USING GIN (texte_francais gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_hadiths_ar_trgm ON hadiths USING GIN (texte_arabe gin_trgm_ops);

-- FIQH RULINGS
CREATE INDEX IF NOT EXISTS idx_fiqh_rite ON fiqh_rulings (rite);
CREATE INDEX IF NOT EXISTS idx_fiqh_topic_trgm ON fiqh_rulings USING GIN (topic gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_fiqh_question_trgm ON fiqh_rulings USING GIN (question gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_fiqh_ruling_text_trgm ON fiqh_rulings USING GIN (ruling_text gin_trgm_ops);

-- INVOCATIONS
CREATE INDEX IF NOT EXISTS idx_invocations_titre_trgm ON invocations USING GIN (titre gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_invocations_ar_trgm ON invocations USING GIN (texte_arabe gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_invocations_tr_trgm ON invocations USING GIN (texte_traduit gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_invocations_categories ON invocations USING GIN (categories);
CREATE INDEX IF NOT EXISTS idx_invocations_tags ON invocations USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_invocations_temps ON invocations USING GIN (temps_recommande);
