@echo off
REM Script de déploiement simplifié pour Heptuple Platform (Windows)
REM Usage: deploy.bat [start|stop|status|logs]

setlocal enabledelayedexpansion

REM Configuration
set COMPOSE_FILE=docker-compose.yml
set ENV_FILE=.env

REM Couleurs pour les messages (Windows)
set RED=[91m
set GREEN=[92m
set YELLOW=[93m
set BLUE=[94m
set NC=[0m

call :log_info "Script de déploiement Heptuple Platform"

if "%1"=="" goto :show_help
if "%1"=="help" goto :show_help
if "%1"=="start" goto :start_services
if "%1"=="stop" goto :stop_services
if "%1"=="status" goto :show_status
if "%1"=="logs" goto :show_logs
goto :show_help

:check_prerequisites
call :log_info "Vérification des prérequis..."
docker --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Docker n'est pas installé. Veuillez l'installer d'abord."
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Docker Compose n'est pas installé. Veuillez l'installer d'abord."
    exit /b 1
)

if not exist "%ENV_FILE%" (
    call :log_warning "Fichier %ENV_FILE% non trouvé. Création depuis le template..."
    if exist "env.example" (
        copy env.example "%ENV_FILE%" >nul
        call :log_warning "Veuillez configurer le fichier %ENV_FILE% avant de continuer."
        exit /b 1
    ) else (
        call :log_error "Aucun template d'environnement trouvé."
        exit /b 1
    )
)

call :log_success "Prérequis vérifiés avec succès."
goto :eof

:create_directories
call :log_info "Création des répertoires nécessaires..."
if not exist "backup" mkdir backup
if not exist "logs" mkdir logs
if not exist "monitoring\prometheus" mkdir monitoring\prometheus
if not exist "monitoring\grafana\dashboards" mkdir monitoring\grafana\dashboards
if not exist "monitoring\grafana\datasources" mkdir monitoring\grafana\datasources
call :log_success "Répertoires créés."
goto :eof

:start_services
call :check_prerequisites
if errorlevel 1 exit /b 1

call :create_directories
call :log_info "Démarrage des services..."

docker-compose -f "%COMPOSE_FILE%" --env-file "%ENV_FILE%" up -d

if errorlevel 1 (
    call :log_error "Erreur lors du démarrage des services."
    exit /b 1
)

call :log_success "Services démarrés avec succès."
call :log_info "Application accessible sur: http://localhost:8080"
call :log_info "API accessible sur: http://localhost:8000"
call :log_info "Prometheus accessible sur: http://localhost:9090"
call :log_info "Grafana accessible sur: http://localhost:3001"
goto :eof

:stop_services
call :log_info "Arrêt des services..."
docker-compose -f "%COMPOSE_FILE%" down
call :log_success "Services arrêtés."
goto :eof

:show_status
call :log_info "Statut des services..."
docker-compose -f "%COMPOSE_FILE%" ps
echo.
call :log_info "Logs des services:"
docker-compose -f "%COMPOSE_FILE%" logs --tail=10
goto :eof

:show_logs
if "%2"=="" (
    call :log_info "Affichage des logs de tous les services..."
    docker-compose -f "%COMPOSE_FILE%" logs -f
) else (
    call :log_info "Affichage des logs du service: %2"
    docker-compose -f "%COMPOSE_FILE%" logs -f %2
)
goto :eof

:show_help
echo Usage: %0 [COMMANDE]
echo.
echo Commandes disponibles:
echo   start     - Démarrer tous les services
echo   stop      - Arrêter tous les services
echo   status    - Afficher le statut des services
echo   logs      - Afficher les logs ^(optionnel: nom du service^)
echo   help      - Afficher cette aide
echo.
echo Exemples:
echo   %0 start
echo   %0 logs api
echo   %0 status
goto :eof

:log_info
echo %BLUE%[INFO]%NC% %~1
goto :eof

:log_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:log_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:log_error
echo %RED%[ERROR]%NC% %~1
goto :eof
