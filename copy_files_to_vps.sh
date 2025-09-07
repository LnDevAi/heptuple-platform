#!/bin/bash
# Script pour copier les fichiers depuis Windows vers le VPS
# À exécuter depuis MobaXterm

set -e

# Configuration
VPS_USER="root"  # Remplacez par votre utilisateur VPS
VPS_IP="YOUR_VPS_IP"  # Remplacez par l'IP de votre VPS
LOCAL_PROJECT_PATH="/drives/c/Users/HP/Documents/GitHub/heptuple-platform"
VPS_PROJECT_PATH="/opt/heptuple"

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "=========================================="
echo "  COPIE DES FICHIERS VERS LE VPS"
echo "=========================================="
echo ""

# Vérification des paramètres
if [ "$VPS_IP" = "YOUR_VPS_IP" ]; then
    log_warning "Veuillez configurer VPS_IP dans le script"
    exit 1
fi

log_info "Copie des fichiers vers le VPS..."
log_info "Source: $LOCAL_PROJECT_PATH"
log_info "Destination: $VPS_USER@$VPS_IP:$VPS_PROJECT_PATH"

# Création du répertoire sur le VPS
ssh $VPS_USER@$VPS_IP "mkdir -p $VPS_PROJECT_PATH"

# Copie des fichiers backend
log_info "Copie du backend..."
rsync -avz --progress \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv' \
    --exclude='.env' \
    --exclude='logs' \
    $LOCAL_PROJECT_PATH/backend/ \
    $VPS_USER@$VPS_IP:$VPS_PROJECT_PATH/backend/

# Copie des fichiers frontend
log_info "Copie du frontend..."
rsync -avz --progress \
    --exclude='node_modules' \
    --exclude='build' \
    --exclude='.env' \
    $LOCAL_PROJECT_PATH/frontend/ \
    $VPS_USER@$VPS_IP:$VPS_PROJECT_PATH/frontend/

# Copie des fichiers de configuration
log_info "Copie des fichiers de configuration..."
rsync -avz --progress \
    $LOCAL_PROJECT_PATH/init.sql \
    $VPS_USER@$VPS_IP:$VPS_PROJECT_PATH/

rsync -avz --progress \
    $LOCAL_PROJECT_PATH/sourates_complete.sql \
    $VPS_USER@$VPS_IP:$VPS_PROJECT_PATH/

rsync -avz --progress \
    $LOCAL_PROJECT_PATH/deploy_vps.sh \
    $VPS_USER@$VPS_IP:$VPS_PROJECT_PATH/

# Copie des scripts de test
log_info "Copie des scripts de test..."
rsync -avz --progress \
    $LOCAL_PROJECT_PATH/test_communication.py \
    $VPS_USER@$VPS_IP:$VPS_PROJECT_PATH/

rsync -avz --progress \
    $LOCAL_PROJECT_PATH/test_api.py \
    $VPS_USER@$VPS_IP:$VPS_PROJECT_PATH/

# Copie de la documentation
log_info "Copie de la documentation..."
rsync -avz --progress \
    $LOCAL_PROJECT_PATH/README*.md \
    $VPS_USER@$VPS_IP:$VPS_PROJECT_PATH/

rsync -avz --progress \
    $LOCAL_PROJECT_PATH/*.md \
    $VPS_USER@$VPS_IP:$VPS_PROJECT_PATH/

# Attribution des permissions
log_info "Attribution des permissions..."
ssh $VPS_USER@$VPS_IP "chown -R $VPS_USER:$VPS_USER $VPS_PROJECT_PATH"
ssh $VPS_USER@$VPS_IP "chmod +x $VPS_PROJECT_PATH/deploy_vps.sh"

log_success "Copie terminée avec succès!"
echo ""
log_info "Vous pouvez maintenant vous connecter au VPS et exécuter:"
echo "ssh $VPS_USER@$VPS_IP"
echo "cd $VPS_PROJECT_PATH"
echo "chmod +x deploy_vps_mobaxterm.sh"
echo "./deploy_vps_mobaxterm.sh"
