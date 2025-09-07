#!/bin/bash

# Script de déploiement Podman pour Heptuple Platform avec gestion multi-instances
# Usage: ./deploy_podman.sh [start|stop|restart|status|logs|backup|update] [instance_id]

set -e

# Configuration
PROJECT_NAME="heptuple-platform"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
BACKUP_DIR="./backup"
LOG_DIR="./logs"

# Instance ID par défaut
DEFAULT_INSTANCE_ID=0
INSTANCE_ID=${2:-$DEFAULT_INSTANCE_ID}

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
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

# Fonction pour calculer les ports automatiquement
calculate_ports() {
    local instance_id=$1
    local port_offset=$((instance_id * 100))
    
    # Calculer les ports pour cette instance
    local nginx_port=$((8080 + port_offset))
    local api_port=$((8000 + port_offset))
    local frontend_port=$((3000 + port_offset))
    local db_port=$((5432 + port_offset))
    local redis_port=$((6379 + port_offset))
    local elasticsearch_port=$((9200 + port_offset))
    local prometheus_port=$((9090 + port_offset))
    local grafana_port=$((3001 + port_offset))
    
    # Exporter les variables
    export INSTANCE_ID=$instance_id
    export NGINX_PORT=$nginx_port
    export API_PORT=$api_port
    export FRONTEND_PORT=$frontend_port
    export DB_PORT=$db_port
    export REDIS_PORT=$redis_port
    export ELASTICSEARCH_PORT=$elasticsearch_port
    export PROMETHEUS_PORT=$prometheus_port
    export GRAFANA_PORT=$grafana_port
    
    log_info "Ports calculés pour l'instance $instance_id:"
    log_info "  Nginx: $nginx_port"
    log_info "  API: $api_port"
    log_info "  Frontend: $frontend_port"
    log_info "  PostgreSQL: $db_port"
    log_info "  Redis: $redis_port"
    log_info "  Elasticsearch: $elasticsearch_port"
    log_info "  Prometheus: $prometheus_port"
    log_info "  Grafana: $grafana_port"
}

# Fonction pour vérifier les prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    # Vérifier si Podman est installé
    if ! command -v podman &> /dev/null; then
        log_error "Podman n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi
    
    # Vérifier si podman-compose est installé
    if ! command -v podman-compose &> /dev/null; then
        log_warning "podman-compose n'est pas installé. Installation..."
        pip install podman-compose
    fi
    
    # Vérifier si le fichier .env existe
    if [ ! -f "$ENV_FILE" ]; then
        log_warning "Fichier $ENV_FILE non trouvé. Création depuis le template..."
        if [ -f "env.example" ]; then
            cp env.example "$ENV_FILE"
            log_warning "Veuillez configurer le fichier $ENV_FILE avant de continuer."
            exit 1
        else
            log_error "Aucun template d'environnement trouvé."
            exit 1
        fi
    fi
    
    log_success "Prérequis vérifiés avec succès."
}

# Fonction pour créer les répertoires nécessaires
create_directories() {
    log_info "Création des répertoires nécessaires..."
    
    mkdir -p "$BACKUP_DIR/instance_$INSTANCE_ID"
    mkdir -p "$LOG_DIR/instance_$INSTANCE_ID"
    mkdir -p "./monitoring/prometheus"
    mkdir -p "./monitoring/grafana/dashboards"
    mkdir -p "./monitoring/grafana/datasources"
    
    log_success "Répertoires créés."
}

# Fonction pour démarrer les services
start_services() {
    log_info "Démarrage des services pour l'instance $INSTANCE_ID..."
    
    # Calculer les ports pour cette instance
    calculate_ports $INSTANCE_ID
    
    # Charger les variables d'environnement
    source "$ENV_FILE"
    
    # Démarrer avec podman-compose
    podman-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    
    log_success "Services démarrés avec succès pour l'instance $INSTANCE_ID."
    log_info "Application accessible sur: http://localhost:$NGINX_PORT"
    log_info "API accessible sur: http://localhost:$API_PORT"
    log_info "Prometheus accessible sur: http://localhost:$PROMETHEUS_PORT"
    log_info "Grafana accessible sur: http://localhost:$GRAFANA_PORT"
}

# Fonction pour arrêter les services
stop_services() {
    log_info "Arrêt des services pour l'instance $INSTANCE_ID..."
    
    # Calculer les ports pour cette instance
    calculate_ports $INSTANCE_ID
    
    podman-compose -f "$COMPOSE_FILE" down
    
    log_success "Services arrêtés pour l'instance $INSTANCE_ID."
}

# Fonction pour redémarrer les services
restart_services() {
    log_info "Redémarrage des services pour l'instance $INSTANCE_ID..."
    
    stop_services
    sleep 5
    start_services
    
    log_success "Services redémarrés pour l'instance $INSTANCE_ID."
}

# Fonction pour afficher le statut des services
show_status() {
    log_info "Statut des services pour l'instance $INSTANCE_ID..."
    
    # Calculer les ports pour cette instance
    calculate_ports $INSTANCE_ID
    
    podman-compose -f "$COMPOSE_FILE" ps
    
    echo ""
    log_info "Logs des services:"
    podman-compose -f "$COMPOSE_FILE" logs --tail=10
}

# Fonction pour afficher les logs
show_logs() {
    local service=${1:-""}
    
    # Calculer les ports pour cette instance
    calculate_ports $INSTANCE_ID
    
    if [ -z "$service" ]; then
        log_info "Affichage des logs de tous les services pour l'instance $INSTANCE_ID..."
        podman-compose -f "$COMPOSE_FILE" logs -f
    else
        log_info "Affichage des logs du service $service pour l'instance $INSTANCE_ID..."
        podman-compose -f "$COMPOSE_FILE" logs -f "$service"
    fi
}

# Fonction pour sauvegarder les données
backup_data() {
    log_info "Sauvegarde des données pour l'instance $INSTANCE_ID..."
    
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_path="$BACKUP_DIR/instance_$INSTANCE_ID/backup_$timestamp"
    
    mkdir -p "$backup_path"
    
    # Calculer les ports pour cette instance
    calculate_ports $INSTANCE_ID
    
    # Sauvegarder PostgreSQL
    log_info "Sauvegarde de PostgreSQL..."
    podman exec heptuple-postgres-$INSTANCE_ID pg_dump -U "heptuple_user_$INSTANCE_ID" "heptuple_db_$INSTANCE_ID" > "$backup_path/postgres_backup.sql"
    
    # Sauvegarder Redis
    log_info "Sauvegarde de Redis..."
    podman exec heptuple-redis-$INSTANCE_ID redis-cli --rdb /data/dump.rdb
    podman cp heptuple-redis-$INSTANCE_ID:/data/dump.rdb "$backup_path/redis_backup.rdb"
    
    # Sauvegarder Elasticsearch
    log_info "Sauvegarde d'Elasticsearch..."
    podman exec heptuple-elasticsearch-$INSTANCE_ID elasticsearch-dump --input=http://localhost:9200 --output="$backup_path/elasticsearch_backup.json"
    
    # Compresser la sauvegarde
    tar -czf "$backup_path.tar.gz" -C "$BACKUP_DIR/instance_$INSTANCE_ID" "backup_$timestamp"
    rm -rf "$backup_path"
    
    log_success "Sauvegarde créée: $backup_path.tar.gz"
}

# Fonction pour mettre à jour les images
update_images() {
    log_info "Mise à jour des images pour l'instance $INSTANCE_ID..."
    
    # Calculer les ports pour cette instance
    calculate_ports $INSTANCE_ID
    
    podman-compose -f "$COMPOSE_FILE" pull
    podman-compose -f "$COMPOSE_FILE" up -d --force-recreate
    
    log_success "Images mises à jour pour l'instance $INSTANCE_ID."
}

# Fonction pour nettoyer les ressources
cleanup() {
    log_info "Nettoyage des ressources pour l'instance $INSTANCE_ID..."
    
    # Calculer les ports pour cette instance
    calculate_ports $INSTANCE_ID
    
    # Arrêter et supprimer les conteneurs
    podman-compose -f "$COMPOSE_FILE" down --remove-orphans
    
    # Supprimer les images non utilisées
    podman image prune -f
    
    # Supprimer les volumes non utilisés
    podman volume prune -f
    
    log_success "Nettoyage terminé pour l'instance $INSTANCE_ID."
}

# Fonction pour lister toutes les instances
list_instances() {
    log_info "Instances Heptuple Platform en cours d'exécution:"
    
    # Chercher tous les conteneurs heptuple
    local containers=$(podman ps --format "table {{.Names}}" | grep "heptuple-")
    
    if [ -z "$containers" ]; then
        log_info "Aucune instance en cours d'exécution."
        return
    fi
    
    # Extraire les IDs d'instance uniques
    local instance_ids=$(echo "$containers" | sed 's/.*heptuple-.*-\([0-9]*\)/\1/' | sort -u)
    
    for id in $instance_ids; do
        local port_offset=$((id * 100))
        local nginx_port=$((8080 + port_offset))
        local api_port=$((8000 + port_offset))
        local grafana_port=$((3001 + port_offset))
        
        echo "Instance $id:"
        echo "  - Application: http://localhost:$nginx_port"
        echo "  - API: http://localhost:$api_port"
        echo "  - Grafana: http://localhost:$grafana_port"
        echo ""
    done
}

# Fonction pour afficher l'aide
show_help() {
    echo "Usage: $0 [COMMANDE] [INSTANCE_ID]"
    echo ""
    echo "Commandes disponibles:"
    echo "  start     - Démarrer tous les services"
    echo "  stop      - Arrêter tous les services"
    echo "  restart   - Redémarrer tous les services"
    echo "  status    - Afficher le statut des services"
    echo "  logs      - Afficher les logs (optionnel: nom du service)"
    echo "  backup    - Créer une sauvegarde des données"
    echo "  update    - Mettre à jour les images et redémarrer"
    echo "  cleanup   - Nettoyer les ressources non utilisées"
    echo "  list      - Lister toutes les instances"
    echo "  help      - Afficher cette aide"
    echo ""
    echo "INSTANCE_ID: Numéro de l'instance (0 par défaut)"
    echo ""
    echo "Exemples:"
    echo "  $0 start           # Démarrer l'instance 0"
    echo "  $0 start 1         # Démarrer l'instance 1"
    echo "  $0 logs api 2      # Logs de l'API de l'instance 2"
    echo "  $0 backup 1        # Sauvegarde de l'instance 1"
    echo "  $0 list           # Lister toutes les instances"
}

# Fonction principale
main() {
    case "${1:-help}" in
        start)
            check_prerequisites
            create_directories
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            check_prerequisites
            restart_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$3"
            ;;
        backup)
            backup_data
            ;;
        update)
            check_prerequisites
            update_images
            ;;
        cleanup)
            cleanup
            ;;
        list)
            list_instances
            ;;
        help|*)
            show_help
            ;;
    esac
}

# Exécuter la fonction principale
main "$@"
