# 🕌 Plateforme Vision Heptuple - Analyse Exégétique Coranique

Plateforme d'analyse exégétique basée sur la **Vision Heptuple de la Fatiha** pour l'étude du Coran selon les 7 dimensions spirituelles.

## 🎯 **Vision du Projet**

Cette plateforme révolutionnaire propose une nouvelle approche d'analyse coranique basée sur la structure de la sourate Al-Fatiha comme clé de compréhension de l'ensemble du Coran :

1. **Mystères** (Verset 1) - Les secrets divins et lettres non élucidées
2. **Création** (Verset 2) - L'univers, les cieux et la terre
3. **Attributs** (Verset 3) - Les noms et qualités d'Allah
4. **Eschatologie** (Verset 4) - Le jour du jugement et l'au-delà
5. **Tawhid** (Verset 5) - L'unicité divine et l'adoration
6. **Guidance** (Verset 6) - Le droit chemin et la guidance
7. **Égarement** (Verset 7) - Les chemins de l'égarement

## 🏗️ **Architecture Technique**

### **Stack Technologique**
- **Backend** : FastAPI (Python 3.11+)
- **Frontend** : React 18 + Tailwind CSS
- **Base de données** : PostgreSQL 15
- **Cache** : Redis 7
- **Recherche** : Elasticsearch 8
- **Reverse Proxy** : NGINX
- **Containerisation** : Docker + Docker Compose

### **Services**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │    │     API     │    │ PostgreSQL  │
│   React     │◄──►│   FastAPI   │◄──►│   Database  │
│   Port Auto │    │  Port Auto  │    │  Port Auto  │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       │                   ▼                   │
       │            ┌─────────────┐            │
       │            │    Redis    │            │
       │            │    Cache    │            │
       │            └─────────────┘            │
       │                                       │
       ▼                                       ▼
┌─────────────┐                        ┌─────────────┐
│    NGINX    │                        │Elasticsearch│
│ Load Balancer│                        │   Search    │
│  Port Auto  │                        │  Port Auto  │
└─────────────┘                        └─────────────┘
```

## 🚀 **Installation et Déploiement**

### **Prérequis**
- Docker 20.10+
- Docker Compose 2.0+
- Git

### **Déploiement Rapide**

1. **Cloner le projet**
```bash
git clone <repository-url>
cd heptuple-platform
```

2. **Configuration environnement**
```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

3. **Lancement des services**
```bash
docker-compose up -d
```

4. **Vérification du déploiement**
```bash
docker-compose ps
```

### **Ports Automatiques**
Le système utilise des ports automatiques pour éviter les conflits :
- **NGINX** : Port assigné automatiquement (point d'entrée principal)
- **Adminer** : Port assigné automatiquement (administration DB)
- **Services internes** : Communication via réseau Docker

Pour connaître les ports assignés :
```bash
docker port heptuple_nginx 80
docker port heptuple_adminer 8080
```

## 📊 **Fonctionnalités**

### **Analyse Heptuple**
- Classification automatique de textes selon les 7 dimensions
- Scores de confiance et métriques de performance
- Cache intelligent des analyses

### **Base de Données Complète**
- 114 sourates avec métadonnées complètes
- Profils heptuple pré-calculés
- Versets avec traductions et classifications
- Analyses exégétiques traditionnelles

### **Interface Utilisateur**
- Interface React moderne et responsive
- Visualisations interactives des profils
- Recherche avancée multilingue
- Comparaisons entre sourates

### **API RESTful**
- Endpoints `/api/v2/*` avec documentation Swagger
- Authentification et autorisation
- Rate limiting et sécurité
- Cache Redis pour performances

## 🔧 **Configuration Avancée**

### **Variables d'Environnement**
```bash
# Base de données
POSTGRES_DB=heptuple_db
POSTGRES_USER=heptuple_user
POSTGRES_PASSWORD=your_secure_password

# Sécurité
SECRET_KEY=your_secret_key_32_chars_minimum

# IA/ML (optionnel)
OPENAI_API_KEY=your_openai_key
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_API_KEY=xxxxx_votre_cle_xxxxx
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_TIMEOUT=30
```

### **Personnalisation**
- Modifiez `init.sql` pour ajouter vos données
- Configurez `nginx/nginx.conf` pour vos domaines
- Ajustez `docker-compose.yml` selon vos besoins

## 📚 **Documentation API**

Une fois déployé, accédez à :
- **Documentation Swagger** : `http://localhost:[PORT]/docs`
- **ReDoc** : `http://localhost:[PORT]/redoc`

### **Endpoints Principaux**
```
GET  /api/v2/sourates          # Liste des sourates
GET  /api/v2/sourates/{id}     # Sourate spécifique
POST /api/v2/analyze           # Analyse de texte
POST /api/v2/compare           # Comparaison sourates
GET  /api/v2/search            # Recherche avancée
```

## 🧪 **Tests et Validation**

### **Health Checks**
```bash
# Vérification API
curl http://localhost:[PORT]/health

# Vérification base de données
docker-compose exec postgres pg_isready

# Logs des services
docker-compose logs -f api
```

### **Tests d'Analyse**
```bash
# Test d'analyse via API
curl -X POST http://localhost:[PORT]/api/v2/analyze \
  -H "Content-Type: application/json" \
  -d '{"texte": "بسم الله الرحمن الرحيم"}'
```

## 🔒 **Sécurité**

- **HTTPS** : Configuration SSL/TLS disponible
- **CORS** : Configuré pour domaines autorisés
- **Rate Limiting** : Protection contre les abus
- **Validation** : Sanitisation des entrées utilisateur
- **Authentification** : JWT tokens pour API

## 📈 **Monitoring**

### **Métriques Disponibles**
- Temps de réponse API
- Utilisation base de données
- Cache hit/miss ratios
- Erreurs et exceptions

### **Logs**
```bash
# Logs centralisés
docker-compose logs -f

# Logs spécifiques
docker-compose logs -f api
docker-compose logs -f nginx
```

## 🤝 **Contribution**

### **Structure du Projet**
```
heptuple-platform/
├── backend/              # API FastAPI
│   ├── main.py          # Point d'entrée
│   ├── models.py        # Modèles Pydantic
│   ├── database.py      # Connexion DB
│   └── services/        # Services métier
├── frontend/            # Interface React
│   ├── src/
│   │   ├── App.js       # Composant principal
│   │   └── components/  # Composants UI
│   └── public/
├── nginx/               # Configuration reverse proxy
├── docker-compose.yml   # Orchestration services
├── init.sql            # Initialisation DB
└── .env.example        # Variables d'environnement
```

### **Développement**
1. Fork le projet
2. Créer une branche feature
3. Développer et tester
4. Soumettre une Pull Request

## 📞 **Support**

- **Issues** : Utilisez GitHub Issues
- **Documentation** : Wiki du projet
- **Contact** : [email de contact]

## 📄 **Licence**

Ce projet est sous licence [TYPE DE LICENCE] - voir le fichier `LICENSE` pour plus de détails.

---

**🌟 Vision Heptuple - Révolutionner l'Exégèse Coranique par l'Innovation Technologique**
