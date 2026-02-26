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
supabase.key=sb_publishable_2vEhYPJjXxrqyZRbYU2kSg_20NSSJ2t

# TMDB Configuration
tmdb.api.key=65a5c670b9644a800c3d59f2885d4d4f
tmdb.api.url=https://api.themoviedb.org/3

# YouTube API Key
youtube.apiKey=AIzaSyD8Rfq5Oj8flv-Y5IazqD0N2P7G7BqM7mM

# Video Analyzer Configuration
video.analyzer.temp-dir=./temp/videos
video.analyzer.max-duration=300

# Application Server
server.port=8080
spring.application.name=pacingscore

# Logging
logging.level.com.pacingscore=DEBUG
```

### Schema Supabase

Exécuter dans l'éditeur SQL Supabase :

```sql
CREATE TABLE video_analyses (
    id BIGSERIAL PRIMARY KEY,
    video_id INTEGER UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    thumbnail_url TEXT,
    video_url TEXT,
    pacing_score FLOAT,
    age_rating VARCHAR(10),
    duration_minutes INTEGER,
    cuts_per_minute FLOAT,
    total_cuts INTEGER,
    tmdb_id INTEGER,
    tmdb_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour la recherche
CREATE INDEX idx_video_analyses_pacing_score ON video_analyses(pacing_score DESC);
CREATE INDEX idx_video_analyses_age_rating ON video_analyses(age_rating);
CREATE INDEX idx_video_analyses_title ON video_analyses(title);

-- Vue pour les recommandations
CREATE OR REPLACE VIEW video_recommendations AS
SELECT 
    *,
    CASE 
        WHEN pacing_score >= 90 THEN 'Très calme - Parfait pour les tout-petits'
        WHEN pacing_score >= 70 THEN 'Calme - Bon rythme adapté'
        WHEN pacing_score >= 50 THEN 'Modéré - À surveiller'
        WHEN pacing_score >= 30 THEN 'Stimulant - Attention au rythme'
        ELSE 'Très stimulant - Peut être trop intense'
    END AS pacing_label
FROM video_analyses
ORDER BY pacing_score DESC, created_at DESC;
```

## Démarrage

### 1. Backend Spring Boot

```bash
cd pacingscore-clean
./mvnw spring-boot:run
```

Le backend sera accessible sur http://localhost:8080

### 2. Frontend Angular

```bash
cd frontend
npm install
ng serve
```

Le frontend sera accessible sur http://localhost:4200

## Utilisation

### 1. Analyse d'une vidéo spécifique

```bash
POST /api/video-analysis/analyze
```

Paramètre :
- `videoUrl` : URL YouTube de la vidéo à analyser

Exemple :
```bash
curl -X POST "http://localhost:8080/api/video-analysis/analyze?videoUrl=https://www.youtube.com/watch?v=VIDEO_ID"
```

### 2. Scan automatique des dessins animés TMDB

```bash
POST /api/analysis/scan-tmdb
```

Ce endpoint scanne les dessins animés pour enfants sur TMDB et :
- Télécharge les premières 5 minutes
- Analyse les cuts de scène avec FFmpeg
- Calcule le score de calme
- Sauvegarde dans Supabase

### 3. Interface Admin

Aller sur http://localhost:4200/admin

## Limitations

### Espace disque
- Chaque analyse télécharge ~5-10MB de vidéo temporaire
- Le nettoyage est automatique mais nécessite de l'espace disponible
- Recommandation : 10GB d'espace libre minimum

### Performance
- Analyse d'une vidéo : ~30-60 secondes
- Scan complet TMDB : plusieurs heures (dépend du nombre de séries)
- Limite d'API YouTube : 10 000 requêtes/jour (gratuit)

### Légalité
- yt-dlp respecte les conditions d'utilisation YouTube
- Téléchargement limité à des fins d'analyse non commerciale
- Pour usage commercial, consulter un avocat

## Problèmes courants

### yt-dlp non trouvé
```bash
# Vérifier l'installation
yt-dlp --version

# Ajouter au PATH si nécessaire
export PATH=$PATH:/chemin/vers/yt-dlp
```

### FFmpeg non trouvé
```bash
# Vérifier l'installation
ffmpeg -version

# Ajouter au PATH
export PATH=$PATH:/chemin/vers/ffmpeg
```

### Erreurs YouTube API
- Vérifier que votre clé API est valide
- Vérifier que l'API YouTube Data v3 est activée
- Vérifier les quotas (10 000 requêtes/jour gratuit)

## Déploiement

### Variables d'environnement

Pour la production, utilisez les variables d'environnement au lieu de `application.properties` :

```bash
export SUPABASE_URL=https://...
export SUPABASE_KEY=...
export TMDB_API_KEY=...
export YOUTUBE_API_KEY=...
```

### Docker

```dockerfile
FROM openjdk:17-jdk-slim

RUN apt-get update && apt-get install -y ffmpeg python3-pip
RUN pip install yt-dlp

WORKDIR /app
COPY target/pacingscore-*.jar app.jar

EXPOSE 8080

CMD ["java", "-jar", "app.jar"]
```

### Services cloud

- **Google Cloud** : VM avec FFmpeg et yt-dlp
- **AWS** : EC2 instance avec les outils installés
- **Heroku** : Pas idéal (limites d'espace et de temps)
- **DigitalOcean** : Droplet recommandé (1GB RAM minimum)