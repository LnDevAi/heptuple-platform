#!/bin/bash

# Script de vérification de santé pour Heptuple Platform avec gestion multi-instances
# Usage: ./scripts/health-check.sh [all|api|frontend|db|redis|elasticsearch|nginx] [instance_id]

set -e

# Configuration
TIMEOUT=10
RETRIES=3

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
    export NGINX_PORT=$nginx_port
    export API_PORT=$api_port
    export FRONTEND_PORT=$frontend_port
    export DB_PORT=$db_port
    export REDIS_PORT=$redis_port
    export ELASTICSEARCH_PORT=$elasticsearch_port
    export PROMETHEUS_PORT=$prometheus_port
    export GRAFANA_PORT=$grafana_port
}

# Fonction pour vérifier un endpoint HTTP
check_http_endpoint() {
    local url="$1"
    local name="$2"
    local expected_status="${3:-200}"
    
    log_info "Vérification de $name: $url"
    
    for i in $(seq 1 $RETRIES); do
        if curl -f -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$url" | grep -q "$expected_status"; then
            log_success "$name est opérationnel"
            return 0
        else
            if [ $i -lt $RETRIES ]; then
                log_warning "Tentative $i/$RETRIES échouée pour $name, nouvelle tentative..."
                sleep 2
            else
                log_error "$name n'est pas accessible"
                return 1
            fi
        fi
    done
}

# Fonction pour vérifier un conteneur Podman
check_container() {
    local container="$1"
    local name="$2"
    
    log_info "Vérification du conteneur $name: $container"
    
    if podman ps --format "table {{.Names}}" | grep -q "$container"; then
        local status=$(podman inspect --format "{{.State.Status}}" "$container")
        if [ "$status" = "running" ]; then
            log_success "$name est en cours d'exécution"
            return 0
        else
            log_error "$name n'est pas en cours d'exécution (statut: $status)"
            return 1
        fi
    else
        log_error "$name n'est pas démarré"
        return 1
    fi
}

# Fonction pour vérifier PostgreSQL
check_postgres() {
    log_info "Vérification de PostgreSQL..."
    
    if check_container "heptuple-postgres-$INSTANCE_ID" "PostgreSQL"; then
        if podman exec heptuple-postgres-$INSTANCE_ID pg_isready -U "heptuple_user_$INSTANCE_ID" -d "heptuple_db_$INSTANCE_ID" > /dev/null 2>&1; then
            log_success "PostgreSQL est prêt à accepter les connexions"
            return 0
        else
            log_error "PostgreSQL n'est pas prêt"
            return 1
        fi
    else
        return 1
    fi
}

# Fonction pour vérifier Redis
check_redis() {
    log_info "Vérification de Redis..."
    
    if check_container "heptuple-redis-$INSTANCE_ID" "Redis"; then
        if podman exec heptuple-redis-$INSTANCE_ID redis-cli ping > /dev/null 2>&1; then
            log_success "Redis répond aux commandes"
            return 0
        else
            log_error "Redis ne répond pas"
            return 1
        fi
    else
        return 1
    fi
}

# Fonction pour vérifier Elasticsearch
check_elasticsearch() {
    log_info "Vérification d'Elasticsearch..."
    
    if check_container "heptuple-elasticsearch-$INSTANCE_ID" "Elasticsearch"; then
        if check_http_endpoint "http://localhost:$ELASTICSEARCH_PORT/_cluster/health" "Elasticsearch"; then
            log_success "Elasticsearch est opérationnel"
            return 0
        else
            log_error "Elasticsearch n'est pas accessible"
            return 1
        fi
    else
        return 1
    fi
}

# Fonction pour vérifier l'API
check_api() {
    log_info "Vérification de l'API..."
    
    if check_container "heptuple-api-$INSTANCE_ID" "API Backend"; then
        if check_http_endpoint "http://localhost:$API_PORT/health" "API Health"; then
            log_success "API est opérationnelle"
            return 0
        else
            log_error "API n'est pas accessible"
            return 1
        fi
    else
        return 1
    fi
}

# Fonction pour vérifier le Frontend
check_frontend() {
    log_info "Vérification du Frontend..."
    
    if check_container "heptuple-frontend-$INSTANCE_ID" "Frontend"; then
        if check_http_endpoint "http://localhost:$FRONTEND_PORT/health" "Frontend Health"; then
            log_success "Frontend est opérationnel"
            return 0
        else
            log_error "Frontend n'est pas accessible"
            return 1
        fi
    else
        return 1
    fi
}

# Fonction pour vérifier Nginx
check_nginx() {
    log_info "Vérification de Nginx..."
    
    if check_container "heptuple-nginx-$INSTANCE_ID" "Nginx"; then
        if check_http_endpoint "http://localhost:$NGINX_PORT/nginx_status" "Nginx Status"; then
            log_success "Nginx est opérationnel"
            return 0
        else
            log_error "Nginx n'est pas accessible"
            return 1
        fi
    else
        return 1
    fi
}

# Fonction pour vérifier Prometheus
check_prometheus() {
    log_info "Vérification de Prometheus..."
    
    if check_container "heptuple-prometheus-$INSTANCE_ID" "Prometheus"; then
        if check_http_endpoint "http://localhost:$PROMETHEUS_PORT/-/healthy" "Prometheus Health"; then
            log_success "Prometheus est opérationnel"
            return 0
        else
            log_error "Prometheus n'est pas accessible"
            return 1
        fi
    else
        return 1
    fi
}

# Fonction pour vérifier Grafana
check_grafana() {
    log_info "Vérification de Grafana..."
    
    if check_container "heptuple-grafana-$INSTANCE_ID" "Grafana"; then
        if check_http_endpoint "http://localhost:$GRAFANA_PORT/api/health" "Grafana Health"; then
            log_success "Grafana est opérationnel"
            return 0
        else
            log_error "Grafana n'est pas accessible"
            return 1
        fi
    else
        return 1
    fi
}

# Fonction pour vérifier tous les services
check_all() {
    log_info "Vérification complète de tous les services pour l'instance $INSTANCE_ID..."
    
    # Calculer les ports pour cette instance
    calculate_ports $INSTANCE_ID
    
    local failed=0
    
    check_postgres || failed=1
    check_redis || failed=1
    check_elasticsearch || failed=1
    check_api || failed=1
    check_frontend || failed=1
    check_nginx || failed=1
    check_prometheus || failed=1
    check_grafana || failed=1
    
    if [ $failed -eq 0 ]; then
        log_success "Tous les services sont opérationnels pour l'instance $INSTANCE_ID!"
        return 0
    else
        log_error "Certains services ne sont pas opérationnels pour l'instance $INSTANCE_ID"
        return 1
    fi
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

# Fonction principale
main() {
    case "${1:-help}" in
        all)
            check_all
            ;;
        api)
            calculate_ports $INSTANCE_ID
            check_api
            ;;
        frontend)
            calculate_ports $INSTANCE_ID
            check_frontend
            ;;
        db|postgres)
            calculate_ports $INSTANCE_ID
            check_postgres
            ;;
        redis)
            calculate_ports $INSTANCE_ID
            check_redis
            ;;
        elasticsearch)
            calculate_ports $INSTANCE_ID
            check_elasticsearch
            ;;
        nginx)
            calculate_ports $INSTANCE_ID
            check_nginx
            ;;
        prometheus)
            calculate_ports $INSTANCE_ID
            check_prometheus
            ;;
        grafana)
            calculate_ports $INSTANCE_ID
            check_grafana
            ;;
        list)
            list_instances
            ;;
        *)
            log_error "Service non reconnu: $1"
            log_error "Usage: $0 [all|api|frontend|db|redis|elasticsearch|nginx|prometheus|grafana|list] [instance_id]"
            exit 1
            ;;
    esac
}
