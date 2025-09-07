# Script de démarrage des services Heptuple Platform
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DEMARRAGE DES SERVICES HEPTUPLE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/4] Démarrage de PostgreSQL..." -ForegroundColor Yellow
try {
    Start-Service -Name "postgresql-x64-15" -ErrorAction SilentlyContinue
    Write-Host "✅ PostgreSQL démarré" -ForegroundColor Green
} catch {
    Write-Host "⚠️  PostgreSQL déjà démarré ou erreur" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[2/4] Démarrage de Redis..." -ForegroundColor Yellow
try {
    Start-Service -Name "Redis" -ErrorAction SilentlyContinue
    Write-Host "✅ Redis démarré" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Redis déjà démarré ou erreur" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[3/4] Démarrage du Backend..." -ForegroundColor Yellow
Set-Location backend
Start-Process -FilePath "cmd" -ArgumentList "/k", "python main.py" -WindowStyle Normal
Set-Location ..

Write-Host ""
Write-Host "[4/4] Démarrage du Frontend..." -ForegroundColor Yellow
Set-Location frontend
Start-Process -FilePath "cmd" -ArgumentList "/k", "npm start" -WindowStyle Normal
Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   SERVICES DÉMARRÉS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend: http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host ""

Read-Host "Appuyez sur Entrée pour tester la communication..."

Write-Host ""
Write-Host "Test de la communication BD ↔ Backend ↔ Frontend..." -ForegroundColor Yellow
python test_communication.py

Write-Host ""
Read-Host "Appuyez sur Entrée pour fermer..."
