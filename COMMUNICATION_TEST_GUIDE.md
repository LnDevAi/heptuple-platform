# Guide de Test de Communication - Heptuple Platform

## 🎯 Objectif
Vérifier que la communication entre la Base de Données, le Backend et le Frontend fonctionne correctement.

## 📋 Prérequis
- PostgreSQL 15 installé et configuré
- Redis installé et configuré
- Python 3.11+ avec les dépendances
- Node.js 18+ pour le frontend

## 🚀 Démarrage Rapide

### Option 1: Script Automatique (Windows)
```bash
# Exécuter le script de démarrage
start_services.bat

# Ou avec PowerShell
.\start_services.ps1
```

### Option 2: Démarrage Manuel
```bash
# 1. Démarrer PostgreSQL
net start postgresql-x64-15

# 2. Démarrer Redis
net start Redis

# 3. Démarrer le Backend
cd backend
python main.py

# 4. Démarrer le Frontend (nouveau terminal)
cd frontend
npm start
```

## 🧪 Test de Communication

### Test Automatique
```bash
python test_communication.py
```

### Test Manuel

#### 1. Test de la Base de Données
```bash
# Connexion PostgreSQL
psql -h localhost -U heptuple_user -d heptuple_db

# Vérifier les tables
\dt

# Compter les sourates
SELECT COUNT(*) FROM sourates;
```

#### 2. Test du Backend API
```bash
# Health check
curl http://localhost:8000/health

# Test de la base de données via l'API
curl http://localhost:8000/api/v2/db/health

# Test des dimensions (endpoint public)
curl http://localhost:8000/api/v2/dimensions
```

#### 3. Test d'Authentification
```bash
# Inscription
curl -X POST http://localhost:8000/api/v2/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"test123456","role":"user"}'

# Connexion
curl -X POST http://localhost:8000/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123456"}'
```

#### 4. Test des Endpoints Authentifiés
```bash
# Récupérer les sourates (avec token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v2/sourates

# Analyser un texte
curl -X POST http://localhost:8000/api/v2/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"texte":"بسم الله الرحمن الرحيم","langue":"ar"}'
```

#### 5. Test du Frontend
- Ouvrir http://localhost:3000
- Vérifier que la page se charge
- Tester la connexion/inscription
- Tester l'analyse de texte
- Tester la recherche universelle

## ✅ Résultats Attendus

### Base de Données
- ✅ Connexion PostgreSQL réussie
- ✅ Tables créées (users, sourates, profils_heptuple, versets, hadiths, fiqh_rulings)
- ✅ Données insérées (114 sourates minimum)

### Backend API
- ✅ Health check: `{"status": "healthy", "timestamp": "..."}`
- ✅ Database health: `{"database": "connected", "tables": 6}`
- ✅ Dimensions: Liste des 7 dimensions heptuple

### Authentification
- ✅ Inscription utilisateur réussie
- ✅ Connexion avec token JWT
- ✅ Accès aux endpoints protégés

### Frontend
- ✅ Page d'accueil chargée
- ✅ Interface d'authentification fonctionnelle
- ✅ Analyse de texte opérationnelle
- ✅ Recherche universelle accessible

## 🚨 Problèmes Courants

### Base de Données
```bash
# Erreur: connexion refusée
# Solution: Vérifier que PostgreSQL est démarré
net start postgresql-x64-15

# Erreur: utilisateur inexistant
# Solution: Créer l'utilisateur et la base
createdb -U postgres heptuple_db
createuser -U postgres heptuple_user
```

### Backend
```bash
# Erreur: port 8000 occupé
# Solution: Changer le port ou tuer le processus
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Erreur: modules manquants
# Solution: Installer les dépendances
pip install -r backend/requirements.txt
```

### Frontend
```bash
# Erreur: port 3000 occupé
# Solution: Changer le port
set PORT=3001 && npm start

# Erreur: modules manquants
# Solution: Installer les dépendances
npm install
```

### Redis
```bash
# Erreur: Redis non accessible
# Solution: Démarrer Redis
net start Redis

# Ou installer Redis si absent
# Télécharger depuis: https://github.com/microsoftarchive/redis/releases
```

## 📊 Interprétation des Résultats

### Test Réussi (100%)
```
✅ Tests réussis: 5/5
❌ Tests échoués: 0/5
📈 Taux de réussite: 100.0%

🎉 COMMUNICATION COMPLÈTE: BD ↔ Backend ↔ Frontend OPÉRATIONNELLE!
```

### Test Partiellement Réussi
```
✅ Tests réussis: 3/5
❌ Tests échoués: 2/5
📈 Taux de réussite: 60.0%

🚨 PROBLÈMES DÉTECTÉS: Vérifiez les composants en erreur
```

## 🔧 Dépannage Avancé

### Logs de Debug
```bash
# Backend avec logs détaillés
cd backend
set LOG_LEVEL=DEBUG
python main.py

# Frontend avec logs
cd frontend
set REACT_APP_DEBUG=true
npm start
```

### Test de Performance
```bash
# Test de charge simple
python -c "
import requests
import time
start = time.time()
for i in range(100):
    requests.get('http://localhost:8000/health')
print(f'100 requêtes en {time.time()-start:.2f}s')
"
```

## 📝 Rapport de Test

Après chaque test, documentez:
1. **Date et heure** du test
2. **Version** des composants
3. **Résultats** de chaque test
4. **Problèmes** rencontrés
5. **Solutions** appliquées
6. **Recommandations** d'amélioration

---

## 🎯 Prochaines Étapes

Une fois la communication validée:
1. **Déploiement VPS** avec `deploy_vps.sh`
2. **Configuration SSL** avec Let's Encrypt
3. **Monitoring** avec Prometheus/Grafana
4. **Tests de charge** avec Apache Bench
5. **Sauvegarde** automatique de la base de données
