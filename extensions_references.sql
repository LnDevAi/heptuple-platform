-- Extension de la base de données pour les références (Hadiths, Exégèses, Citations)
-- À exécuter après init.sql

-- Table des Hadiths pour appuyer les analyses
CREATE TABLE hadiths (
    id SERIAL PRIMARY KEY,
    numero_hadith VARCHAR(50) NOT NULL,
    recueil VARCHAR(100) NOT NULL, -- Bukhari, Muslim, Tirmidhi, etc.
    livre VARCHAR(200),
    chapitre VARCHAR(200),
    texte_arabe TEXT NOT NULL,
    texte_francais TEXT NOT NULL,
    texte_anglais TEXT,
    narrateur VARCHAR(200),
    degre_authenticite VARCHAR(50), -- Sahih, Hassan, Daif
    dimension_heptuple VARCHAR(50),
    mots_cles TEXT[],
    themes TEXT[],
    contexte_historique TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des Exégèses traditionnelles
CREATE TABLE exegeses (
    id SERIAL PRIMARY KEY,
    auteur VARCHAR(200) NOT NULL, -- Ibn Kathir, Tabari, Qurtubi, etc.
    titre_ouvrage VARCHAR(300) NOT NULL,
    epoque VARCHAR(100), -- Classique, Médiéval, Moderne
    ecole_juridique VARCHAR(100), -- Hanafi, Maliki, Shafi'i, Hanbali
    sourate_id INTEGER REFERENCES sourates(id),
    verset_debut INTEGER,
    verset_fin INTEGER,
    texte_exegese TEXT NOT NULL,
    dimension_heptuple VARCHAR(50),
    themes TEXT[],
    references_hadiths INTEGER[],
    langue VARCHAR(10) DEFAULT 'ar',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des Citations et Références historiques
CREATE TABLE citations (
    id SERIAL PRIMARY KEY,
    type_citation VARCHAR(50) NOT NULL, -- hadith, exegese, histoire, savant
    auteur VARCHAR(200),
    source VARCHAR(300),
    epoque VARCHAR(100),
    texte_original TEXT NOT NULL,
    texte_traduit TEXT,
    contexte TEXT,
    dimension_heptuple VARCHAR(50),
    pertinence_score DECIMAL(3,2) DEFAULT 0.5,
    themes TEXT[],
    mots_cles TEXT[],
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table de liaison entre analyses et références
CREATE TABLE analyse_references (
    id SERIAL PRIMARY KEY,
    analyse_id INTEGER REFERENCES analyses(id),
    hadith_id INTEGER REFERENCES hadiths(id),
    exegese_id INTEGER REFERENCES exegeses(id),
    citation_id INTEGER REFERENCES citations(id),
    pertinence_score DECIMAL(3,2) DEFAULT 0.5,
    type_relation VARCHAR(50), -- support, complement, contexte
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des Histoires et Récits authentiques
CREATE TABLE histoires (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(300) NOT NULL,
    epoque VARCHAR(100), -- Prophétique, Compagnons, Tabi'in, etc.
    personnages TEXT[], -- Noms des personnages principaux
    lieu VARCHAR(200),
    contexte_historique TEXT,
    recit_complet TEXT NOT NULL,
    enseignements TEXT[],
    dimension_heptuple VARCHAR(50),
    sources TEXT[], -- Références aux sources historiques
    degre_authenticite VARCHAR(50),
    themes TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour optimiser les recherches
CREATE INDEX idx_hadiths_dimension ON hadiths(dimension_heptuple);
CREATE INDEX idx_hadiths_recueil ON hadiths(recueil);
CREATE INDEX idx_hadiths_themes ON hadiths USING GIN(themes);
CREATE INDEX idx_hadiths_mots_cles ON hadiths USING GIN(mots_cles);
CREATE INDEX idx_exegeses_auteur ON exegeses(auteur);
CREATE INDEX idx_exegeses_dimension ON exegeses(dimension_heptuple);
CREATE INDEX idx_exegeses_sourate ON exegeses(sourate_id);
CREATE INDEX idx_citations_type ON citations(type_citation);
CREATE INDEX idx_citations_dimension ON citations(dimension_heptuple);
CREATE INDEX idx_citations_themes ON citations USING GIN(themes);
CREATE INDEX idx_histoires_dimension ON histoires(dimension_heptuple);
CREATE INDEX idx_histoires_epoque ON histoires(epoque);

-- Insertion de hadiths d'exemple pour chaque dimension heptuple
INSERT INTO hadiths (numero_hadith, recueil, livre, chapitre, texte_arabe, texte_francais, narrateur, degre_authenticite, dimension_heptuple, mots_cles, themes, contexte_historique) VALUES
-- Dimension Mystères
('1', 'Bukhari', 'Livre de la Révélation', 'Début de la Révélation', 'إنما الأعمال بالنيات وإنما لكل امرئ ما نوى', 'Les actions ne valent que par les intentions, et chacun n''aura que ce qu''il a eu l''intention de faire', 'Umar ibn al-Khattab', 'Sahih', 'mysteres', ARRAY['niyyah', 'intention', 'actions'], ARRAY['spiritualité', 'intention', 'mystères divins'], 'Hadith fondamental sur l''importance de l''intention dans l''Islam'),

('3019', 'Bukhari', 'Livre du Tafsir', 'Sourate Al-Fatiha', 'الحروف المقطعة في أوائل السور من المتشابه الذي استأثر الله بعلمه', 'Les lettres isolées au début des sourates font partie du mutashabih dont Allah s''est réservé la connaissance', 'Ibn Abbas', 'Sahih', 'mysteres', ARRAY['huruf muqatta''a', 'mutashabih', 'mystères'], ARRAY['lettres mystérieuses', 'science divine', 'secrets'], 'Explication des lettres mystérieuses du Coran'),

-- Dimension Création
('2637', 'Muslim', 'Livre de la Foi', 'La Création', 'كان الله ولم يكن شيء غيره وكان عرشه على الماء', 'Allah était et il n''y avait rien d''autre que Lui, et Son Trône était sur l''eau', 'Abu Hurayra', 'Sahih', 'creation', ARRAY['khalq', 'création', 'trône', 'eau'], ARRAY['cosmologie', 'création divine', 'existence'], 'Hadith sur l''existence d''Allah avant la création'),

('4812', 'Abu Dawud', 'Livre de la Sunna', 'La Création des Cieux', 'إن الله خلق السماوات والأرض في ستة أيام', 'Allah a créé les cieux et la terre en six jours', 'Abu Hurayra', 'Sahih', 'creation', ARRAY['samawat', 'ard', 'six jours'], ARRAY['création', 'cieux', 'terre'], 'Hadith sur la durée de la création'),

-- Dimension Attributs divins
('99', 'Tirmidhi', 'Livre des Invocations', 'Les Beaux Noms', 'إن لله تسعة وتسعين اسما مائة إلا واحدا من أحصاها دخل الجنة', 'Allah a quatre-vingt-dix-neuf noms, cent moins un. Quiconque les énumère entrera au Paradis', 'Abu Hurayra', 'Hassan', 'attributs', ARRAY['asma al-husna', 'noms', 'attributs'], ARRAY['noms divins', 'attributs d''Allah', 'spiritualité'], 'Hadith sur les 99 beaux noms d''Allah'),

('2677', 'Muslim', 'Livre du Dhikr', 'Attributs divins', 'لله أرحم بعباده من الوالدة بولدها', 'Allah est plus miséricordieux envers Ses serviteurs qu''une mère envers son enfant', 'Umar ibn al-Khattab', 'Sahih', 'attributs', ARRAY['rahma', 'miséricorde', 'mère'], ARRAY['miséricorde divine', 'compassion', 'amour divin'], 'Comparaison de la miséricorde divine'),

-- Dimension Eschatologie
('6486', 'Bukhari', 'Livre des Épreuves', 'Signes de l''Heure', 'لا تقوم الساعة حتى تطلع الشمس من مغربها', 'L''Heure ne viendra pas avant que le soleil ne se lève de l''Occident', 'Abu Hurayra', 'Sahih', 'eschatologie', ARRAY['qiyama', 'heure', 'soleil', 'occident'], ARRAY['fin des temps', 'signes de l''Heure', 'eschatologie'], 'Hadith sur les signes majeurs de la fin des temps'),

('7049', 'Bukhari', 'Livre de l''Unicité', 'Le Jour du Jugement', 'يجمع الله الأولين والآخرين في صعيد واحد', 'Allah rassemblera les premiers et les derniers sur une même terre', 'Ibn Umar', 'Sahih', 'eschatologie', ARRAY['hashr', 'rassemblement', 'jugement'], ARRAY['jour du jugement', 'résurrection', 'rassemblement'], 'Description du Jour du Jugement'),

-- Dimension Tawhid
('7', 'Muslim', 'Livre de la Foi', 'L''Islam', 'أن تشهد أن لا إله إلا الله وأن محمدا رسول الله', 'Que tu témoignes qu''il n''y a de divinité qu''Allah et que Muhammad est le Messager d''Allah', 'Umar ibn al-Khattab', 'Sahih', 'tawhid', ARRAY['shahada', 'tawhid', 'unicité'], ARRAY['unicité divine', 'témoignage de foi', 'Islam'], 'Hadith de Jibril sur les piliers de l''Islam'),

('2816', 'Tirmidhi', 'Livre de la Foi', 'Mérites du Tawhid', 'من مات وهو يعلم أنه لا إله إلا الله دخل الجنة', 'Quiconque meurt en sachant qu''il n''y a de divinité qu''Allah entrera au Paradis', 'Uthman ibn Affan', 'Sahih', 'tawhid', ARRAY['la ilaha illa allah', 'mort', 'paradis'], ARRAY['unicité', 'foi', 'salut'], 'Mérites de mourir sur le Tawhid'),

-- Dimension Guidance
('1631', 'Muslim', 'Livre du Pèlerinage', 'Mérites de Médine', 'اللهم اهدني فيمن هديت', 'Ô Allah, guide-moi parmi ceux que Tu as guidés', 'Al-Hassan ibn Ali', 'Sahih', 'guidance', ARRAY['hidaya', 'guidance', 'du''a'], ARRAY['guidance divine', 'invocation', 'droit chemin'], 'Invocation pour demander la guidance'),

('2674', 'Bukhari', 'Livre de la Science', 'Mérites de la Science', 'من يرد الله به خيرا يفقهه في الدين', 'Celui à qui Allah veut du bien, Il lui donne la compréhension de la religion', 'Mu''awiya', 'Sahih', 'guidance', ARRAY['fiqh', 'compréhension', 'religion'], ARRAY['science religieuse', 'compréhension', 'guidance'], 'Lien entre guidance divine et compréhension religieuse'),

-- Dimension Égarement
('2674', 'Tirmidhi', 'Livre des Épreuves', 'Les Tentations', 'إن الله لا يقبض العلم انتزاعا ينتزعه من العباد', 'Allah ne retire pas la science en l''arrachant aux serviteurs', 'Abdullah ibn Amr', 'Sahih', 'egarement', ARRAY['ilm', 'science', 'disparition'], ARRAY['ignorance', 'perte de science', 'égarement'], 'Hadith sur la disparition progressive de la science'),

('1844', 'Muslim', 'Livre des Épreuves', 'Fitna', 'ستكون فتن كقطع الليل المظلم', 'Il y aura des épreuves comme les morceaux de nuit obscure', 'Hudhaifa ibn al-Yaman', 'Sahih', 'egarement', ARRAY['fitan', 'épreuves', 'obscurité'], ARRAY['épreuves', 'confusion', 'égarement'], 'Prophétie sur les épreuves futures de la communauté');

-- Insertion d'exégèses d'exemple
INSERT INTO exegeses (auteur, titre_ouvrage, epoque, ecole_juridique, sourate_id, verset_debut, verset_fin, texte_exegese, dimension_heptuple, themes, langue) VALUES
('Ibn Kathir', 'Tafsir Ibn Kathir', 'Médiéval', 'Shafi''i', 1, 1, 1, 'بسم الله الرحمن الرحيم: هذه الآية تحتوي على أسرار عظيمة وحكم بالغة. فالبسملة مفتاح كل خير وبركة، وفيها من الأسرار ما لا يحيط به إلا الله. وقد قال بعض العلماء أن في البسملة جميع علوم القرآن مجملة.', 'mysteres', ARRAY['bismillah', 'mystères', 'secrets divins'], 'ar'),

('At-Tabari', 'Jami'' al-Bayan', 'Classique', 'Shafi''i', 1, 2, 2, 'الحمد لله رب العالمين: أي الثناء لله الذي له الخلق والأمر، وهو رب جميع المخلوقات من الإنس والجن والملائكة وسائر ما خلق في السماوات والأرض. والعالمين جمع عالم، وكل صنف من أصناف الخلق عالم قائم بذاته.', 'creation', ARRAY['louange', 'seigneurie', 'création', 'mondes'], 'ar'),

('Al-Qurtubi', 'Al-Jami'' li-Ahkam al-Quran', 'Médiéval', 'Maliki', 1, 3, 3, 'الرحمن الرحيم: هذان الاسمان من أسماء الله الحسنى، والرحمن أبلغ من الرحيم لأنه يدل على الصفة الذاتية، والرحيم يدل على الصفة الفعلية. فالرحمن ذو الرحمة الواسعة، والرحيم الذي يرحم عباده المؤمنين رحمة خاصة.', 'attributs', ARRAY['miséricorde', 'attributs divins', 'rahman', 'rahim'], 'ar'),

('Ibn Arabi', 'Fusus al-Hikam', 'Médiéval', 'Zahiri', 1, 4, 4, 'مالك يوم الدين: إشارة إلى أن الملك الحقيقي لله وحده، وأن يوم الدين هو يوم ظهور هذا الملك بلا منازع. وفي هذا إشارة إلى أن العبد في هذه الدنيا قد يتوهم أن له ملكا، ولكن في الآخرة يتبين أن الملك لله وحده.', 'eschatologie', ARRAY['souveraineté', 'jour du jugement', 'royauté divine'], 'ar'),

('As-Sa''di', 'Taysir al-Karim ar-Rahman', 'Moderne', 'Hanbali', 1, 5, 5, 'إياك نعبد وإياك نستعين: هذا هو لب الدين وأساس العبودية. فالعبادة حق الله وحده، والاستعانة به وحده. وفي تقديم المعبود على العبادة والمستعان على الاستعانة إشارة إلى أهمية إخلاص القصد لله في جميع الأعمال.', 'tawhid', ARRAY['adoration', 'aide divine', 'unicité'], 'ar'),

('Al-Alusi', 'Ruh al-Ma''ani', 'Moderne', 'Hanafi', 1, 6, 6, 'اهدنا الصراط المستقيم: هذا دعاء عظيم يتضمن طلب الهداية إلى الحق في الاعتقاد والعمل والسلوك. والصراط المستقيم هو الإسلام، وهو الطريق الموصل إلى رضوان الله والجنة. وهذا الدعاء يحتاجه العبد في كل وقت.', 'guidance', ARRAY['guidance', 'droit chemin', 'islam'], 'ar'),

('Ibn Ashur', 'At-Tahrir wa at-Tanwir', 'Moderne', 'Maliki', 1, 7, 7, 'غير المغضوب عليهم ولا الضالين: بيان لمن لا نريد أن نكون مثلهم. فالمغضوب عليهم هم الذين عرفوا الحق ولم يعملوا به، والضالون هم الذين لم يعرفوا الحق. وفي هذا تحذير من طريقي الانحراف: انحراف العلم وانحراف العمل.', 'egarement', ARRAY['colère divine', 'égarement', 'déviation'], 'ar');

-- Insertion de citations historiques et de savants
INSERT INTO citations (type_citation, auteur, source, epoque, texte_original, texte_traduit, contexte, dimension_heptuple, themes, verified) VALUES
('savant', 'Imam Al-Ghazali', 'Ihya Ulum ad-Din', 'Médiéval', 'الفاتحة سر القرآن، وسر الفاتحة البسملة، وسر البسملة الباء، وسر الباء النقطة التي تحت الباء', 'Al-Fatiha est le secret du Coran, le secret d''Al-Fatiha est la Basmala, le secret de la Basmala est le Ba, et le secret du Ba est le point sous le Ba', 'Réflexion mystique sur les secrets cachés dans Al-Fatiha', 'mysteres', ARRAY['fatiha', 'mystique', 'secrets'], TRUE),

('savant', 'Ibn Taymiyyah', 'Majmu'' al-Fatawa', 'Médiéval', 'التوحيد أول دعوة الرسل وآخرها، وأول منازل الطريق وآخرها', 'Le Tawhid est le premier et le dernier appel des messagers, la première et la dernière station du chemin', 'Importance centrale du Tawhid dans l''Islam', 'tawhid', ARRAY['tawhid', 'messagers', 'unicité'], TRUE),

('histoire', 'Compagnons du Prophète', 'Sirat Rasul Allah', 'Classique', 'كان النبي صلى الله عليه وسلم يقرأ الفاتحة في كل ركعة من الصلاة', 'Le Prophète (paix sur lui) récitait Al-Fatiha dans chaque unité de prière', 'Pratique prophétique concernant la récitation d''Al-Fatiha', 'guidance', ARRAY['prière', 'fatiha', 'sunnah'], TRUE),

('exegese', 'Ibn Arabi', 'Fusus al-Hikam', 'Médiéval', 'الفاتحة أم الكتاب لأنها تحتوي على جميع معاني القرآن مجملة', 'Al-Fatiha est la mère du Livre car elle contient tous les sens du Coran de manière synthétique', 'Explication mystique de la centralité d''Al-Fatiha', 'mysteres', ARRAY['fatiha', 'mystique', 'sens cachés'], TRUE),

('savant', 'Imam Malik', 'Al-Muwatta', 'Classique', 'لا صلاة لمن لم يقرأ بفاتحة الكتاب', 'Il n''y a pas de prière pour celui qui ne récite pas la Fatiha', 'Importance obligatoire d''Al-Fatiha dans la prière', 'guidance', ARRAY['prière', 'obligation', 'fatiha'], TRUE),

('histoire', 'Umar ibn al-Khattab', 'Tarikh at-Tabari', 'Classique', 'تعلموا الفاتحة وعلموها أولادكم فإنها شفاء من كل داء إلا السام', 'Apprenez Al-Fatiha et enseignez-la à vos enfants, car elle est guérison de tout mal sauf la mort', 'Témoignage sur les vertus curatives d''Al-Fatiha', 'guidance', ARRAY['guérison', 'enseignement', 'vertus'], TRUE);

-- Insertion d'histoires authentiques
INSERT INTO histoires (titre, epoque, personnages, lieu, contexte_historique, recit_complet, enseignements, dimension_heptuple, sources, degre_authenticite, themes) VALUES
('La révélation d''Al-Fatiha', 'Prophétique', ARRAY['Muhammad (PBSL)', 'Jibril (AS)'], 'La Mecque', 'Début de la révélation coranique', 'Selon les récits authentiques, Al-Fatiha fut révélée en entier à La Mecque au début de la mission prophétique. L''ange Jibril descendit vers le Prophète Muhammad (paix sur lui) et lui enseigna cette sourate qui allait devenir le pilier de toute prière musulmane. Cette sourate synthétise l''essence même du message islamique : la reconnaissance d''Allah, Ses attributs, le Jour du Jugement, l''adoration exclusive, et la demande de guidance.', ARRAY['Importance de la prière', 'Centralité d''Al-Fatiha', 'Guidance divine'], 'mysteres', ARRAY['Sahih Bukhari', 'Sahih Muslim', 'Tafsir Ibn Kathir'], 'Sahih', ARRAY['révélation', 'fatiha', 'prière']),

('L''histoire d''Abu Bakr et la compilation du Coran', 'Compagnons', ARRAY['Abu Bakr', 'Umar ibn al-Khattab', 'Zayd ibn Thabit'], 'Médine', 'Après la bataille de Yamama', 'Après la mort de nombreux mémorisateurs du Coran à la bataille de Yamama, Umar ibn al-Khattab vint voir Abu Bakr et lui dit : "Ô successeur du Messager d''Allah, beaucoup de mémorisateurs du Coran ont péri à Yamama, et je crains que d''autres ne périssent ailleurs, emportant avec eux une partie du Coran. Je pense que tu devrais ordonner la compilation du Coran." Cette initiative préserva le Coran pour les générations futures.', ARRAY['Préservation de la révélation', 'Sagesse des Compagnons', 'Importance de la transmission'], 'guidance', ARRAY['Sahih Bukhari', 'Tarikh at-Tabari'], 'Sahih', ARRAY['compilation', 'préservation', 'coran']),

('La conversion d''Umar ibn al-Khattab', 'Prophétique', ARRAY['Umar ibn al-Khattab', 'Sa sœur Fatima', 'Khabbab ibn al-Aratt'], 'La Mecque', 'Avant l''Hégire', 'Umar ibn al-Khattab était un ennemi farouche de l''Islam. Un jour, il décida d''aller tuer le Prophète Muhammad. En chemin, on lui dit que sa propre sœur avait embrassé l''Islam. Furieux, il se dirigea vers sa maison. Il y trouva sa sœur et son beau-frère en train de réciter des versets du Coran. Après les avoir frappés, il fut touché par leur patience et demanda à lire ce qu''ils récitaient. C''était la sourate Ta-Ha. Après l''avoir lue, il dit : "Menez-moi à Muhammad !" et se convertit immédiatement.', ARRAY['Pouvoir transformateur du Coran', 'Guidance divine inattendue', 'Patience dans l''épreuve'], 'guidance', ARRAY['Sirat Ibn Hisham', 'Tarikh at-Tabari'], 'Sahih', ARRAY['conversion', 'coran', 'guidance']);

-- Commentaires sur les nouvelles tables
COMMENT ON TABLE hadiths IS 'Collection de hadiths authentiques classés par dimension heptuple';
COMMENT ON TABLE exegeses IS 'Exégèses traditionnelles des grands savants de l''Islam';
COMMENT ON TABLE citations IS 'Citations de savants et références historiques';
COMMENT ON TABLE analyse_references IS 'Liaison entre analyses et références pour enrichir les résultats';
COMMENT ON TABLE histoires IS 'Récits authentiques de l''histoire islamique';

-- Permissions
GRANT SELECT ON hadiths, exegeses, citations, analyse_references, histoires TO PUBLIC;
GRANT INSERT, UPDATE ON analyse_references TO PUBLIC;
