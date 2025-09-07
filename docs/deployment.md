# Guide de Déploiement Multi-Instances Heptuple Platform avec Podman

## 📋 Table des matières

1. [Prérequis](#prérequis)
2. [Installation](#installation)
3. [Configuration Multi-Instances](#configuration-multi-instances)
4. [Déploiement](#déploiement)
5. [Gestion des Instances](#gestion-des-instances)
6. [Monitoring](#monitoring)
7. [Maintenance](#maintenance)
8. [Troubleshooting](#troubleshooting)

## 🔧 Prérequis

### Système d'exploitation
- Linux (Ubuntu 20.04+, CentOS 8+, RHEL 8+)
- Windows 10/11 avec WSL2
- macOS 10.15+

### Logiciels requis
- Podman 4.0+
- Python 3.11+
- Node.js 18+
- Git

### Ressources système recommandées
- **Par instance**: CPU 2 cœurs, RAM 4 GB, Stockage 20 GB
- **Total recommandé**: CPU 8 cœurs, RAM 16 GB, Stockage 100 GB
- Réseau: Connexion Internet stable

## 🚀 Installation

### 1. Installation de Podman

#### Ubuntu/Debian
```bash
# Ajouter le repository
sudo apt-get update
sudo apt-get install -y podman

# Vérifier l'installation
podman --version
```

#### CentOS/RHEL
```bash
# Installation via dnf
sudo dnf install -y podman

# Vérifier l'installation
podman --version
```

### 2. Installation de podman-compose
```bash
# Installation via pip
pip install podman-compose

# Vérifier l'installation
podman-compose --version
```

### 3. Cloner le projet
```bash
git clone https://github.com/votre-username/heptuple-platform.git
cd heptuple-platform
```

## ⚙️ Configuration Multi-Instances

### 1. Gestion automatique des ports

Le système utilise une gestion automatique des ports basée sur l'`INSTANCE_ID` :

```
Instance 0: 8080, 8000, 3000, 5432, 6379, 9200, 9090, 3001
Instance 1: 8180, 8100, 3100, 5532, 6479, 9300, 9190, 3101
Instance 2: 8280, 8200, 3200, 5632, 6579, 9400, 9290, 3201
...
```

**Formule**: `PORT_BASE + (INSTANCE_ID * 100)`

### 2. Configuration des variables d'environnement

```bash
# Copier le template
cp env.example .env

# Éditer le fichier .env avec vos valeurs
nano .env
```

### 3. Variables importantes à configurer

```bash
# Instance ID (0 = première instance, 1 = deuxième, etc.)
INSTANCE_ID=0

# Base de données (suffixée automatiquement par l'instance ID)
DB_PASSWORD=votre_mot_de_passe_securise
DB_USER=heptuple_user_0
DB_NAME=heptuple_db_0

# Redis (base de données séparée par instance)
REDIS_PASSWORD=votre_mot_de_passe_redis
REDIS_DB=0

# Elasticsearch
ELASTICSEARCH_PASSWORD=votre_mot_de_passe_elastic

# Sécurité
SECRET_KEY=votre_cle_secrete_tres_longue
JWT_SECRET_KEY=votre_cle_jwt_secrete

# Monitoring
GRAFANA_PASSWORD=votre_mot_de_passe_grafana
```

## 🚀 Déploiement

### 1. Démarrage d'une instance

```bash
# Rendre le script exécutable
chmod +x deploy_podman.sh

# Démarrer l'instance 0 (par défaut)
./deploy_podman.sh start

# Démarrer l'instance 1
./deploy_podman.sh start 1

# Démarrer l'instance 2
./deploy_podman.sh start 2
```

### 2. Démarrage manuel

```bash
# Créer les répertoires nécessaires
mkdir -p backup logs monitoring/prometheus monitoring/grafana/dashboards monitoring/grafana/datasources

# Démarrer avec podman-compose (instance 0)
INSTANCE_ID=0 podman-compose -f docker-compose.yml --env-file .env up -d

# Démarrer avec podman-compose (instance 1)
INSTANCE_ID=1 podman-compose -f docker-compose.yml --env-file .env up -d
```

### 3. Vérification du déploiement

```bash
# Vérifier le statut de l'instance 0
./deploy_podman.sh status

# Vérifier le statut de l'instance 1
./deploy_podman.sh status 1

# Vérifier la santé de l'instance 0
./scripts/health-check.sh all

# Vérifier la santé de l'instance 1
./scripts/health-check.sh all 1
```

## 🎛️ Gestion des Instances

### 1. Lister toutes les instances

```bash
# Lister toutes les instances en cours d'exécution
./deploy_podman.sh list

# Ou avec le script de santé
./scripts/health-check.sh list
```

### 2. Commandes par instance

```bash
# Instance 0 (par défaut)
./deploy_podman.sh start
./deploy_podman.sh stop
./deploy_podman.sh restart
./deploy_podman.sh status
./deploy_podman.sh logs

# Instance 1
./deploy_podman.sh start 1
./deploy_podman.sh stop 1
./deploy_podman.sh restart 1
./deploy_podman.sh status 1
./deploy_podman.sh logs 1

# Instance 2
./deploy_podman.sh start 2
./deploy_podman.sh stop 2
./deploy_podman.sh restart 2
./deploy_podman.sh status 2
./deploy_podman.sh logs 2
```

### 3. Logs spécifiques

```bash
# Logs de l'API de l'instance 0
./deploy_podman.sh logs api

# Logs de l'API de l'instance 1
./deploy_podman.sh logs api 1

# Logs du frontend de l'instance 2
./deploy_podman.sh logs frontend 2
```

## 📊 Monitoring

### 1. Accès aux interfaces par instance

#### Instance 0
- **Application principale**: http://localhost:8080
- **API Documentation**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

#### Instance 1
- **Application principale**: http://localhost:8180
- **API Documentation**: http://localhost:8100/docs
- **Prometheus**: http://localhost:9190
- **Grafana**: http://localhost:3101 (admin/admin)

#### Instance 2
- **Application principale**: http://localhost:8280
- **API Documentation**: http://localhost:8200/docs
- **Prometheus**: http://localhost:9290
- **Grafana**: http://localhost:3201 (admin/admin)

### 2. Configuration Grafana multi-instances

Chaque instance Grafana est configurée avec :
- Un nom d'instance unique
- Des dashboards spécifiques
- Des métriques isolées

### 3. Métriques disponibles par instance

- **API**: Taux de requêtes, temps de réponse, erreurs
- **Base de données**: Connexions actives, requêtes lentes
- **Redis**: Utilisation mémoire, commandes par seconde
- **Elasticsearch**: Indices, requêtes de recherche
- **Système**: CPU, mémoire, disque, réseau

## 🔧 Maintenance

### 1. Sauvegarde par instance

```bash
# Sauvegarde complète de l'instance 0
./scripts/backup.sh full

# Sauvegarde complète de l'instance 1
./scripts/backup.sh full 1

# Sauvegarde spécifique de l'instance 2
./scripts/backup.sh db 2
./scripts/backup.sh redis 2
./scripts/backup.sh elasticsearch 2
```

### 2. Restauration par instance

```bash
# Lister les sauvegardes de l'instance 0
./scripts/restore.sh list db

# Lister les sauvegardes de l'instance 1
./scripts/restore.sh list db 1

# Restaurer une sauvegarde de l'instance 0
./scripts/restore.sh db backup/instance_0/postgres_backup_20231201_120000.sql

# Restaurer une sauvegarde de l'instance 1
./scripts/restore.sh db backup/instance_1/postgres_backup_20231201_120000.sql 1
```

### 3. Mise à jour par instance

```bash
# Mettre à jour l'instance 0
./deploy_podman.sh update

# Mettre à jour l'instance 1
./deploy_podman.sh update 1

# Redémarrer l'instance 2
./deploy_podman.sh restart 2
```

### 4. Vérification de santé par instance

```bash
# Vérification complète de l'instance 0
./scripts/health-check.sh all

# Vérification complète de l'instance 1
./scripts/health-check.sh all 1

# Vérification spécifique de l'API de l'instance 2
./scripts/health-check.sh api 2
```

## 🛠️ Troubleshooting

### Problèmes courants

#### 1. Conflits de ports

```bash
# Vérifier les ports utilisés
netstat -tulpn | grep :8080
netstat -tulpn | grep :8180

# Vérifier les conteneurs en cours d'exécution
podman ps | grep heptuple
```

#### 2. Services ne démarrent pas

```bash
# Vérifier les logs de l'instance 0
./deploy_podman.sh logs

# Vérifier les logs de l'instance 1
./deploy_podman.sh logs 1

# Vérifier l'espace disque
df -h

# Vérifier la mémoire
free -h
```

#### 3. Problèmes de connexion à la base de données

```bash
# Vérifier le conteneur PostgreSQL de l'instance 0
podman exec heptuple-postgres-0 pg_isready -U heptuple_user_0

# Vérifier le conteneur PostgreSQL de l'instance 1
podman exec heptuple-postgres-1 pg_isready -U heptuple_user_1

# Vérifier les logs PostgreSQL
podman logs heptuple-postgres-0
podman logs heptuple-postgres-1
```

### Commandes utiles

```bash
# Arrêter toutes les instances
for i in {0..9}; do ./deploy_podman.sh stop $i 2>/dev/null || true; done

# Nettoyer toutes les instances
for i in {0..9}; do ./deploy_podman.sh cleanup $i 2>/dev/null || true; done

# Vérifier la santé de toutes les instances
for i in {0..9}; do ./scripts/health-check.sh all $i 2>/dev/null || true; done

# Voir les métriques système de toutes les instances
podman stats
```

## 🔒 Sécurité Multi-Instances

### 1. Isolation des instances

- **Réseaux séparés**: Chaque instance utilise son propre réseau Docker
- **Volumes isolés**: Données séparées par instance
- **Bases de données séparées**: PostgreSQL et Redis isolés
- **Conteneurs nommés**: Suffixés par l'instance ID

### 2. Bonnes pratiques

- Utilisez des mots de passe différents pour chaque instance
- Surveillez les logs de toutes les instances
- Effectuez des sauvegardes régulières pour chaque instance
- Limitez l'accès réseau aux services

### 3. Configuration SSL/TLS

Pour la production, configurez SSL/TLS pour chaque instance :

```bash
# Ajouter les certificats SSL pour chaque instance
mkdir -p ssl/instance_0/
mkdir -p ssl/instance_1/
# Copier vos certificats dans chaque dossier

# Modifier nginx/nginx.conf pour SSL
# Voir la documentation Nginx pour plus de détails
```

## 📈 Performance Multi-Instances

### 1. Optimisations recommandées

- **Ressources par instance**: Ajustez selon la charge
- **Base de données**: Optimisez les paramètres PostgreSQL
- **Redis**: Configurez la persistance et la mémoire
- **Elasticsearch**: Optimisez les indices et les requêtes
- **Nginx**: Activez la compression et le cache

### 2. Monitoring des performances

- Surveillez les métriques de chaque instance
- Configurez des alertes Grafana par instance
- Analysez les logs d'application
- Surveillez l'utilisation des ressources

### 3. Scaling horizontal

```bash
# Ajouter une nouvelle instance
INSTANCE_ID=3 ./deploy_podman.sh start

# Vérifier la nouvelle instance
./scripts/health-check.sh all 3

# Configurer le load balancer (optionnel)
# Voir la documentation de votre load balancer
```

## 📞 Support

Pour obtenir de l'aide :

1. Consultez les logs : `./deploy_podman.sh logs [instance_id]`
2. Vérifiez la santé : `./scripts/health-check.sh all [instance_id]`
3. Consultez la documentation de chaque service
4. Ouvrez une issue sur GitHub

---

**Note**: Ce guide est spécifique à l'architecture multi-instances Heptuple Platform. Adaptez les configurations selon vos besoins spécifiques.
