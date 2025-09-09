from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import re

class DimensionType(int, Enum):
    MYSTERES = 1
    CREATION = 2
    ATTRIBUTS = 3
    ESCHATOLOGIE = 4
    TAWHID = 5
    GUIDANCE = 6
    EGAREMENT = 7

class RevelationType(str, Enum):
    MECQUOISE = "Mecquoise"
    MEDINOISE = "Médinoise"

class ProfilHeptuple(BaseModel):
    mysteres: int = Field(..., ge=0, le=100, description="Score pour la dimension Mystères")
    creation: int = Field(..., ge=0, le=100, description="Score pour la dimension Création")
    attributs: int = Field(..., ge=0, le=100, description="Score pour la dimension Attributs")
    eschatologie: int = Field(..., ge=0, le=100, description="Score pour la dimension Eschatologie")
    tawhid: int = Field(..., ge=0, le=100, description="Score pour la dimension Tawhid")
    guidance: int = Field(..., ge=0, le=100, description="Score pour la dimension Guidance")
    egarement: int = Field(..., ge=0, le=100, description="Score pour la dimension Égarement")
    
    def to_array(self) -> List[int]:
        """Convertit le profil en tableau"""
        return [
            self.mysteres, self.creation, self.attributs,
            self.eschatologie, self.tawhid, self.guidance, self.egarement
        ]
    
    def get_dimension_names(self) -> List[str]:
        """Retourne les noms des dimensions"""
        return [
            "Mystères", "Création", "Attributs", 
            "Eschatologie", "Tawhid", "Guidance", "Égarement"
        ]
    
    def get_dominant_dimension(self) -> int:
        """Retourne la dimension dominante (1-7)"""
        scores = self.to_array()
        return scores.index(max(scores)) + 1
    
    def get_intensity_max(self) -> int:
        """Retourne l'intensité maximale"""
        return max(self.to_array())

class Sourate(BaseModel):
    id: Optional[int] = None
    numero: int = Field(..., ge=1, le=114, description="Numéro de la sourate")
    nom_arabe: str = Field(..., description="Nom arabe de la sourate")
    nom_francais: str = Field(..., description="Nom français de la sourate")
    type_revelation: RevelationType = Field(..., description="Type de révélation")
    nombre_versets: int = Field(..., gt=0, description="Nombre de versets")
    ordre_revelation: Optional[int] = Field(None, description="Ordre de révélation")
    profil_heptuple: Optional[ProfilHeptuple] = Field(None, description="Profil heptuple de la sourate")
    themes: List[str] = Field(default_factory=list, description="Thèmes principaux")

class Verset(BaseModel):
    id: Optional[int] = None
    sourate_id: int = Field(..., description="ID de la sourate")
    numero_verset: int = Field(..., description="Numéro du verset")
    texte_arabe: str = Field(..., description="Texte arabe du verset")
    traduction_francaise: Optional[str] = Field(None, description="Traduction française")
    dimension_principale: Optional[DimensionType] = Field(None, description="Dimension principale")
    dimensions_secondaires: List[DimensionType] = Field(default_factory=list, description="Dimensions secondaires")
    mots_cles: List[str] = Field(default_factory=list, description="Mots-clés du verset")

class AnalyseRequest(BaseModel):
    texte: str = Field(..., min_length=1, max_length=10000, description="Texte à analyser")
    langue: str = Field(default="auto", pattern="^(ar|fr|en|auto)$", description="Langue du texte")
    include_confidence: bool = Field(default=True, description="Inclure les scores de confiance")
    include_details: bool = Field(default=False, description="Inclure les détails d'analyse")
    
    @validator('texte')
    def validate_text(cls, v):
        """Validation et nettoyage du texte"""
        if not v.strip():
            raise ValueError("Le texte ne peut pas être vide")
        
        # Suppression des caractères dangereux
        cleaned = re.sub(r'[<>"\']', '', v)
        return cleaned.strip()

class AnalyseResponse(BaseModel):
    profil_heptuple: ProfilHeptuple = Field(..., description="Profil heptuple calculé")
    confidence_scores: Optional[List[float]] = Field(None, description="Scores de confiance par dimension")
    dimension_dominante: DimensionType = Field(..., description="Dimension dominante")
    intensity_max: int = Field(..., description="Intensité maximale")
    details: Optional[Dict] = Field(None, description="Détails de l'analyse")
    processing_time_ms: int = Field(..., description="Temps de traitement en millisecondes")
    version: str = Field(default="1.0.0", description="Version du modèle utilisé")

class ComparisonRequest(BaseModel):
    sourate_ids: List[int] = Field(..., min_items=2, max_items=10, description="IDs des sourates à comparer")
    dimensions_focus: Optional[List[DimensionType]] = Field(None, description="Dimensions sur lesquelles se concentrer")
    include_statistics: bool = Field(default=True, description="Inclure les statistiques")

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Requête de recherche")
    search_type: str = Field(default="semantic", pattern="^(semantic|keyword|hybrid)$", description="Type de recherche")
    dimensions_filter: Optional[List[DimensionType]] = Field(None, description="Filtre par dimensions")
    sourates_filter: Optional[List[int]] = Field(None, description="Filtre par sourates")
    limit: int = Field(default=20, ge=1, le=100, description="Nombre maximum de résultats")

class SearchResult(BaseModel):
    verset: Verset = Field(..., description="Verset trouvé")
    sourate: Sourate = Field(..., description="Sourate du verset")
    similarity_score: Optional[float] = Field(None, description="Score de similarité")
    score: Optional[float] = Field(None, description="Score de pertinence")
    highlights: Optional[Dict[str, List[str]]] = Field(None, description="Mots surlignés")

class FeedbackRequest(BaseModel):
    analyse_id: int
    rating: int = Field(..., ge=1, le=5)
    commentaire: Optional[str] = None
    suggestions: Optional[str] = None

class HadithModel(BaseModel):
    id: Optional[int] = None
    numero_hadith: str
    recueil: str
    livre: Optional[str] = None
    chapitre: Optional[str] = None
    texte_arabe: str
    texte_francais: str
    texte_anglais: Optional[str] = None
    narrateur: Optional[str] = None
    degre_authenticite: Optional[str] = None
    dimension_heptuple: Optional[str] = None
    mots_cles: Optional[List[str]] = None
    themes: Optional[List[str]] = None
    contexte_historique: Optional[str] = None

class ExegeseModel(BaseModel):
    id: Optional[int] = None
    auteur: str
    titre_ouvrage: str
    epoque: Optional[str] = None
    ecole_juridique: Optional[str] = None
    sourate_id: Optional[int] = None
    verset_debut: Optional[int] = None
    verset_fin: Optional[int] = None
    texte_exegese: str
    dimension_heptuple: Optional[str] = None
    themes: Optional[List[str]] = None
    langue: Optional[str] = 'ar'

class CitationModel(BaseModel):
    id: Optional[int] = None
    type_citation: str
    auteur: Optional[str] = None
    source: Optional[str] = None
    epoque: Optional[str] = None
    texte_original: str
    texte_traduit: Optional[str] = None
    contexte: Optional[str] = None
    dimension_heptuple: Optional[str] = None
    pertinence_score: Optional[float] = 0.5
    themes: Optional[List[str]] = None
    verified: Optional[bool] = False

class HistoireModel(BaseModel):
    id: Optional[int] = None
    titre: str
    epoque: Optional[str] = None
    personnages: Optional[List[str]] = None
    lieu: Optional[str] = None
    contexte_historique: Optional[str] = None
    recit_complet: str
    enseignements: Optional[List[str]] = None
    dimension_heptuple: Optional[str] = None
    sources: Optional[List[str]] = None
    degre_authenticite: Optional[str] = None
    themes: Optional[List[str]] = None

class AnalyseEnrichie(BaseModel):
    analyse: AnalyseResponse
    hadiths: List[HadithModel] = []
    exegeses: List[ExegeseModel] = []
    citations: List[CitationModel] = []
    histoires: List[HistoireModel] = []
    score_enrichissement: float = Field(..., description="Score d'enrichissement")

# Modèle d'invocation (dou'a)
class InvocationModel(BaseModel):
    id: Optional[int] = None
    titre: str
    texte_arabe: str
    texte_traduit: Optional[str] = None
    source: Optional[str] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    temps_recommande: Optional[List[str]] = None  # matin, soir, après-prière, etc.

# Modèles d'authentification
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nom d'utilisateur")
    email: str = Field(..., description="Adresse email")
    password: str = Field(..., min_length=8, description="Mot de passe")
    role: Optional[str] = Field(default="user", description="Rôle de l'utilisateur")
    specialization: Optional[str] = Field(None, description="Spécialisation")
    preferences: Optional[Dict] = Field(default_factory=dict, description="Préférences utilisateur")

class UserLogin(BaseModel):
    username: str = Field(..., description="Nom d'utilisateur")
    password: str = Field(..., description="Mot de passe")

class Token(BaseModel):
    access_token: str = Field(..., description="Token d'accès")
    token_type: str = Field(default="bearer", description="Type de token")
    expires_in: int = Field(..., description="Durée d'expiration en secondes")

class UserResponse(BaseModel):
    id: int = Field(..., description="ID de l'utilisateur")
    username: str = Field(..., description="Nom d'utilisateur")
    email: str = Field(..., description="Adresse email")
    role: str = Field(..., description="Rôle")
    specialization: Optional[str] = Field(None, description="Spécialisation")
    preferences: Dict = Field(default_factory=dict, description="Préférences")
    is_active: bool = Field(..., description="Statut actif")
    created_at: datetime = Field(..., description="Date de création")

# Modèles de recherche avancée
class UniversalSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Requête de recherche")
    search_types: List[str] = Field(default=["coran", "hadiths", "fiqh"], description="Types de recherche")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filtres de recherche")
    limit: int = Field(default=20, ge=1, le=100, description="Nombre maximum de résultats")

class SearchFilters(BaseModel):
    sourate_id: Optional[int] = Field(None, description="ID de la sourate")
    dimension: Optional[int] = Field(None, description="Dimension heptuple")
    recueil: Optional[str] = Field(None, description="Recueil de hadiths")
    authenticite: Optional[str] = Field(None, description="Degré d'authenticité")
    rite: Optional[str] = Field(None, description="Rite juridique")
    topic: Optional[str] = Field(None, description="Sujet de jurisprudence")
