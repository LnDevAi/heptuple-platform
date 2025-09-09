from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from typing import List, Optional, Dict
import os
import time
import hashlib
import logging
import json
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt

# Import des modèles et services
from models import (
    ProfilHeptuple, AnalyseRequest, AnalyseResponse, 
    ComparisonRequest, SearchRequest, SearchResult,
    FeedbackRequest, Sourate, Verset, DimensionType,
    HadithModel, ExegeseModel, CitationModel, HistoireModel, InvocationModel,
    UserCreate, UserLogin, Token, UserResponse
)
from services.heptuple_analyzer import HeptupleAnalyzer
from services.auth_service import AuthService
from services.search_service import SearchService
from services.redis_service import RedisService
from database import get_db, DatabaseService, check_database_connection, User
from sqlalchemy.orm import Session

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration de sécurité
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production-32-chars-min")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key-change-in-production-32-chars-min")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuration du hashage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Configuration CORS sécurisée
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

app = FastAPI(
    title="API Vision Heptuple", 
    description="API d'analyse exégétique selon la vision heptuple de la Fatiha",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware de sécurité
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=ALLOWED_HOSTS
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initialisation des services
analyzer = HeptupleAnalyzer()
auth_service = AuthService()
redis_service = RedisService()

# Cache simple en mémoire (fallback si Redis indisponible)
analysis_cache = {}

# Fonctions d'authentification
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crée un token d'accès JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Vérifie un token JWT"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(username: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Récupère l'utilisateur actuel"""
    user = auth_service.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Récupère l'utilisateur actuel actif"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Utilisateur inactif")
    return current_user

# Fonctions utilitaires
def get_text_hash(text: str) -> str:
    """Génère un hash pour un texte"""
    return hashlib.sha256(text.encode()).hexdigest()

def log_error(error: Exception, context: str = ""):
    """Log une erreur avec contexte"""
    logger.error(f"{context}: {str(error)}", exc_info=True)

 

@app.get("/")
async def root():
    """Endpoint racine avec informations sur l'API"""
    return {
        "message": "API Vision Heptuple", 
        "status": "running", 
        "version": "2.0.0",
        "description": "Analyse exégétique selon la vision heptuple de la Fatiha",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "analyze": "/api/v2/analyze",
            "sourates": "/api/v2/sourates",
            "compare": "/api/v2/compare",
            "search": "/api/v2/search",
            "feedback": "/api/v2/feedback"
        }
    }

@app.get("/health")
async def health():
    """Health check de l'API"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }

@app.get("/api/v2/sourates", response_model=List[Dict])
async def get_sourates(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Récupère la liste des sourates avec leurs profils heptuple"""
    try:
        # Vérification du cache Redis
        cached_sourates = redis_service.get_cached_sourates()
        if cached_sourates:
            logger.info("Sourates récupérées du cache Redis")
            return cached_sourates
        
        db_service = DatabaseService(db)
        sourates = db_service.get_sourates_all()
        
        if not sourates:
            raise HTTPException(status_code=404, detail="Aucune sourate trouvée dans la base de données")
        
        result = []
        for sourate in sourates:
            profil = db_service.get_profil_heptuple_by_sourate(sourate.id)
            sourate_dict = {
                "id": sourate.id,
                "numero": sourate.numero,
                "nom_arabe": sourate.nom_arabe,
                "nom_francais": sourate.nom_francais,
                "type_revelation": sourate.type_revelation,
                "nombre_versets": sourate.nombre_versets,
                "profil_heptuple": None
            }
            
            if profil:
                sourate_dict["profil_heptuple"] = {
                    "mysteres": profil.mysteres_score,
                    "creation": profil.creation_score,
                    "attributs": profil.attributs_score,
                    "eschatologie": profil.eschatologie_score,
                    "tawhid": profil.tawhid_score,
                    "guidance": profil.guidance_score,
                    "egarement": profil.egarement_score
                }
            
            result.append(sourate_dict)
        
        # Mise en cache des résultats
        redis_service.cache_sourates(result, 3600)
        
        # Log de l'action utilisateur
        db_service.log_user_action(
            user_id=current_user.id,
            action="get_sourates",
            resource_type="sourates"
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, "Erreur de récupération des sourates")
        raise HTTPException(status_code=500, detail="Erreur de récupération des sourates")

@app.get("/api/v2/sourates/{numero}", response_model=Dict)
async def get_sourate(numero: int, db: Session = Depends(get_db)):
    """Récupère une sourate spécifique par son numéro"""
    db_service = DatabaseService(db)
    s = db_service.get_sourate_by_numero(numero)
    if not s:
        raise HTTPException(status_code=404, detail=f"Sourate {numero} non trouvée")
    profil = db_service.get_profil_heptuple_by_sourate(s.id)
    sourate_dict = {
        "id": s.id,
        "numero": s.numero,
        "nom_arabe": s.nom_arabe,
        "nom_francais": s.nom_francais,
        "type_revelation": s.type_revelation,
        "nombre_versets": s.nombre_versets,
        "profil_heptuple": None
    }
    if profil:
        sourate_dict["profil_heptuple"] = {
            "mysteres": profil.mysteres_score,
            "creation": profil.creation_score,
            "attributs": profil.attributs_score,
            "eschatologie": profil.eschatologie_score,
            "tawhid": profil.tawhid_score,
            "guidance": profil.guidance_score,
            "egarement": profil.egarement_score
        }
    return sourate_dict

@app.post("/api/v2/analyze")
async def analyze_text(
    request: AnalyseRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Analyse un texte selon la vision heptuple de la Fatiha"""
    try:
        # Génération du hash du texte pour le cache
        text_hash = get_text_hash(request.texte)
        
        # Vérification du cache Redis
        cached_analysis = redis_service.get_cached_analysis(text_hash)
        if cached_analysis:
            logger.info(f"Analyse récupérée du cache pour le texte: {request.texte[:50]}...")
            return cached_analysis
        
        # Analyse du texte
        analysis: AnalyseResponse = analyzer.analyze_text_heptuple(
            request.texte, 
            include_confidence=request.include_confidence, 
            include_details=request.include_details
        )

        # Conversion en structure conviviale pour le front
        profil: ProfilHeptuple = analysis.profil_heptuple
        scores_dict = {
            "mysteres": profil.mysteres,
            "creation": profil.creation,
            "attributs": profil.attributs,
            "eschatologie": profil.eschatologie,
            "tawhid": profil.tawhid,
            "guidance": profil.guidance,
            "egarement": profil.egarement,
        }

        confidence_score = None
        if analysis.confidence_scores:
            confidence_score = round(sum(analysis.confidence_scores) / len(analysis.confidence_scores), 3)

        response = {
            "texte_analyse": request.texte,
            "dimension_dominante": int(analysis.dimension_dominante),
            "scores": scores_dict,
            "intensity_max": analysis.intensity_max,
            "confidence_score": confidence_score,
            "processing_time_ms": analysis.processing_time_ms,
            "version": analysis.version,
        }
        
        # Mise en cache de l'analyse
        redis_service.cache_analysis(text_hash, response, 7200)
        
        # Sauvegarde de la prédiction IA en base
        db_service = DatabaseService(db)
        db_service.save_ai_prediction(
            text_hash=text_hash,
            text=request.texte,
            profile=profil.to_array(),
            confidence=analysis.confidence_scores or [],
            model_version=analysis.version,
            processing_time=analysis.processing_time_ms
        )
        
        # Log de l'action utilisateur
        db_service.log_user_action(
            user_id=current_user.id,
            action="text_analysis",
            resource_type="analysis",
            metadata={"text_length": len(request.texte), "dimension_dominante": int(analysis.dimension_dominante)}
        )
        
        return response
    except Exception as e:
        log_error(e, "Erreur lors de l'analyse")
        raise HTTPException(status_code=500, detail="Erreur lors de l'analyse")

@app.post("/api/v2/analyze-enriched")
async def analyze_text_enriched(request: AnalyseRequest, db: Session = Depends(get_db)):
    """Analyse enrichie avec hadiths, exégèses et citations"""
    try:
        # Analyse de base
        analyzer = HeptupleAnalyzer()
        analysis: AnalyseResponse = analyzer.analyze_text_heptuple(
            request.texte, include_confidence=request.include_confidence, include_details=request.include_details
        )
        # Conversion pour le front
        profil: ProfilHeptuple = analysis.profil_heptuple
        scores_dict = {
            "mysteres": profil.mysteres,
            "creation": profil.creation,
            "attributs": profil.attributs,
            "eschatologie": profil.eschatologie,
            "tawhid": profil.tawhid,
            "guidance": profil.guidance,
            "egarement": profil.egarement,
        }
        confidence_score = None
        if analysis.confidence_scores:
            confidence_score = round(sum(analysis.confidence_scores) / len(analysis.confidence_scores), 3)
        analyse_base = {
            "texte_analyse": request.texte,
            "dimension_dominante": int(analysis.dimension_dominante),
            "scores": scores_dict,
            "intensity_max": analysis.intensity_max,
            "confidence_score": confidence_score,
            "processing_time_ms": analysis.processing_time_ms,
            "version": analysis.version,
        }
        
        # Enrichissement avec références
        db_service = DatabaseService(db)
        
        # Récupération des références par dimension
        hadiths = db_service.get_hadiths_by_dimension(str(int(analysis.dimension_dominante)), 3)
        exegeses = db_service.get_exegeses_by_dimension(str(int(analysis.dimension_dominante)), 2)
        citations = db_service.get_citations_by_dimension(str(int(analysis.dimension_dominante)), 2)
        histoires = db_service.get_histoires_by_dimension(str(int(analysis.dimension_dominante)), 1)
        
        # Conversion en modèles Pydantic
        hadiths_models = [HadithModel(
            id=h.id,
            numero_hadith=h.numero_hadith,
            recueil=h.recueil,
            livre=h.livre,
            chapitre=h.chapitre,
            texte_arabe=h.texte_arabe,
            texte_francais=h.texte_francais,
            narrateur=h.narrateur,
            degre_authenticite=h.degre_authenticite,
            dimension_heptuple=h.dimension_heptuple,
            mots_cles=h.mots_cles or [],
            themes=h.themes or [],
            contexte_historique=h.contexte_historique
        ) for h in hadiths]
        
        exegeses_models = [ExegeseModel(
            id=e.id,
            auteur=e.auteur,
            titre_ouvrage=e.titre_ouvrage,
            epoque=e.epoque,
            ecole_juridique=e.ecole_juridique,
            sourate_id=e.sourate_id,
            verset_debut=e.verset_debut,
            verset_fin=e.verset_fin,
            texte_exegese=e.texte_exegese,
            dimension_heptuple=e.dimension_heptuple,
            themes=e.themes or [],
            langue=e.langue
        ) for e in exegeses]
        
        citations_models = [CitationModel(
            id=c.id,
            type_citation=c.type_citation,
            auteur=c.auteur,
            source=c.source,
            epoque=c.epoque,
            texte_original=c.texte_original,
            texte_traduit=c.texte_traduit,
            contexte=c.contexte,
            dimension_heptuple=c.dimension_heptuple,
            pertinence_score=float(c.pertinence_score) if c.pertinence_score else 0.5,
            themes=c.themes or [],
            verified=c.verified
        ) for c in citations]
        
        histoires_models = [HistoireModel(
            id=h.id,
            titre=h.titre,
            epoque=h.epoque,
            personnages=h.personnages or [],
            lieu=h.lieu,
            contexte_historique=h.contexte_historique,
            recit_complet=h.recit_complet,
            enseignements=h.enseignements or [],
            dimension_heptuple=h.dimension_heptuple,
            sources=h.sources or [],
            degre_authenticite=h.degre_authenticite,
            themes=h.themes or []
        ) for h in histoires]
        
        # Calcul du score d'enrichissement
        score_enrichissement = min(1.0, (len(hadiths) * 0.3 + len(exegeses) * 0.3 + 
                                        len(citations) * 0.2 + len(histoires) * 0.2))
        
        # Réponse enrichie
        response_enrichie = {
            "analyse": analyse_base,
            "hadiths": hadiths_models,
            "exegeses": exegeses_models,
            "citations": citations_models,
            "histoires": histoires_models,
            "score_enrichissement": score_enrichissement,
            "nombre_references": len(hadiths) + len(exegeses) + len(citations) + len(histoires)
        }
        
        return response_enrichie
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse enrichie: {str(e)}")

@app.get("/api/v2/db/health")
async def db_health():
    """Vérifie l'état de la base de données"""
    try:
        ok = check_database_connection()
        return {"database": "up" if ok else "down", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        return JSONResponse(status_code=500, content={"database": "error", "detail": str(e)})

@app.get("/api/v2/search/advanced", response_model=List[SearchResult])
async def advanced_search(query: str, search_type: str = "keyword", limit: int = 20, db: Session = Depends(get_db)):
    """Recherche avancée dans le Coran et les hadiths (fallback LIKE)
    Retourne uniquement des objets réels issus de la base sans valeurs factices.
    """
    try:
        db_service = DatabaseService(db)
        results: List[SearchResult] = []

        # Versets
        versets = db_service.search_versets(query, limit=limit)
        for v in versets:
            s = db_service.get_sourate_by_id(v.sourate_id)
            if not s:
                continue
            verset_model = Verset(
                id=v.id,
                sourate_id=v.sourate_id,
                numero_verset=v.numero_verset,
                texte_arabe=v.texte_arabe,
                traduction_francaise=v.traduction_francaise
            )
            sourate_model = Sourate(
                id=s.id, numero=s.numero, nom_arabe=s.nom_arabe, nom_francais=s.nom_francais,
                type_revelation=s.type_revelation, nombre_versets=s.nombre_versets
            )
            results.append(SearchResult(verset=verset_model, sourate=sourate_model, similarity_score=None, score=None))

        # Hadiths: si besoin de les retourner, créer un endpoint/modele dédié. Ici, on reste strict: pas de dummy.
        return results[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de recherche: {str(e)}")

@app.get("/api/v2/fiqh/search")
async def search_fiqh(query: str, rite: Optional[str] = None, limit: int = 10, db: Session = Depends(get_db)):
    """Recherche de jurisprudence des rites (fiqh) par sujet/mots-clés"""
    try:
        db_service = DatabaseService(db)
        rulings = db_service.search_fiqh(query=query, rite=rite, limit=limit)
        return [
            {
                "id": r.id,
                "rite": r.rite,
                "topic": r.topic,
                "question": r.question,
                "ruling_text": r.ruling_text,
                "evidences": r.evidences,
                "sources": r.sources,
                "keywords": r.keywords,
            }
            for r in rulings
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur fiqh: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

@app.get("/api/v2/hadiths/{dimension}")
async def get_hadiths_by_dimension(dimension: str, limit: int = 10, db: Session = Depends(get_db)):
    """Récupère les hadiths par dimension heptuple"""
    try:
        db_service = DatabaseService(db)
        hadiths = db_service.get_hadiths_by_dimension(dimension, limit)
        
        return [HadithModel(
            id=h.id,
            numero_hadith=h.numero_hadith,
            recueil=h.recueil,
            livre=h.livre,
            chapitre=h.chapitre,
            texte_arabe=h.texte_arabe,
            texte_francais=h.texte_francais,
            narrateur=h.narrateur,
            degre_authenticite=h.degre_authenticite,
            dimension_heptuple=h.dimension_heptuple,
            mots_cles=h.mots_cles or [],
            themes=h.themes or [],
            contexte_historique=h.contexte_historique
        ) for h in hadiths]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.get("/api/v2/hadiths/collections")
async def get_hadiths_collections(db: Session = Depends(get_db)):
    """Retourne la liste des recueils avec leur nombre de hadiths (BD réelle)."""
    try:
        db_service = DatabaseService(db)
        return db_service.get_hadiths_collections_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.get("/api/v2/hadiths")
async def search_hadiths_authentic(
    query: Optional[str] = None,
    recueils: Optional[str] = None,  # CSV: "Bukhari,Muslim"
    authenticite: Optional[str] = None,  # ex: "Sahih%"
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Recherche de hadiths authentiques par texte/recueil/authenticité (BD réelle)."""
    try:
        db_service = DatabaseService(db)
        rec_list = [r.strip() for r in recueils.split(',')] if recueils else None
        hadiths = db_service.search_hadiths_authentic(query=query, recueils=rec_list,
                                                      authenticite=authenticite, limit=limit, offset=offset)
        return [
            {
                "id": h.id,
                "numero_hadith": h.numero_hadith,
                "recueil": h.recueil,
                "livre": h.livre,
                "chapitre": h.chapitre,
                "texte_arabe": h.texte_arabe,
                "texte_francais": h.texte_francais,
                "narrateur": h.narrateur,
                "degre_authenticite": h.degre_authenticite,
                "dimension_heptuple": h.dimension_heptuple,
                "mots_cles": h.mots_cles or [],
                "themes": h.themes or [],
                "contexte_historique": h.contexte_historique
            }
            for h in hadiths
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.get("/api/v2/exegeses/{dimension}")
async def get_exegeses_by_dimension(dimension: str, limit: int = 5, db: Session = Depends(get_db)):
    """Récupère les exégèses par dimension heptuple"""
    try:
        db_service = DatabaseService(db)
        exegeses = db_service.get_exegeses_by_dimension(dimension, limit)
        
        return [ExegeseModel(
            id=e.id,
            auteur=e.auteur,
            titre_ouvrage=e.titre_ouvrage,
            epoque=e.epoque,
            ecole_juridique=e.ecole_juridique,
            sourate_id=e.sourate_id,
            verset_debut=e.verset_debut,
            verset_fin=e.verset_fin,
            texte_exegese=e.texte_exegese,
            dimension_heptuple=e.dimension_heptuple,
            themes=e.themes or [],
            langue=e.langue
        ) for e in exegeses]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.post("/api/v2/compare", response_model=Dict)
async def compare_sourates(request: ComparisonRequest, db: Session = Depends(get_db)):
    """Compare plusieurs sourates selon leurs profils heptuple (depuis la BD)"""
    db_service = DatabaseService(db)
    sourates_to_compare = []
    for sourate_id in request.sourate_ids:
        s = db_service.get_sourate_by_id(sourate_id)
        if not s:
            raise HTTPException(status_code=404, detail=f"Sourate {sourate_id} non trouvée")
        profil = db_service.get_profil_heptuple_by_sourate(s.id)
        sourate_dict = {
            "id": s.id,
            "numero": s.numero,
            "nom_arabe": s.nom_arabe,
            "nom_francais": s.nom_francais,
            "type_revelation": s.type_revelation,
            "nombre_versets": s.nombre_versets,
            "profil_heptuple": None
        }
        if profil:
            sourate_dict["profil_heptuple"] = {
                "mysteres": profil.mysteres_score,
                "creation": profil.creation_score,
                "attributs": profil.attributs_score,
                "eschatologie": profil.eschatologie_score,
                "tawhid": profil.tawhid_score,
                "guidance": profil.guidance_score,
                "egarement": profil.egarement_score
            }
        sourates_to_compare.append(sourate_dict)

    if len(sourates_to_compare) < 2:
        raise HTTPException(status_code=400, detail="Au moins 2 sourates requises pour la comparaison")

    similarity_matrix = []
    for i, sourate_a in enumerate(sourates_to_compare):
        row = []
        for j, sourate_b in enumerate(sourates_to_compare):
            if i == j:
                row.append(1.0)
            else:
                similarity = calculate_similarity(
                    sourate_a["profil_heptuple"],
                    sourate_b["profil_heptuple"]
                )
                row.append(similarity)
        similarity_matrix.append(row)

    stats = calculate_comparison_statistics(sourates_to_compare)
    return {
        "sourates": sourates_to_compare,
        "similarity_matrix": similarity_matrix,
        "statistics": stats,
        "insights": generate_comparison_insights(sourates_to_compare)
    }

@app.get("/api/v2/search", response_model=List[SearchResult])
async def search_content(
    query: str,
    search_type: str = "keyword",
    dimensions: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Recherche dans le corpus (fallback LIKE)"""
    db_service = DatabaseService(db)
    results: List[SearchResult] = []
    versets = db_service.search_versets(query, limit=limit)
    for v in versets:
        sourate_obj = db_service.get_sourate_by_id(v.sourate_id)
        sourate_model = Sourate(
            id=sourate_obj.id,
            numero=sourate_obj.numero,
            nom_arabe=sourate_obj.nom_arabe,
            nom_francais=sourate_obj.nom_francais,
            type_revelation=sourate_obj.type_revelation,
            nombre_versets=sourate_obj.nombre_versets
        ) if sourate_obj else Sourate(id=0, numero=0, nom_arabe="", nom_francais="", type_revelation="Mecquoise", nombre_versets=0)
        verset_model = Verset(
            id=v.id,
            sourate_id=v.sourate_id,
            numero_verset=v.numero_verset,
            texte_arabe=v.texte_arabe,
            traduction_francaise=v.traduction_francaise
        )
        results.append(SearchResult(verset=verset_model, sourate=sourate_model))
    return results[:limit]

@app.post("/api/v2/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Soumission de feedback pour améliorer l'IA"""
    
    # Enregistrement du feedback (à implémenter avec base de données)
    feedback_data = {
        "text": request.text,
        "predicted_profile": request.predicted_profile,
        "correct_profile": request.correct_profile,
        "user_notes": request.user_notes,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Calcul de l'erreur pour amélioration du modèle
    error = calculate_prediction_error(request.predicted_profile, request.correct_profile)
    
    return {
        "status": "success",
        "message": "Feedback enregistré avec succès",
        "error_score": error,
        "feedback_id": hashlib.md5(str(feedback_data).encode()).hexdigest()[:8]
    }

@app.get("/api/v2/dimensions")
async def get_dimensions():
    """Retourne les descriptions des 7 dimensions heptuple"""
    return {
        "dimensions": [
            {
                "id": 1,
                "name": "Mystères",
                "description": "Les mystères divins, les lettres non élucidées, les secrets de l'univers",
                "fatiha_verse": 1,
                "keywords": ["غيب", "سر", "مجهول", "mystère", "secret", "inconnu"]
            },
            {
                "id": 2,
                "name": "Création",
                "description": "La création de l'univers, les cieux et la terre, les signes de la création",
                "fatiha_verse": 2,
                "keywords": ["خلق", "السماء", "الأرض", "création", "ciel", "terre"]
            },
            {
                "id": 3,
                "name": "Attributs",
                "description": "Les attributs divins, les noms d'Allah, sa puissance et ses qualités",
                "fatiha_verse": 3,
                "keywords": ["الرحمن", "الرحيم", "العزيز", "miséricordieux", "sage", "puissant"]
            },
            {
                "id": 4,
                "name": "Eschatologie",
                "description": "Le jour de la résurrection, le paradis, l'enfer, l'au-delà",
                "fatiha_verse": 4,
                "keywords": ["القيامة", "الآخرة", "الجنة", "résurrection", "au-delà", "paradis"]
            },
            {
                "id": 5,
                "name": "Tawhid",
                "description": "L'unicité divine, les invocations, l'adoration exclusive à Allah",
                "fatiha_verse": 5,
                "keywords": ["الله", "واحد", "أحد", "dieu", "un", "unique"]
            },
            {
                "id": 6,
                "name": "Guidance",
                "description": "Le droit chemin, la guidance, tout ce qui mène vers le bien",
                "fatiha_verse": 6,
                "keywords": ["الهداية", "الرشد", "الصراط المستقيم", "guidance", "droiture", "chemin"]
            },
            {
                "id": 7,
                "name": "Égarement",
                "description": "Le chemin du diable, des égarés et des maudits",
                "fatiha_verse": 7,
                "keywords": ["الضلال", "الغواية", "الشر", "égarement", "tentation", "mal"]
            }
        ]
    }

# ===== ENDPOINTS D'AUTHENTIFICATION =====

@app.post("/api/v2/auth/register", response_model=UserResponse)
async def register_user(user_create: UserCreate, db: Session = Depends(get_db)):
    """Enregistrement d'un nouvel utilisateur"""
    try:
        user = auth_service.create_user(db, user_create)
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            specialization=user.specialization,
            preferences=user.preferences,
            is_active=user.is_active,
            created_at=user.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, "Erreur d'enregistrement utilisateur")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.post("/api/v2/auth/login", response_model=Token)
async def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    """Connexion d'un utilisateur"""
    try:
        user = auth_service.authenticate_user(db, user_login.username, user_login.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nom d'utilisateur ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        # Mise en cache de la session
        session_data = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "login_time": datetime.utcnow().isoformat()
        }
        redis_service.cache_user_session(user.id, session_data, ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, "Erreur de connexion utilisateur")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.get("/api/v2/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Récupère les informations de l'utilisateur actuel"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        specialization=current_user.specialization,
        preferences=current_user.preferences,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )

@app.post("/api/v2/auth/logout")
async def logout_user(current_user: User = Depends(get_current_active_user)):
    """Déconnexion d'un utilisateur"""
    try:
        redis_service.invalidate_user_session(current_user.id)
        return {"message": "Déconnexion réussie"}
    except Exception as e:
        log_error(e, "Erreur de déconnexion")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

# ===== ENDPOINTS DE RECHERCHE AVANCÉE =====

@app.post("/api/v2/search/universal")
async def universal_search(
    request: UniversalSearchRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Recherche universelle dans Coran, Hadiths et Fiqh"""
    try:
        # Génération du hash de la requête pour le cache
        query_hash = get_text_hash(f"{request.query}_{request.search_types}_{request.filters}")
        
        # Vérification du cache
        cached_results = redis_service.get_cached_search_results(query_hash)
        if cached_results:
            logger.info(f"Résultats de recherche récupérés du cache pour: {request.query}")
            return cached_results
        
        # Recherche dans la base de données
        search_service = SearchService(db)
        results = search_service.search_universal(
            request.query,
            request.search_types,
            request.limit
        )
        
        # Mise en cache des résultats
        redis_service.cache_search_results(query_hash, results, 1800)
        
        # Log de l'action utilisateur
        db_service = DatabaseService(db)
        db_service.log_user_action(
            user_id=current_user.id,
            action="universal_search",
            resource_type="search",
            metadata={"query": request.query, "types": request.search_types}
        )
        
        return results
        
    except Exception as e:
        log_error(e, "Erreur de recherche universelle")
        raise HTTPException(status_code=500, detail="Erreur de recherche")

@app.get("/api/v2/search/coran")
async def search_coran(
    query: str,
    filters: Optional[str] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Recherche avancée dans le Coran"""
    try:
        search_service = SearchService(db)
        filter_dict = json.loads(filters) if filters else None
        results = search_service.search_coran_advanced(query, filter_dict, limit)
        
        # Log de l'action utilisateur
        db_service = DatabaseService(db)
        db_service.log_user_action(
            user_id=current_user.id,
            action="coran_search",
            resource_type="search",
            metadata={"query": query, "filters": filter_dict}
        )
        
        return {"results": results, "total": len(results)}
        
    except Exception as e:
        log_error(e, "Erreur de recherche Coran")
        raise HTTPException(status_code=500, detail="Erreur de recherche Coran")

@app.get("/api/v2/search/hadiths")
async def search_hadiths(
    query: str,
    filters: Optional[str] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Recherche avancée dans les Hadiths Sahih"""
    try:
        search_service = SearchService(db)
        filter_dict = json.loads(filters) if filters else None
        results = search_service.search_hadiths_advanced(query, filter_dict, limit)
        
        # Log de l'action utilisateur
        db_service = DatabaseService(db)
        db_service.log_user_action(
            user_id=current_user.id,
            action="hadiths_search",
            resource_type="search",
            metadata={"query": query, "filters": filter_dict}
        )
        
        return {"results": results, "total": len(results)}
        
    except Exception as e:
        log_error(e, "Erreur de recherche Hadiths")
        raise HTTPException(status_code=500, detail="Erreur de recherche Hadiths")

@app.get("/api/v2/search/fiqh")
async def search_fiqh_advanced(
    query: str,
    filters: Optional[str] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Recherche avancée dans la jurisprudence (Fiqh)"""
    try:
        search_service = SearchService(db)
        filter_dict = json.loads(filters) if filters else None
        results = search_service.search_fiqh_advanced(query, filter_dict, limit)
        
        # Log de l'action utilisateur
        db_service = DatabaseService(db)
        db_service.log_user_action(
            user_id=current_user.id,
            action="fiqh_search",
            resource_type="search",
            metadata={"query": query, "filters": filter_dict}
        )
        
        return {"results": results, "total": len(results)}
        
    except Exception as e:
        log_error(e, "Erreur de recherche Fiqh")
        raise HTTPException(status_code=500, detail="Erreur de recherche Fiqh")

# ===== MODULE FIQH (RITES) =====

@app.get("/api/v2/fiqh/rites")
async def list_fiqh_rites(db: Session = Depends(get_db)):
    """Liste des rites disponibles (BD réelle)."""
    try:
        db_service = DatabaseService(db)
        return {"rites": db_service.list_fiqh_rites()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ===== MODULE INVOCATIONS =====

@app.get("/api/v2/invocations")
async def search_invocations(
    query: Optional[str] = None,
    categories: Optional[str] = None,  # CSV
    tags: Optional[str] = None,  # CSV
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Recherche d'invocations (dou'a) dans la BD avec filtres et pagination."""
    try:
        db_service = DatabaseService(db)
        cat_list = [c.strip() for c in categories.split(',')] if categories else None
        tag_list = [t.strip() for t in tags.split(',')] if tags else None
        invocs = db_service.search_invocations(query=query, categories=cat_list, tags=tag_list, limit=limit, offset=offset)
        return [
            InvocationModel(
                id=i.id,
                titre=i.titre,
                texte_arabe=i.texte_arabe,
                texte_traduit=i.texte_traduit,
                source=i.source,
                categories=i.categories or [],
                tags=i.tags or [],
                temps_recommande=i.temps_recommande or []
            )
            for i in invocs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.get("/api/v2/invocations/categories")
async def list_invocation_categories(db: Session = Depends(get_db)):
    """Liste des catégories d'invocations disponibles."""
    try:
        db_service = DatabaseService(db)
        return {"categories": db_service.list_invocation_categories()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.get("/api/v2/fiqh/rulings")
async def list_fiqh_rulings(
    query: Optional[str] = None,
    rite: Optional[str] = None,
    topic: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Recherche paginée des rulings fiqh (BD réelle)."""
    try:
        db_service = DatabaseService(db)
        rulings = db_service.search_fiqh_rulings(query=query, rite=rite, topic=topic, limit=limit, offset=offset)
        return [
            {
                "id": r.id,
                "rite": r.rite,
                "topic": r.topic,
                "question": r.question,
                "ruling_text": r.ruling_text,
                "evidences": r.evidences or [],
                "sources": r.sources or [],
                "keywords": r.keywords or []
            }
            for r in rulings
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# Fonctions utilitaires
def calculate_similarity(profile_a: Dict, profile_b: Dict) -> float:
    """Calcule la similarité cosinus entre deux profils"""
    values_a = list(profile_a.values())
    values_b = list(profile_b.values())
    
    dot_product = sum(a * b for a, b in zip(values_a, values_b))
    magnitude_a = sum(a * a for a in values_a) ** 0.5
    magnitude_b = sum(b * b for b in values_b) ** 0.5
    
    if magnitude_a * magnitude_b == 0:
        return 0.0
    
    return dot_product / (magnitude_a * magnitude_b)

def calculate_comparison_statistics(sourates: List[Dict]) -> Dict:
    """Calcule les statistiques de comparaison"""
    profiles = [s["profil_heptuple"] for s in sourates]
    
    # Moyennes par dimension
    dimensions = ["mysteres", "creation", "attributs", "eschatologie", "tawhid", "guidance", "egarement"]
    averages = {}
    
    for dim in dimensions:
        values = [p[dim] for p in profiles]
        averages[dim] = sum(values) / len(values)
    
    return {
        "averages": averages,
        "total_sourates": len(sourates),
        "similarity_range": {
            "min": min(calculate_similarity(profiles[i], profiles[j]) 
                      for i in range(len(profiles)) 
                      for j in range(i+1, len(profiles))),
            "max": max(calculate_similarity(profiles[i], profiles[j]) 
                      for i in range(len(profiles)) 
                      for j in range(i+1, len(profiles)))
        }
    }

def generate_comparison_insights(sourates: List[Dict]) -> List[str]:
    """Génère des insights sur la comparaison"""
    insights = []
    
    # Trouver la dimension la plus variable
    profiles = [s["profil_heptuple"] for s in sourates]
    dimensions = ["mysteres", "creation", "attributs", "eschatologie", "tawhid", "guidance", "egarement"]
    
    variances = {}
    for dim in dimensions:
        values = [p[dim] for p in profiles]
        mean_val = sum(values) / len(values)
        variance = sum((v - mean_val) ** 2 for v in values) / len(values)
        variances[dim] = variance
    
    most_variable = max(variances, key=variances.get)
    insights.append(f"La dimension '{most_variable}' présente la plus grande variabilité entre les sourates.")
    
    # Trouver les sourates les plus similaires
    max_similarity = 0
    most_similar_pair = None
    
    for i in range(len(profiles)):
        for j in range(i+1, len(profiles)):
            similarity = calculate_similarity(profiles[i], profiles[j])
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_pair = (sourates[i]["nom_francais"], sourates[j]["nom_francais"])
    
    if most_similar_pair:
        insights.append(f"Les sourates '{most_similar_pair[0]}' et '{most_similar_pair[1]}' sont les plus similaires (similarité: {max_similarity:.2f}).")
    
    return insights

def calculate_prediction_error(predicted: List[int], correct: List[int]) -> float:
    """Calcule l'erreur de prédiction"""
    if len(predicted) != len(correct):
        return 1.0
    
    total_error = sum(abs(p - c) for p, c in zip(predicted, correct))
    max_possible_error = len(predicted) * 100  # 100 est le score max
    
    return total_error / max_possible_error