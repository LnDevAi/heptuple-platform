# 🚀 Guide de Déploiement VPS Contabo - Heptuple Platform

## 📋 Prérequis

- **VPS Contabo** avec Ubuntu 20.04+ ou Debian 11+
- **Accès root** au serveur
- **Domaine** configuré (optionnel mais recommandé)
- **Certificat SSL** (Let's Encrypt recommandé)

## ⚡ Installation Automatique

### 1. **Préparation du serveur**

```bash
# Connexion au VPS
ssh root@votre-ip-vps

# Mise à jour du système
apt update && apt upgrade -y

# Installation de Git
apt install -y git

# Clonage du projet
git clone https://github.com/votre-repo/heptuple-platform.git
cd heptuple-platform
```

### 2. **Installation automatique**

```bash
# Rendre le script exécutable
chmod +x deploy_vps.sh

# Installation complète
./deploy_vps.sh install
```

Cette commande va :
- Installer toutes les dépendances système
- Configurer PostgreSQL, Redis et Nginx
- Créer l'utilisateur système
- Déployer l'application
- Configurer les services systemd
- Initialiser la base de données
- Démarrer tous les services

### 3. **Configuration du domaine (optionnel)**

```bash
# Configuration Nginx pour votre domaine
nano /etc/nginx/sites-available/heptuple-platform

# Remplacer 'server_name _;' par 'server_name votre-domaine.com;'

# Test de la configuration
nginx -t

# Redémarrage de Nginx
systemctl restart nginx
```

### 4. **Configuration SSL avec Let's Encrypt**

```bash
# Installation de Certbot
apt install -y certbot python3-certbot-nginx

# Génération du certificat SSL
certbot --nginx -d votre-domaine.com -d www.votre-domaine.com

# Test du renouvellement automatique
certbot renew --dry-run
```

## 🗄️ Base de données et données réelles

Après l'installation, appliquez extensions, index et ingestion d'exemples:

```bash
sudo -u postgres psql -d heptuple_db -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
sudo -u postgres psql -d heptuple_db -c "CREATE EXTENSION IF NOT EXISTS unaccent;"

# Index et optimisations
psql -U heptuple_user -d heptuple_db -f /opt/heptuple-platform/db/schema_indexes.sql || true

# Exemples d'ingestion (remplacez par vos datasets réels)
psql -U heptuple_user -d heptuple_db -f /opt/heptuple-platform/db/ingest_samples.sql || true

# Ingestion depuis CSV (gabarits fournis dans db/csv_templates)
psql -U heptuple_user -d heptuple_db -f /opt/heptuple-platform/db/ingest_from_csv.sql || true
```

Ces scripts préparent la recherche rapide (trigram, GIN) pour hadiths, fiqh, invocations.

## 🔧 Gestion des Services

### Commandes de base

```bash
# Démarrage des services
./deploy_vps.sh start

# Arrêt des services
./deploy_vps.sh stop

# Redémarrage des services
./deploy_vps.sh restart

# Statut des services
./deploy_vps.sh status

# Affichage des logs
./deploy_vps.sh logs

# Mise à jour de l'application
./deploy_vps.sh update
```

### Services systemd

```bash
# Statut de l'API
systemctl status heptuple-platform

# Logs de l'API
journalctl -u heptuple-platform -f

# Redémarrage de l'API
systemctl restart heptuple-platform
```

## 🌐 Accès aux Services

Une fois déployé, accédez aux services suivants :

| Service | URL | Description |
|---------|-----|-------------|
| **Application** | https://votre-domaine.com | Interface principale |
| **API** | https://votre-domaine.com/api | API Backend |
| **API Docs** | https://votre-domaine.com/docs | Documentation Swagger |
| **ReDoc** | https://votre-domaine.com/redoc | Documentation ReDoc |

## 🔒 Sécurité

### Configuration de base

1. **Changer les mots de passe par défaut**
```bash
# Édition du fichier .env
nano /opt/heptuple-platform/.env

# Changer tous les mots de passe
DB_PASSWORD=votre_mot_de_passe_securise
REDIS_PASSWORD=votre_mot_de_passe_redis
SECRET_KEY=votre_cle_secrete_tres_longue
JWT_SECRET_KEY=votre_jwt_secret_key_tres_longue
```

2. **Configuration du firewall**
```bash
# Installation d'UFW
apt install -y ufw

# Configuration des règles
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

3. **Configuration SSH**
```bash
# Édition de la configuration SSH
nano /etc/ssh/sshd_config

# Désactiver la connexion root
PermitRootLogin no

# Redémarrage du service SSH
systemctl restart ssh
```

## 📊 Monitoring

### Logs

```bash
# Logs de l'application
tail -f /var/log/heptuple-platform/nginx_access.log
tail -f /var/log/heptuple-platform/nginx_error.log

# Logs systemd
journalctl -u heptuple-platform -f
```

### Surveillance des ressources

```bash
# Utilisation CPU et mémoire
htop

# Utilisation disque
df -h

# Utilisation réseau
netstat -tlnp
```

## 🔄 Sauvegarde

### Sauvegarde automatique

```bash
# Création du script de sauvegarde
nano /opt/heptuple-platform/backup.sh

# Contenu du script
#!/bin/bash
BACKUP_DIR="/opt/heptuple-platform/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Sauvegarde de la base de données
pg_dump -h localhost -U heptuple_user heptuple_db > $BACKUP_DIR/db_backup_$DATE.sql

# Sauvegarde des fichiers
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz /opt/heptuple-platform

# Nettoyage des anciennes sauvegardes (garde 30 jours)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### Configuration cron

```bash
# Édition du crontab
crontab -e

# Ajout de la sauvegarde quotidienne à 2h du matin
0 2 * * * /opt/heptuple-platform/backup.sh
```

## 🧪 Tests

### Test de l'API

```bash
# Installation des dépendances de test
pip install requests

# Exécution des tests
python3 test_api.py --url https://votre-domaine.com/api

# Test avec mode verbeux
python3 test_api.py --url https://votre-domaine.com/api --verbose
```

### Test de santé

```bash
# Test de l'API
curl https://votre-domaine.com/api/health

# Test de la base de données
curl https://votre-domaine.com/api/v2/db/health
```

## 🚨 Dépannage

### Problèmes courants

1. **Service ne démarre pas**
```bash
# Vérification des logs
journalctl -u heptuple-platform -n 50

# Vérification de la configuration
systemctl status heptuple-platform
```

2. **Erreur de base de données**
```bash
# Vérification du service PostgreSQL
systemctl status postgresql

# Test de connexion
sudo -u postgres psql -c "SELECT version();"
```

3. **Erreur Redis**
```bash
# Vérification du service Redis
systemctl status redis-server

# Test de connexion
redis-cli ping
```

4. **Erreur Nginx**
```bash
# Test de la configuration
nginx -t

# Vérification des logs
tail -f /var/log/nginx/error.log
```

### Réinitialisation complète

```bash
# Arrêt des services
./deploy_vps.sh stop

# Suppression des données
rm -rf /opt/heptuple-platform
rm -rf /var/log/heptuple-platform

# Réinstallation
./deploy_vps.sh install
```

## 📈 Optimisation

### Performance

1. **Configuration PostgreSQL**
```bash
# Édition de la configuration
nano /etc/postgresql/*/main/postgresql.conf

# Optimisations recommandées
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
```

2. **Configuration Redis**
```bash
# Édition de la configuration
nano /etc/redis/redis.conf

# Optimisations recommandées
maxmemory 256mb
maxmemory-policy allkeys-lru
```

3. **Configuration Nginx**
```bash
# Édition de la configuration
nano /etc/nginx/nginx.conf

# Optimisations recommandées
worker_processes auto;
worker_connections 1024;
```

## 🔄 Mise à jour

### Mise à jour de l'application

```bash
# Sauvegarde avant mise à jour
./deploy_vps.sh stop
cp -r /opt/heptuple-platform /opt/heptuple-platform.backup

# Mise à jour du code
cd /opt/heptuple-platform
git pull origin main

# Mise à jour des dépendances
source venv/bin/activate
pip install -r backend/requirements.txt

# Redémarrage
./deploy_vps.sh start
```

## 📞 Support

### Logs utiles

```bash
# Logs de l'application
journalctl -u heptuple-platform -f

# Logs Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Logs PostgreSQL
tail -f /var/log/postgresql/postgresql-*.log

# Logs Redis
tail -f /var/log/redis/redis-server.log
```

### Informations système

```bash
# Informations sur le système
uname -a
lsb_release -a

# Utilisation des ressources
free -h
df -h
top
```

---

**🌟 Heptuple Platform - Révolutionner l'Exégèse Coranique par l'Innovation Technologique**
