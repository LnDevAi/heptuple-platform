-- Sample ingestion examples (replace with real datasets)

-- HADITHS (minimal columns used by the app)
INSERT INTO hadiths (numero_hadith, recueil, livre, chapitre, texte_arabe, texte_francais, narrateur, degre_authenticite, dimension_heptuple, mots_cles, themes, contexte_historique)
VALUES
('1', 'Bukhari', 'Livre de la foi', 'Chapitre 1', 'إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ', 'Les actions ne valent que par les intentions', 'Omar ibn al-Khattab', 'Sahih', '5', ARRAY['intention','foi'], ARRAY['aqida'], 'Médine'),
('2', 'Muslim', 'Livre de la prière', 'Chapitre 2', 'الصلاة عماد الدين', 'La prière est le pilier de la religion', 'Anas ibn Malik', 'Sahih', '6', ARRAY['prière','salat'], ARRAY['fiqh'], 'Médine');

-- FIQH RULINGS
INSERT INTO fiqh_rulings (rite, topic, question, ruling_text, evidences, sources, keywords)
VALUES
('malikite', 'Prière', 'Doit-on lever les mains au takbir ?', 'Recommandé selon la majorité, détails selon les écoles.', ARRAY['Hadith Bukhari #735','Consensus'], ARRAY['Muwatta Malik'], ARRAY['takbir','salat']),
('hanafite', 'Jeûne', 'Cassure du jeûne par inadvertance ?', 'Le jeûne reste valide s’il n’y a pas d’intention.', ARRAY['Quran 2:187'], ARRAY['Hidaya'], ARRAY['sawm','inadvertance']);

-- INVOCATIONS
INSERT INTO invocations (titre, texte_arabe, texte_traduit, source, categories, tags, temps_recommande)
VALUES
('Doua du matin', 'أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ', 'Nous sommes entrés au matin et la royauté appartient à Allah', 'Hisn al-Muslim', ARRAY['matin'], ARRAY['dhikr','matin'], ARRAY['matin']),
('Après la prière', 'اللَّهُمَّ أَعِنِّي عَلَى ذِكْرِكَ', 'Ô Allah, aide-moi à me souvenir de Toi', 'Sunan', ARRAY['apres-priere'], ARRAY['dhikr'], ARRAY['après-prière']);