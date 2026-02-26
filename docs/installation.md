# Installation et Configuration

## Prérequis

### 1. Outils requis sur le serveur

```bash
# yt-dlp (pour télécharger les vidéos YouTube)
# Installation :
pip install yt-dlp
# ou
brew install yt-dlp
# ou
# Télécharger depuis https://github.com/yt-dlp/yt-dlp/releases

# FFmpeg (pour analyser les vidéos)
# Installation :
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Télécharger depuis https://ffmpeg.org/download.html
```

### 2. Clés d'API nécessaires

#### TMDB (The Movie Database)
- Aller sur https://www.themoviedb.org/settings/api
- Créer une clé API (gratuite)
- Ajouter dans `application.properties`:
```
tmdb.api.key=VOTRE_CLE_TMDB
```

#### YouTube Data API v3
- Aller sur https://console.cloud.google.com/
- Créer un projet et activer YouTube Data API v3
- Créer une clé API
- Ajouter dans `application.properties`:
```
youtube.apiKey=VOTRE_CLE_YOUTUBE
```

#### Supabase
- Aller sur https://supabase.com/
- Créer un projet gratuit
- Récupérer l'URL et la clé publique
- Ajouter dans `application.properties`:
```
supabase.url=https://VOTRE-PROJET.supabase.co
supabase.key=VOTRE_CLE_SUPABASE
```

## Configuration

### Fichier application.properties

```properties
# Supabase Configuration
supabase.url=https://gjkwsrzmaecmtfozkwmw.supabase.co
supabase.key=VOTRE_CLE_SUPABASE_ICI

# TMDB Configuration
tmdb.api.key=VOTRE_CLE_TMDB_ICI
tmdb.api.url=https://api.themoviedb.org/3

# YouTube API Key
youtube.apiKey=VOTRE_CLE_YOUTUBE_ICI

# Video Analyzer Configuration
video.analyzer.temp-dir=./temp/videos
video.analyzer.max-duration=300

# Application Server
server.port=8080
spring.application.name=pacingscore

# Logging
logging.level.com.pacingscore=DEBUG
```

## Démarrage

### 1. Backend Spring Boot

```bash
cd pacingscore-clean
./mvnw spring-boot:run
```

Le backend sera accessible sur http://localhost:8080

### 2. Service Python (Optionnel - Recommandé)

```bash
cd video-analyzer-service
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

pip install -r requirements.txt
python api.py
```

Le service sera accessible sur http://localhost:5000

### 3. Frontend Angular

```bash
cd frontend
npm install
ng serve
```

Le frontend sera accessible sur http://localhost:4200

## Utilisation

### Analyser une vidéo via l'API Python

```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

### Scan automatique des dessins animés

```bash
curl -X POST http://localhost:8080/api/analysis/scan-tmdb
```

### Interface Admin

Aller sur http://localhost:4200/admin

## Variables d'environnement (Production)

Pour le déploiement, utilisez les variables d'environnement :

```bash
export SUPABASE_URL=https://gjkwsrzmaecmtfozkwmw.supabase.co
export SUPABASE_KEY=votre_cle_supabase
export TMDB_API_KEY=votre_cle_tmdb
export YOUTUBE_API_KEY=votre_cle_youtube
```

## Docker

```dockerfile
FROM openjdk:17-jdk-slim

RUN apt-get update && apt-get install -y ffmpeg python3-pip
RUN pip install yt-dlp

WORKDIR /app
COPY target/pacingscore-*.jar app.jar

EXPOSE 8080

CMD ["java", "-jar", "app.jar"]
```