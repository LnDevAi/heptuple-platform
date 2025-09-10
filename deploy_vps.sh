#!/bin/bash

# Script de déploiement pour VPS Contabo sans containers
# Usage: ./deploy_vps.sh [start|stop|restart|status|logs]

set -e

# Configuration
PROJECT_NAME="heptuple-platform"
PROJECT_DIR="/opt/$PROJECT_NAME"
SERVICE_USER="heptuple"
PYTHON_VERSION="3.11"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="/var/log/$PROJECT_NAME"
NGINX_CONFIG="/etc/nginx/sites-available/$PROJECT_NAME"
NGINX_ENABLED="/etc/nginx/sites-enabled/$PROJECT_NAME"
SYSTEMD_SERVICE="/etc/systemd/system/$PROJECT_NAME.service"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions utilitaires
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

# Vérification des privilèges root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "Ce script doit être exécuté en tant que root"
        exit 1
    fi
}

# Installation des dépendances système
install_system_dependencies() {
    log_info "Installation des dépendances système..."
    
    # Mise à jour du système
    apt update && apt upgrade -y
    
    # Installation des packages nécessaires
    apt install -y \
        python3.11 \
        python3.11-venv \
        python3.11-dev \
        python3-pip \
        nodejs \
        npm \
        postgresql \
        postgresql-contrib \
        redis-server \
        nginx \
        git \
        curl \
        wget \
        build-essential \
        libpq-dev \
        libssl-dev \
        libffi-dev \
        supervisor \
        certbot \
        python3-certbot-nginx
    
    log_success "Dépendances système installées"
}

# Configuration de PostgreSQL
setup_postgresql() {
    log_info "Configuration de PostgreSQL..."
    
    # Démarrage du service PostgreSQL
    systemctl start postgresql
    systemctl enable postgresql
    
    # Création de l'utilisateur et de la base de données
    sudo -u postgres psql << EOF
CREATE USER heptuple_user WITH PASSWORD 'heptuple_secure_password_2024';
CREATE DATABASE heptuple_db OWNER heptuple_user;
GRANT ALL PRIVILEGES ON DATABASE heptuple_db TO heptuple_user;
\q
EOF
    
    # Configuration de PostgreSQL pour accepter les connexions locales
    sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" /etc/postgresql/*/main/postgresql.conf
    
    systemctl restart postgresql
    log_success "PostgreSQL configuré"
}

# Configuration de Redis
setup_redis() {
    log_info "Configuration de Redis..."
    
    # Démarrage du service Redis
    systemctl start redis-server
    systemctl enable redis-server
    
    # Configuration de Redis
    sed -i 's/# requirepass foobared/requirepass heptuple_redis_password_2024/' /etc/redis/redis.conf
    sed -i 's/requirepass foobared/requirepass heptuple_redis_password_2024/' /etc/redis/redis.conf
    
    systemctl restart redis-server
    log_success "Redis configuré"
}

# Création de l'utilisateur système
create_system_user() {
    log_info "Création de l'utilisateur système..."
    
    if ! id "$SERVICE_USER" &>/dev/null; then
        useradd -r -s /bin/bash -d "$PROJECT_DIR" -m "$SERVICE_USER"
        log_success "Utilisateur $SERVICE_USER créé"
    else
        log_warning "Utilisateur $SERVICE_USER existe déjà"
    fi
}

# Déploiement de l'application
deploy_application() {
    log_info "Déploiement de l'application..."
    
    # Création du répertoire du projet
    mkdir -p "$PROJECT_DIR"
    mkdir -p "$LOG_DIR"
    
    # Copie des fichiers du projet
    cp -r backend/ "$PROJECT_DIR/"
    cp -r frontend/ "$PROJECT_DIR/"
    cp -r nginx/ "$PROJECT_DIR/"
    cp -r monitoring/ "$PROJECT_DIR/"
    cp *.sql "$PROJECT_DIR/" 2>/dev/null || true
    cp *.md "$PROJECT_DIR/" 2>/dev/null || true
    cp .env.example "$PROJECT_DIR/.env"
    
    # Création de l'environnement virtuel Python
    python3.11 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    
    # Installation des dépendances Python
    pip install --upgrade pip
    pip install -r "$PROJECT_DIR/backend/requirements.txt"
    
    # Build du frontend (React)
    if [ -d "$PROJECT_DIR/frontend" ]; then
        pushd "$PROJECT_DIR/frontend" >/dev/null
        if command -v npm >/dev/null 2>&1; then
            npm ci || npm install
            npm run build
        else
            log_warning "npm non trouvé: le frontend ne sera pas buildé"
        fi
        popd >/dev/null
    fi
    
    # Configuration des permissions
    chown -R "$SERVICE_USER:$SERVICE_USER" "$PROJECT_DIR"
    chown -R "$SERVICE_USER:$SERVICE_USER" "$LOG_DIR"
    chmod +x "$PROJECT_DIR/backend/main.py"
    
    log_success "Application déployée"
}

# Configuration de l'environnement
setup_environment() {
    log_info "Configuration de l'environnement..."
    
    # Création du fichier .env
    cat > "$PROJECT_DIR/.env" << EOF
# Configuration de la base de données
DB_HOST=localhost
DB_PORT=5432
DB_NAME=heptuple_db
DB_USER=heptuple_user
DB_PASSWORD=heptuple_secure_password_2024

# Configuration Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=heptuple_redis_password_2024
REDIS_DB=0

# Configuration Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_PASSWORD=heptuple_elastic_password_2024

# Configuration de sécurité
SECRET_KEY=heptuple_super_secret_key_2024_change_in_production_32_chars_min
JWT_SECRET_KEY=heptuple_jwt_secret_key_2024_change_in_production_32_chars_min

# Configuration CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
ALLOWED_HOSTS=localhost,127.0.0.1

# Configuration de l'environnement
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
INSTANCE_ID=0
EOF
    
    chown "$SERVICE_USER:$SERVICE_USER" "$PROJECT_DIR/.env"
    chmod 600 "$PROJECT_DIR/.env"
    
    log_success "Environnement configuré"
}

# Configuration de Nginx
setup_nginx() {
    log_info "Configuration de Nginx..."
    
    # Création de la configuration Nginx
    cat > "$NGINX_CONFIG" << EOF
server {
    listen 80;
    server_name _;
    
    # Redirection vers HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name _;
    
    # Configuration SSL (à remplacer par vos certificats)
    ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;
    
    # Configuration SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Headers de sécurité
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Logs
    access_log $LOG_DIR/nginx_access.log;
    error_log $LOG_DIR/nginx_error.log;
    
    # Frontend React (statique)
    root $PROJECT_DIR/frontend/build;
    index index.html;
    location / {
        try_files \$uri /index.html;
    }
    
    # Cache pour les assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API Backend
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        # Timeout pour les analyses longues
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
    
    # Documentation API
    location /docs {
        proxy_pass http://localhost:8000/docs;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Redoc
    location /redoc {
        proxy_pass http://localhost:8000/redoc;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
    
    # Activation du site
    ln -sf "$NGINX_CONFIG" "$NGINX_ENABLED"
    
    # Test de la configuration
    nginx -t
    
    # Redémarrage de Nginx
    systemctl restart nginx
    systemctl enable nginx
    
    log_success "Nginx configuré"
}

# Configuration du service systemd
setup_systemd_service() {
    log_info "Configuration du service systemd..."
    
    # Création du service systemd pour l'API
    cat > "$SYSTEMD_SERVICE" << EOF
[Unit]
Description=Heptuple Platform API
After=network.target postgresql.service redis-server.service
Requires=postgresql.service redis-server.service

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$PROJECT_DIR/backend
Environment=PATH=$VENV_DIR/bin
ExecStart=$VENV_DIR/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=heptuple-api

# Variables d'environnement
EnvironmentFile=$PROJECT_DIR/.env

[Install]
WantedBy=multi-user.target
EOF
    
    # Rechargement de systemd
    systemctl daemon-reload
    systemctl enable "$PROJECT_NAME"
    
    log_success "Service systemd configuré"
}

# Initialisation de la base de données
init_database() {
    log_info "Initialisation de la base de données..."
    
    # Exécution des scripts SQL
    sudo -u postgres psql -d heptuple_db -f "$PROJECT_DIR/init.sql" 2>/dev/null || true
    sudo -u postgres psql -d heptuple_db -f "$PROJECT_DIR/sourates_complete.sql" 2>/dev/null || true
    sudo -u postgres psql -d heptuple_db -f "$PROJECT_DIR/extensions_references.sql" 2>/dev/null || true
    
    log_success "Base de données initialisée"
}

# Démarrage des services
start_services() {
    log_info "Démarrage des services..."
    
    # Démarrage des services de base
    systemctl start postgresql
    systemctl start redis-server
    systemctl start nginx
    
    # Démarrage de l'application
    systemctl start "$PROJECT_NAME"
    
    # Vérification du statut
    sleep 5
    if systemctl is-active --quiet "$PROJECT_NAME"; then
        log_success "Services démarrés avec succès"
    else
        log_error "Erreur lors du démarrage des services"
        systemctl status "$PROJECT_NAME"
        exit 1
    fi
}

# Arrêt des services
stop_services() {
    log_info "Arrêt des services..."
    
    systemctl stop "$PROJECT_NAME"
    systemctl stop nginx
    systemctl stop redis-server
    systemctl stop postgresql
    
    log_success "Services arrêtés"
}

# Redémarrage des services
restart_services() {
    log_info "Redémarrage des services..."
    
    systemctl restart "$PROJECT_NAME"
    systemctl restart nginx
    
    log_success "Services redémarrés"
}

# Statut des services
status_services() {
    log_info "Statut des services:"
    
    echo "PostgreSQL: $(systemctl is-active postgresql)"
    echo "Redis: $(systemctl is-active redis-server)"
    echo "Nginx: $(systemctl is-active nginx)"
    echo "Heptuple API: $(systemctl is-active $PROJECT_NAME)"
    
    echo ""
    echo "Ports utilisés:"
    netstat -tlnp | grep -E ":(5432|6379|80|443|8000|3000)"
}

# Affichage des logs
show_logs() {
    log_info "Logs des services:"
    
    echo "=== Logs de l'API ==="
    journalctl -u "$PROJECT_NAME" -n 50 --no-pager
    
    echo ""
    echo "=== Logs de Nginx ==="
    tail -n 20 "$LOG_DIR/nginx_access.log" 2>/dev/null || echo "Pas de logs d'accès"
    tail -n 20 "$LOG_DIR/nginx_error.log" 2>/dev/null || echo "Pas de logs d'erreur"
}

# Fonction principale
main() {
    case "${1:-start}" in
        "install")
            check_root
            install_system_dependencies
            setup_postgresql
            setup_redis
            create_system_user
            deploy_application
            setup_environment
            setup_nginx
            setup_systemd_service
            init_database
            start_services
            log_success "Installation complète terminée!"
            log_info "L'application est accessible sur https://localhost"
            ;;
        "start")
            check_root
            start_services
            ;;
        "stop")
            check_root
            stop_services
            ;;
        "restart")
            check_root
            restart_services
            ;;
        "status")
            status_services
            ;;
        "logs")
            show_logs
            ;;
        "update")
            check_root
            log_info "Mise à jour de l'application..."
            systemctl stop "$PROJECT_NAME"
            deploy_application
            systemctl start "$PROJECT_NAME"
            log_success "Application mise à jour"
            ;;
        *)
            echo "Usage: $0 {install|start|stop|restart|status|logs|update}"
            echo ""
            echo "  install  - Installation complète du système"
            echo "  start    - Démarrage des services"
            echo "  stop     - Arrêt des services"
            echo "  restart  - Redémarrage des services"
            echo "  status   - Statut des services"
            echo "  logs     - Affichage des logs"
            echo "  update   - Mise à jour de l'application"
            exit 1
            ;;
    esac
}

# Exécution du script
main "$@"
