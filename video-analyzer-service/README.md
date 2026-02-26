# PacingScore Video Analyzer Service

Service Python pour l'analyse réelle des cuts de scène avec **PySceneDetect** et **FFmpeg**.

## 🎯 Principe

L'analyse se base sur l'**ASL (Average Shot Length)** - la durée moyenne d'un plan :
- **ASL < 4s** → Très stimulant (mauvais pour les enfants)
- **ASL 4-9s** → Stimulant
- **ASL 9-14s** → Calme (bon)
- **ASL > 14s** → Très calme (excellent)

## 📦 Installation

### 1. Python et dépendances

```bash
# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### 2. FFmpeg (requis pour PySceneDetect)

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Télécharger depuis https://ffmpeg.org/download.html
# et ajouter au PATH
```

### 3. yt-dlp (pour télécharger les vidéos YouTube)

```bash
pip install yt-dlp
# ou
sudo apt install yt-dlp  # Ubuntu/Debian
# ou
brew install yt-dlp  # macOS
```

## 🚀 Utilisation

### API Flask (Service en ligne)

```bash
# Démarrer le serveur
python api.py

# Le service sera accessible sur http://localhost:5000
```

#### Endpoints

**1. Analyser une vidéo YouTube**

```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

**2. Analyser un trailer depuis TMDB**

```bash
curl -X POST http://localhost:5000/analyze-from-trailer \
  -H "Content-Type: application/json" \
  -d '{
    "trailer_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "series_title": "Babar"
  }'
```

**3. Scanner des séries depuis TMDB**

```bash
python tmdb_trailer_analyzer.py
```

## 📊 Format des résultats

```json
{
  "success": true,
  "series_title": "Babar",
  "tmdb_id": 12345,
  "trailer_url": "https://www.youtube.com/watch?v=...",
  "video_duration": 125.5,
  "num_scenes": 42,
  "average_shot_length": 10.2,
  "pacing_score": 85.0,
  "evaluation": {
    "label": "TRÈS CALME",
    "description": "Cuts rares (10-14s). Idéal pour les tout-petits.",
    "color": "green"
  }
}
```

## 🔧 Architecture

```
video-analyzer-service/
├── analyzer.py          # Coeur de l'analyse (PySceneDetect)
├── api.py               # API Flask
├── tmdb_trailer_analyzer.py  # Analyseur TMDB
├── requirements.txt     # Dépendances Python
└── README.md           # Ce fichier
```

## 🎬 Workflow complet

### 1. Récupération depuis TMDB

```python
# tmdb_trailer_analyzer.py
analyzer = TMDBTrailerAnalyzer("VOTRE_CLE_TMDB")
results = analyzer.scan_popular_shows(genre_ids=[16, 10751], max_shows=5)
```

### 2. Téléchargement du trailer

```
yt-dlp --format worst[height<=480] --download-sections "*0:00-2:00" [URL]
```

### 3. Analyse avec PySceneDetect

```python
from scenedetect import detect, ContentDetector

scene_list = detect(video_path, ContentDetector(threshold=27.0))
num_scenes = len(scene_list)
total_duration = get_duration(video_path)
asl = total_duration / num_scenes
```

### 4. Calcul du score

```
ASL = Durée totale / Nombre de scènes

Score = 100 - (facteur × ASL bas)

Exemple:
ASL = 10s → Score = 100
ASL = 2s  → Score = 20
```

## 🔗 Intégration avec Spring Boot

### Configuration backend

```yaml
# application.properties
video.analyzer.url=http://localhost:5000
video.analyzer.enabled=true
```

### Appel depuis Spring Boot

```java
@Service
public class VideoAnalysisService {
    
    @Value("${video.analyzer.url}")
    private String analyzerUrl;
    
    public VideoAnalysisResult analyzeVideo(String videoUrl) {
        // Appel API Python
        String requestBody = "{\"video_url\": \"" + videoUrl + "\"}";
        
        // Retourner les résultats
        return restTemplate.postForObject(
            analyzerUrl + "/analyze",
            requestBody,
            VideoAnalysisResult.class
        );
    }
}
```

## ⚙️ Paramètres

### Seuil de détection (threshold)

- **20-25** : Détecte plus de scènes (plus sensible)
- **27** : Valeur par défaut (équilibrée)
- **30-35** : Détecte moins de scènes (moins sensible)

### Durée d'analyse

- **2 minutes** : Suffisant pour détecter le style de montage
- **Plus = meilleur** mais plus long à télécharger

## 🎯 Métriques d'évaluation

| ASL (s) | Score | Évaluation |
|---------|-------|------------|
| < 4 | < 25 | 🔴 Très stimulant |
| 4-6 | 25-45 | 🟠 Stimulant |
| 6-8 | 45-65 | 🟡 Modéré |
| 8-10 | 65-80 | 🟢 Calme |
| 10-14 | 80-95 | 🟢 Très calme |
| > 14 | > 95 | 🟢 Contemplatif |

## ⚠️ Limitations

### Légalité
- yt-dlp respecte les conditions d'utilisation YouTube
- Téléchargement limité à des fins d'analyse non commerciale
- Pour usage commercial, consulter un avocat

### Performance
- Analyse d'une vidéo : 30-60 secondes
- Téléchargement : dépend de la vitesse réseau
- Espace disque : ~50MB par vidéo (nettoyé automatiquement)

### Précision
- L'analyse de la bande-annonce est représentative du style de la série
- Les séries sans trailer ne peuvent pas être analysées
- L'ASL est une métrique objective mais ne capture pas tout

## 🔮 Évolutions possibles

- [ ] Analyse du motion blur (flou de mouvement)
- [ ] Détection des flashs et saturation lumineuse
- [ ] Intégration des retours utilisateurs
- [ ] Analyse du volume sonore
- [ ] Modèle ML pour prédire l'impact sur les enfants

## 📚 Ressources

- [PySceneDetect Documentation](https://pyscenedetect.readthedocs.io/)
- [FFmpeg Scene Detection](https://ffmpeg.org/ffmpeg-filters.html#select-1)
- [TMDB API Documentation](https://developers.themoviedb.org/3)
- [ASL Standard Industry](https://en.wikipedia.org/wiki/Average_shot_length)

## 🐛 Dépannage

### PySceneDetect non installé
```bash
pip install pyscenedetect
```

### FFmpeg non trouvé
```bash
ffmpeg -version
# Si pas installé: sudo apt install ffmpeg
```

### Erreur yt-dlp
```bash
yt-dlp --version
# Mettre à jour: pip install --upgrade yt-dlp
```

### Problèmes de permissions
```bash
# Créer le dossier temporaire
mkdir -p ./temp/videos
chmod 755 ./temp/videos
```