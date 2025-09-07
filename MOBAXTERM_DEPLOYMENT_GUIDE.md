# 🚀 Guide de Déploiement VPS avec MobaXterm

## 📋 Prérequis
- MobaXterm installé sur Windows
- Accès SSH à votre VPS Contabo
- Domaine configuré (optionnel mais recommandé)

## 🔧 Configuration MobaXterm

### 1. Connexion SSH
```bash
# Ouvrir une session SSH dans MobaXterm
ssh root@YOUR_VPS_IP
# ou
ssh username@YOUR_VPS_IP
```

### 2. Accès aux fichiers Windows
Dans MobaXterm, vos disques Windows sont accessibles via :
```bash
/drives/c/Users/HP/Documents/GitHub/heptuple-platform
```

## 📁 Scripts de Déploiement

### Script Principal : `deploy_vps_mobaxterm.sh`
```bash
# 1. Copier le script sur le VPS
scp deploy_vps_mobaxterm.sh root@YOUR_VPS_IP:/root/

# 2. Se connecter au VPS
ssh root@YOUR_VPS_IP

# 3. Rendre le script exécutable
chmod +x deploy_vps_mobaxterm.sh

# 4. Exécuter le déploiement
./deploy_vps_mobaxterm.sh
```

### Script de Copie : `copy_files_to_vps.sh`
```bash
# À exécuter depuis MobaXterm (Windows)
# 1. Modifier les variables dans le script :
#    - VPS_IP="YOUR_VPS_IP"
#    - VPS_USER="root" (ou votre utilisateur)

# 2. Exécuter le script
chmod +x copy_files_to_vps.sh
./copy_files_to_vps.sh
```

## 🎯 Étapes de Déploiement

### Étape 1: Préparation
```bash
# Dans MobaXterm, naviguer vers votre projet
cd /drives/c/Users/HP/Documents/GitHub/heptuple-platform

# Vérifier que tous les fichiers sont présents
ls -la
```

### Étape 2: Copie des Fichiers
```bash
# Option A: Via le script automatique
./copy_files_to_vps.sh

# Option B: Copie manuelle
scp -r backend/ root@YOUR_VPS_IP:/opt/heptuple/
scp -r frontend/ root@YOUR_VPS_IP:/opt/heptuple/
scp *.sql root@YOUR_VPS_IP:/opt/heptuple/
scp *.py root@YOUR_VPS_IP:/opt/heptuple/
scp *.md root@YOUR_VPS_IP:/opt/heptuple/
```

### Étape 3: Déploiement sur le VPS
```bash
# Se connecter au VPS
ssh root@YOUR_VPS_IP

# Aller dans le répertoire du projet
cd /opt/heptuple

# Exécuter le script de déploiement
chmod +x deploy_vps_mobaxterm.sh
./deploy_vps_mobaxterm.sh
```

## ⚙️ Configuration Post-Déploiement

### 1. Configuration du Domaine
```bash
# Éditer les fichiers de configuration
nano /opt/heptuple/backend/.env
nano /opt/heptuple/frontend/.env
nano /etc/nginx/sites-available/heptuple

# Remplacer 'your-domain.com' par votre vrai domaine
```

### 2. Configuration SSL
```bash
# Obtenir un certificat SSL
certbot --nginx -d your-domain.com -d www.your-domain.com

# Vérifier le renouvellement automatique
certbot renew --dry-run
```

### 3. Vérification des Services
```bash
# Statut des services
systemctl status heptuple-backend
systemctl status heptuple-frontend
systemctl status nginx
systemctl status postgresql
systemctl status redis-server

# Logs en temps réel
journalctl -u heptuple-backend -f
journalctl -u heptuple-frontend -f
```

## 🧪 Tests de Validation

### Test de Connectivité
```bash
# Test du backend
curl http://localhost:8000/health

# Test du frontend
curl http://localhost:3000

# Test via Nginx
curl http://your-domain.com/health
```

### Test de l'Application
```bash
# Exécuter les tests de communication
cd /opt/heptuple
python3 test_communication.py
```

## 🔧 Commandes Utiles

### Gestion des Services
```bash
# Redémarrer un service
systemctl restart heptuple-backend
systemctl restart heptuple-frontend
systemctl restart nginx

# Voir les logs
journalctl -u heptuple-backend --since "1 hour ago"
tail -f /var/log/nginx/access.log
```

### Gestion de la Base de Données
```bash
# Connexion PostgreSQL
sudo -u postgres psql -d heptuple_db

# Sauvegarde
pg_dump -U heptuple_user heptuple_db > backup.sql

# Restauration
psql -U heptuple_user heptuple_db < backup.sql
```

### Mise à Jour
```bash
# Mise à jour du code
cd /opt/heptuple
git pull origin main  # si vous utilisez Git

# Redéploiement du frontend
cd frontend
npm run build
systemctl restart heptuple-frontend

# Redéploiement du backend
cd ../backend
source venv/bin/activate
pip install -r requirements.txt
systemctl restart heptuple-backend
```

## 🚨 Dépannage

### Problèmes Courants

#### Service Backend ne démarre pas
```bash
# Vérifier les logs
journalctl -u heptuple-backend -n 50

# Vérifier la configuration
cd /opt/heptuple/backend
source venv/bin/activate
python main.py  # Test en mode debug
```

#### Service Frontend ne démarre pas
```bash
# Vérifier les logs
journalctl -u heptuple-frontend -n 50

# Vérifier le build
cd /opt/heptuple/frontend
npm run build
```

#### Problème de Base de Données
```bash
# Vérifier la connexion
sudo -u postgres psql -d heptuple_db

# Vérifier les permissions
sudo -u postgres psql -c "\du"
```

#### Problème Nginx
```bash
# Tester la configuration
nginx -t

# Recharger la configuration
systemctl reload nginx

# Vérifier les logs
tail -f /var/log/nginx/error.log
```

## 📊 Monitoring

### Surveillance des Ressources
```bash
# Utilisation CPU/Mémoire
htop

# Espace disque
df -h

# Connexions réseau
netstat -tulpn
```

### Surveillance des Logs
```bash
# Logs en temps réel
tail -f /var/log/nginx/access.log
journalctl -u heptuple-backend -f
journalctl -u heptuple-frontend -f
```

## 🔒 Sécurité

### Configuration du Pare-feu
```bash
# Vérifier le statut
ufw status

# Autoriser seulement les ports nécessaires
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
```

### Mise à Jour de Sécurité
```bash
# Mise à jour du système
apt update && apt upgrade -y

# Mise à jour des dépendances
cd /opt/heptuple/backend
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

## 📞 Support

En cas de problème :
1. Vérifiez les logs des services
2. Testez la connectivité réseau
3. Vérifiez la configuration des fichiers
4. Consultez la documentation du projet

---

## 🎉 Félicitations !

Votre plateforme Heptuple est maintenant déployée sur votre VPS Contabo ! 🚀

**URLs d'accès :**
- Frontend : https://your-domain.com
- Backend API : https://your-domain.com/api
- Health Check : https://your-domain.com/health
