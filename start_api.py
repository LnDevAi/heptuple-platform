#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple pour demarrer l'API Vision Heptuple
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Demarre l'API FastAPI locale"""
    print("Vision Heptuple - Demarrage API locale")
    print("=" * 50)
    
    # Aller dans le dossier backend
    backend_dir = Path(__file__).parent / "backend"
    
    if not backend_dir.exists():
        print("ERREUR: Dossier backend non trouve")
        sys.exit(1)
    
    # Installer les dependances si necessaire
    requirements_file = backend_dir / "requirements.txt"
    if requirements_file.exists():
        print("Installation des dependances...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True, cwd=backend_dir)
            print("OK: Dependances installees")
        except subprocess.CalledProcessError:
            print("ATTENTION: Erreur installation dependances")
    
    # Initialiser la base de donnees
    print("Initialisation base de donnees...")
    try:
        subprocess.run([
            sys.executable, "-c", 
            "from database_local import init_database; init_database()"
        ], check=True, cwd=backend_dir)
        print("OK: Base de donnees prete")
    except subprocess.CalledProcessError:
        print("ATTENTION: Erreur initialisation DB")
    
    # Demarrer le serveur
    print("Demarrage serveur API...")
    print("URL: http://localhost:8081")
    print("Health: http://localhost:8081/api/health")
    print("Docs: http://localhost:8081/docs")
    print("Ctrl+C pour arreter")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "main_simple.py"
        ], cwd=backend_dir)
    except KeyboardInterrupt:
        print("\nArret du serveur...")
    except Exception as e:
        print(f"ERREUR: {e}")

if __name__ == "__main__":
    main()
