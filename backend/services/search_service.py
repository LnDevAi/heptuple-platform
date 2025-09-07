"""
Service de recherche avancée pour Coran, Hadiths et Fiqh
"""
import logging
import re
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, text
from database import (
    DatabaseService, Sourate, Verset, Hadith, Exegese, 
    Citation, Histoire, FiqhRuling, ProfilHeptuple
)
from models import SearchResult, Sourate as SourateModel, Verset as VersetModel

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, db: Session):
        self.db = db
        self.db_service = DatabaseService(db)
    
    def search_coran_advanced(self, query: str, filters: Optional[Dict[str, Any]] = None, limit: int = 20) -> List[SearchResult]:
        """Recherche avancée dans le Coran"""
        try:
            results = []
            query_clean = query.strip()
            
            if not query_clean:
                return results
            
            # Recherche dans les versets
            versets = self._search_versets(query_clean, filters, limit)
            
            for verset in versets:
                sourate = self.db_service.get_sourate_by_id(verset.sourate_id)
                if sourate:
                    verset_model = VersetModel(
                        id=verset.id,
                        sourate_id=verset.sourate_id,
                        numero_verset=verset.numero_verset,
                        texte_arabe=verset.texte_arabe,
                        traduction_francaise=verset.traduction_francaise
                    )
                    
                    sourate_model = SourateModel(
                        id=sourate.id,
                        numero=sourate.numero,
                        nom_arabe=sourate.nom_arabe,
                        nom_francais=sourate.nom_francais,
                        type_revelation=sourate.type_revelation,
                        nombre_versets=sourate.nombre_versets
                    )
                    
                    # Calcul du score de pertinence
                    relevance_score = self._calculate_relevance_score(query_clean, verset)
                    
                    result = SearchResult(
                        verset=verset_model,
                        sourate=sourate_model,
                        similarity_score=relevance_score,
                        score=relevance_score,
                        highlights=self._generate_highlights(query_clean, verset)
                    )
                    results.append(result)
            
            # Tri par score de pertinence
            results.sort(key=lambda x: x.score or 0, reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Erreur de recherche Coran: {e}")
            return []
    
    def search_hadiths_advanced(self, query: str, filters: Optional[Dict[str, Any]] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Recherche avancée dans les Hadiths Sahih"""
        try:
            results = []
            query_clean = query.strip()
            
            if not query_clean:
                return results
            
            # Construction de la requête
            q = f"%{query_clean}%"
            query_builder = self.db.query(Hadith).filter(
                or_(
                    Hadith.texte_arabe.ilike(q),
                    Hadith.texte_francais.ilike(q),
                    Hadith.narrateur.ilike(q),
                    Hadith.recueil.ilike(q)
                )
            )
            
            # Filtres additionnels
            if filters:
                if filters.get("recueil"):
                    query_builder = query_builder.filter(Hadith.recueil.ilike(f"%{filters['recueil']}%"))
                
                if filters.get("authenticite"):
                    query_builder = query_builder.filter(Hadith.degre_authenticite == filters["authenticite"])
                
                if filters.get("dimension"):
                    query_builder = query_builder.filter(Hadith.dimension_heptuple == filters["dimension"])
            
            hadiths = query_builder.limit(limit).all()
            
            for hadith in hadiths:
                result = {
                    "id": hadith.id,
                    "numero_hadith": hadith.numero_hadith,
                    "recueil": hadith.recueil,
                    "livre": hadith.livre,
                    "chapitre": hadith.chapitre,
                    "texte_arabe": hadith.texte_arabe,
                    "texte_francais": hadith.texte_francais,
                    "narrateur": hadith.narrateur,
                    "degre_authenticite": hadith.degre_authenticite,
                    "dimension_heptuple": hadith.dimension_heptuple,
                    "mots_cles": hadith.mots_cles or [],
                    "themes": hadith.themes or [],
                    "contexte_historique": hadith.contexte_historique,
                    "relevance_score": self._calculate_hadith_relevance_score(query_clean, hadith),
                    "highlights": self._generate_hadith_highlights(query_clean, hadith)
                }
                results.append(result)
            
            # Tri par score de pertinence
            results.sort(key=lambda x: x["relevance_score"], reverse=True)
            return results
            
        except Exception as e:
            logger.error(f"Erreur de recherche Hadiths: {e}")
            return []
    
    def search_fiqh_advanced(self, query: str, filters: Optional[Dict[str, Any]] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Recherche avancée dans la jurisprudence (Fiqh)"""
        try:
            results = []
            query_clean = query.strip()
            
            if not query_clean:
                return results
            
            # Construction de la requête
            q = f"%{query_clean}%"
            query_builder = self.db.query(FiqhRuling).filter(
                or_(
                    FiqhRuling.topic.ilike(q),
                    FiqhRuling.question.ilike(q),
                    FiqhRuling.ruling_text.ilike(q)
                )
            )
            
            # Filtres additionnels
            if filters:
                if filters.get("rite"):
                    query_builder = query_builder.filter(FiqhRuling.rite == filters["rite"])
                
                if filters.get("topic"):
                    query_builder = query_builder.filter(FiqhRuling.topic.ilike(f"%{filters['topic']}%"))
            
            rulings = query_builder.limit(limit).all()
            
            for ruling in rulings:
                result = {
                    "id": ruling.id,
                    "rite": ruling.rite,
                    "topic": ruling.topic,
                    "question": ruling.question,
                    "ruling_text": ruling.ruling_text,
                    "evidences": ruling.evidences or [],
                    "sources": ruling.sources or [],
                    "keywords": ruling.keywords or [],
                    "relevance_score": self._calculate_fiqh_relevance_score(query_clean, ruling),
                    "highlights": self._generate_fiqh_highlights(query_clean, ruling)
                }
                results.append(result)
            
            # Tri par score de pertinence
            results.sort(key=lambda x: x["relevance_score"], reverse=True)
            return results
            
        except Exception as e:
            logger.error(f"Erreur de recherche Fiqh: {e}")
            return []
    
    def search_universal(self, query: str, search_types: List[str] = None, limit: int = 20) -> Dict[str, List[Any]]:
        """Recherche universelle dans tous les corpus"""
        try:
            if search_types is None:
                search_types = ["coran", "hadiths", "fiqh"]
            
            results = {
                "coran": [],
                "hadiths": [],
                "fiqh": [],
                "total_results": 0
            }
            
            query_clean = query.strip()
            if not query_clean:
                return results
            
            # Recherche dans le Coran
            if "coran" in search_types:
                coran_results = self.search_coran_advanced(query_clean, limit=limit//3)
                results["coran"] = coran_results
            
            # Recherche dans les Hadiths
            if "hadiths" in search_types:
                hadith_results = self.search_hadiths_advanced(query_clean, limit=limit//3)
                results["hadiths"] = hadith_results
            
            # Recherche dans le Fiqh
            if "fiqh" in search_types:
                fiqh_results = self.search_fiqh_advanced(query_clean, limit=limit//3)
                results["fiqh"] = fiqh_results
            
            # Calcul du total
            results["total_results"] = len(results["coran"]) + len(results["hadiths"]) + len(results["fiqh"])
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur de recherche universelle: {e}")
            return {"coran": [], "hadiths": [], "fiqh": [], "total_results": 0}
    
    def _search_versets(self, query: str, filters: Optional[Dict[str, Any]], limit: int) -> List[Verset]:
        """Recherche dans les versets avec filtres"""
        try:
            q = f"%{query}%"
            query_builder = self.db.query(Verset).filter(
                or_(
                    Verset.texte_arabe.ilike(q),
                    Verset.traduction_francaise.ilike(q)
                )
            )
            
            # Filtres additionnels
            if filters:
                if filters.get("sourate_id"):
                    query_builder = query_builder.filter(Verset.sourate_id == filters["sourate_id"])
                
                if filters.get("dimension"):
                    query_builder = query_builder.filter(Verset.dimension_principale == filters["dimension"])
            
            return query_builder.limit(limit).all()
            
        except Exception as e:
            logger.error(f"Erreur de recherche versets: {e}")
            return []
    
    def _calculate_relevance_score(self, query: str, verset: Verset) -> float:
        """Calcule le score de pertinence pour un verset"""
        try:
            score = 0.0
            query_lower = query.lower()
            
            # Score basé sur la correspondance dans le texte arabe
            if verset.texte_arabe:
                arabic_matches = len(re.findall(re.escape(query_lower), verset.texte_arabe.lower()))
                score += arabic_matches * 2.0
            
            # Score basé sur la correspondance dans la traduction
            if verset.traduction_francaise:
                french_matches = len(re.findall(re.escape(query_lower), verset.traduction_francaise.lower()))
                score += french_matches * 1.5
            
            # Bonus pour correspondance exacte
            if query_lower in (verset.texte_arabe or "").lower():
                score += 1.0
            if query_lower in (verset.traduction_francaise or "").lower():
                score += 0.5
            
            return min(score, 10.0)  # Score maximum de 10
            
        except Exception as e:
            logger.error(f"Erreur de calcul de score: {e}")
            return 0.0
    
    def _calculate_hadith_relevance_score(self, query: str, hadith: Hadith) -> float:
        """Calcule le score de pertinence pour un hadith"""
        try:
            score = 0.0
            query_lower = query.lower()
            
            # Score basé sur la correspondance dans le texte
            if hadith.texte_francais:
                french_matches = len(re.findall(re.escape(query_lower), hadith.texte_francais.lower()))
                score += french_matches * 2.0
            
            if hadith.texte_arabe:
                arabic_matches = len(re.findall(re.escape(query_lower), hadith.texte_arabe.lower()))
                score += arabic_matches * 1.5
            
            # Bonus pour correspondance dans le narrateur
            if hadith.narrateur and query_lower in hadith.narrateur.lower():
                score += 1.0
            
            # Bonus pour correspondance dans le recueil
            if hadith.recueil and query_lower in hadith.recueil.lower():
                score += 0.5
            
            return min(score, 10.0)
            
        except Exception as e:
            logger.error(f"Erreur de calcul de score hadith: {e}")
            return 0.0
    
    def _calculate_fiqh_relevance_score(self, query: str, ruling: FiqhRuling) -> float:
        """Calcule le score de pertinence pour un ruling fiqh"""
        try:
            score = 0.0
            query_lower = query.lower()
            
            # Score basé sur la correspondance dans le ruling
            if ruling.ruling_text:
                ruling_matches = len(re.findall(re.escape(query_lower), ruling.ruling_text.lower()))
                score += ruling_matches * 2.0
            
            # Score basé sur la correspondance dans la question
            if ruling.question:
                question_matches = len(re.findall(re.escape(query_lower), ruling.question.lower()))
                score += question_matches * 1.5
            
            # Score basé sur la correspondance dans le topic
            if ruling.topic:
                topic_matches = len(re.findall(re.escape(query_lower), ruling.topic.lower()))
                score += topic_matches * 1.0
            
            return min(score, 10.0)
            
        except Exception as e:
            logger.error(f"Erreur de calcul de score fiqh: {e}")
            return 0.0
    
    def _generate_highlights(self, query: str, verset: Verset) -> Dict[str, List[str]]:
        """Génère les highlights pour un verset"""
        try:
            highlights = {"arabe": [], "francais": []}
            query_clean = query.strip()
            
            if verset.texte_arabe and query_clean in verset.texte_arabe:
                highlights["arabe"].append(verset.texte_arabe)
            
            if verset.traduction_francaise and query_clean in verset.traduction_francaise:
                highlights["francais"].append(verset.traduction_francaise)
            
            return highlights
            
        except Exception as e:
            logger.error(f"Erreur de génération highlights: {e}")
            return {"arabe": [], "francais": []}
    
    def _generate_hadith_highlights(self, query: str, hadith: Hadith) -> Dict[str, List[str]]:
        """Génère les highlights pour un hadith"""
        try:
            highlights = {"francais": [], "arabe": []}
            query_clean = query.strip()
            
            if hadith.texte_francais and query_clean in hadith.texte_francais:
                highlights["francais"].append(hadith.texte_francais)
            
            if hadith.texte_arabe and query_clean in hadith.texte_arabe:
                highlights["arabe"].append(hadith.texte_arabe)
            
            return highlights
            
        except Exception as e:
            logger.error(f"Erreur de génération highlights hadith: {e}")
            return {"francais": [], "arabe": []}
    
    def _generate_fiqh_highlights(self, query: str, ruling: FiqhRuling) -> Dict[str, List[str]]:
        """Génère les highlights pour un ruling fiqh"""
        try:
            highlights = {"ruling": [], "question": []}
            query_clean = query.strip()
            
            if ruling.ruling_text and query_clean in ruling.ruling_text:
                highlights["ruling"].append(ruling.ruling_text)
            
            if ruling.question and query_clean in ruling.question:
                highlights["question"].append(ruling.question)
            
            return highlights
            
        except Exception as e:
            logger.error(f"Erreur de génération highlights fiqh: {e}")
            return {"ruling": [], "question": []}
