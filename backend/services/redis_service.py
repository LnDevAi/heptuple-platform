"""
Service Redis pour le cache et la gestion des sessions
"""
import os
import json
import logging
from typing import Optional, Dict, Any, List
import redis
from datetime import timedelta

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_password = os.getenv("REDIS_PASSWORD", "")
        self.redis_db = int(os.getenv("REDIS_DB", "0"))
        
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password if self.redis_password else None,
                db=self.redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test de connexion
            self.redis_client.ping()
            logger.info("Connexion Redis établie avec succès")
        except Exception as e:
            logger.error(f"Erreur de connexion Redis: {e}")
            self.redis_client = None
    
    def is_connected(self) -> bool:
        """Vérifie si Redis est connecté"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
        except Exception as e:
            logger.error(f"Redis non connecté: {e}")
        return False
    
    def set_cache(self, key: str, value: Any, expire_seconds: int = 3600) -> bool:
        """Met en cache une valeur"""
        try:
            if not self.is_connected():
                return False
            
            # Sérialisation JSON
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, ensure_ascii=False)
            else:
                serialized_value = str(value)
            
            self.redis_client.setex(key, expire_seconds, serialized_value)
            logger.debug(f"Cache mis à jour: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur de mise en cache: {e}")
            return False
    
    def get_cache(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        try:
            if not self.is_connected():
                return None
            
            value = self.redis_client.get(key)
            if value is None:
                return None
            
            # Tentative de désérialisation JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.error(f"Erreur de récupération du cache: {e}")
            return None
    
    def delete_cache(self, key: str) -> bool:
        """Supprime une valeur du cache"""
        try:
            if not self.is_connected():
                return False
            
            result = self.redis_client.delete(key)
            logger.debug(f"Cache supprimé: {key}")
            return result > 0
            
        except Exception as e:
            logger.error(f"Erreur de suppression du cache: {e}")
            return False
    
    def cache_analysis(self, text_hash: str, analysis_result: Dict[str, Any], expire_seconds: int = 7200) -> bool:
        """Met en cache un résultat d'analyse"""
        cache_key = f"analysis:{text_hash}"
        return self.set_cache(cache_key, analysis_result, expire_seconds)
    
    def get_cached_analysis(self, text_hash: str) -> Optional[Dict[str, Any]]:
        """Récupère un résultat d'analyse du cache"""
        cache_key = f"analysis:{text_hash}"
        return self.get_cache(cache_key)
    
    def cache_search_results(self, query_hash: str, search_results: Dict[str, Any], expire_seconds: int = 1800) -> bool:
        """Met en cache des résultats de recherche"""
        cache_key = f"search:{query_hash}"
        return self.set_cache(cache_key, search_results, expire_seconds)
    
    def get_cached_search_results(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """Récupère des résultats de recherche du cache"""
        cache_key = f"search:{query_hash}"
        return self.get_cache(cache_key)
    
    def cache_user_session(self, user_id: int, session_data: Dict[str, Any], expire_seconds: int = 1800) -> bool:
        """Met en cache une session utilisateur"""
        cache_key = f"session:{user_id}"
        return self.set_cache(cache_key, session_data, expire_seconds)
    
    def get_user_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Récupère une session utilisateur du cache"""
        cache_key = f"session:{user_id}"
        return self.get_cache(cache_key)
    
    def invalidate_user_session(self, user_id: int) -> bool:
        """Invalide une session utilisateur"""
        cache_key = f"session:{user_id}"
        return self.delete_cache(cache_key)
    
    def cache_sourates(self, sourates_data: List[Dict[str, Any]], expire_seconds: int = 3600) -> bool:
        """Met en cache la liste des sourates"""
        cache_key = "sourates:all"
        return self.set_cache(cache_key, sourates_data, expire_seconds)
    
    def get_cached_sourates(self) -> Optional[List[Dict[str, Any]]]:
        """Récupère la liste des sourates du cache"""
        cache_key = "sourates:all"
        return self.get_cache(cache_key)
    
    def cache_sourate(self, sourate_id: int, sourate_data: Dict[str, Any], expire_seconds: int = 3600) -> bool:
        """Met en cache une sourate spécifique"""
        cache_key = f"sourate:{sourate_id}"
        return self.set_cache(cache_key, sourate_data, expire_seconds)
    
    def get_cached_sourate(self, sourate_id: int) -> Optional[Dict[str, Any]]:
        """Récupère une sourate spécifique du cache"""
        cache_key = f"sourate:{sourate_id}"
        return self.get_cache(cache_key)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques du cache"""
        try:
            if not self.is_connected():
                return {"connected": False}
            
            info = self.redis_client.info()
            return {
                "connected": True,
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0)
            }
            
        except Exception as e:
            logger.error(f"Erreur de récupération des stats Redis: {e}")
            return {"connected": False, "error": str(e)}
    
    def clear_all_cache(self) -> bool:
        """Vide tout le cache"""
        try:
            if not self.is_connected():
                return False
            
            self.redis_client.flushdb()
            logger.info("Cache Redis vidé")
            return True
            
        except Exception as e:
            logger.error(f"Erreur de vidage du cache: {e}")
            return False
    
    def get_keys_pattern(self, pattern: str) -> List[str]:
        """Récupère les clés correspondant à un pattern"""
        try:
            if not self.is_connected():
                return []
            
            return self.redis_client.keys(pattern)
            
        except Exception as e:
            logger.error(f"Erreur de récupération des clés: {e}")
            return []
    
    def increment_counter(self, key: str, expire_seconds: int = 86400) -> int:
        """Incrémente un compteur"""
        try:
            if not self.is_connected():
                return 0
            
            count = self.redis_client.incr(key)
            if count == 1:  # Première incrémentation
                self.redis_client.expire(key, expire_seconds)
            
            return count
            
        except Exception as e:
            logger.error(f"Erreur d'incrémentation: {e}")
            return 0
