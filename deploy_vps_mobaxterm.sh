#!/bin/bash
# Script de déploiement Heptuple Platform sur VPS via MobaXterm
# Chemin du projet: C:\Users\HP\Documents\GitHub\heptuple-platform

set -e  # Arrêter en cas d'erreur

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
PROJECT_NAME="heptuple-platform"
BACKEND_DIR="/opt/heptuple/backend"
FRONTEND_DIR="/opt/heptuple/frontend"
NGINX_DIR="/etc/nginx/sites-available"
SERVICE_DIR="/etc/systemd/system"
LOG_DIR="/var/log/heptuple"

echo "=========================================="
echo "  DEPLOIEMENT HEPTUPLE PLATFORM VPS"
echo "=========================================="
echo ""

# 1. Mise à jour du système
log_info "Mise à jour du système..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git build-essential

# 2. Installation de Python 3.11+
log_info "Installation de Python 3.11+..."
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
sudo apt install -y python3.11-distutils

# 3. Installation de Node.js 18+
log_info "Installation de Node.js 18+..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 4. Installation de PostgreSQL 15
log_info "Installation de PostgreSQL 15..."
sudo apt install -y postgresql-15 postgresql-client-15 postgresql-contrib-15

# 5. Installation de Redis
log_info "Installation de Redis..."
sudo apt install -y redis-server

# 6. Installation de Nginx
log_info "Installation de Nginx..."
sudo apt install -y nginx

# 7. Installation de Certbot pour SSL
log_info "Installation de Certbot..."
sudo apt install -y certbot python3-certbot-nginx

# 8. Création des répertoires
log_info "Création des répertoires..."
sudo mkdir -p $BACKEND_DIR
sudo mkdir -p $FRONTEND_DIR
sudo mkdir -p $LOG_DIR
sudo chown -R $USER:$USER /opt/heptuple
sudo chown -R $USER:$USER $LOG_DIR

# 9. Copie des fichiers du projet
log_info "Copie des fichiers du projet..."

# Note: Vous devrez copier vos fichiers depuis Windows vers le VPS
# Option 1: Via SCP depuis MobaXterm
log_warning "IMPORTANT: Copiez vos fichiers depuis Windows vers le VPS:"
echo "scp -r C:/Users/HP/Documents/GitHub/heptuple-platform/* user@your-vps-ip:/opt/heptuple/"
echo ""

# Option 2: Via Git (si vous avez poussé sur GitHub)
log_info "Clonage depuis GitHub (si disponible)..."
if [ ! -d "/opt/heptuple/backend" ]; then
    # Remplacez par votre URL GitHub
    # git clone https://github.com/votre-username/heptuple-platform.git /opt/heptuple
    log_warning "Veuillez cloner votre repository ou copier les fichiers manuellement"
fi

# 10. Configuration de PostgreSQL
log_info "Configuration de PostgreSQL..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Création de l'utilisateur et de la base de données
sudo -u postgres psql << EOF
CREATE USER heptuple_user WITH PASSWORD 'heptuple_secure_password_2024';
CREATE DATABASE heptuple_db OWNER heptuple_user;
GRANT ALL PRIVILEGES ON DATABASE heptuple_db TO heptuple_user;
\q
EOF

# 11. Configuration de Redis
log_info "Configuration de Redis..."
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Configuration du mot de passe Redis
sudo sed -i 's/# requirepass foobared/requirepass heptuple_redis_password_2024/' /etc/redis/redis.conf
sudo systemctl restart redis-server

# 12. Configuration du Backend
log_info "Configuration du Backend..."
cd $BACKEND_DIR

# Création de l'environnement virtuel
python3.11 -m venv venv
source venv/bin/activate

# Installation des dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Création du fichier .env
cat > .env << EOF
# Application Settings
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=heptuple_db
DB_USER=heptuple_user
DB_PASSWORD=heptuple_secure_password_2024

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=heptuple_redis_password_2024
REDIS_DB=0

# Security Keys (CHANGEZ CES CLÉS EN PRODUCTION!)
SECRET_KEY=heptuple_super_secret_key_production_2024_min_32_chars
JWT_SECRET_KEY=heptuple_jwt_secret_key_production_2024_min_32_chars

# CORS and Trusted Hosts
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,localhost

# API Ports
API_PORT=8000
FRONTEND_PORT=3000
NGINX_PORT=80
NGINX_HTTPS_PORT=443
EOF

# Initialisation de la base de données
log_info "Initialisation de la base de données..."
python3.11 -c "
from database import create_tables, check_database_connection
if check_database_connection():
    create_tables()
    print('Tables créées avec succès')
else:
    print('Erreur de connexion à la base de données')
"

# 13. Configuration du Frontend
log_info "Configuration du Frontend..."
cd $FRONTEND_DIR

# Installation des dépendances
npm install

# Création du fichier .env
cat > .env << EOF
REACT_APP_API_BASE=https://your-domain.com
REACT_APP_API_URL=https://your-domain.com/api
EOF

# Build de production
npm run build

# 14. Configuration des services systemd
log_info "Configuration des services systemd..."

# Service Backend
sudo tee $SERVICE_DIR/heptuple-backend.service > /dev/null << EOF
[Unit]
Description=Heptuple Platform Backend
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$BACKEND_DIR/venv/bin
ExecStart=$BACKEND_DIR/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=heptuple-backend

[Install]
WantedBy=multi-user.target
EOF

# Service Frontend (serveur de fichiers statiques)
sudo tee $SERVICE_DIR/heptuple-frontend.service > /dev/null << EOF
[Unit]
Description=Heptuple Platform Frontend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$FRONTEND_DIR
ExecStart=/usr/bin/npx serve -s build -l 3000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=heptuple-frontend

[Install]
WantedBy=multi-user.target
EOF

# 15. Configuration de Nginx
log_info "Configuration de Nginx..."

# Installation de serve (pour servir les fichiers statiques)
sudo npm install -g serve

# Configuration Nginx
sudo tee $NGINX_DIR/heptuple << EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirection vers HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration (sera configuré par Certbot)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Activation du site
sudo ln -sf $NGINX_DIR/heptuple /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test de la configuration Nginx
sudo nginx -t

# 16. Démarrage des services
log_info "Démarrage des services..."

# Rechargement systemd
sudo systemctl daemon-reload

# Démarrage des services
sudo systemctl enable heptuple-backend
sudo systemctl enable heptuple-frontend
sudo systemctl enable nginx

sudo systemctl start heptuple-backend
sudo systemctl start heptuple-frontend
sudo systemctl start nginx

# 17. Configuration du pare-feu
log_info "Configuration du pare-feu..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 18. Configuration SSL avec Let's Encrypt
log_info "Configuration SSL avec Let's Encrypt..."
log_warning "IMPORTANT: Remplacez 'your-domain.com' par votre vrai domaine avant d'exécuter:"
echo "sudo certbot --nginx -d your-domain.com -d www.your-domain.com"

# 19. Vérification des services
log_info "Vérification des services..."
echo ""
echo "=== STATUT DES SERVICES ==="
sudo systemctl status heptuple-backend --no-pager -l
echo ""
sudo systemctl status heptuple-frontend --no-pager -l
echo ""
sudo systemctl status nginx --no-pager -l
echo ""
sudo systemctl status postgresql --no-pager -l
echo ""
sudo systemctl status redis-server --no-pager -l

# 20. Test de connectivité
log_info "Test de connectivité..."
echo ""
echo "=== TESTS DE CONNECTIVITÉ ==="
curl -s http://localhost:8000/health || log_error "Backend non accessible"
curl -s http://localhost:3000 || log_error "Frontend non accessible"
curl -s http://localhost/health || log_error "Nginx non accessible"

echo ""
echo "=========================================="
echo "  DEPLOIEMENT TERMINE!"
echo "=========================================="
echo ""
log_success "Services démarrés:"
echo "  - Backend: http://localhost:8000"
echo "  - Frontend: http://localhost:3000"
echo "  - Nginx: http://localhost"
echo ""
log_warning "ÉTAPES SUIVANTES:"
echo "1. Remplacez 'your-domain.com' par votre vrai domaine"
echo "2. Configurez SSL: sudo certbot --nginx -d your-domain.com"
echo "3. Testez l'application: https://your-domain.com"
echo ""
log_info "Logs des services:"
echo "  - Backend: sudo journalctl -u heptuple-backend -f"
echo "  - Frontend: sudo journalctl -u heptuple-frontend -f"
echo "  - Nginx: sudo tail -f /var/log/nginx/access.log"
echo ""
log_success "Déploiement terminé avec succès! 🚀"
