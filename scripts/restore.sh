#!/bin/bash

# Script de restauration pour Heptuple Platform avec gestion multi-instances
# Usage: ./scripts/restore.sh [db|redis|elasticsearch] <backup_file> [instance_id]

set -e

# Configuration
BACKUP_DIR="./backup"

# Instance ID par défaut
DEFAULT_INSTANCE_ID=0
INSTANCE_ID=${3:-$DEFAULT_INSTANCE_ID}

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

# Fonction de restauration PostgreSQL
restore_postgres() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        log_error "Fichier de sauvegarde PostgreSQL non trouvé: $backup_file"
        exit 1
    fi
    
    log_info "Restauration de PostgreSQL depuis: $backup_file"
    
    # Arrêter temporairement l'API
    podman stop heptuple-api-$INSTANCE_ID 2>/dev/null || true
    
    # Restaurer la base de données
    podman exec -i heptuple-postgres-$INSTANCE_ID psql \
        -U "heptuple_user_$INSTANCE_ID" \
        -d "heptuple_db_$INSTANCE_ID" < "$backup_file"
    
    # Redémarrer l'API
    podman start heptuple-api-$INSTANCE_ID
    
    log_success "PostgreSQL restauré avec succès!"
}

# Fonction de restauration Redis
restore_redis() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        log_error "Fichier de sauvegarde Redis non trouvé: $backup_file"
        exit 1
    fi
    
    log_info "Restauration de Redis depuis: $backup_file"
    
    # Copier le fichier de sauvegarde dans le conteneur
    podman cp "$backup_file" heptuple-redis-$INSTANCE_ID:/data/dump.rdb
    
    # Redémarrer Redis pour charger la sauvegarde
    podman restart heptuple-redis-$INSTANCE_ID
    
    log_success "Redis restauré avec succès!"
}

# Fonction de restauration Elasticsearch
restore_elasticsearch() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        log_error "Fichier de sauvegarde Elasticsearch non trouvé: $backup_file"
        exit 1
    fi
    
    log_info "Restauration d'Elasticsearch depuis: $backup_file"
    
    # Arrêter temporairement l'API
    podman stop heptuple-api-$INSTANCE_ID 2>/dev/null || true
    
    # Supprimer tous les indices existants
    podman exec heptuple-elasticsearch-$INSTANCE_ID curl -X DELETE "localhost:9200/_all"
    
    # Restaurer depuis le fichier de sauvegarde
    podman exec -i heptuple-elasticsearch-$INSTANCE_ID elasticsearch-dump \
        --input="$backup_file" \
        --output=http://localhost:9200
    
    # Redémarrer l'API
    podman start heptuple-api-$INSTANCE_ID
    
    log_success "Elasticsearch restauré avec succès!"
}

# Fonction pour lister les sauvegardes disponibles
list_backups() {
    local service="$1"
    
    log_info "Sauvegardes disponibles pour $service (instance $INSTANCE_ID):"
    
    case "$service" in
        db|postgres)
            find "$BACKUP_DIR/instance_$INSTANCE_ID" -name "postgres_backup_*.sql" -printf "%f\n" | sort -r
            ;;
        redis)
            find "$BACKUP_DIR/instance_$INSTANCE_ID" -name "redis_backup_*.rdb" -printf "%f\n" | sort -r
            ;;
        elasticsearch)
            find "$BACKUP_DIR/instance_$INSTANCE_ID" -name "elasticsearch_backup_*.json" -printf "%f\n" | sort -r
            ;;
        *)
            log_error "Service non reconnu: $service"
            exit 1
            ;;
    esac
}

# Fonction principale
main() {
    if [ $# -lt 1 ]; then
        log_error "Usage: $0 [db|redis|elasticsearch] <backup_file> [instance_id]"
        log_error "Ou: $0 list [db|redis|elasticsearch] [instance_id]"
        exit 1
    fi
    
    case "$1" in
        list)
            if [ -z "$2" ]; then
                log_error "Spécifiez un service pour lister les sauvegardes"
                exit 1
            fi
            list_backups "$2"
            ;;
        db|postgres)
            if [ -z "$2" ]; then
                log_error "Spécifiez un fichier de sauvegarde PostgreSQL"
                exit 1
            fi
            restore_postgres "$2"
            ;;
        redis)
            if [ -z "$2" ]; then
                log_error "Spécifiez un fichier de sauvegarde Redis"
                exit 1
            fi
            restore_redis "$2"
            ;;
        elasticsearch)
            if [ -z "$2" ]; then
                log_error "Spécifiez un fichier de sauvegarde Elasticsearch"
                exit 1
            fi
            restore_elasticsearch "$2"
            ;;
        *)
            log_error "Service non reconnu: $1"
            log_error "Usage: $0 [db|redis|elasticsearch] <backup_file> [instance_id]"
            exit 1
            ;;
    esac
}
