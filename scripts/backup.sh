#!/bin/bash

# Script de sauvegarde pour Heptuple Platform avec gestion multi-instances
# Usage: ./scripts/backup.sh [full|db|redis|elasticsearch] [instance_id]

set -e

# Configuration
BACKUP_DIR="./backup"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=30

# Instance ID par défaut
DEFAULT_INSTANCE_ID=0
INSTANCE_ID=${2:-$DEFAULT_INSTANCE_ID}

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} Instance ${INSTANCE_ID}: $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} Instance ${INSTANCE_ID}: $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} Instance ${INSTANCE_ID}: $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} Instance ${INSTANCE_ID}: $1"
}

# Fonction de sauvegarde PostgreSQL
backup_postgres() {
    log_info "Sauvegarde de PostgreSQL..."
    
    local backup_file="$BACKUP_DIR/instance_$INSTANCE_ID/postgres_backup_$TIMESTAMP.sql"
    
    podman exec heptuple-postgres-$INSTANCE_ID pg_dump \
        -U "heptuple_user_$INSTANCE_ID" \
        -d "heptuple_db_$INSTANCE_ID" \
        --clean --if-exists --create > "$backup_file"
    
    log_success "PostgreSQL sauvegardé: $backup_file"
}

# Fonction de sauvegarde Redis
backup_redis() {
    log_info "Sauvegarde de Redis..."
    
    local backup_file="$BACKUP_DIR/instance_$INSTANCE_ID/redis_backup_$TIMESTAMP.rdb"
    
    podman exec heptuple-redis-$INSTANCE_ID redis-cli --rdb /data/dump.rdb
    podman cp heptuple-redis-$INSTANCE_ID:/data/dump.rdb "$backup_file"
    
    log_success "Redis sauvegardé: $backup_file"
}

# Fonction de sauvegarde Elasticsearch
backup_elasticsearch() {
    log_info "Sauvegarde d'Elasticsearch..."
    
    local backup_file="$BACKUP_DIR/instance_$INSTANCE_ID/elasticsearch_backup_$TIMESTAMP.json"
    
    # Créer un snapshot
    podman exec heptuple-elasticsearch-$INSTANCE_ID curl -X PUT \
        "localhost:9200/_snapshot/backup_repo/snapshot_$TIMESTAMP?wait_for_completion=true"
    
    # Exporter les données
    podman exec heptuple-elasticsearch-$INSTANCE_ID elasticsearch-dump \
        --input=http://localhost:9200 \
        --output="$backup_file"
    
    log_success "Elasticsearch sauvegardé: $backup_file"
}

# Fonction de nettoyage des anciennes sauvegardes
cleanup_old_backups() {
    log_info "Nettoyage des anciennes sauvegardes..."
    
    find "$BACKUP_DIR/instance_$INSTANCE_ID" -name "*.sql" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR/instance_$INSTANCE_ID" -name "*.rdb" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR/instance_$INSTANCE_ID" -name "*.json" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR/instance_$INSTANCE_ID" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
    
    log_success "Nettoyage terminé."
}

# Fonction principale
main() {
    # Créer le répertoire de sauvegarde
    mkdir -p "$BACKUP_DIR/instance_$INSTANCE_ID"
    
    case "${1:-full}" in
        full)
            log_info "Sauvegarde complète pour l'instance $INSTANCE_ID..."
            backup_postgres
            backup_redis
            backup_elasticsearch
            ;;
        db)
            backup_postgres
            ;;
        redis)
            backup_redis
            ;;
        elasticsearch)
            backup_elasticsearch
            ;;
        *)
            log_error "Usage: $0 [full|db|redis|elasticsearch] [instance_id]"
            exit 1
            ;;
    esac
    
    # Nettoyer les anciennes sauvegardes
    cleanup_old_backups
    
    log_success "Sauvegarde terminée avec succès pour l'instance $INSTANCE_ID!"
}
