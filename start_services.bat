@echo off
echo ========================================
echo   DEMARRAGE DES SERVICES HEPTUPLE
echo ========================================
echo.

echo [1/4] Demarrage de PostgreSQL...
net start postgresql-x64-15
if %errorlevel% neq 0 (
    echo ⚠️  PostgreSQL deja demarre ou erreur
)

echo.
echo [2/4] Demarrage de Redis...
net start Redis
if %errorlevel% neq 0 (
    echo ⚠️  Redis deja demarre ou erreur
)

echo.
echo [3/4] Demarrage du Backend...
cd backend
start "Heptuple Backend" cmd /k "python main.py"
cd ..

echo.
echo [4/4] Demarrage du Frontend...
cd frontend
start "Heptuple Frontend" cmd /k "npm start"
cd ..

echo.
echo ========================================
echo   SERVICES DEMARRES
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Appuyez sur une touche pour tester la communication...
pause

echo.
echo Test de la communication BD ↔ Backend ↔ Frontend...
python test_communication.py

echo.
echo Appuyez sur une touche pour fermer...
pause
