#!/usr/bin/env python3
"""
Script de test complet pour l'API Heptuple Platform
"""
import requests
import json
import time
import sys
from typing import Dict, Any, Optional

class HeptupleAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token: Optional[str] = None
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log un résultat de test"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        if success:
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {message}")
    
    def test_health_check(self) -> bool:
        """Test du health check"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return False
    
    def test_database_health(self) -> bool:
        """Test de la santé de la base de données"""
        try:
            response = self.session.get(f"{self.base_url}/api/v2/db/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Database Health", True, f"Database: {data.get('database')}")
                return True
            else:
                self.log_test("Database Health", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Database Health", False, str(e))
            return False
    
    def test_user_registration(self) -> bool:
        """Test d'enregistrement d'utilisateur"""
        try:
            user_data = {
                "username": "test_user",
                "email": "test@example.com",
                "password": "test_password_123",
                "role": "user",
                "specialization": "Test"
            }
            
            response = self.session.post(f"{self.base_url}/api/v2/auth/register", json=user_data)
            if response.status_code == 200:
                data = response.json()
                self.log_test("User Registration", True, f"User ID: {data.get('id')}")
                return True
            else:
                self.log_test("User Registration", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("User Registration", False, str(e))
            return False
    
    def test_user_login(self) -> bool:
        """Test de connexion utilisateur"""
        try:
            login_data = {
                "username": "test_user",
                "password": "test_password_123"
            }
            
            response = self.session.post(f"{self.base_url}/api/v2/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_test("User Login", True, f"Token obtenu")
                return True
            else:
                self.log_test("User Login", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("User Login", False, str(e))
            return False
    
    def test_get_sourates(self) -> bool:
        """Test de récupération des sourates"""
        try:
            response = self.session.get(f"{self.base_url}/api/v2/sourates")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Sourates", True, f"Nombre de sourates: {len(data)}")
                return True
            else:
                self.log_test("Get Sourates", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Sourates", False, str(e))
            return False
    
    def test_get_sourate_by_number(self) -> bool:
        """Test de récupération d'une sourate spécifique"""
        try:
            response = self.session.get(f"{self.base_url}/api/v2/sourates/1")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Sourate by Number", True, f"Sourate: {data.get('nom_francais')}")
                return True
            else:
                self.log_test("Get Sourate by Number", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Sourate by Number", False, str(e))
            return False
    
    def test_text_analysis(self) -> bool:
        """Test d'analyse de texte"""
        try:
            analysis_data = {
                "texte": "بسم الله الرحمن الرحيم",
                "langue": "ar",
                "include_confidence": True,
                "include_details": True
            }
            
            response = self.session.post(f"{self.base_url}/api/v2/analyze", json=analysis_data)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Text Analysis", True, f"Dimension dominante: {data.get('dimension_dominante')}")
                return True
            else:
                self.log_test("Text Analysis", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Text Analysis", False, str(e))
            return False
    
    def test_enriched_analysis(self) -> bool:
        """Test d'analyse enrichie"""
        try:
            analysis_data = {
                "texte": "الحمد لله رب العالمين",
                "langue": "ar",
                "include_confidence": True,
                "include_details": True
            }
            
            response = self.session.post(f"{self.base_url}/api/v2/analyze-enriched", json=analysis_data)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Enriched Analysis", True, f"Score d'enrichissement: {data.get('score_enrichissement')}")
                return True
            else:
                self.log_test("Enriched Analysis", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Enriched Analysis", False, str(e))
            return False
    
    def test_universal_search(self) -> bool:
        """Test de recherche universelle"""
        try:
            search_data = {
                "query": "الله",
                "search_types": ["coran", "hadiths", "fiqh"],
                "limit": 10
            }
            
            response = self.session.post(f"{self.base_url}/api/v2/search/universal", json=search_data)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Universal Search", True, f"Total résultats: {data.get('total_results')}")
                return True
            else:
                self.log_test("Universal Search", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Universal Search", False, str(e))
            return False
    
    def test_coran_search(self) -> bool:
        """Test de recherche dans le Coran"""
        try:
            response = self.session.get(f"{self.base_url}/api/v2/search/coran?query=الله&limit=5")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Coran Search", True, f"Résultats: {data.get('total')}")
                return True
            else:
                self.log_test("Coran Search", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Coran Search", False, str(e))
            return False
    
    def test_hadiths_search(self) -> bool:
        """Test de recherche dans les Hadiths"""
        try:
            response = self.session.get(f"{self.base_url}/api/v2/search/hadiths?query=صلاة&limit=5")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Hadiths Search", True, f"Résultats: {data.get('total')}")
                return True
            else:
                self.log_test("Hadiths Search", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Hadiths Search", False, str(e))
            return False
    
    def test_fiqh_search(self) -> bool:
        """Test de recherche dans le Fiqh"""
        try:
            response = self.session.get(f"{self.base_url}/api/v2/search/fiqh?query=صلاة&limit=5")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Fiqh Search", True, f"Résultats: {data.get('total')}")
                return True
            else:
                self.log_test("Fiqh Search", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Fiqh Search", False, str(e))
            return False
    
    def test_get_dimensions(self) -> bool:
        """Test de récupération des dimensions"""
        try:
            response = self.session.get(f"{self.base_url}/api/v2/dimensions")
            if response.status_code == 200:
                data = response.json()
                dimensions = data.get("dimensions", [])
                self.log_test("Get Dimensions", True, f"Nombre de dimensions: {len(dimensions)}")
                return True
            else:
                self.log_test("Get Dimensions", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Dimensions", False, str(e))
            return False
    
    def test_user_info(self) -> bool:
        """Test de récupération des informations utilisateur"""
        try:
            response = self.session.get(f"{self.base_url}/api/v2/auth/me")
            if response.status_code == 200:
                data = response.json()
                self.log_test("User Info", True, f"Username: {data.get('username')}")
                return True
            else:
                self.log_test("User Info", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("User Info", False, str(e))
            return False
    
    def test_user_logout(self) -> bool:
        """Test de déconnexion utilisateur"""
        try:
            response = self.session.post(f"{self.base_url}/api/v2/auth/logout")
            if response.status_code == 200:
                data = response.json()
                self.log_test("User Logout", True, data.get("message", "Déconnexion réussie"))
                return True
            else:
                self.log_test("User Logout", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("User Logout", False, str(e))
            return False
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("🧪 Démarrage des tests de l'API Heptuple Platform")
        print("=" * 60)
        
        # Tests de base
        self.test_health_check()
        self.test_database_health()
        
        # Tests d'authentification
        self.test_user_registration()
        self.test_user_login()
        
        # Tests des fonctionnalités principales
        self.test_get_sourates()
        self.test_get_sourate_by_number()
        self.test_text_analysis()
        self.test_enriched_analysis()
        
        # Tests de recherche
        self.test_universal_search()
        self.test_coran_search()
        self.test_hadiths_search()
        self.test_fiqh_search()
        
        # Tests des dimensions
        self.test_get_dimensions()
        
        # Tests utilisateur
        self.test_user_info()
        self.test_user_logout()
        
        # Résumé des résultats
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 60)
        print(f"✅ Tests réussis: {self.test_results['passed']}")
        print(f"❌ Tests échoués: {self.test_results['failed']}")
        print(f"📈 Taux de réussite: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n🚨 ERREURS DÉTECTÉES:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        return self.test_results['failed'] == 0

def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Testeur de l'API Heptuple Platform")
    parser.add_argument("--url", default="http://localhost:8000", help="URL de base de l'API")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mode verbeux")
    
    args = parser.parse_args()
    
    tester = HeptupleAPITester(args.url)
    
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
