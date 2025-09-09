from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, TIMESTAMP, DECIMAL, ARRAY, JSON, ForeignKey, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
import os
from typing import Generator

"""
Construction sûre de l'URL de base de données depuis les variables d'environnement.
Évite les identifiants en dur et respecte un fallback minimal uniquement si toutes
les variables nécessaires sont fournies.
"""

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

env_database_url = os.getenv("DATABASE_URL")

if env_database_url:
    DATABASE_URL = env_database_url
elif all([db_host, db_port, db_name, db_user, db_password]):
    DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
else:
    # Fallback local explicite et non recommandé pour la prod; penser à fournir un .env
    DATABASE_URL = "postgresql://heptuple_user:heptuple_pass@localhost:5432/heptuple_db"

# Création de l'engine SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Mettre à True pour debug SQL
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

# Modèles SQLAlchemy
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    specialization = Column(String(100))
    preferences = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class Sourate(Base):
    __tablename__ = "sourates"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(Integer, unique=True, nullable=False, index=True)
    nom_arabe = Column(String(100), nullable=False)
    nom_francais = Column(String(100), nullable=False)
    nom_anglais = Column(String(100))
    type_revelation = Column(String(20), nullable=False)
    periode_detaillee = Column(String(50))
    nombre_versets = Column(Integer, nullable=False)
    ordre_revelation = Column(Integer)
    annee_revelation = Column(Integer)
    lieu_revelation = Column(String(100))
    themes = Column(JSON, default=[])
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class ProfilHeptuple(Base):
    __tablename__ = "profils_heptuple"
    
    id = Column(Integer, primary_key=True, index=True)
    sourate_id = Column(Integer, nullable=False, index=True)
    mysteres_score = Column(Integer)
    creation_score = Column(Integer)
    attributs_score = Column(Integer)
    eschatologie_score = Column(Integer)
    tawhid_score = Column(Integer)
    guidance_score = Column(Integer)
    egarement_score = Column(Integer)
    version = Column(String(20), default="1.0")
    validateur_expert_id = Column(Integer)
    confidence_score = Column(DECIMAL(3, 2))
    created_at = Column(TIMESTAMP, server_default=func.now())

class Verset(Base):
    __tablename__ = "versets"
    
    id = Column(Integer, primary_key=True, index=True)
    sourate_id = Column(Integer, nullable=False, index=True)
    numero_verset = Column(Integer, nullable=False)
    texte_arabe = Column(Text, nullable=False)
    texte_translitteration = Column(Text)
    traduction_francaise = Column(Text)
    traduction_anglaise = Column(Text)
    dimension_principale = Column(Integer)
    dimensions_secondaires = Column(ARRAY(Integer), default=[])
    mots_cles = Column(JSON, default=[])
    notes_exegetiques = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

class AnalyseExegetique(Base):
    __tablename__ = "analyses_exegetiques"
    
    id = Column(Integer, primary_key=True, index=True)
    verset_id = Column(Integer, index=True)
    sourate_id = Column(Integer, index=True)
    type_analyse = Column(String(50), nullable=False)
    source = Column(String(100))
    contenu = Column(Text, nullable=False)
    dimension_ciblee = Column(Integer)
    citations = Column(JSON, default=[])
    tags = Column(ARRAY(String), default=[])
    author_id = Column(Integer)
    is_validated = Column(Boolean, default=False)
    validation_date = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())

class AIPrediction(Base):
    __tablename__ = "ai_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    input_text_hash = Column(String(64), unique=True, nullable=False, index=True)
    input_text = Column(Text, nullable=False)
    predicted_profile = Column(ARRAY(Integer), nullable=False)
    confidence_scores = Column(ARRAY(DECIMAL(3, 2)))
    model_version = Column(String(20), nullable=False)
    processing_time_ms = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())

class UsageAnalytics(Base):
    __tablename__ = "usage_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    action = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    metadata_info = Column(JSON, default={})
    ip_address = Column(String(45))  # Support IPv6
    user_agent = Column(Text)
    session_id = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)

# Fonction pour obtenir une session de base de données
def get_db() -> Generator[Session, None, None]:
    """
    Générateur de session de base de données pour FastAPI Dependency Injection
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fonction pour créer les tables
def create_tables():
    """
    Crée toutes les tables dans la base de données
    """
    Base.metadata.create_all(bind=engine)

# Fonction pour vérifier la connexion
def check_database_connection() -> bool:
    """
    Vérifie si la connexion à la base de données fonctionne
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")
        return False

# Fonctions utilitaires pour les requêtes
class Hadith(Base):
    __tablename__ = "hadiths"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_hadith = Column(String(50), nullable=False)
    recueil = Column(String(100), nullable=False)
    livre = Column(String(200))
    chapitre = Column(String(200))
    texte_arabe = Column(Text, nullable=False)
    texte_francais = Column(Text, nullable=False)
    texte_anglais = Column(Text)
    narrateur = Column(String(200))
    degre_authenticite = Column(String(50))
    dimension_heptuple = Column(String(50))
    mots_cles = Column(ARRAY(String))
    themes = Column(ARRAY(String))
    contexte_historique = Column(Text)
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now())

class Exegese(Base):
    __tablename__ = "exegeses"
    
    id = Column(Integer, primary_key=True, index=True)
    auteur = Column(String(200), nullable=False)
    titre_ouvrage = Column(String(300), nullable=False)
    epoque = Column(String(100))
    ecole_juridique = Column(String(100))
    sourate_id = Column(Integer, ForeignKey('sourates.id'))
    verset_debut = Column(Integer)
    verset_fin = Column(Integer)
    texte_exegese = Column(Text, nullable=False)
    dimension_heptuple = Column(String(50))
    themes = Column(ARRAY(String))
    references_hadiths = Column(ARRAY(Integer))
    langue = Column(String(10), default='ar')
    created_at = Column(TIMESTAMP, default=func.now())

class Citation(Base):
    __tablename__ = "citations"
    
    id = Column(Integer, primary_key=True, index=True)
    type_citation = Column(String(50), nullable=False)
    auteur = Column(String(200))
    source = Column(String(300))
    epoque = Column(String(100))
    texte_original = Column(Text, nullable=False)
    texte_traduit = Column(Text)
    contexte = Column(Text)
    dimension_heptuple = Column(String(50))
    pertinence_score = Column(DECIMAL(3,2), default=0.5)
    themes = Column(ARRAY(String))
    mots_cles = Column(ARRAY(String))
    verified = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=func.now())

class Histoire(Base):
    __tablename__ = "histoires"
    
    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(300), nullable=False)
    epoque = Column(String(100))
    personnages = Column(ARRAY(String))
    lieu = Column(String(200))
    contexte_historique = Column(Text)
    recit_complet = Column(Text, nullable=False)
    enseignements = Column(ARRAY(String))
    dimension_heptuple = Column(String(50))
    sources = Column(ARRAY(String))
    degre_authenticite = Column(String(50))
    themes = Column(ARRAY(String))
    created_at = Column(TIMESTAMP, default=func.now())

class FiqhRuling(Base):
    __tablename__ = "fiqh_rulings"
    
    id = Column(Integer, primary_key=True, index=True)
    rite = Column(String(50), index=True)  # hanafite, malikite, chafiite, hanbalite, ja'farite, etc.
    topic = Column(String(200), index=True)
    question = Column(Text)
    ruling_text = Column(Text, nullable=False)
    evidences = Column(ARRAY(Text))
    sources = Column(ARRAY(String))
    keywords = Column(ARRAY(String))
    created_at = Column(TIMESTAMP, default=func.now(), index=True)

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_sourate_by_numero(self, numero: int) -> Sourate:
        """Récupère une sourate par son numéro"""
        return self.db.query(Sourate).filter(Sourate.numero == numero).first()
    
    def get_sourate_by_id(self, sourate_id: int) -> Sourate:
        """Récupère une sourate par son id"""
        return self.db.query(Sourate).filter(Sourate.id == sourate_id).first()
    
    def get_sourates_all(self) -> list[Sourate]:
        """Récupère toutes les sourates"""
        return self.db.query(Sourate).order_by(Sourate.numero).all()
    
    def get_profil_heptuple_by_sourate(self, sourate_id: int) -> ProfilHeptuple:
        """Récupère le profil heptuple d'une sourate"""
        return self.db.query(ProfilHeptuple).filter(
            ProfilHeptuple.sourate_id == sourate_id
        ).first()
    
    def get_versets_by_sourate(self, sourate_id: int) -> list[Verset]:
        """Récupère tous les versets d'une sourate"""
        return self.db.query(Verset).filter(
            Verset.sourate_id == sourate_id
        ).order_by(Verset.numero_verset).all()
    
    def get_analyses_by_dimension(self, dimension: str, limit: int = 10):
        """Récupère les analyses par dimension dominante"""
        return self.db.query(AnalyseExegetique).filter(
            AnalyseExegetique.dimension_ciblee == dimension
        ).limit(limit).all()

    # Références par dimension
    def get_hadiths_by_dimension(self, dimension: str, limit: int = 10):
        return self.db.query(Hadith).filter(Hadith.dimension_heptuple == dimension).limit(limit).all()

    def get_exegeses_by_dimension(self, dimension: str, limit: int = 5):
        return self.db.query(Exegese).filter(Exegese.dimension_heptuple == dimension).limit(limit).all()

    def get_citations_by_dimension(self, dimension: str, limit: int = 5):
        return self.db.query(Citation).filter(Citation.dimension_heptuple == dimension).limit(limit).all()

    def get_histoires_by_dimension(self, dimension: str, limit: int = 5):
        return self.db.query(Histoire).filter(Histoire.dimension_heptuple == dimension).limit(limit).all()
    
    def save_ai_prediction(self, text_hash: str, text: str, profile: list, 
                          confidence: list, model_version: str, processing_time: int):
        """Sauvegarde une prédiction IA en cache"""
        prediction = AIPrediction(
            input_text_hash=text_hash,
            input_text=text,
            predicted_profile=profile,
            confidence_scores=confidence,
            model_version=model_version,
            processing_time_ms=processing_time
        )
        self.db.add(prediction)
        self.db.commit()
        return prediction
    
    def get_ai_prediction_by_hash(self, text_hash: str) -> AIPrediction:
        """Récupère une prédiction IA depuis le cache"""
        return self.db.query(AIPrediction).filter(
            AIPrediction.input_text_hash == text_hash
        ).first()
    
    def log_user_action(self, user_id: int, action: str, resource_type: str = None,
                       resource_id: int = None, metadata: dict = None, 
                       ip_address: str = None, user_agent: str = None):
        """Enregistre une action utilisateur pour analytics"""
        analytics = UsageAnalytics(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.db.add(analytics)
        self.db.commit()
        return analytics

    # Recherches simples (fallback LIKE)
    def search_versets(self, query: str, limit: int = 20):
        q = f"%{query}%"
        return self.db.query(Verset).filter(
            or_(Verset.texte_arabe.ilike(q), Verset.traduction_francaise.ilike(q))
        ).limit(limit).all()

    def search_hadiths(self, query: str, limit: int = 20):
        q = f"%{query}%"
        return self.db.query(Hadith).filter(
            or_(Hadith.texte_francais.ilike(q), Hadith.texte_arabe.ilike(q), Hadith.mots_cles.any(query))
        ).limit(limit).all()

    def search_hadiths_authentic(self, query: str | None = None, recueils: list[str] | None = None,
                                  authenticite: str | None = None, limit: int = 20, offset: int = 0):
        """Recherche de hadiths authentiques avec filtres (recueils, authenticité, texte)."""
        query_builder = self.db.query(Hadith)
        if query:
            q = f"%{query}%"
            query_builder = query_builder.filter(
                or_(
                    Hadith.texte_francais.ilike(q),
                    Hadith.texte_arabe.ilike(q),
                    Hadith.narrateur.ilike(q),
                    Hadith.recueil.ilike(q)
                )
            )
        if recueils:
            query_builder = query_builder.filter(Hadith.recueil.in_(recueils))
        if authenticite:
            query_builder = query_builder.filter(Hadith.degre_authenticite.ilike(authenticite))
        return query_builder.offset(offset).limit(limit).all()

    def get_hadiths_collections_summary(self) -> list[dict]:
        """Retourne le nombre de hadiths par recueil."""
        rows = self.db.query(Hadith.recueil, func.count(Hadith.id)).group_by(Hadith.recueil).order_by(func.count(Hadith.id).desc()).all()
        return [{"recueil": r[0], "count": int(r[1])} for r in rows]

    def search_exegeses(self, query: str, limit: int = 20):
        q = f"%{query}%"
        return self.db.query(Exegese).filter(
            or_(Exegese.texte_exegese.ilike(q), Exegese.auteur.ilike(q), Exegese.titre_ouvrage.ilike(q))
        ).limit(limit).all()

    def search_citations(self, query: str, limit: int = 20):
        q = f"%{query}%"
        return self.db.query(Citation).filter(
            or_(Citation.texte_original.ilike(q), Citation.texte_traduit.ilike(q), Citation.auteur.ilike(q))
        ).limit(limit).all()

    def search_histoires(self, query: str, limit: int = 20):
        q = f"%{query}%"
        return self.db.query(Histoire).filter(
            or_(Histoire.recit_complet.ilike(q), Histoire.titre.ilike(q))
        ).limit(limit).all()

    def search_fiqh(self, query: str, rite: str | None = None, limit: int = 10):
        q = f"%{query}%"
        filters = [
            or_(
                FiqhRuling.topic.ilike(q),
                FiqhRuling.question.ilike(q),
                FiqhRuling.ruling_text.ilike(q)
            )
        ]
        if rite:
            filters.append(FiqhRuling.rite == rite)
        return self.db.query(FiqhRuling).filter(*filters).limit(limit).all()

    def list_fiqh_rites(self) -> list[str]:
        """Liste distincte des rites disponibles dans les rulings."""
        rows = self.db.query(FiqhRuling.rite).distinct().all()
        return [r[0] for r in rows if r[0]]

    def search_fiqh_rulings(self, query: str | None = None, rite: str | None = None,
                             topic: str | None = None, limit: int = 20, offset: int = 0):
        """Recherche paginée de rulings fiqh avec filtres."""
        qb = self.db.query(FiqhRuling)
        if query:
            q = f"%{query}%"
            qb = qb.filter(or_(
                FiqhRuling.topic.ilike(q),
                FiqhRuling.question.ilike(q),
                FiqhRuling.ruling_text.ilike(q)
            ))
        if rite:
            qb = qb.filter(FiqhRuling.rite == rite)
        if topic:
            qb = qb.filter(FiqhRuling.topic.ilike(f"%{topic}%"))
        return qb.offset(offset).limit(limit).all()
