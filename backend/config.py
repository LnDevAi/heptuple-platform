"""
Configuration automatique des ports et de l'environnement
"""
import os
import socket
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Charger le fichier .env du répertoire backend
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

logger = logging.getLogger(__name__)

class Config:
    """Configuration automatique de l'application"""
    
    def __init__(self):
        self._find_available_ports()
        self._load_environment_config()
    
    def _find_available_ports(self):
        """Trouve automatiquement des ports disponibles"""
        self.API_PORT = self._get_available_port(8000, 8100)
        self.DB_PORT = self._get_available_port(5432, 5500)
        self.REDIS_PORT = self._get_available_port(6379, 6500)
        self.ELASTICSEARCH_PORT = self._get_available_port(9200, 9300)
        self.FRONTEND_PORT = self._get_available_port(3000, 3100)
        self.NGINX_PORT = self._get_available_port(8080, 8200)
        
        logger.info(f"Ports assignés automatiquement:")
        logger.info(f"  API: {self.API_PORT}")
        logger.info(f"  DB: {self.DB_PORT}")
        logger.info(f"  Redis: {self.REDIS_PORT}")
        logger.info(f"  Elasticsearch: {self.ELASTICSEARCH_PORT}")
        logger.info(f"  Frontend: {self.FRONTEND_PORT}")
        logger.info(f"  Nginx: {self.NGINX_PORT}")
    
    def _get_available_port(self, start_port: int, end_port: int) -> int:
        """Trouve un port disponible dans une plage donnée"""
        for port in range(start_port, end_port):
            if self._is_port_available(port):
                return port
        
        # Si aucun port n'est trouvé, utiliser le port de base
        logger.warning(f"Aucun port disponible dans la plage {start_port}-{end_port}, utilisation du port {start_port}")
        return start_port
    
    def _is_port_available(self, port: int) -> bool:
        """Vérifie si un port est disponible"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def _load_environment_config(self):
        """Charge la configuration depuis les variables d'environnement"""
        # Configuration de la base de données
        self.DB_HOST = os.getenv("DB_HOST", "localhost")
        self.DB_NAME = os.getenv("DB_NAME", "heptuple_db")
        self.DB_USER = os.getenv("DB_USER", "heptuple_user")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", "heptuple_pass")
        
        # Configuration Redis
        self.REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
        self.REDIS_DB = int(os.getenv("REDIS_DB", "0"))
        
        # Configuration Elasticsearch
        self.ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
        self.ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "")
        
        # Configuration de sécurité
        self.SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production-32-chars-min")
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key-change-in-production-32-chars-min")
        
        # Configuration CORS
        self.ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", f"http://localhost:{self.FRONTEND_PORT},http://localhost:{self.NGINX_PORT}").split(",")
        self.ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
        
        # Configuration de l'environnement
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
        # Configuration de l'instance
        self.INSTANCE_ID = os.getenv("INSTANCE_ID", "0")
    
    def get_database_url(self) -> str:
        """Retourne l'URL de connexion à la base de données"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    def get_redis_url(self) -> str:
        """Retourne l'URL de connexion à Redis"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        else:
            return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    def get_elasticsearch_url(self) -> str:
        """Retourne l'URL de connexion à Elasticsearch"""
        if self.ELASTICSEARCH_PASSWORD:
            return f"https://{self.ELASTICSEARCH_HOST}:{self.ELASTICSEARCH_PORT}"
        else:
            return f"http://{self.ELASTICSEARCH_HOST}:{self.ELASTICSEARCH_PORT}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Retourne la configuration sous forme de dictionnaire"""
        return {
            "ports": {
                "api": self.API_PORT,
                "db": self.DB_PORT,
                "redis": self.REDIS_PORT,
                "elasticsearch": self.ELASTICSEARCH_PORT,
                "frontend": self.FRONTEND_PORT,
                "nginx": self.NGINX_PORT
            },
            "database": {
                "host": self.DB_HOST,
                "port": self.DB_PORT,
                "name": self.DB_NAME,
                "user": self.DB_USER,
                "url": self.get_database_url()
            },
            "redis": {
                "host": self.REDIS_HOST,
                "port": self.REDIS_PORT,
                "password": self.REDIS_PASSWORD,
                "db": self.REDIS_DB,
                "url": self.get_redis_url()
            },
            "elasticsearch": {
                "host": self.ELASTICSEARCH_HOST,
                "port": self.ELASTICSEARCH_PORT,
                "password": self.ELASTICSEARCH_PASSWORD,
                "url": self.get_elasticsearch_url()
            },
            "security": {
                "secret_key": self.SECRET_KEY,
                "jwt_secret_key": self.JWT_SECRET_KEY,
                "allowed_origins": self.ALLOWED_ORIGINS,
                "allowed_hosts": self.ALLOWED_HOSTS
            },
            "environment": {
                "name": self.ENVIRONMENT,
                "debug": self.DEBUG,
                "log_level": self.LOG_LEVEL,
                "instance_id": self.INSTANCE_ID
            }
        }

# Instance globale de configuration
config = Config()
