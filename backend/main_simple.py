"""
API FastAPI simple pour développement local - Port 8081
Version simplifiée sans dépendances complexes
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import uvicorn
from datetime import datetime

# Initialisation de l'application FastAPI
app = FastAPI(
    title="API Vision Heptuple - Simple", 
    description="API d'analyse exégétique selon la vision heptuple de la Fatiha",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Données de test simples
SOURATES_DATA = [
    {
        "id": 1, "numero": 1,
        "nom_arabe": "الفاتحة", "nom_francais": "Al-Fatiha",
        "type_revelation": "Mecquoise", "nombre_versets": 7,
        "profil_heptuple": {
            "mysteres": 85, "creation": 20, "attributs": 90,
            "eschatologie": 15, "tawhid": 95, "guidance": 80, "egarement": 10
        }
    },
    {
        "id": 2, "numero": 2,
        "nom_arabe": "البقرة", "nom_francais": "Al-Baqara",
        "type_revelation": "Médinoise", "nombre_versets": 286,
        "profil_heptuple": {
            "mysteres": 30, "creation": 60, "attributs": 40,
            "eschatologie": 70, "tawhid": 50, "guidance": 80, "egarement": 20
        }
    },
    {
        "id": 112, "numero": 112,
        "nom_arabe": "الإخلاص", "nom_francais": "Al-Ikhlas",
        "type_revelation": "Mecquoise", "nombre_versets": 4,
        "profil_heptuple": {
            "mysteres": 20, "creation": 10, "attributs": 95,
            "eschatologie": 5, "tawhid": 100, "guidance": 30, "egarement": 0
        }
    }
]

@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "API Vision Heptuple - Simple",
        "status": "running",
        "version": "2.1.0",
        "port": 8081,
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "health": "/api/health",
            "sourates": "/api/v2/sourates",
            "analyze": "/api/v2/analyze",
            "dimensions": "/api/v2/dimensions"
        }
    }

@app.get("/api/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.1.0",
        "port": 8081
    }

@app.get("/api/v2/sourates")
async def get_sourates():
    """Récupère toutes les sourates"""
    return SOURATES_DATA

@app.get("/api/v2/sourates/{numero}")
async def get_sourate(numero: int):
    """Récupère une sourate par numéro"""
    for sourate in SOURATES_DATA:
        if sourate["numero"] == numero:
            return sourate
    raise HTTPException(status_code=404, detail=f"Sourate {numero} non trouvée")

@app.post("/api/v2/analyze")
async def analyze_text(request: dict):
    """Analyse un texte (simulation)"""
    texte = request.get("texte", "")
    langue = request.get("langue", "auto")
    
    # Simulation d'analyse
    scores = {
        "mysteres": 45,
        "creation": 30,
        "attributs": 60,
        "eschatologie": 25,
        "tawhid": 70,
        "guidance": 55,
        "egarement": 15
    }
    
    return {
        "texte_analyse": texte,
        "langue_detectee": langue,
        "dimension_dominante": "tawhid",
        "scores": scores,
        "intensity_max": 70,
        "confidence_score": 0.85,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v2/dimensions")
async def get_dimensions():
    """Retourne les 7 dimensions"""
    return {
        "dimensions": [
            {"id": 1, "name": "Mystères", "description": "Les mystères divins"},
            {"id": 2, "name": "Création", "description": "La création de l'univers"},
            {"id": 3, "name": "Attributs", "description": "Les attributs divins"},
            {"id": 4, "name": "Eschatologie", "description": "Le jour dernier"},
            {"id": 5, "name": "Tawhid", "description": "L'unicité divine"},
            {"id": 6, "name": "Guidance", "description": "Le droit chemin"},
            {"id": 7, "name": "Égarement", "description": "Les voies de l'égarement"}
        ]
    }

if __name__ == "__main__":
    print("API Vision Heptuple - Demarrage sur port 8081")
    print("Documentation: http://localhost:8081/docs")
    print("Health check: http://localhost:8081/api/health")
    print("Ctrl+C pour arreter")
    
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8081,
        reload=True,
        log_level="info"
    )
