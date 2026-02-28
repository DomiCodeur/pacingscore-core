# PacingScore - Analyse de Pacing Vidéo

## 🎯 Objectif
PacingScore est un système d'analyse vidéo automatisé qui détecte les "cuts" de scène dans des vidéos YouTube et calcule un **score de pacing** pour évaluer si le contenu est adapté aux enfants.

---

## 🏗️ Architecture

```
PacingScore/
├── video-analyzer-service/     # Service Python Flask
│   ├── api.py                  # API REST (port 5000)
│   ├── analyzer.py             # Analyseur vidéo (PySceneDetect + OpenCV)
│   ├── supabase_manager.py     # Gestionnaire base de données
│   ├── scheduled_scanner.py    # Scanner programmé
│   ├── requirements.txt        # Dépendances Python
│   ├── .env.example            # Exemple de configuration
│   ├── static/                 # Interface web
│   │   └── index.html
│   └── temp/                   # Vidéos temporaires (à créer)
└── Supabase                    # Base de données cloud
    └── analysis_results        # Table de stockage
```

---

## 📦 Installation

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Configurer l'environnement
Copiez `.env.example` vers `.env` et remplissez vos valeurs :
```bash
cp .env.example .env
# Éditez .env avec vos valeurs réelles
```

### 3. Créer le dossier temporaire
```bash
mkdir temp
```

---

## 🚀 Lancement

### En mode développement (Flask)
```bash
# Terminal 1
python api.py
```

### En mode production (Waitress - recommandé)
```bash
# Terminal 1
set USE_WAITRESS=true
python api.py
```

### Interface web
Ouvrez votre navigateur sur :
```
http://localhost:5000
```

---

## 📡 Endpoints API

### 1. Analyser une vidéo
**POST `/analyze`**

```json
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
    "evaluation": {
        "label": "CALME",
        "description": "Cuts modérés...",
        "color": "lime"
    },
    "motion_analysis": {
        "motion_intensity": 12.5,
        "level": "Calme"
    },
    "flash_analysis": {
        "black_frames": 2,
        "flashes": 3,
        "intensity": 15.0
    }
}
```

### 2. Comparer deux vidéos
**POST `/compare`**

```json
{
    "video1_url": "https://www.youtube.com/watch?v=...",
    "video2_url": "https://www.youtube.com/watch?v=...",
    "name1": "Puffin Rock",
    "name2": "Cocomelon"
}
```

### 3. Analyser un trailer vs épisode
**POST `/analyze-trailer`**

```json
{
    "trailer_url": "https://www.youtube.com/watch?v=...",
    "episode_url": "https://www.youtube.com/watch?v=...",
    "series_title": "Nom de la série"
}
```

### 4. Récupérer l'historique
**GET `/history?limit=10`**

---

## 🧪 Tests

### Test local (vidéo de test)
```bash
python test_local.py
```

### Test API
```bash
# Avec PowerShell
$body = @{
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    max_duration = 60
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/analyze" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

### Test scan programmé
```bash
python scheduled_scanner.py
```

---

## 🔧 Fonctionnalités Avancées

### 1. Analyse du mouvement (Motion Intensity)
Calcul du flux optique avec OpenCV pour détecter les mouvements de caméra intensifs.

**Activation :**
```json
{ "analyze_motion": true }
```

**Limitation :** Analyse les 30 premières secondes pour la performance.

### 2. Détection des flashs
Détecte les passages noirs et les changements brutaux de luminosité.

**Métriques :**
- `black_frames`: Nombre de frames quasi-noires
- `flashes`: Nombre de transitions brutales
- `intensity`: Score d'intensité (0-100)

### 3. Score composite
Combine plusieurs facteurs pour un score plus précis :

```
Score = f(ASL, Mouvement, Flashs)
```

### 4. Scanner programmé
Analyse automatique des nouveautés selon des priorités :

**Priorité 1 :** Nouveautés TMDB
**Priorité 2 :** Séries avec tags "Animation" + "Bébé"
**Priorité 3 :** Séries non scannées récemment

---

## 📊 Échelle de Score

| Score | ASL (sec/plan) | Évaluation | Niveau de stimulation |
|-------|----------------|------------|----------------------|
| 0-20  | < 4s           | HYPER-STIMULANT | Très mauvais |
| 20-40 | 4-6s           | STIMULANT | Mauvais |
| 40-60 | 6-8s           | MODÉRÉ | Acceptable |
| 60-80 | 8-10s          | CALME | Bon |
| 80-100| > 10s          | TRÈS CALME | Excellent |

---

## 🔧 Configuration

### Variables d'environnement (.env)

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# API
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Analyseur
SCENEDETECT_THRESHOLD=27.0
MIN_SCENE_LEN=15
MAX_VIDEO_DURATION=120

# yt-dlp
YT_DLP_QUALITY=bestvideo[height<=480]
YT_DLP_OUTPUT_TEMPLATE=temp/%(id)s.%(ext)s

# Serveur
USE_WAITRESS=true
```

---

## 🐛 Dépannage

### Problème : yt-dlp ne télécharge pas
**Solution :** Vérifier que yt-dlp est installé :
```bash
pip install yt-dlp --upgrade
```

### Problème : Port 5000 déjà utilisé
**Solution :** Changer le port dans `.env` :
```env
FLASK_PORT=5001
```

### Problème : PySceneDetect API error
**Solution :** Vérifier la version :
```bash
pip show scenedetect
# Devrait afficher 0.6.7.1 ou plus
```

### Problème : Supabase non configuré
**Solution :** Le système fonctionne en mode "mock" sans Supabase.
Pour la production, configurez les variables `SUPABASE_URL` et `SUPABASE_ANON_KEY`.

---

## 📈 Métriques détaillées

### ASL (Average Shot Length)
Durée moyenne d'un plan en secondes.
- **Calcul :** Durée totale / Nombre de scènes détectées
- **Seuil de détection :** Configurable (défaut : 27.0)

### Intensité du mouvement
Score 0-100 basé sur le flux optique Lucas-Kanade.
- **Méthode :** Analyse des 30 premières secondes
- **Détails :** Magnitude moyenne des vecteurs de mouvement

### Détection des flashs
Changements de luminosité > 100 niveaux de gris.
- **Frames noirs :** Luminosité moyenne < 10
- **Flashs :** Variation de luminosité > 100

---

## 🔮 Prochaines évolutions

1. **Intégration TMDB** : Récupération automatique des séries populaires
2. **Cache Redis** : Mémoriser les analyses pour éviter les downloads répétés
3. **API GraphQL** : API plus flexible pour les requêtes complexes
4. **Batch processing** : Analyse parallèle de multiples vidéos
5. **Alertes email** : Notification quand une série dépasse un seuil
6. **Widget Embeddable** : Intégration sur des sites tiers

---

## 📚 Ressources

- **Documentation PySceneDetect** : https://www.scenedetect.com/docs/
- **API Supabase** : https://supabase.com/docs
- **yt-dlp documentation** : https://github.com/yt-dlp/yt-dlp/wiki

---

## 📝 Notes techniques

### Performances
- **Analyse simple** : 1-2 minutes pour une vidéo de 2 minutes
- **Avec mouvement** : +30-60 secondes pour l'analyse de flux optique
- **Téléchargement** : Dépend de la vitesse de connexion

### Limites
- YouTube peut bloquer certaines vidéos (géorestrictions)
- Les vidéos > 10 minutes sont tronquées par défaut
- Le détection de scènes dépend du seuil configuré

### Sécurité
- L'API n'a pas d'authentification (à ajouter en production)
- Les fichiers temporaires sont nettoyés après analyse
- Pas de stockage persistant des vidéos (sauf dans temp/)

---

## 💡 Exemples d'utilisation

### Pour un parent
```json
{
    "video_url": "https://www.youtube.com/watch?v=différentie_puffin_rock",
    "max_duration": 60
}
```
→ Score : 78 (TRÈS CALME) ✅ Recommandé pour les jeunes enfants

### Pour comparer Cocomelon vs Puffin Rock
```json
{
    "video1_url": "...cocomelon...",
    "video2_url": "...puffin_rock...",
    "name1": "Cocomelon",
    "name2": "Puffin Rock"
}
```
→ Cocomelon : Score 25 (STIMULANT) ❌ / Puffin Rock : Score 78 (CALME) ✅

---

**Projet développé avec ❤️ pour aider les parents**