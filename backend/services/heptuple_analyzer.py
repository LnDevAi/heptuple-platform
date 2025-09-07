import re
import time
from typing import List, Dict, Tuple, Optional
from models import ProfilHeptuple, DimensionType, AnalyseResponse

class HeptupleAnalyzer:
    """Service d'analyse heptuple basé sur la vision de la Fatiha"""
    
    def __init__(self):
        # Mots-clés par dimension
        self.dimension_keywords = {
            DimensionType.MYSTERES: {
                'ar': ['غيب', 'سر', 'مجهول', 'خفية', 'أسرار'],
                'fr': ['mystère', 'secret', 'inconnu', 'caché', 'mystérieux'],
                'en': ['mystery', 'secret', 'unknown', 'hidden', 'mysterious']
            },
            DimensionType.CREATION: {
                'ar': ['خلق', 'خلقنا', 'السماء', 'الأرض', 'الكون'],
                'fr': ['création', 'créé', 'ciel', 'terre', 'univers'],
                'en': ['creation', 'created', 'heaven', 'earth', 'universe']
            },
            DimensionType.ATTRIBUTS: {
                'ar': ['الرحمن', 'الرحيم', 'العزيز', 'الحكيم', 'السميع'],
                'fr': ['miséricordieux', 'sage', 'puissant', 'entendant', 'voyant'],
                'en': ['merciful', 'wise', 'powerful', 'hearing', 'seeing']
            },
            DimensionType.ESCHATOLOGIE: {
                'ar': ['القيامة', 'الآخرة', 'الجنة', 'النار', 'الحساب'],
                'fr': ['résurrection', 'au-delà', 'paradis', 'enfer', 'jugement'],
                'en': ['resurrection', 'hereafter', 'paradise', 'hell', 'judgment']
            },
            DimensionType.TAWHID: {
                'ar': ['الله', 'واحد', 'أحد', 'لا إله إلا الله', 'التوحيد'],
                'fr': ['dieu', 'un', 'unique', 'unicité', 'adoration'],
                'en': ['god', 'one', 'unique', 'oneness', 'worship']
            },
            DimensionType.GUIDANCE: {
                'ar': ['الهداية', 'الرشد', 'الصراط المستقيم', 'الخير', 'الحق'],
                'fr': ['guidance', 'droiture', 'chemin droit', 'bien', 'vérité'],
                'en': ['guidance', 'righteousness', 'straight path', 'good', 'truth']
            },
            DimensionType.EGAREMENT: {
                'ar': ['الضلال', 'الغواية', 'الشر', 'الباطل', 'الظلم'],
                'fr': ['égarement', 'tentation', 'mal', 'faux', 'injustice'],
                'en': ['misguidance', 'temptation', 'evil', 'false', 'injustice']
            }
        }
    
    def detect_language(self, text: str) -> str:
        """Détecte la langue du texte"""
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        total_chars = len(re.sub(r'\s', '', text))
        
        if total_chars == 0:
            return 'fr'
        
        if arabic_chars / total_chars > 0.3:
            return 'ar'
        elif re.search(r'\b(the|and|or|in|on|at)\b', text.lower()):
            return 'en'
        else:
            return 'fr'
    
    def analyze_text_heptuple(self, text: str, include_confidence: bool = True, include_details: bool = False) -> AnalyseResponse:
        """Analyse un texte selon la grille heptuple"""
        start_time = time.time()
        
        # Détection de la langue
        detected_lang = self.detect_language(text)
        
        # Analyse par mots-clés
        scores = self._analyze_keywords(text, detected_lang)
        
        # Normalisation
        normalized_scores = self._normalize_scores(scores)
        
        # Création du profil
        profil = ProfilHeptuple(
            mysteres=normalized_scores[0],
            creation=normalized_scores[1],
            attributs=normalized_scores[2],
            eschatologie=normalized_scores[3],
            tawhid=normalized_scores[4],
            guidance=normalized_scores[5],
            egarement=normalized_scores[6]
        )
        
        # Métadonnées
        dimension_dominante = profil.get_dominant_dimension()
        intensity_max = profil.get_intensity_max()
        processing_time = int((time.time() - start_time) * 1000)
        
        # Scores de confiance
        confidence_scores = None
        if include_confidence:
            confidence_scores = self._calculate_confidence_scores(text, normalized_scores)
        
        # Détails
        details = None
        if include_details:
            details = {
                "language_detected": detected_lang,
                "text_length": len(text),
                "word_count": len(text.split()),
                "analysis_method": "keyword_based"
            }
        
        return AnalyseResponse(
            profil_heptuple=profil,
            confidence_scores=confidence_scores,
            dimension_dominante=DimensionType(dimension_dominante),
            intensity_max=intensity_max,
            details=details,
            processing_time_ms=processing_time,
            version="1.0.0"
        )
    
    def _analyze_keywords(self, text: str, language: str) -> List[float]:
        """Analyse basée sur les mots-clés"""
        text_lower = text.lower()
        scores = [0.0] * 7
        
        for dim_id, keywords in self.dimension_keywords.items():
            lang_keywords = keywords.get(language, keywords.get('fr', []))
            
            for keyword in lang_keywords:
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                matches = len(re.findall(pattern, text_lower))
                scores[dim_id - 1] += matches * 10
        
        return scores
    
    def _normalize_scores(self, scores: List[float]) -> List[int]:
        """Normalise les scores entre 0 et 100"""
        if not scores or max(scores) == 0:
            return [14] * 7
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score == min_score:
            return [50] * 7
        
        normalized = []
        for score in scores:
            normalized_score = int(((score - min_score) / (max_score - min_score)) * 100)
            normalized.append(max(0, min(100, normalized_score)))
        
        return normalized
    
    def _calculate_confidence_scores(self, text: str, scores: List[int]) -> List[float]:
        """Calcule les scores de confiance"""
        confidence_scores = []
        
        for i, score in enumerate(scores):
            text_length_factor = min(1.0, len(text) / 1000)
            score_intensity_factor = score / 100
            
            confidence = (text_length_factor * 0.5 + score_intensity_factor * 0.5)
            confidence_scores.append(round(confidence, 3))
        
        return confidence_scores
