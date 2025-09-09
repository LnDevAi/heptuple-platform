-- CSV ingestion script (PostgreSQL). Adjust paths as needed.
-- Requires: arrays in CSV as Postgres array literal (e.g. "{a,b}") and UTF-8 encoding.

\copy hadiths (numero_hadith, recueil, livre, chapitre, texte_arabe, texte_francais, narrateur, degre_authenticite, dimension_heptuple, mots_cles, themes, contexte_historique)
FROM '/opt/heptuple-platform/db/csv_templates/hadiths.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

\copy fiqh_rulings (rite, topic, question, ruling_text, evidences, sources, keywords)
FROM '/opt/heptuple-platform/db/csv_templates/fiqh_rulings.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

\copy invocations (titre, texte_arabe, texte_traduit, source, categories, tags, temps_recommande)
FROM '/opt/heptuple-platform/db/csv_templates/invocations.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
