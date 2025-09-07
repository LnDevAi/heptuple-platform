#!/bin/bash

# Script de déploiement simplifié pour Heptuple Platform
# Usage: ./deploy.sh [start|stop|status|logs]

set -e

# Configuration
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Fonction pour vérifier les prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    # Vérifier si Docker est installé
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi
    
    # Vérifier si Docker Compose est installé
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose n'est pas installé. Veuillez l'installer d'abord."
        exit 1
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
    
    mkdir -p backup logs monitoring/prometheus monitoring/grafana/dashboards monitoring/grafana/datasources
    
    log_success "Répertoires créés."
}

# Fonction pour démarrer les services
start_services() {
    log_info "Démarrage des services..."
    
    # Charger les variables d'environnement
    source "$ENV_FILE"
    
    # Démarrer avec docker-compose
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    
    log_success "Services démarrés avec succès."
    log_info "Application accessible sur: http://localhost:8080"
    log_info "API accessible sur: http://localhost:8000"
    log_info "Prometheus accessible sur: http://localhost:9090"
    log_info "Grafana accessible sur: http://localhost:3001"
}

# Fonction pour arrêter les services
stop_services() {
    log_info "Arrêt des services..."
    
    docker-compose -f "$COMPOSE_FILE" down
    
    log_success "Services arrêtés."
}

# Fonction pour afficher le statut des services
show_status() {
    log_info "Statut des services..."
    
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo ""
    log_info "Logs des services:"
    docker-compose -f "$COMPOSE_FILE" logs --tail=10
}

# Fonction pour afficher les logs
show_logs() {
    local service=${1:-""}
    
    if [ -z "$service" ]; then
        log_info "Affichage des logs de tous les services..."
        docker-compose -f "$COMPOSE_FILE" logs -f
    else
        log_info "Affichage des logs du service: $service"
        docker-compose -f "$COMPOSE_FILE" logs -f "$service"
    fi
}

# Fonction pour afficher l'aide
show_help() {
    echo "Usage: $0 [COMMANDE]"
    echo ""
    echo "Commandes disponibles:"
    echo "  start     - Démarrer tous les services"
    echo "  stop      - Arrêter tous les services"
    echo "  status    - Afficher le statut des services"
    echo "  logs      - Afficher les logs (optionnel: nom du service)"
    echo "  help      - Afficher cette aide"
    echo ""
    echo "Exemples:"
    echo "  $0 start"
    echo "  $0 logs api"
    echo "  $0 status"
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
        status)
            show_status
            ;;
        logs)
            show_logs "$2"
            ;;
        help|*)
            show_help
            ;;
    esac
}

# Exécuter la fonction principale
main "$@"
