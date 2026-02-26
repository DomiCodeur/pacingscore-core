# 🛡️ PacingScore - Kids Protection

Video pacing analysis engine for children's content safety - **Analyse réelle des cuts de scène**.

## ⚠️ IMPORTANT - Configuration Requise

Ce projet nécessite une configuration de clés API. **NE PAS** commiter le fichier `application.properties` avec des clés réelles.

### Installation rapide

```bash
# 1. Cloner le repo
git clone https://github.com/DomiCodeur/pacingscore-core.git
cd pacingscore-core

# 2. Créer application.properties avec vos clés
cp src/main/resources/application.properties.example src/main/resources/application.properties
# Editer le fichier pour ajouter vos clés API

# 3. Vérifier .gitignore est configuré
cat .gitignore | grep application.properties
```

### Fichier application.properties requis

```properties
# Application local - À créer manuellement
# Le fichier example est fourni sans clés

supabase.url=https://gjkwsrzmaecmtfozkwmw.supabase.co
supabase.key=VOTRE_CLE_SUPABASE

tmdb.api.key=VOTRE_CLE_TMDB
tmdb.api.url=https://api.themoviedb.org/3

youtube.apiKey=VOTRE_CLE_YOUTUBE

server.port=8080
spring.application.name=pacingscore
```

## 🌟 La Vision

**PacingScore** est le "Yuka" des contenus jeunesse. L'objectif est de protéger la santé cognitive des enfants en offrant aux parents un indicateur clair sur le niveau de stimulation visuelle des dessins animés.

**Innovation technique** : Le système utilise **FFmpeg + yt-dlp** pour analyser réellement les vidéos et détecter la fréquence des cuts de scène (changements de scène), pas seulement les médonnées.

**Référence** : Les séries sont récupérées via **TMDB** (themoviedb.org/u/devrick) puis analysées en temps réel.

## 🎯 Méthodologie : Analyse Réelle des Cuts de Scène

### ASL (Average Shot Length) - Durée Moyenne des Plans

```
ASL = Durée totale de la vidéo / Nombre de scènes détectées
```

Plus l'ASL est élevée, plus le contenu est calme et adapté aux enfants.

### Échelle d'évaluation

| ASL (secondes) | Score | Évaluation | Description |
|----------------|-------|------------|-------------|
| < 4 | < 25% | 🔴 Très stimulant | Cuts extrêmement fréquents |
| 4-6 | 25-45% | 🟠 Stimulant | Cuts fréquents |
| 6-8 | 45-65% | 🟡 Modéré | Cuts normaux |
| 8-10 | 65-80% | 🟢 Calme | Cuts modérés |
| 10-14 | 80-95% | 🟢 Très calme | Cuts rares |
| > 14 | > 95% | 🟢 Contemplatif | Cuts très rares |

### Exemples Concrets

| Dessin animé | ASL | Score | Évaluation |
|-------------|-----|-------|------------|
| **Cocomelon** | ~2-3s | 5-15% | 🔴 Très stimulant |
| **Baby Shark** | ~1-2s | 2-5% | 🔴 Extrêmement stimulant |
| **Babar** | ~12-15s | 85-95% | 🟢 Très calme |
| **Totoro** | ~15-20s | 95-98% | 🟢 Contemplatif |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Frontend Angular 18                             │
└─────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Spring Boot Backend (Java)                        │
│  Orchestration: Récupère séries TMDB → Appelle service Python          │
└─────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  Video Analyzer Service (Python)                         │
│  - API Flask (port 5000)                                                │
│  - PySceneDetect + FFmpeg pour détecter les cuts                        │
│  - ASL = Durée totale / Nombre de scènes                                │
└─────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     Supabase (PostgreSQL)                                │
└─────────────────────────────────────────────────────────────────────────┘
```

## 🚀 Installation

### Prérequis

```bash
# FFmpeg (pour l'analyse vidéo)
# Ubuntu: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg
# Windows: https://ffmpeg.org/download.html

# yt-dlp (pour télécharger les vidéos YouTube)
pip install yt-dlp
```

### Service Python (Analyse vidéo)

```bash
cd video-analyzer-service
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

pip install -r requirements.txt
python api.py
# Le service est maintenant sur http://localhost:5000
```

### Backend Spring Boot

```bash
# Dans le dossier racine
./mvnw spring-boot:run
# Le backend est sur http://localhost:8080
```

### Frontend Angular

```bash
cd frontend
npm install
ng serve
# L'interface est sur http://localhost:4200
```

## 🔧 Utilisation

### 1. Analyse d'une vidéo YouTube

```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

### 2. Scan TMDB (automatique)

```bash
curl -X POST http://localhost:8080/api/analysis/scan-tmdb
```

### 3. Interface Admin

Aller sur http://localhost:4200/admin pour :
- Lancer le scan TMDB
- Analyser des vidéos individuelles
- Voir les résultats

## 📁 Structure du projet

```
pacingscore-core/
├── frontend/                    # Angular 18
├── src/main/java/               # Spring Boot Backend
├── video-analyzer-service/      # Service Python
│   ├── analyzer.py             # PySceneDetect + ASL
│   ├── api.py                  # API Flask
│   ├── tmdb_trailer_analyzer.py
│   ├── requirements.txt
│   └── README.md
├── docs/                        # Documentation
│   ├── SECURITY.md             # Politique de sécurité
│   └── installation.md
└── README.md
```

## 🔐 Sécurité

⚠️ **IMPORTANT** : Lire `docs/SECURITY.md` avant toute contribution.

- Toujours utiliser `application.properties.example` comme référence
- Ne JAMAIS commiter de clés API
- Utiliser les variables d'environnement en production
- Renouveler immédiatement toute clé exposée

## 📊 Technologies

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| Backend | Spring Boot 3 | Orchestration |
| Analyse vidéo | Python + PySceneDetect | Détection cuts |
| Téléchargement | yt-dlp | Vidéos YouTube |
| Analyse image | FFmpeg | Détecteur de scènes |
| Frontend | Angular 18 | Interface |
| BDD | Supabase (PostgreSQL) | Persistance |
| API Films | TMDB | Base données séries |
| API YouTube | YouTube Data v3 | Métadonnées |

## 🎯 Fonctionnalités

- ✅ Analyse réelle des cuts de scène avec PySceneDetect
- ✅ Métrique ASL (Average Shot Length)
- ✅ Score basé sur la fréquence réelle des changements
- ✅ Récupération automatique depuis TMDB
- ✅ Interface Netflix-like pour les parents
- ✅ Détection d'âge recommandé (0+, 3+, 6+, 10+, 14+)
- ✅ Stockage persistant dans Supabase

## 📚 Documentation

- [SECURITY.md](docs/SECURITY.md) - Politique de sécurité
- [installation.md](docs/installation.md) - Guide d'installation
- [video-analysis-technical-spec.md](docs/video-analysis-technical-spec.md) - Spécifications techniques

## 🔗 Liens

- [GitHub](https://github.com/DomiCodeur/pacing-score-core)
- [TMDB](https://www.themoviedb.org/u/devrick)
- [ClawHub](https://clawhub.com)

---

**Projet développé pour protéger la santé cognitive des enfants** 🛡️