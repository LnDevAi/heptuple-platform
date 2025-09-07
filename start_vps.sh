#!/bin/bash

# Script de démarrage rapide pour VPS Contabo
# Usage: ./start_vps.sh

set -e

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Démarrage de Heptuple Platform sur VPS${NC}"
echo "=================================="

# Vérification des privilèges
if [[ $EUID -ne 0 ]]; then
   echo -e "${YELLOW}⚠️  Ce script doit être exécuté en tant que root${NC}"
   echo "Utilisez: sudo ./start_vps.sh"
   exit 1
fi

# Vérification de l'installation
if [ ! -f "/opt/heptuple-platform/backend/main.py" ]; then
    echo -e "${YELLOW}⚠️  Installation non détectée${NC}"
    echo "Exécutez d'abord: ./deploy_vps.sh install"
    exit 1
fi

# Démarrage des services
echo -e "${BLUE}📡 Démarrage des services...${NC}"

# PostgreSQL
echo "  - PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

# Redis
echo "  - Redis..."
systemctl start redis-server
systemctl enable redis-server

# Nginx
echo "  - Nginx..."
systemctl start nginx
systemctl enable nginx

# Heptuple Platform
echo "  - Heptuple Platform API..."
systemctl start heptuple-platform
systemctl enable heptuple-platform

# Attente du démarrage
echo -e "${BLUE}⏳ Attente du démarrage des services...${NC}"
sleep 10

# Vérification du statut
echo -e "${BLUE}🔍 Vérification du statut...${NC}"

# Test de l'API
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ API Backend: Opérationnel${NC}"
else
    echo -e "${YELLOW}⚠️  API Backend: Problème détecté${NC}"
fi

# Test de la base de données
if curl -s http://localhost:8000/api/v2/db/health > /dev/null; then
    echo -e "${GREEN}✅ Base de données: Opérationnelle${NC}"
else
    echo -e "${YELLOW}⚠️  Base de données: Problème détecté${NC}"
fi

# Test de Nginx
if curl -s http://localhost/health > /dev/null; then
    echo -e "${GREEN}✅ Nginx: Opérationnel${NC}"
else
    echo -e "${YELLOW}⚠️  Nginx: Problème détecté${NC}"
fi

# Affichage des informations
echo ""
echo -e "${GREEN}🎉 Heptuple Platform est maintenant opérationnel !${NC}"
echo "=================================="
echo ""
echo "📱 Accès aux services:"
echo "  - Application: http://localhost"
echo "  - API: http://localhost/api"
echo "  - Documentation: http://localhost/docs"
echo ""
echo "🔧 Commandes utiles:"
echo "  - Statut: ./deploy_vps.sh status"
echo "  - Logs: ./deploy_vps.sh logs"
echo "  - Redémarrage: ./deploy_vps.sh restart"
echo "  - Arrêt: ./deploy_vps.sh stop"
echo ""
echo "🧪 Test de l'API:"
echo "  - python3 test_api.py --url http://localhost/api"
echo ""

# Affichage des ports utilisés
echo -e "${BLUE}🔌 Ports utilisés:${NC}"
netstat -tlnp | grep -E ":(80|443|8000|5432|6379)" | while read line; do
    echo "  $line"
done

echo ""
echo -e "${GREEN}✨ Démarrage terminé avec succès !${NC}"
