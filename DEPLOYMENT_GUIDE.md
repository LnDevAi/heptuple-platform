# 🚀 Guide de Déploiement Heptuple Platform

## 📋 Prérequis

- **Docker Desktop** (Windows/Mac) ou **Docker Engine** (Linux)
- **Docker Compose** (inclus avec Docker Desktop)
- **Git** (pour cloner le projet)

## ⚡ Démarrage Rapide

### 1. **Configuration de l'environnement**

```bash
# Copier le fichier d'environnement
copy env.example .env

# Éditer le fichier .env avec vos paramètres
notepad .env
```

### 2. **Démarrage des services**

**Windows:**
```cmd
deploy.bat start
```

**Linux/Mac:**
```bash
./deploy.sh start
```

### 3. **Vérification du déploiement**

```bash
# Vérifier le statut des services
deploy.bat status

# Voir les logs
deploy.bat logs
```

## 🌐 Accès aux services

Une fois déployé, accédez aux services suivants :

| Service | URL | Description |
|---------|-----|-------------|
| **Application** | http://localhost:8080 | Interface principale |
| **API** | http://localhost:8000 | API Backend |
| **API Docs** | http://localhost:8000/docs | Documentation Swagger |
| **Prometheus** | http://localhost:9090 | Monitoring |
| **Grafana** | http://localhost:3001 | Visualisation (admin/admin) |

## 🔧 Configuration

### Variables d'environnement importantes

Éditez le fichier `.env` pour configurer :

```bash
# Base de données
DB_PASSWORD=votre_mot_de_passe_securise
DB_USER=heptuple_user
DB_NAME=heptuple_db

# Cache et recherche
REDIS_PASSWORD=votre_mot_de_passe_redis
ELASTICSEARCH_PASSWORD=votre_mot_de_passe_elastic

# Sécurité
SECRET_KEY=votre_cle_secrete_tres_longue
JWT_SECRET_KEY=votre_jwt_secret_key

# Monitoring
GRAFANA_PASSWORD=admin
```

## 🛠️ Commandes utiles

### Gestion des services

```bash
# Démarrer
deploy.bat start

# Arrêter
deploy.bat stop

# Statut
deploy.bat status

# Logs
deploy.bat logs
deploy.bat logs api
deploy.bat logs frontend
```

### Docker Compose direct

```bash
# Démarrer en mode détaché
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down

# Reconstruire les images
docker-compose build --no-cache
```

## 🔍 Dépannage

### Problèmes courants

1. **Ports déjà utilisés**
   - Vérifiez qu'aucun autre service n'utilise les ports 8080, 8000, 5432, 6379, 9200
   - Modifiez les ports dans le fichier `.env` si nécessaire

2. **Erreur de connexion à la base de données**
   - Vérifiez que PostgreSQL démarre correctement : `deploy.bat logs postgres`
   - Vérifiez les variables d'environnement dans `.env`

3. **Erreur de build**
   - Reconstruisez les images : `docker-compose build --no-cache`
   - Vérifiez les logs de build : `docker-compose logs api`

### Vérification de santé

```bash
# Vérifier l'API
curl http://localhost:8000/health

# Vérifier le frontend
curl http://localhost:8080

# Vérifier Prometheus
curl http://localhost:9090/-/healthy
```

## 📊 Monitoring

### Prometheus
- **URL**: http://localhost:9090
- **Métriques**: Temps de réponse, utilisation CPU/mémoire, erreurs

### Grafana
- **URL**: http://localhost:3001
- **Login**: admin/admin
- **Dashboards**: Pré-configurés pour Heptuple Platform

## 🔒 Sécurité

### Recommandations de production

1. **Changer tous les mots de passe par défaut**
2. **Utiliser des certificats SSL/TLS**
3. **Configurer un firewall**
4. **Limiter l'accès aux ports de monitoring**
5. **Utiliser des secrets Docker pour les mots de passe**

### Variables sensibles

```bash
# À changer absolument en production
SECRET_KEY=change_this_in_production
JWT_SECRET_KEY=change_this_in_production
DB_PASSWORD=change_this_in_production
REDIS_PASSWORD=change_this_in_production
ELASTICSEARCH_PASSWORD=change_this_in_production
```

## 📝 Logs

### Emplacement des logs

- **Application**: `logs/` (monté dans les conteneurs)
- **Nginx**: `logs/nginx/`
- **Base de données**: Gérés par Docker

### Consultation des logs

```bash
# Tous les services
deploy.bat logs

# Service spécifique
deploy.bat logs api
deploy.bat logs postgres
deploy.bat logs nginx
```

## 🚀 Production

### Recommandations pour la production

1. **Utiliser un reverse proxy** (Nginx/Traefik)
2. **Configurer des sauvegardes automatiques**
3. **Mettre en place un monitoring avancé**
4. **Utiliser des volumes persistants**
5. **Configurer la haute disponibilité**

### Variables d'environnement de production

```bash
# Production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Sécurité renforcée
SECRET_KEY=your_very_long_and_secure_secret_key_here
JWT_SECRET_KEY=your_very_long_and_secure_jwt_secret_key_here
```

---

**🌟 Heptuple Platform - Révolutionner l'Exégèse Coranique par l'Innovation Technologique**
