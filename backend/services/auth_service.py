"""
Service d'authentification et de gestion des utilisateurs
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import User
from models import UserCreate, UserLogin, Token, UserResponse

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key-change-in-production-32-chars-min")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Vérifie un mot de passe"""
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Erreur de vérification du mot de passe: {e}")
            return False
    
    def get_password_hash(self, password: str) -> str:
        """Hash un mot de passe"""
        try:
            return self.pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Erreur de hashage du mot de passe: {e}")
            raise HTTPException(status_code=500, detail="Erreur de traitement du mot de passe")
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Crée un token JWT"""
        try:
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Erreur de création du token: {e}")
            raise HTTPException(status_code=500, detail="Erreur de création du token")
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Vérifie un token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.warning(f"Token invalide: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur de vérification du token: {e}")
            return None
    
    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authentifie un utilisateur"""
        try:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                logger.warning(f"Utilisateur non trouvé: {username}")
                return None
            
            if not self.verify_password(password, user.password_hash):
                logger.warning(f"Mot de passe incorrect pour l'utilisateur: {username}")
                return None
            
            if not user.is_active:
                logger.warning(f"Utilisateur inactif: {username}")
                return None
            
            logger.info(f"Utilisateur authentifié avec succès: {username}")
            return user
        except Exception as e:
            logger.error(f"Erreur d'authentification: {e}")
            return None
    
    def create_user(self, db: Session, user_create: UserCreate) -> User:
        """Crée un nouvel utilisateur"""
        try:
            # Vérifier si l'utilisateur existe déjà
            existing_user = db.query(User).filter(
                (User.username == user_create.username) | 
                (User.email == user_create.email)
            ).first()
            
            if existing_user:
                if existing_user.username == user_create.username:
                    raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")
                else:
                    raise HTTPException(status_code=400, detail="Email déjà utilisé")
            
            # Créer le nouvel utilisateur
            hashed_password = self.get_password_hash(user_create.password)
            db_user = User(
                username=user_create.username,
                email=user_create.email,
                password_hash=hashed_password,
                role=user_create.role or "user",
                specialization=user_create.specialization,
                preferences=user_create.preferences or {}
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"Utilisateur créé avec succès: {user_create.username}")
            return db_user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur de création d'utilisateur: {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail="Erreur de création d'utilisateur")
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Récupère un utilisateur par son ID"""
        try:
            return db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"Erreur de récupération d'utilisateur: {e}")
            return None
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """Récupère un utilisateur par son nom d'utilisateur"""
        try:
            return db.query(User).filter(User.username == username).first()
        except Exception as e:
            logger.error(f"Erreur de récupération d'utilisateur: {e}")
            return None
    
    def update_user(self, db: Session, user_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        """Met à jour un utilisateur"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            for key, value in update_data.items():
                if hasattr(user, key) and key != "id":
                    setattr(user, key, value)
            
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
            
            logger.info(f"Utilisateur mis à jour: {user.username}")
            return user
        except Exception as e:
            logger.error(f"Erreur de mise à jour d'utilisateur: {e}")
            db.rollback()
            return None
    
    def deactivate_user(self, db: Session, user_id: int) -> bool:
        """Désactive un utilisateur"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.is_active = False
            user.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Utilisateur désactivé: {user.username}")
            return True
        except Exception as e:
            logger.error(f"Erreur de désactivation d'utilisateur: {e}")
            db.rollback()
            return False
