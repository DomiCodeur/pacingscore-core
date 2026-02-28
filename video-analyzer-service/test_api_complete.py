"""
Test complet de l'API PacingScore
Teste les différents endpoints avec des vidéos YouTube réelles
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Test du endpoint health"""
    print("=" * 60)
    print("TEST 1: Endpoint /health")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erreur: {e}")
        return False

def test_analyze_youtube():
    """Test d'analyse d'une vidéo YouTube"""
    print("\n" + "=" * 60)
    print("TEST 2: Analyse vidéo YouTube")
    print("=" * 60)
    
    # Vidéo courte et populaire
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    payload = {
        "video_url": test_url,
        "max_duration": 60,
        "analyze_motion": False,
        "analyze_flashes": True
    }
    
    try:
        print(f"URL: {test_url}")
        print("Envoi de la requête...")
        
        response = requests.post(
            f"{BASE_URL}/analyze",
            json=payload,
            timeout=300  # 5 minutes max
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nRésultat:")
            print(f"  Success: {result.get('success')}")
            print(f"  Durée vidéo: {result.get('video_duration')}s")
            print(f"  Nombre scènes: {result.get('num_scenes')}")
            print(f"  ASL: {result.get('average_shot_length')}s")
            print(f"  Score composite: {result.get('composite_score')}")
            print(f"  Évaluation: {result.get('composite_evaluation', {}).get('label', 'N/A')}")
            
            if result.get('motion_analysis'):
                print(f"  Mouvement: {result['motion_analysis']['motion_intensity']}/100")
            
            if result.get('flash_analysis'):
                print(f"  Flashs: {result['flash_analysis']['flashes']} détectés")
            
            return True
        else:
            print(f"Erreur: {response.text}")
            return False
            
    except Exception as e:
        print(f"Erreur: {e}")
        return False

def test_history():
    """Test de l'historique"""
    print("\n" + "=" * 60)
    print("TEST 3: Historique des analyses")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/history?limit=5")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                history = result.get('data', [])
                print(f"Nombre d'entrées: {len(history)}")
                for item in history[:3]:
                    print(f"  - {item.get('series_title', 'N/A')}: {item.get('composite_score', item.get('pacing_score', 'N/A'))}")
            return True
        else:
            print(f"Erreur: {response.text}")
            return False
            
    except Exception as e:
        print(f"Erreur: {e}")
        return False

def test_ui():
    """Test de l'interface web"""
    print("\n" + "=" * 60)
    print("TEST 4: Interface web")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            if "PacingScore" in html and "Analyser" in html:
                print("Interface web accessible ✓")
                return True
            else:
                print("Interface web non détectée")
                return False
        else:
            print(f"Erreur: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Erreur: {e}")
        return False

def main():
    """Exécute tous les tests"""
    print("🚀 Lancement des tests PacingScore API")
    print(f"Serveur: {BASE_URL}")
    print("=" * 60)
    
    # Attendre que le serveur démarre
    print("\nAttente du démarrage du serveur...")
    for i in range(10):
        try:
            requests.get(f"{BASE_URL}/health", timeout=1)
            print("✓ Serveur prêt!")
            break
        except:
            if i < 9:
                print(f"  Tentative {i+1}/10...")
                time.sleep(2)
            else:
                print("❌ Serveur non démarré")
                return
    
    results = []
    
    # Tests
    results.append(("Health", test_health()))
    results.append(("Analyse YouTube", test_analyze_youtube()))
    results.append(("Historique", test_history()))
    results.append(("Interface web", test_ui()))
    
    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, r in results if r)
    
    print(f"\n{passed}/{total} tests passés")
    
    if passed == total:
        print("\n🎉 Tous les tests ont réussi!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) en échec")
        return 1

if __name__ == "__main__":
    exit(main())