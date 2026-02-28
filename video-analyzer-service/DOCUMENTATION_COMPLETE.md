# PacingScore - Documentation Complète

## 🎯 Résumé du Projet

**PacingScore** est un système complet d'analyse vidéo qui analyse les "cuts" de scène dans des vidéos YouTube et calcule un score de pacing pour évaluer la stimulation visuelle.

---

## ✅ ÉTAT ACTUEL - Tout fonctionne !

### **Ce qui est OPÉRATIONNEL :**

1. **✅ Analyseur vidéo** - Détection de scènes avec PySceneDetect
2. **✅ Détection des flashs** - Analyse des transitions de luminosité
3. **✅ Score composite** - Combinaison ASL + Mouvement + Flashs
4. **✅ yt-dlp Python** - Téléchargement direct (plus besoin de .exe)
5. **✅ Interface web** - UI complète et fonctionnelle
6. **✅ API REST** - Endpoints `/analyze`, `/compare`, `/history`, `/health`
7. **✅ Supabase** - Mode mock activé (configurable pour la production)

---

## 📊 Résultats des Tests

### **Test 1 : Analyseur Vidéo**
```
Vidéo: 6.0 secondes
Scènes: 2 détectées
ASL: 3.0 secondes/plan
Score composite: 9.76
Évaluation: HYPER-STIMULANT
Flashs: 2 détectés
```

### **Test 2 : Interface Web**
```
Statut: SUCCES
URL: http://localhost:5000
Fonctionnalités: Analyse, Comparaison, Historique
```

### **Test 3 : API REST**
```
Health Check: 200 OK
Analyse vidéo: Fonctionne
Historique: Fonctionne (mock)
```

---

## 🚀 Démarrage Rapide

### **Méthode 1 : Exécutable Batch (Recommandé)**

1. Ouvrir le dossier :
   ```
   cd "C:\Users\mathi\Documents\Github\pacingscore-clean\video-analyzer-service"
   ```

2. Exécuter :
   ```
   start_server.bat
   ```

3. Ouvrir votre navigateur sur :
   ```
   http://localhost:5000
   ```

### **Méthode 2 : Terminal PowerShell**

```powershell
cd "C:\Users\mathi\Documents\Github\pacingscore-clean\video-analyzer-service"
python simple_server.py
```

Puis ouvrez http://localhost:5000 dans votre navigateur.

---

## 🌐 Interface Web

### **Accès :** http://localhost:5000

### **Fonctionnalités :**

#### **1. Onglet "Analyser"**
- Entrez l'URL d'une vidéo YouTube
- Option: Analyser le mouvement (plus lent)
- Option: Détecter les flashs
- Lancer l'analyse (1-2 minutes)

#### **2. Onglet "Comparer"**
- Comparez deux vidéos côte-à-côte
- Affichage graphique des différences
- Recommandations automatiques

#### **3. Onglet "Historique"**
- Liste des analyses précédentes
- Scores et évaluations

---

## 📡 API REST - Endpoints

### **1. Health Check**
```bash
GET http://localhost:5000/health
```

### **2. Analyser une vidéo**
```bash
POST http://localhost:5000/analyze
Content-Type: application/json

{
    "video_url": "https://www.youtube.com/watch?v=...",
    "max_duration": 120,
    "analyze_motion": false,
    "analyze_flashes": true
}
```

**Réponse :**
```json
{
    "success": true,
    "video_duration": 120.0,
    "num_scenes": 15,
    "average_shot_length": 8.0,
    "pacing_score": 65,
    "composite_score": 62,
    "composite_evaluation": {
        "label": "CALME",
        "description": "Rythme standard...",
        "color": "lime"
    },
    "motion_analysis": {...},
    "flash_analysis": {...}
}
```

### **3. Comparer deux vidéos**
```bash
POST http://localhost:5000/compare
Content-Type: application/json

{
    "video1_url": "https://www.youtube.com/watch?v=...",
    "video2_url": "https://www.youtube.com/watch?v=...",
    "name1": "Vidéo 1",
    "name2": "Vidéo 2"
}
```

### **4. Historique**
```bash
GET http://localhost:5000/history?limit=10
```

### **5. Interface Web**
```bash
GET http://localhost:5000/
```

---

## 📈 Métriques et Scores

### **Échelle ASL (Average Shot Length)**

| ASL (sec/plan) | Score | Évaluation | Description |
|----------------|-------|------------|-------------|
| < 4s | 10 | HYPER-STIMULANT | Très intense - Déconseillé |
| 4-6s | 25 | STIMULANT | Intense - Limitation recommandée |
| 6-8s | 45 | MODÉRÉ | Standard - OK enfants + grands |
| 8-10s | 65 | CALME | Doux - Bon pour jeunes enfants |
| 10-14s | 80 | TRÈS CALME | Idéal pour les tout-petits |
| > 14s | 90+ | CONTEMPLATIF | Parfait pour la concentration |

### **Facteurs du Score Composite**

1. **ASL** (50% du score)
2. **Intensité du mouvement** (30%)
3. **Flashs détectés** (20%)

### **Détection des Flashs**

- **Frames noirs** : Luminosité moyenne < 10
- **Flashs** : Changement > 100 niveaux de gris
- **Intensité** : Score 0-100 basé sur la quantité

### **Analyse du Mouvement (Optionnel)**

- **Méthode** : Flux optique Lucas-Kanade
- **Zone** : 30 premières secondes (pour la performance)
- **Score** : Magnitude moyenne des vecteurs (0-100)

---

## 🔧 Configuration

### **Fichier .env (à créer)**

```env
# Supabase (optionnel - sinon mode mock)
SUPABASE_URL=https://votre-project.supabase.co
SUPABASE_ANON_KEY=votre-anon-key

# API
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Analyseur
SCENEDETECT_THRESHOLD=27.0
MIN_SCENE_LEN=15
MAX_VIDEO_DURATION=120

# yt-dlp
YT_DLP_QUALITY=bestvideo[height<=480]
```

---

## 🔍 Résolution de Problèmes

### **Problème : Le serveur ne démarre pas**

**Solution :**
```powershell
# Vérifier si le port est utilisé
netstat -ano | findstr :5000

# Si oui, tuer le processus
taskkill /PID <PID> /F
```

### **Problème : yt-dlp ne télécharge pas**

**Solution :**
- Vérifier que yt-dlp est installé : `pip show yt-dlp`
- Mettre à jour : `pip install --upgrade yt-dlp`

### **Problème : Encodage Unicode**

**Solution :** Les emojis sont désactivés pour la compatibilité Windows. Utilisez du texte simple.

### **Problème : Supabase non configuré**

**Solution :** Le système fonctionne en mode mock. Pour la production, configurez les variables d'environnement.

---

## 📁 Structure des Fichiers

```
video-analyzer-service/
├── api.py                    # API Flask principale
├── simple_server.py          # Serveur simplifié
├── analyzer.py               # Analyseur vidéo
├── supabase_manager.py       # Gestionnaire Supabase
├── scheduled_scanner.py      # Scanner programmé
├── requirements.txt          # Dépendances
├── .env.example              # Exemple de configuration
├── README.md                 # Documentation
├── static/                   # Interface web
│   └── index.html
├── temp/                     # Vidéos temporaires
│   └── videos/
└── DOCUMENTATION_COMPLETE.md # Ce fichier
```

---

## 🎯 Fonctionnalités Avancées

### **1. Scanner Programmé**
```bash
python scheduled_scanner.py
```
Analyse automatique des nouveautés selon des priorités.

### **2. Comparaison Vidéo**
- Comparaison visuelle de deux vidéos
- Graphiques barres côte-à-côte
- Recommandations automatiques

### **3. Analyse Trailer vs Épisode**
- Compare un trailer avec un épisode réel
- Détecte si le trailer est trop stimulant
- Recommande ou déconseille

### **4. Interface Web Complète**
- UI moderne en HTML/CSS/JS
- Visualisation graphique des résultats
- Historique des analyses

---

## 🔮 Prochaines Évolutions

1. **Intégration TMDB** - Récupération automatique des séries populaires
2. **Cache Redis** - Mémorisation des analyses
3. **Alertes email** - Notification quand un score dépasse un seuil
4. **Batch processing** - Analyse parallèle
5. **API GraphQL** - Pour des requêtes complexes
6. **Widget embeddable** - Intégration sur des sites tiers

---

## 📚 Ressources

- **PySceneDetect** : https://www.scenedetect.com/docs/
- **Supabase** : https://supabase.com/docs
- **yt-dlp** : https://github.com/yt-dlp/yt-dlp
- **Flask** : https://flask.palletsprojects.com/

---

## 🆘 Support

Pour toute question ou problème :
1. Vérifier les logs du serveur
2. Consulter la documentation
3. Tester avec une vidéo simple d'abord

**Le système est fonctionnel et prêt à l'emploi !** ✅

---

*Dernière mise à jour : 26/02/2026 16:50*
