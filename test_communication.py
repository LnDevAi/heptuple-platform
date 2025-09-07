#!/usr/bin/env python3
"""
Script de test pour vérifier la communication BD ↔ Backend ↔ Frontend
"""
import requests
import psycopg2
import redis
import json
import time
import sys
from typing import Dict, Any, Optional

class CommunicationTester:
    def __init__(self):
        self.results = {
            "database": {"status": "unknown", "details": ""},
            "backend": {"status": "unknown", "details": ""},
            "frontend": {"status": "unknown", "details": ""},
            "communication": {"status": "unknown", "details": ""}
        }
    
    def test_database_connection(self) -> bool:
        """Test de connexion à la base de données PostgreSQL"""
        try:
            # Configuration de la base de données
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="heptuple_db",
                user="heptuple_user",
                password="heptuple_pass"
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            
            # Test des tables principales
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('users', 'sourates', 'profils_heptuple', 'versets')
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            # Test des données
            cursor.execute("SELECT COUNT(*) FROM sourates;")
            sourates_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM profils_heptuple;")
            profils_count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            self.results["database"] = {
                "status": "success",
                "details": f"PostgreSQL {version[0][:50]}... | Tables: {len(tables)}/4 | Sourates: {sourates_count} | Profils: {profils_count}"
            }
            
            print(f"✅ Base de données: Connexion réussie")
            print(f"   - Version: {version[0][:50]}...")
            print(f"   - Tables trouvées: {len(tables)}/4")
            print(f"   - Sourates: {sourates_count}")
            print(f"   - Profils heptuple: {profils_count}")
            
            return True
            
        except Exception as e:
            self.results["database"] = {
                "status": "error",
                "details": str(e)
            }
            print(f"❌ Base de données: Erreur de connexion - {e}")
            return False
    
    def test_redis_connection(self) -> bool:
        """Test de connexion à Redis"""
        try:
            r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            r.ping()
            
            # Test d'écriture/lecture
            r.set('test_key', 'test_value', ex=10)
            value = r.get('test_key')
            r.delete('test_key')
            
            if value == 'test_value':
                self.results["redis"] = {
                    "status": "success",
                    "details": "Redis opérationnel - Lecture/écriture OK"
                }
                print(f"✅ Redis: Connexion et opérations réussies")
                return True
            else:
                raise Exception("Test de lecture/écriture échoué")
                
        except Exception as e:
            self.results["redis"] = {
                "status": "error",
                "details": str(e)
            }
            print(f"❌ Redis: Erreur - {e}")
            return False
    
    def test_backend_api(self) -> bool:
        """Test de l'API Backend"""
        try:
            # Test du health check
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code != 200:
                raise Exception(f"Health check failed: {response.status_code}")
            
            health_data = response.json()
            
            # Test de la connexion à la base de données via l'API
            response = requests.get("http://localhost:8000/api/v2/db/health", timeout=5)
            if response.status_code != 200:
                raise Exception(f"Database health check failed: {response.status_code}")
            
            db_health = response.json()
            
            # Test d'un endpoint qui nécessite la base de données
            # Note: Cet endpoint nécessite maintenant une authentification
            # On va tester l'endpoint des dimensions qui est public
            response = requests.get("http://localhost:8000/api/v2/dimensions", timeout=5)
            if response.status_code != 200:
                raise Exception(f"Dimensions endpoint failed: {response.status_code}")
            
            dimensions_data = response.json()
            
            self.results["backend"] = {
                "status": "success",
                "details": f"API opérationnelle | Health: {health_data.get('status')} | DB: {db_health.get('database')} | Dimensions: {len(dimensions_data.get('dimensions', []))}"
            }
            
            print(f"✅ Backend API: Opérationnel")
            print(f"   - Health: {health_data.get('status')}")
            print(f"   - Base de données: {db_health.get('database')}")
            print(f"   - Dimensions disponibles: {len(dimensions_data.get('dimensions', []))}")
            
            return True
            
        except Exception as e:
            self.results["backend"] = {
                "status": "error",
                "details": str(e)
            }
            print(f"❌ Backend API: Erreur - {e}")
            return False
    
    def test_frontend_access(self) -> bool:
        """Test d'accès au frontend"""
        try:
            # Test du frontend React
            response = requests.get("http://localhost:3000", timeout=5)
            if response.status_code != 200:
                raise Exception(f"Frontend not accessible: {response.status_code}")
            
            # Vérification que c'est bien une page React
            if "react" not in response.text.lower() and "heptuple" not in response.text.lower():
                raise Exception("Page ne semble pas être le frontend Heptuple")
            
            self.results["frontend"] = {
                "status": "success",
                "details": f"Frontend accessible | Status: {response.status_code} | Taille: {len(response.text)} chars"
            }
            
            print(f"✅ Frontend: Accessible")
            print(f"   - Status: {response.status_code}")
            print(f"   - Taille de la page: {len(response.text)} caractères")
            
            return True
            
        except Exception as e:
            self.results["frontend"] = {
                "status": "error",
                "details": str(e)
            }
            print(f"❌ Frontend: Erreur - {e}")
            return False
    
    def test_communication_flow(self) -> bool:
        """Test du flux de communication complet"""
        try:
            print("\n🔄 Test du flux de communication complet...")
            
            # 1. Test de l'authentification
            print("   1. Test d'inscription utilisateur...")
            register_data = {
                "username": "test_user_comm",
                "email": "test@example.com",
                "password": "test_password_123",
                "role": "user"
            }
            
            response = requests.post("http://localhost:8000/api/v2/auth/register", 
                                   json=register_data, timeout=10)
            
            if response.status_code not in [200, 400]:  # 400 si utilisateur existe déjà
                raise Exception(f"Registration failed: {response.status_code}")
            
            print("   ✅ Inscription OK")
            
            # 2. Test de connexion
            print("   2. Test de connexion...")
            login_data = {
                "username": "test_user_comm",
                "password": "test_password_123"
            }
            
            response = requests.post("http://localhost:8000/api/v2/auth/login", 
                                   json=login_data, timeout=10)
            
            if response.status_code != 200:
                raise Exception(f"Login failed: {response.status_code}")
            
            login_result = response.json()
            token = login_result.get("access_token")
            
            if not token:
                raise Exception("Token non reçu")
            
            print("   ✅ Connexion OK")
            
            # 3. Test d'accès aux sourates avec authentification
            print("   3. Test d'accès aux sourates...")
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get("http://localhost:8000/api/v2/sourates", 
                                  headers=headers, timeout=10)
            
            if response.status_code != 200:
                raise Exception(f"Sourates access failed: {response.status_code}")
            
            sourates_data = response.json()
            
            if not sourates_data or len(sourates_data) == 0:
                raise Exception("Aucune sourate récupérée")
            
            print(f"   ✅ Sourates récupérées: {len(sourates_data)}")
            
            # 4. Test d'analyse de texte
            print("   4. Test d'analyse de texte...")
            analysis_data = {
                "texte": "بسم الله الرحمن الرحيم",
                "langue": "ar",
                "include_confidence": True
            }
            
            response = requests.post("http://localhost:8000/api/v2/analyze", 
                                   json=analysis_data, headers=headers, timeout=15)
            
            if response.status_code != 200:
                raise Exception(f"Analysis failed: {response.status_code}")
            
            analysis_result = response.json()
            
            if not analysis_result.get("scores"):
                raise Exception("Analyse sans scores")
            
            print("   ✅ Analyse de texte OK")
            
            # 5. Test de recherche
            print("   5. Test de recherche universelle...")
            search_data = {
                "query": "الله",
                "search_types": ["coran"],
                "limit": 5
            }
            
            response = requests.post("http://localhost:8000/api/v2/search/universal", 
                                   json=search_data, headers=headers, timeout=10)
            
            if response.status_code != 200:
                raise Exception(f"Search failed: {response.status_code}")
            
            search_result = response.json()
            
            print(f"   ✅ Recherche OK: {search_result.get('total_results', 0)} résultats")
            
            self.results["communication"] = {
                "status": "success",
                "details": f"Flux complet OK | Sourates: {len(sourates_data)} | Analyse: OK | Recherche: {search_result.get('total_results', 0)} résultats"
            }
            
            print("\n✅ Communication complète: SUCCÈS")
            return True
            
        except Exception as e:
            self.results["communication"] = {
                "status": "error",
                "details": str(e)
            }
            print(f"\n❌ Communication complète: ÉCHEC - {e}")
            return False
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("🧪 Test de Communication BD ↔ Backend ↔ Frontend")
        print("=" * 60)
        
        # Tests individuels
        db_ok = self.test_database_connection()
        redis_ok = self.test_redis_connection()
        backend_ok = self.test_backend_api()
        frontend_ok = self.test_frontend_access()
        
        # Test du flux complet
        if db_ok and backend_ok:
            communication_ok = self.test_communication_flow()
        else:
            communication_ok = False
            self.results["communication"] = {
                "status": "skipped",
                "details": "Tests prérequis échoués"
            }
        
        # Résumé
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 60)
        
        total_tests = 5
        passed_tests = sum([
            db_ok,
            redis_ok, 
            backend_ok,
            frontend_ok,
            communication_ok
        ])
        
        print(f"✅ Tests réussis: {passed_tests}/{total_tests}")
        print(f"❌ Tests échoués: {total_tests - passed_tests}/{total_tests}")
        print(f"📈 Taux de réussite: {(passed_tests/total_tests*100):.1f}%")
        
        print("\n📋 DÉTAILS:")
        for component, result in self.results.items():
            status_icon = "✅" if result["status"] == "success" else "❌" if result["status"] == "error" else "⏭️"
            print(f"  {status_icon} {component.upper()}: {result['details']}")
        
        if communication_ok:
            print("\n🎉 COMMUNICATION COMPLÈTE: BD ↔ Backend ↔ Frontend OPÉRATIONNELLE!")
        else:
            print("\n🚨 PROBLÈMES DÉTECTÉS: Vérifiez les composants en erreur")
        
        return communication_ok

def main():
    """Fonction principale"""
    tester = CommunicationTester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur fatale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
